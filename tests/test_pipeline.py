import csv
import json
import tempfile
import unittest
from pathlib import Path

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
            self._write_source(raw / SEISMIC_SCHEMA.filename, SEISMIC_SCHEMA.column_map, seismic)

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
