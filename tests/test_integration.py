import unittest

from california_seismic.integration import join_sources
from california_seismic.schema import SEISMIC_ONLY_COLUMNS, SHARED_COLUMNS
from california_seismic.validation import ValidationError


def shared_row() -> dict[str, object]:
    return {
        "county_code": "01 - Alameda",
        "facility_id": "00123",
        "facility_name": "Example Hospital",
        "city": "Example City",
        "building_id": "BLD-00001",
        "building_name": "Main Building",
        "building_status": "OSHPD 1-In Service",
        "spc_rating": "3",
        "ab_1882_notice": "",
        "latitude": 37.7,
        "longitude": -122.2,
        "record_count": 1,
    }


class IntegrationTests(unittest.TestCase):
    def test_joins_on_facility_and_building_ids(self) -> None:
        building = shared_row() | {
            "building_url": "https://example.test/building",
            "height_ft": 50.0,
            "stories": 4,
            "building_code": "1998 California Building Code (CBC)",
            "building_code_year": 1998,
            "year_completed": 2001,
        }
        seismic = shared_row() | {
            "hazus_2007_pct": 0.5,
            "hazus_2010_pct": None,
            "npc_rating": "4",
        }

        joined, audit = join_sources([building], [seismic])

        self.assertEqual(audit.matched_rows, 1)
        self.assertEqual(joined[0]["facility_id"], "00123")
        self.assertEqual(joined[0]["height_ft"], 50.0)
        self.assertEqual(joined[0]["npc_rating"], "4")
        self.assertNotIn("review_flags", joined[0])

    def test_rejects_shared_field_disagreement(self) -> None:
        building = shared_row()
        seismic = shared_row()
        seismic["city"] = "Different City"
        for column in SEISMIC_ONLY_COLUMNS:
            seismic[column] = None

        with self.assertRaisesRegex(ValidationError, "Shared fields disagree"):
            join_sources([building], [seismic])

    def test_rejects_unmatched_keys(self) -> None:
        building = shared_row()
        seismic = shared_row()
        seismic["building_id"] = "BLD-00002"
        for column in SEISMIC_ONLY_COLUMNS:
            seismic[column] = None

        with self.assertRaisesRegex(ValidationError, "Join is incomplete"):
            join_sources([building], [seismic])


if __name__ == "__main__":
    unittest.main()
