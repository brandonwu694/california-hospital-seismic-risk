"""Read source CSVs without implicit type or missing-value conversion."""

import csv
from pathlib import Path

from .schema import ENCODING, SourceSchema


class IngestionError(ValueError):
    """Raised when a source file cannot be read as the documented schema."""


def read_source_csv(path: Path, schema: SourceSchema) -> list[dict[str, str]]:
    """Load all source cells as strings using the documented encoding."""
    try:
        handle = path.open(encoding=ENCODING, newline="")
    except OSError as exc:
        raise IngestionError(f"Cannot open {schema.name} source: {path}") from exc

    with handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise IngestionError(f"{schema.name} source has no header")
        stripped = [name.strip() for name in reader.fieldnames]
        if len(stripped) != len(set(stripped)):
            raise IngestionError(f"{schema.name} source has duplicate normalized headers")
        reader.fieldnames = stripped
        rows = list(reader)

    if not rows:
        raise IngestionError(f"{schema.name} source has no records")
    if any(None in row for row in rows):
        raise IngestionError(f"{schema.name} source contains records wider than its header")
    return rows
