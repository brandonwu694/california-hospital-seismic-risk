"""Parse canonical values while retaining categorical missing markers."""

from typing import TypeAlias

from ..schema import FLOAT_COLUMNS, INTEGER_COLUMNS, TEXT_COLUMNS


Scalar: TypeAlias = str | int | float | None


class ValueParsingError(ValueError):
    """Raised when a nonblank numeric source value cannot be parsed."""


def parse_values(rows: list[dict[str, str]]) -> list[dict[str, Scalar]]:
    return [{column: _parse(column, value) for column, value in row.items()} for row in rows]


def _parse(column: str, value: str) -> Scalar:
    if column in TEXT_COLUMNS:
        return value.strip()
    if column in FLOAT_COLUMNS:
        return _parse_float(column, value)
    if column in INTEGER_COLUMNS:
        return _parse_integer(column, value)
    raise ValueParsingError(f"No canonical type declared for {column!r}")


def _parse_float(column: str, value: str) -> float | None:
    value = value.strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError as exc:
        raise ValueParsingError(f"{column} must be numeric; received {value!r}") from exc


def _parse_integer(column: str, value: str) -> int | None:
    value = value.strip()
    if not value:
        return None
    try:
        number = float(value)
    except ValueError as exc:
        raise ValueParsingError(f"{column} must be an integer; received {value!r}") from exc
    if not number.is_integer():
        raise ValueParsingError(f"{column} must be an integer; received {value!r}")
    return int(number)
