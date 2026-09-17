# California Hospital Earthquake Risk

A project to integrate California hospital building characteristics and seismic assessments, with earthquake scenario modeling planned for later work.

The repository contains project documentation, reproducible EDA notebooks, and a validated Phase 1 cleaning and integration pipeline. Modeling-population selection, trained models, and earthquake-scenario analysis remain future work.

## Start here

- [Project scope](docs/PROJECT_SCOPE.md): goals, boundaries, and Phase 1 deliverables.
- [Data sources](docs/DATA_SOURCES.md): download instructions, provenance, and citations.
- [Seismic data guide](docs/SEISMIC_DATA.md): ratings, collapse probabilities, and field definitions.
- [Seismic EDA notebook](notebooks/01_eda_seismic.ipynb): data structure, column types, missingness, distributions, and cleanup decisions, with saved inline results.
- [Hospital building data guide](docs/HOSPITAL_BUILDING_DATA.md): building characteristics and joining guidance.
- [Building EDA notebook](notebooks/02_eda_hospital_building.ipynb): missingness, physical characteristics, code/completion years, and cleanup decisions, with saved inline results.
- [Cleaning pipeline](docs/CLEANING_PIPELINE.md): canonical schema, validation behavior, integration audit, outputs, and test command.
- [Repository guidance](AGENTS.md): conventions for contributing changes.

## Structure

```text
.
├── data/
│   ├── raw/                       # Original downloaded CSVs
│   ├── interim/                   # Independently cleaned source tables
│   └── processed/                 # Integrated data, reports, and manifests
├── docs/
│   ├── CLEANING_PIPELINE.md
│   ├── DATA_SOURCES.md
│   ├── HOSPITAL_BUILDING_DATA.md
│   ├── PROJECT_SCOPE.md
│   └── SEISMIC_DATA.md
├── notebooks/
│   ├── 01_eda_seismic.ipynb
│   └── 02_eda_hospital_building.ipynb
├── src/
│   └── california_seismic/
│       ├── cleaning/
│       │   ├── columns.py
│       │   ├── quality.py
│       │   └── values.py
│       ├── artifacts.py
│       ├── ingestion.py
│       ├── integration.py
│       ├── pipeline.py
│       ├── schema.py
│       ├── storage.py
│       └── validation.py
├── tests/
│   ├── test_artifacts.py
│   ├── test_cleaning.py
│   ├── test_ingestion.py
│   ├── test_integration.py
│   ├── test_pipeline.py
│   └── test_validation.py
├── .gitignore
├── AGENTS.md
├── README.md
└── pyproject.toml
```

Data files are excluded from Git; `.gitkeep` files preserve the directories. After cloning, follow [Getting the data](docs/DATA_SOURCES.md#getting-the-data) to populate `data/raw/`. Keep raw files unchanged and generate derived data through code.

## Development status

[pyproject.toml](pyproject.toml) defines the project metadata, a Python 3.12+ baseline, PyArrow for typed Parquet datasets, and the `notebook` dependency group for JupyterLab and the Python kernel.

Python environments, generated data, and model artifacts are excluded by `.gitignore`.

## Build the integrated dataset

Install the project in an active Python environment:

```sh
python3 -m pip install .
```

After placing both source CSVs in `data/raw/`, run:

```sh
build-integrated-data
python3 -m unittest discover -s tests -v
```

The pipeline preserves all source records, writes independently cleaned Parquet tables to `data/interim/`, and publishes the integrated dataset, validation report, and hashed completion manifest to `data/processed/`. See the [cleaning pipeline guide](docs/CLEANING_PIPELINE.md) for validation and failure behavior.
