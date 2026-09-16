"""Run source ingestion, cleaning, validation, integration, and output."""

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from .cleaning import normalize_columns, parse_values
from .cleaning.values import Scalar
from .ingestion import read_source_csv
from .integration import JoinAudit, join_sources
from .schema import (
    BUILDING_SCHEMA,
    BUILDING_COLUMNS,
    OUTPUT_COLUMNS,
    SEISMIC_COLUMNS,
    SEISMIC_SCHEMA,
    SourceSchema,
    default_interim_dir,
    default_processed_dir,
    default_raw_dir,
)
from .storage import read_parquet, write_parquet
from .validation import (
    summarize_review_flags,
    validate_keys,
    validate_required_columns,
    validate_value_ranges,
)


@dataclass(frozen=True)
class PipelineResult:
    building_interim: Path
    seismic_interim: Path
    output_parquet: Path
    validation_report: Path
    rows_written: int
    join_audit: JoinAudit


def load_clean_validate(path: Path, schema: SourceSchema) -> list[dict[str, Scalar]]:
    rows = read_source_csv(path, schema)
    normalized = normalize_columns(rows, schema)
    parsed = parse_values(normalized)
    validate_required_columns(parsed, schema)
    validate_keys(parsed, schema.name)
    validate_value_ranges(parsed, schema.name)
    return parsed


def run_pipeline(raw_dir: Path, interim_dir: Path, processed_dir: Path) -> PipelineResult:
    building = load_clean_validate(raw_dir / BUILDING_SCHEMA.filename, BUILDING_SCHEMA)
    seismic = load_clean_validate(raw_dir / SEISMIC_SCHEMA.filename, SEISMIC_SCHEMA)

    building_interim = interim_dir / "hospital_buildings_clean.parquet"
    seismic_interim = interim_dir / "seismic_ratings_clean.parquet"
    write_parquet(building_interim, building, BUILDING_COLUMNS)
    write_parquet(seismic_interim, seismic, SEISMIC_COLUMNS)

    building = read_parquet(building_interim, BUILDING_COLUMNS)
    seismic = read_parquet(seismic_interim, SEISMIC_COLUMNS)
    integrated, audit = join_sources(building, seismic)
    validate_keys(integrated, "integrated")
    validate_value_ranges(integrated, "integrated")
    _validate_output_schema(integrated)

    output_parquet = processed_dir / "hospital_buildings_integrated.parquet"
    validation_report = processed_dir / "hospital_buildings_validation.json"
    write_parquet(output_parquet, integrated, OUTPUT_COLUMNS)
    _write_report(validation_report, integrated, audit)
    return PipelineResult(
        building_interim=building_interim,
        seismic_interim=seismic_interim,
        output_parquet=output_parquet,
        validation_report=validation_report,
        rows_written=len(integrated),
        join_audit=audit,
    )


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
    path: Path, rows: list[dict[str, Scalar]], audit: JoinAudit
) -> None:
    report = {
        "status": "passed",
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
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


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


if __name__ == "__main__":
    main()
