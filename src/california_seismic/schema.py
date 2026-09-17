"""Source schemas, canonical columns, and validation constants."""

from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias


Scalar: TypeAlias = str | int | float | None
ENCODING = "cp1252"
JOIN_KEYS = ("facility_id", "building_id")

SHARED_COLUMNS = (
    "county_code",
    "facility_id",
    "facility_name",
    "city",
    "building_id",
    "building_name",
    "building_status",
    "spc_rating",
    "ab_1882_notice",
    "latitude",
    "longitude",
    "record_count",
)

BUILDING_ONLY_COLUMNS = (
    "building_url",
    "height_ft",
    "stories",
    "building_code",
    "building_code_year",
    "year_completed",
)

SEISMIC_ONLY_COLUMNS = (
    "hazus_2007_pct",
    "hazus_2010_pct",
    "npc_rating",
)

OUTPUT_COLUMNS = (
    *SHARED_COLUMNS,
    *BUILDING_ONLY_COLUMNS,
    *SEISMIC_ONLY_COLUMNS,
    "review_flags",
)

TEXT_COLUMNS = {
    "county_code",
    "facility_id",
    "facility_name",
    "city",
    "building_id",
    "building_name",
    "building_status",
    "spc_rating",
    "building_url",
    "building_code",
    "ab_1882_notice",
    "npc_rating",
}

FLOAT_COLUMNS = {
    "height_ft",
    "hazus_2007_pct",
    "hazus_2010_pct",
    "latitude",
    "longitude",
}

INTEGER_COLUMNS = {
    "stories",
    "building_code_year",
    "year_completed",
    "record_count",
}

BUILDING_COLUMN_MAP = {
    "County Code": "county_code",
    "Perm ID": "facility_id",
    "Facility Name": "facility_name",
    "City": "city",
    "Building Nbr": "building_id",
    "Building Name": "building_name",
    "Building Status": "building_status",
    "SPC Rating *": "spc_rating",
    "Building URL": "building_url",
    "Height (ft)": "height_ft",
    "Stories": "stories",
    "Building Code": "building_code",
    "Building Code Year": "building_code_year",
    "Year Completed": "year_completed",
    "AB 1882 Notice": "ab_1882_notice",
    "Latitude": "latitude",
    "Longitude": "longitude",
    "Count": "record_count",
}

SEISMIC_COLUMN_MAP = {
    "County Code": "county_code",
    "Perm ID": "facility_id",
    "Facility Name": "facility_name",
    "City": "city",
    "Building Nbr": "building_id",
    "Building Name": "building_name",
    "Building Status": "building_status",
    "SPC Rating": "spc_rating",
    "2007 Hazus Score (%)": "hazus_2007_pct",
    "2010 Hazus Score (%)": "hazus_2010_pct",
    "HCAI NPC Rating": "npc_rating",
    "AB 1882 Notice": "ab_1882_notice",
    "Latitude": "latitude",
    "Longitude": "longitude",
    "Count": "record_count",
}

BUILDING_COLUMNS = tuple(BUILDING_COLUMN_MAP.values())
SEISMIC_COLUMNS = tuple(SEISMIC_COLUMN_MAP.values())


@dataclass(frozen=True)
class SourceSchema:
    name: str
    filename: str
    column_map: dict[str, str]

    @property
    def required_source_columns(self) -> frozenset[str]:
        return frozenset(self.column_map)

    @property
    def required_canonical_columns(self) -> frozenset[str]:
        return frozenset(self.column_map.values())


BUILDING_SCHEMA = SourceSchema(
    name="hospital_building",
    filename="hospital-building-data-.csv",
    column_map=BUILDING_COLUMN_MAP,
)

SEISMIC_SCHEMA = SourceSchema(
    name="seismic_ratings",
    filename="seismic-ratings-and-collapse-probabilities-of-california-hospitals-.csv",
    column_map=SEISMIC_COLUMN_MAP,
)


def default_raw_dir() -> Path:
    return Path.cwd() / "data" / "raw"


def default_interim_dir() -> Path:
    return Path.cwd() / "data" / "interim"


def default_processed_dir() -> Path:
    return Path.cwd() / "data" / "processed"
