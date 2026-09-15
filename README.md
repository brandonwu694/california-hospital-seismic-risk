# California Hospital Earthquake Risk

A project to integrate California hospital building characteristics and seismic assessments, with earthquake scenario modeling planned for later work.

The repository currently contains project documentation and reproducible EDA notebooks for the seismic and building datasets. The first planned phase is a validated dataset with one record per hospital building. The integration pipeline, trained models, and an automated test suite have not been implemented yet.

## Start here

- [Project scope](docs/PROJECT_SCOPE.md): goals, boundaries, and Phase 1 deliverables.
- [Data sources](docs/DATA_SOURCES.md): download instructions, provenance, and citations.
- [Seismic data guide](docs/SEISMIC_DATA.md): ratings, collapse probabilities, and field definitions.
- [Seismic EDA notebook](notebooks/01_eda_seismic.ipynb): data structure, column types, missingness, distributions, and cleanup decisions, with saved inline results.
- [Hospital building data guide](docs/HOSPITAL_BUILDING_DATA.md): building characteristics and joining guidance.
- [Building EDA notebook](notebooks/02_eda_hospital_building.ipynb): missingness, physical characteristics, code/completion years, and cleanup decisions, with saved inline results.
- [Repository guidance](AGENTS.md): conventions for contributing changes.

## Structure

```text
data/
  raw/          Original downloaded CSVs
  interim/      Intermediate transformation outputs
  processed/    Validated datasets for analysis
docs/           Scope, source references, and dataset guides
notebooks/      Exploratory analysis with inline results
AGENTS.md       Repository working instructions
pyproject.toml  Project metadata and dependencies
```

Data files are excluded from Git; `.gitkeep` files preserve the directories. After cloning, follow [Getting the data](docs/DATA_SOURCES.md#getting-the-data) to populate `data/raw/`. Keep raw files unchanged and generate derived data through code.

## Development status

[pyproject.toml](pyproject.toml) defines the project metadata, a Python 3.12+ baseline, and the `notebook` dependency group for JupyterLab and the Python kernel. The analysis itself uses the standard library. Runtime dependencies remain empty; package installation and build configuration can be added when reusable pipeline code is introduced.

Python environments, generated data, and model artifacts are excluded by `.gitignore`.
