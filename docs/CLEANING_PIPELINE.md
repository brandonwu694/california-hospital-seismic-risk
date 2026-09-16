# Cleaning and integration pipeline

The Phase 1 pipeline reads both HCAI source CSVs, cleans and validates each source independently, persists the typed source tables, joins building records, and writes an integrated dataset with an audit report. It does not filter the modeling population or choose a target.

## Modules

| Module | Responsibility |
| --- | --- |
| `schema.py` | Source mappings, canonical columns, types, join keys, and snapshot constants. |
| `ingestion.py` | Windows-1252 CSV loading with every source cell initially retained as text. |
| `cleaning/columns.py` | Header normalization, including both source SPC headers mapping to `spc_rating`. |
| `cleaning/values.py` | Nullable numeric parsing while retaining text markers such as `N/A`. |
| `cleaning/quality.py` | Nonfatal review flags without modifying source values. |
| `validation.py` | Required fields, string identifiers, unique keys, finite numbers, geographic bounds, and plausible value ranges. |
| `integration.py` | Composite-key join, unmatched-key audit, and shared-field comparison. |
| `storage.py` | Explicit Arrow schemas and compressed Parquet input/output. |
| `pipeline.py` | Pipeline orchestration and validation-report output. |

## Run

From the repository root:

```sh
build-integrated-data
```

This command is installed with the project as described in the repository README.

The default inputs are the two documented files in `data/raw/`. The independently cleaned, typed sources are ignored by Git and written to:

- `data/interim/hospital_buildings_clean.parquet`
- `data/interim/seismic_ratings_clean.parquet`

The pipeline reads those interim files back before joining and writes:

- `data/processed/hospital_buildings_integrated.parquet`
- `data/processed/hospital_buildings_validation.json`

Use `--raw-dir`, `--interim-dir`, or `--processed-dir` to override those directories.

## Validation behavior

The pipeline stops on schema changes, blank or duplicate composite keys, malformed IDs, nonfinite numeric values, values outside broad physical/date/geographic bounds, incomplete joins, or disagreements among shared source fields. For example, a completion year of 3025 or a height of -123 feet fails validation.

Values that are questionable but not demonstrably wrong remain in the output with semicolon-delimited `review_flags`. Current flags cover zero height, zero stories, completion before building-code year, inconsistent city labels within a facility, unverified or non-applicable SPC labels, and records outside the exact in-service status.

The current snapshot produces 4,690 integrated records from a complete one-to-one join. No records are filtered. The JSON report records join coverage, blank counts, and review-flag counts.

## Tests

Run the test suite with:

```sh
python3 -m unittest discover -s tests -v
```

Tests cover SPC header reconciliation, string IDs, missing markers, review flags, impossible value rejection, duplicate keys, shared-field conflicts, unmatched records, and an end-to-end Parquet pipeline.
