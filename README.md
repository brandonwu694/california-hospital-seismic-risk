# California Hospital Earthquake Risk

A project to integrate California hospital building characteristics and seismic assessments, with earthquake scenario modeling planned for later work.

The repository currently contains project documentation and the data directory structure. The first planned phase is a validated dataset with one record per hospital building. Pipeline code, trained models, and automated tests have not been implemented yet.

## Start here

- [Project scope](docs/PROJECT_SCOPE.md): goals, boundaries, and Phase 1 deliverables.
- [Data sources](docs/DATA_SOURCES.md): download instructions, provenance, and citations.
- [Seismic data guide](docs/SEISMIC_DATA.md): ratings, collapse probabilities, and field definitions.
- [Hospital building data guide](docs/HOSPITAL_BUILDING_DATA.md): building characteristics and joining guidance.
- [Repository guidance](AGENTS.md): conventions for contributing changes.

## Structure

```text
data/
  raw/          Original downloaded CSVs
  interim/      Intermediate transformation outputs
  processed/    Validated datasets for analysis
docs/           Scope, source references, and dataset guides
AGENTS.md       Repository working instructions
pyproject.toml  Project metadata and dependencies
```

Data files are excluded from Git; `.gitkeep` files preserve the directories. After cloning, follow [Getting the data](docs/DATA_SOURCES.md#getting-the-data) to populate `data/raw/`. Keep raw files unchanged and generate derived data through code.

## Development status

[pyproject.toml](pyproject.toml) defines the project metadata, a Python 3.12+ baseline, and an empty dependency list. Add dependencies there as implementation begins. Package installation, build configuration, and development tools are not configured yet; introduce them alongside the code that needs them.

Python environments, generated data, and model artifacts are excluded by `.gitignore`.
