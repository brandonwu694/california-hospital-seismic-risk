import csv
import tempfile
import unittest
from pathlib import Path

from california_seismic.ingestion import IngestionError, read_source_csv
from california_seismic.schema import BUILDING_SCHEMA


class IngestionTests(unittest.TestCase):
    def test_rejects_record_shorter_than_header_with_context(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "short.csv"
            columns = list(BUILDING_SCHEMA.column_map)
            with path.open("w", encoding="cp1252", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(columns)
                writer.writerow(["value"] * (len(columns) - 1))

            with self.assertRaisesRegex(
                IngestionError,
                r"hospital_building record 2 is missing fields: \['Count'\]",
            ):
                read_source_csv(path, BUILDING_SCHEMA)


if __name__ == "__main__":
    unittest.main()
