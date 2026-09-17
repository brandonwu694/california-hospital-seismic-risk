import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from california_seismic.artifacts import ArtifactError, verify_manifest
from california_seismic.integration import JoinValidationError
from california_seismic.pipeline import run_pipeline
from california_seismic.schema import (
    BUILDING_COLUMNS,
    BUILDING_SCHEMA,
    OUTPUT_COLUMNS,
    SEISMIC_COLUMNS,
    SEISMIC_SCHEMA,
)
from california_seismic.storage import read_parquet


CANONICAL_SHARED = {
    "county_code": "01 - Alameda",
    "facility_id": "00123",
    "facility_name": "Example Hospital",
    "city": "Example City",
    "building_id": "BLD-00001",
    "building_name": "Main Building",
    "building_status": "OSHPD 1-In Service",
    "spc_rating": "3",
    "ab_1882_notice": "",
    "latitude": "37.7",
    "longitude": "-122.2",
    "record_count": "1",
}


class PipelineTests(unittest.TestCase):
    def test_end_to_end_pipeline_writes_validated_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            raw, interim, processed = self._write_fixture(root)

            result = run_pipeline(raw, interim, processed)

            self.assertEqual(result.rows_written, 1)
            self.assertTrue(result.building_interim.is_file())
            self.assertTrue(result.seismic_interim.is_file())
            self.assertEqual(
                read_parquet(result.building_interim, BUILDING_COLUMNS)[0]["facility_id"],
                "00123",
            )
            self.assertEqual(
                read_parquet(result.seismic_interim, SEISMIC_COLUMNS)[0]["facility_id"],
                "00123",
            )
            output = read_parquet(result.output_parquet, OUTPUT_COLUMNS)
            self.assertEqual(output[0]["facility_id"], "00123")
            self.assertEqual(output[0]["spc_rating"], "3")
            self.assertEqual(output[0]["review_flags"], "zero_height")
            self.assertEqual(output[0]["stories"], 2)
            self.assertIsInstance(output[0]["height_ft"], float)
            self.assertIsNone(output[0]["hazus_2010_pct"])

            report = json.loads(result.validation_report.read_text())
            self.assertEqual(report["status"], "passed")
            self.assertEqual(report["join"]["matched_rows"], 1)
            self.assertEqual(report["blank_values"]["hazus_2010_pct"], 1)
            self.assertEqual(report["run"]["run_id"], result.run_id)
            self.assertEqual(report["run"]["schema_version"], 1)
            self.assertEqual(len(report["run"]["package_code_sha256"]), 64)
            self.assertIn("sha256", report["inputs"]["hospital_building"])
            self.assertEqual(
                report["inputs"]["hospital_building"]["path"],
                f"../raw/{BUILDING_SCHEMA.filename}",
            )

            manifest = json.loads(result.completion_manifest.read_text())
            self.assertEqual(manifest["status"], "complete")
            self.assertEqual(manifest["run"]["run_id"], result.run_id)
            self.assertEqual(len(manifest["artifacts"]), 4)
            verify_manifest(result.completion_manifest)

            result.output_parquet.write_bytes(b"tampered")
            with self.assertRaisesRegex(ArtifactError, "does not match manifest"):
                verify_manifest(result.completion_manifest)

    def test_join_failure_preserves_previous_completed_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            raw, interim, processed = self._write_fixture(root)
            seismic_path = raw / SEISMIC_SCHEMA.filename
            with seismic_path.open(encoding="cp1252", newline="") as handle:
                rows = list(csv.DictReader(handle))
            rows[0]["City"] = "Different City"
            with seismic_path.open("w", encoding="cp1252", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=SEISMIC_SCHEMA.column_map)
                writer.writeheader()
                writer.writerows(rows)

            sentinels = self._seed_previous_run(interim, processed)
            with self.assertRaises(JoinValidationError):
                run_pipeline(raw, interim, processed)

            self._assert_previous_run_unchanged(sentinels)
            failures = list(processed.glob("hospital_buildings_failure_*.json"))
            self.assertEqual(len(failures), 1)
            failure = json.loads(failures[0].read_text())
            self.assertEqual(failure["status"], "failed")
            self.assertEqual(failure["diagnostics"]["audit"]["shared_field_mismatches"], 1)

    def test_report_failure_does_not_publish_staged_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            raw, interim, processed = self._write_fixture(root)
            sentinels = self._seed_previous_run(interim, processed)

            with patch(
                "california_seismic.pipeline._write_report",
                side_effect=OSError("simulated report failure"),
            ):
                with self.assertRaisesRegex(OSError, "simulated report failure"):
                    run_pipeline(raw, interim, processed)

            self._assert_previous_run_unchanged(sentinels)
            failures = list(processed.glob("hospital_buildings_failure_*.json"))
            self.assertEqual(len(failures), 1)

    def _write_fixture(self, root: Path) -> tuple[Path, Path, Path]:
        raw = root / "raw"
        interim = root / "interim"
        processed = root / "processed"
        raw.mkdir()
        building = CANONICAL_SHARED | {
            "building_url": "https://example.test/building",
            "height_ft": "0",
            "stories": "2",
            "building_code": "1998 California Building Code (CBC)",
            "building_code_year": "1998",
            "year_completed": "2001",
        }
        seismic = CANONICAL_SHARED | {
            "hazus_2007_pct": "0.5",
            "hazus_2010_pct": "",
            "npc_rating": "4",
        }
        self._write_source(
            raw / BUILDING_SCHEMA.filename, BUILDING_SCHEMA.column_map, building
        )
        self._write_source(
            raw / SEISMIC_SCHEMA.filename, SEISMIC_SCHEMA.column_map, seismic
        )
        return raw, interim, processed

    @staticmethod
    def _seed_previous_run(interim: Path, processed: Path) -> dict[Path, bytes]:
        interim.mkdir()
        processed.mkdir()
        paths = [
            interim / "hospital_buildings_clean.parquet",
            interim / "seismic_ratings_clean.parquet",
            processed / "hospital_buildings_integrated.parquet",
            processed / "hospital_buildings_validation.json",
            processed / "hospital_buildings_manifest.json",
        ]
        sentinels = {path: f"previous:{path.name}".encode() for path in paths}
        for path, value in sentinels.items():
            path.write_bytes(value)
        return sentinels

    def _assert_previous_run_unchanged(self, sentinels: dict[Path, bytes]) -> None:
        for path, expected in sentinels.items():
            self.assertEqual(path.read_bytes(), expected)

    @staticmethod
    def _write_source(
        path: Path, column_map: dict[str, str], canonical: dict[str, str]
    ) -> None:
        with path.open("w", encoding="cp1252", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=column_map)
            writer.writeheader()
            writer.writerow({source: canonical[target] for source, target in column_map.items()})


if __name__ == "__main__":
    unittest.main()
