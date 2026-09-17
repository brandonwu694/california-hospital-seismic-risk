"""Read and write typed Parquet datasets at pipeline boundaries."""

from collections.abc import Sequence
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from .schema import FLOAT_COLUMNS, INTEGER_COLUMNS, JOIN_KEYS, TEXT_COLUMNS, Scalar


def parquet_schema(columns: Sequence[str]) -> pa.Schema:
    fields = []
    for column in columns:
        if column in TEXT_COLUMNS or column == "review_flags":
            data_type = pa.string()
        elif column in FLOAT_COLUMNS:
            data_type = pa.float64()
        elif column in INTEGER_COLUMNS:
            data_type = pa.int64()
        else:
            raise ValueError(f"No Parquet type is defined for {column!r}")
        fields.append(pa.field(column, data_type, nullable=column not in JOIN_KEYS))
    return pa.schema(fields)


def write_parquet(
    path: Path,
    rows: list[dict[str, Scalar]],
    columns: Sequence[str],
) -> None:
    expected = set(columns)
    for index, row in enumerate(rows, start=1):
        if set(row) != expected:
            raise ValueError(
                f"Row {index} does not match the Parquet schema; "
                f"missing={sorted(expected - set(row))}, "
                f"unexpected={sorted(set(row) - expected)}"
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist(rows, schema=parquet_schema(columns))
    pq.write_table(table, path, compression="zstd")


def read_parquet(path: Path, columns: Sequence[str]) -> list[dict[str, Scalar]]:
    expected_schema = parquet_schema(columns)
    table = pq.read_table(path)
    if not table.schema.equals(expected_schema):
        raise ValueError(
            f"Unexpected Parquet schema in {path}; "
            f"expected={expected_schema}, observed={table.schema}"
        )
    return table.to_pylist()
