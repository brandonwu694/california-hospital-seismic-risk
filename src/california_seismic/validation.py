"""Hard validation rules and nonfatal data-quality summaries."""

import math
import re
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from .schema import JOIN_KEYS, Scalar, SourceSchema


@dataclass(frozen=True)
class ValidationConfig:
    """Explicit plausibility policy for a particular source snapshot."""

    snapshot_year: int
    minimum_year: int = 1800
    minimum_height_ft: float = 0
    maximum_height_ft: float = 2_000
    minimum_stories: int = 0
    maximum_stories: int = 200
    minimum_latitude: float = 32
    maximum_latitude: float = 42.1
    minimum_longitude: float = -124.5
    maximum_longitude: float = -114
    minimum_hazus_pct: float = 0
    maximum_hazus_pct: float = 100
    hazus_2010_fault_marker: float = -50


DEFAULT_VALIDATION_CONFIG = ValidationConfig(snapshot_year=2026)


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


def validate_value_ranges(
    rows: list[dict[str, Scalar]],
    source_name: str,
    config: ValidationConfig = DEFAULT_VALIDATION_CONFIG,
) -> None:
    for index, row in enumerate(rows, start=2):
        _check_identifier(row, index, source_name)
        _check_finite_numbers(row, index, source_name)
        _check_range(
            row,
            "height_ft",
            minimum=config.minimum_height_ft,
            maximum=config.maximum_height_ft,
            index=index,
            source=source_name,
        )
        _check_range(
            row,
            "stories",
            minimum=config.minimum_stories,
            maximum=config.maximum_stories,
            index=index,
            source=source_name,
        )
        _check_range(
            row,
            "building_code_year",
            minimum=config.minimum_year,
            maximum=config.snapshot_year,
            index=index,
            source=source_name,
        )
        _check_range(
            row,
            "year_completed",
            minimum=config.minimum_year,
            maximum=config.snapshot_year,
            index=index,
            source=source_name,
        )
        _check_range(
            row,
            "latitude",
            minimum=config.minimum_latitude,
            maximum=config.maximum_latitude,
            index=index,
            source=source_name,
        )
        _check_range(
            row,
            "longitude",
            minimum=config.minimum_longitude,
            maximum=config.maximum_longitude,
            index=index,
            source=source_name,
        )
        _check_hazus(row, index, source_name, config)
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


def _check_hazus(
    row: Mapping[str, Scalar],
    index: int,
    source: str,
    config: ValidationConfig,
) -> None:
    value_2007 = row.get("hazus_2007_pct")
    if (
        value_2007 is not None
        and not config.minimum_hazus_pct
        <= value_2007
        <= config.maximum_hazus_pct  # type: ignore[operator]
    ):
        raise ValidationError(f"{source} row {index}: invalid 2007 Hazus percentage")
    value_2010 = row.get("hazus_2010_pct")
    if (
        value_2010 is not None
        and value_2010 != config.hazus_2010_fault_marker
        and not config.minimum_hazus_pct
        <= value_2010
        <= config.maximum_hazus_pct  # type: ignore[operator]
    ):
        raise ValidationError(f"{source} row {index}: invalid 2010 Hazus percentage")
