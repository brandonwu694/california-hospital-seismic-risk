import unittest

from california_seismic.cleaning.columns import normalize_columns
from california_seismic.cleaning.quality import add_dataset_review_flags, add_review_flags
from california_seismic.cleaning.values import parse_values
from california_seismic.schema import BUILDING_SCHEMA, SEISMIC_SCHEMA


class CleaningTests(unittest.TestCase):
    def test_spc_headers_reconcile_to_one_canonical_name(self) -> None:
        building = {source: "" for source in BUILDING_SCHEMA.column_map}
        seismic = {source: "" for source in SEISMIC_SCHEMA.column_map}
        building["SPC Rating *"] = "5s"
        seismic["SPC Rating"] = "5s"

        building_clean = normalize_columns([building], BUILDING_SCHEMA)[0]
        seismic_clean = normalize_columns([seismic], SEISMIC_SCHEMA)[0]

        self.assertEqual(building_clean["spc_rating"], "5s")
        self.assertEqual(seismic_clean["spc_rating"], "5s")
        self.assertNotIn("SPC Rating *", building_clean)

    def test_ids_and_missing_markers_are_preserved_as_strings(self) -> None:
        parsed = parse_values(
            [{
                "facility_id": "00123",
                "building_id": "BLD-00001",
                "spc_rating": "N/A",
                "height_ft": "",
                "stories": "2",
            }],
            "fixture",
        )[0]

        self.assertEqual(parsed["facility_id"], "00123")
        self.assertEqual(parsed["building_id"], "BLD-00001")
        self.assertEqual(parsed["spc_rating"], "N/A")
        self.assertIsNone(parsed["height_ft"])
        self.assertEqual(parsed["stories"], 2)

    def test_review_flags_do_not_change_values(self) -> None:
        row = {
            "height_ft": 0.0,
            "stories": 0,
            "building_code_year": 2010,
            "year_completed": 1995,
            "spc_rating": "5s",
            "building_status": "OSHPD 1-Proposed",
        }
        flagged = add_review_flags(row)

        self.assertEqual(flagged["height_ft"], 0.0)
        self.assertEqual(flagged["year_completed"], 1995)
        self.assertEqual(
            flagged["review_flags"],
            "zero_height;zero_stories;completion_before_code_year;spc_unverified;not_in_service",
        )
        self.assertEqual(add_review_flags(flagged), flagged)

    def test_facility_city_inconsistency_flags_all_affected_rows(self) -> None:
        rows = [
            {"facility_id": "00123", "city": "Alpha", "review_flags": ""},
            {"facility_id": "00123", "city": "Alhpa", "review_flags": "zero_height"},
            {"facility_id": "00456", "city": "Beta", "review_flags": ""},
        ]

        flagged = add_dataset_review_flags(rows)

        self.assertEqual(flagged[0]["review_flags"], "facility_city_inconsistent")
        self.assertEqual(
            flagged[1]["review_flags"], "zero_height;facility_city_inconsistent"
        )
        self.assertEqual(flagged[2]["review_flags"], "")

        flagged_again = add_dataset_review_flags(flagged)
        self.assertEqual(flagged_again, flagged)

    def test_numeric_parse_error_includes_source_record_and_key(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "fixture record 2.*facility_id='00123'.*building_id='BLD-00001'",
        ):
            parse_values(
                [{
                    "facility_id": "00123",
                    "building_id": "BLD-00001",
                    "height_ft": "not-a-number",
                }],
                "fixture",
            )


if __name__ == "__main__":
    unittest.main()
