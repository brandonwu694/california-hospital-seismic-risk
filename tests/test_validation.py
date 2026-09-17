import unittest
from dataclasses import replace

from california_seismic.validation import (
    DEFAULT_VALIDATION_CONFIG,
    ValidationError,
    validate_keys,
    validate_value_ranges,
)


def valid_row() -> dict[str, object]:
    return {
        "facility_id": "00123",
        "building_id": "BLD-00001",
        "height_ft": 45.5,
        "stories": 4,
        "building_code_year": 1998,
        "year_completed": 2001,
        "latitude": 34.1,
        "longitude": -118.2,
        "record_count": 1,
    }


class ValidationTests(unittest.TestCase):
    def test_rejects_impossible_year(self) -> None:
        row = valid_row()
        row["year_completed"] = 3025
        with self.assertRaisesRegex(ValidationError, "year_completed=3025"):
            validate_value_ranges([row], "fixture")

    def test_rejects_negative_height(self) -> None:
        row = valid_row()
        row["height_ft"] = -123.0
        with self.assertRaisesRegex(ValidationError, "height_ft=-123"):
            validate_value_ranges([row], "fixture")

    def test_rejects_duplicate_composite_keys(self) -> None:
        row = valid_row()
        with self.assertRaisesRegex(ValidationError, "duplicate join keys"):
            validate_keys([row, dict(row)], "fixture")

    def test_accepts_documented_2010_hazus_fault_marker(self) -> None:
        row = valid_row()
        row["hazus_2010_pct"] = -50.0
        validate_value_ranges([row], "fixture")

    def test_snapshot_year_is_configurable(self) -> None:
        row = valid_row()
        row["year_completed"] = 2027
        with self.assertRaises(ValidationError):
            validate_value_ranges([row], "fixture")

        config = replace(DEFAULT_VALIDATION_CONFIG, snapshot_year=2027)
        validate_value_ranges([row], "fixture", config)


if __name__ == "__main__":
    unittest.main()
