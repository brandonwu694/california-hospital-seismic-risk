"""Hard validation rules and nonfatal data-quality summaries."""

import math
import re
from collections import Counter
from collections.abc import Iterable, Mapping

from .cleaning.values import Scalar
from .schema import JOIN_KEYS, SNAPSHOT_YEAR, SourceSchema


class ValidationError(ValueError):
    """Raised when data violates an invariant required by the pipeline."""


def validate_required_columns(
    rows: list[dict[str, Scalar]], schema: SourceSchema
) -> None:
    if not rows:
        raise ValidationError(f"{schema.name} contains no records")
    observed = set(rows[0])
    missing = schema.required_canonical_columns - observed
    if missing:
        raise ValidationError(f"{schema.name} missing canonical columns: {sorted(missing)}")


def validate_keys(rows: list[dict[str, Scalar]], source_name: str) -> None:
    keys: list[tuple[str, str]] = []
    for index, row in enumerate(rows, start=2):
        values = tuple(row.get(column) for column in JOIN_KEYS)
        if not all(isinstance(value, str) and value for value in values):
            raise ValidationError(f"{source_name} row {index} has a blank join key")
        keys.append(values)  # type: ignore[arg-type]

    duplicates = [key for key, count in Counter(keys).items() if count > 1]
    if duplicates:
        raise ValidationError(
            f"{source_name} has {len(duplicates)} duplicate join keys; sample={duplicates[:5]}"
        )


def validate_value_ranges(rows: list[dict[str, Scalar]], source_name: str) -> None:
    for index, row in enumerate(rows, start=2):
        _check_identifier(row, index, source_name)
        _check_finite_numbers(row, index, source_name)
        _check_range(row, "height_ft", minimum=0, maximum=2_000, index=index, source=source_name)
        _check_range(row, "stories", minimum=0, maximum=200, index=index, source=source_name)
        _check_range(
            row,
            "building_code_year",
            minimum=1800,
            maximum=SNAPSHOT_YEAR,
            index=index,
            source=source_name,
        )
        _check_range(
            row,
            "year_completed",
            minimum=1800,
            maximum=SNAPSHOT_YEAR,
            index=index,
            source=source_name,
        )
        _check_range(row, "latitude", minimum=32, maximum=42.1, index=index, source=source_name)
        _check_range(row, "longitude", minimum=-124.5, maximum=-114, index=index, source=source_name)
        _check_hazus(row, index, source_name)
        if row.get("record_count") != 1:
            raise ValidationError(f"{source_name} row {index}: record_count must equal 1")


def summarize_review_flags(rows: Iterable[Mapping[str, Scalar]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        value = row.get("review_flags")
        if isinstance(value, str) and value:
            counts.update(value.split(";"))
    return dict(sorted(counts.items()))


def _check_identifier(row: Mapping[str, Scalar], index: int, source: str) -> None:
    facility_id = row.get("facility_id")
    building_id = row.get("building_id")
    if not isinstance(facility_id, str) or re.fullmatch(r"\d{5}", facility_id) is None:
        raise ValidationError(f"{source} row {index}: invalid facility_id {facility_id!r}")
    if not isinstance(building_id, str) or re.fullmatch(r"BLD-\d{5}", building_id) is None:
        raise ValidationError(f"{source} row {index}: invalid building_id {building_id!r}")


def _check_finite_numbers(row: Mapping[str, Scalar], index: int, source: str) -> None:
    for column, value in row.items():
        if isinstance(value, float) and not math.isfinite(value):
            raise ValidationError(f"{source} row {index}: {column} must be finite")


def _check_range(
    row: Mapping[str, Scalar],
    column: str,
    *,
    minimum: float,
    maximum: float,
    index: int,
    source: str,
) -> None:
    value = row.get(column)
    if value is not None and isinstance(value, (int, float)) and not minimum <= value <= maximum:
        raise ValidationError(
            f"{source} row {index}: {column}={value} outside [{minimum}, {maximum}]"
        )


def _check_hazus(row: Mapping[str, Scalar], index: int, source: str) -> None:
    value_2007 = row.get("hazus_2007_pct")
    if value_2007 is not None and not 0 <= value_2007 <= 100:  # type: ignore[operator]
        raise ValidationError(f"{source} row {index}: invalid 2007 Hazus percentage")
    value_2010 = row.get("hazus_2010_pct")
    if value_2010 is not None and value_2010 != -50 and not 0 <= value_2010 <= 100:  # type: ignore[operator]
        raise ValidationError(f"{source} row {index}: invalid 2010 Hazus percentage")
