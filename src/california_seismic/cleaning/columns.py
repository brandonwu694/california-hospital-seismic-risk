"""Normalize source-specific headers to the canonical schema."""

from collections.abc import Mapping

from ..schema import SourceSchema


class SchemaError(ValueError):
    """Raised when source columns do not match the documented schema."""


def normalize_columns(
    rows: list[dict[str, str]], schema: SourceSchema
) -> list[dict[str, str]]:
    if not rows:
        raise SchemaError(f"{schema.name} has no rows")

    observed = set(rows[0])
    missing = schema.required_source_columns - observed
    unexpected = observed - schema.required_source_columns
    if missing or unexpected:
        raise SchemaError(
            f"{schema.name} schema mismatch; missing={sorted(missing)}, "
            f"unexpected={sorted(unexpected)}"
        )

    return [_rename_row(row, schema.column_map) for row in rows]


def _rename_row(
    row: Mapping[str, str], column_map: Mapping[str, str]
) -> dict[str, str]:
    return {column_map[source]: row[source] for source in column_map}
