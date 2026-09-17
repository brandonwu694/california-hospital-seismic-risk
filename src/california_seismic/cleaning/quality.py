"""Annotate questionable values without changing or removing source records."""

from collections import defaultdict

from ..schema import Scalar


def add_review_flags(row: dict[str, Scalar]) -> dict[str, Scalar]:
    flags = _existing_flags(row)

    if row.get("height_ft") == 0:
        _append_once(flags, "zero_height")
    if row.get("stories") == 0:
        _append_once(flags, "zero_stories")

    completed = row.get("year_completed")
    code_year = row.get("building_code_year")
    if isinstance(completed, int) and isinstance(code_year, int) and completed < code_year:
        _append_once(flags, "completion_before_code_year")
    if row.get("spc_rating") == "N/A":
        _append_once(flags, "spc_not_applicable")
    elif isinstance(row.get("spc_rating"), str) and row["spc_rating"].endswith("s"):
        _append_once(flags, "spc_unverified")

    if row.get("building_status") != "OSHPD 1-In Service":
        _append_once(flags, "not_in_service")

    enriched = dict(row)
    enriched["review_flags"] = ";".join(flags)
    return enriched


def add_dataset_review_flags(
    rows: list[dict[str, Scalar]],
) -> list[dict[str, Scalar]]:
    """Add flags that require comparisons across multiple records."""
    cities_by_facility: defaultdict[str, set[str]] = defaultdict(set)
    for row in rows:
        facility_id = row.get("facility_id")
        city = row.get("city")
        if isinstance(facility_id, str) and isinstance(city, str):
            cities_by_facility[facility_id].add(city)

    inconsistent = {
        facility_id for facility_id, cities in cities_by_facility.items() if len(cities) > 1
    }
    output: list[dict[str, Scalar]] = []
    for row in rows:
        enriched = dict(row)
        if row.get("facility_id") in inconsistent:
            flags = _existing_flags(enriched)
            _append_once(flags, "facility_city_inconsistent")
            enriched["review_flags"] = ";".join(flags)
        output.append(enriched)
    return output


def _existing_flags(row: dict[str, Scalar]) -> list[str]:
    current = row.get("review_flags")
    return current.split(";") if isinstance(current, str) and current else []


def _append_once(flags: list[str], flag: str) -> None:
    if flag not in flags:
        flags.append(flag)
