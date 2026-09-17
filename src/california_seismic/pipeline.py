"""Run source ingestion, cleaning, validation, integration, and output."""

import argparse
import platform
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any
from uuid import uuid4

import pyarrow

from . import __version__
from .artifacts import (
    artifact_record,
    fingerprint,
    publish_artifacts,
    write_json,
    write_json_atomic,
)
from .cleaning import (
    add_dataset_review_flags,
    add_review_flags,
    normalize_columns,
    parse_values,
)
from .ingestion import read_source_csv
from .integration import JoinAudit, join_sources
from .schema import (
    BUILDING_SCHEMA,
    BUILDING_COLUMNS,
    OUTPUT_COLUMNS,
    SCHEMA_VERSION,
    SEISMIC_COLUMNS,
    SEISMIC_SCHEMA,
    Scalar,
    SourceSchema,
    default_interim_dir,
    default_processed_dir,
    default_raw_dir,
)
from .storage import read_parquet, write_parquet
from .validation import (
    DEFAULT_VALIDATION_CONFIG,
    ValidationConfig,
    summarize_review_flags,
    validate_keys,
    validate_required_columns,
    validate_value_ranges,
)


@dataclass(frozen=True)
class PipelineResult:
    run_id: str
    building_interim: Path
    seismic_interim: Path
    output_parquet: Path
    validation_report: Path
    completion_manifest: Path
    rows_written: int
    join_audit: JoinAudit


def load_clean_validate(
    path: Path,
    schema: SourceSchema,
    validation_config: ValidationConfig = DEFAULT_VALIDATION_CONFIG,
) -> list[dict[str, Scalar]]:
    rows = read_source_csv(path, schema)
    normalized = normalize_columns(rows, schema)
    parsed = parse_values(normalized, schema.name)
    validate_required_columns(parsed, schema)
    validate_keys(parsed, schema.name)
    validate_value_ranges(parsed, schema.name, validation_config)
    return parsed


def run_pipeline(
    raw_dir: Path,
    interim_dir: Path,
    processed_dir: Path,
    validation_config: ValidationConfig = DEFAULT_VALIDATION_CONFIG,
) -> PipelineResult:
    run = _run_metadata(validation_config)
    run_id = str(run["run_id"])
    source_paths = {
        "hospital_building": raw_dir / BUILDING_SCHEMA.filename,
        "seismic_ratings": raw_dir / SEISMIC_SCHEMA.filename,
    }
    inputs: dict[str, dict[str, str | int]] = {}

    building_interim = interim_dir / "hospital_buildings_clean.parquet"
    seismic_interim = interim_dir / "seismic_ratings_clean.parquet"
    output_parquet = processed_dir / "hospital_buildings_integrated.parquet"
    validation_report = processed_dir / "hospital_buildings_validation.json"
    completion_manifest = processed_dir / "hospital_buildings_manifest.json"

    try:
        interim_dir.mkdir(parents=True, exist_ok=True)
        processed_dir.mkdir(parents=True, exist_ok=True)
        _require_same_filesystem(interim_dir, processed_dir)
        inputs = {
            name: fingerprint(path, relative_to=processed_dir)
            for name, path in source_paths.items()
        }

        building = load_clean_validate(
            source_paths["hospital_building"], BUILDING_SCHEMA, validation_config
        )
        seismic = load_clean_validate(
            source_paths["seismic_ratings"], SEISMIC_SCHEMA, validation_config
        )
        _validate_input_fingerprints(source_paths, inputs, processed_dir)

        with tempfile.TemporaryDirectory(
            prefix=f".hospital-seismic-{run_id}-", dir=processed_dir.parent
        ) as temporary:
            staging_dir = Path(temporary)
            staged_building = staging_dir / building_interim.name
            staged_seismic = staging_dir / seismic_interim.name
            staged_output = staging_dir / output_parquet.name
            staged_report = staging_dir / validation_report.name

            write_parquet(staged_building, building, BUILDING_COLUMNS)
            write_parquet(staged_seismic, seismic, SEISMIC_COLUMNS)

            persisted_building = read_parquet(staged_building, BUILDING_COLUMNS)
            persisted_seismic = read_parquet(staged_seismic, SEISMIC_COLUMNS)
            integrated, audit = join_sources(persisted_building, persisted_seismic)
            integrated = [add_review_flags(row) for row in integrated]
            integrated = add_dataset_review_flags(integrated)
            validate_keys(integrated, "integrated")
            validate_value_ranges(integrated, "integrated", validation_config)
            _validate_output_schema(integrated)

            write_parquet(staged_output, integrated, OUTPUT_COLUMNS)
            _write_report(staged_report, integrated, audit, run, inputs)

            artifacts = [
                (staged_building, building_interim),
                (staged_seismic, seismic_interim),
                (staged_output, output_parquet),
                (staged_report, validation_report),
            ]
            artifact_metadata = {
                "building_interim": artifact_record(
                    staged_building,
                    building_interim,
                    relative_to=processed_dir,
                ),
                "seismic_interim": artifact_record(
                    staged_seismic,
                    seismic_interim,
                    relative_to=processed_dir,
                ),
                "integrated_dataset": artifact_record(
                    staged_output,
                    output_parquet,
                    relative_to=processed_dir,
                ),
                "validation_report": artifact_record(
                    staged_report,
                    validation_report,
                    relative_to=processed_dir,
                ),
            }
            manifest = {
                "status": "complete",
                "completed_at_utc": _utc_now(),
                "run": run,
                "inputs": inputs,
                "artifacts": artifact_metadata,
            }
            publish_artifacts(
                artifacts, completion_manifest, manifest, staging_dir
            )

        return PipelineResult(
            run_id=run_id,
            building_interim=building_interim,
            seismic_interim=seismic_interim,
            output_parquet=output_parquet,
            validation_report=validation_report,
            completion_manifest=completion_manifest,
            rows_written=len(integrated),
            join_audit=audit,
        )
    except Exception as exc:
        _record_failure(processed_dir, run, inputs, exc)
        raise


def _validate_output_schema(rows: list[dict[str, Scalar]]) -> None:
    expected = set(OUTPUT_COLUMNS)
    for index, row in enumerate(rows, start=2):
        if set(row) != expected:
            raise ValueError(
                f"Integrated row {index} has unexpected output schema; "
                f"missing={sorted(expected - set(row))}, "
                f"unexpected={sorted(set(row) - expected)}"
            )


def _write_report(
    path: Path,
    rows: list[dict[str, Scalar]],
    audit: JoinAudit,
    run: dict[str, Any],
    inputs: dict[str, dict[str, str | int]],
) -> None:
    report = {
        "status": "passed",
        "run": run,
        "inputs": inputs,
        "rows_written": len(rows),
        "unique_facilities": len({row["facility_id"] for row in rows}),
        "unique_buildings": len({row["building_id"] for row in rows}),
        "join": audit.as_dict(),
        "blank_values": {
            column: sum(row[column] in (None, "") for row in rows)
            for column in OUTPUT_COLUMNS
            if column != "review_flags"
        },
        "review_flags": summarize_review_flags(rows),
        "notes": [
            "No records were filtered from the integrated output.",
            "Review flags identify questionable or out-of-scope values without correcting them.",
            "The modeling population and target have not yet been selected.",
        ],
    }
    write_json(path, report)


def _run_metadata(validation_config: ValidationConfig) -> dict[str, Any]:
    return {
        "run_id": f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid4().hex[:8]}",
        "started_at_utc": _utc_now(),
        "package_version": __version__,
        "package_code_sha256": _package_code_sha256(),
        "schema_version": SCHEMA_VERSION,
        "python_version": platform.python_version(),
        "pyarrow_version": pyarrow.__version__,
        "validation_config": asdict(validation_config),
    }


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _package_code_sha256() -> str:
    package_root = Path(__file__).resolve().parent
    digest = sha256()
    for path in sorted(package_root.rglob("*.py")):
        digest.update(str(path.relative_to(package_root)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _require_same_filesystem(interim_dir: Path, processed_dir: Path) -> None:
    if interim_dir.stat().st_dev != processed_dir.stat().st_dev:
        raise RuntimeError(
            "Interim and processed directories must share a filesystem for atomic publication"
        )


def _validate_input_fingerprints(
    paths: dict[str, Path],
    expected: dict[str, dict[str, str | int]],
    relative_to: Path,
) -> None:
    observed = {
        name: fingerprint(path, relative_to=relative_to)
        for name, path in paths.items()
    }
    if observed != expected:
        raise RuntimeError("A source file changed while the pipeline was reading it")


def _record_failure(
    processed_dir: Path,
    run: dict[str, Any],
    inputs: dict[str, dict[str, str | int]],
    error: Exception,
) -> None:
    failure_path = processed_dir / f"hospital_buildings_failure_{run['run_id']}.json"
    payload: dict[str, Any] = {
        "status": "failed",
        "failed_at_utc": _utc_now(),
        "run": run,
        "inputs": inputs,
        "error": {"type": type(error).__name__, "message": str(error)},
    }
    diagnostics = getattr(error, "diagnostics", None)
    if diagnostics is not None:
        payload["diagnostics"] = diagnostics
    try:
        write_json_atomic(failure_path, payload)
    except Exception as reporting_error:
        error.add_note(f"Could not write failure report: {reporting_error}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=default_raw_dir())
    parser.add_argument("--interim-dir", type=Path, default=default_interim_dir())
    parser.add_argument("--processed-dir", type=Path, default=default_processed_dir())
    args = parser.parse_args()
    result = run_pipeline(
        args.raw_dir.resolve(),
        args.interim_dir.resolve(),
        args.processed_dir.resolve(),
    )
    print(f"Wrote {result.rows_written:,} rows to {result.output_parquet}")
    print(f"Validation report: {result.validation_report}")
    print(f"Completion manifest: {result.completion_manifest}")


if __name__ == "__main__":
    main()
