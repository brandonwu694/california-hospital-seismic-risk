"""Parse canonical values while retaining categorical missing markers."""

from ..schema import FLOAT_COLUMNS, INTEGER_COLUMNS, TEXT_COLUMNS, Scalar


class ValueParsingError(ValueError):
    """Raised when a nonblank numeric source value cannot be parsed."""


def parse_values(
    rows: list[dict[str, str]], source_name: str
) -> list[dict[str, Scalar]]:
    parsed: list[dict[str, Scalar]] = []
    for record_number, row in enumerate(rows, start=2):
        try:
            parsed.append(
                {column: _parse(column, value) for column, value in row.items()}
            )
        except ValueParsingError as exc:
            key = (
                f"facility_id={row.get('facility_id')!r}, "
                f"building_id={row.get('building_id')!r}"
            )
            raise ValueParsingError(
                f"{source_name} record {record_number} ({key}): {exc}"
            ) from exc
    return parsed


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
