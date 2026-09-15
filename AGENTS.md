# Repository guidance

## Project documentation

- Read [PROJECT_SCOPE.md](docs/PROJECT_SCOPE.md) before changing analysis or implementation. It defines the objectives, conceptual model, unit of analysis, modeling population, and phase-specific deliverables and validation requirements.
- Consult [DATA_SOURCES.md](docs/DATA_SOURCES.md) for dataset provenance, citations, source links, and instructions for adding datasets.
- Read [SEISMIC_DATA.md](docs/SEISMIC_DATA.md) when working with seismic ratings, Hazus scores, or their interpretation.
- Keep seismic EDA and its findings in [01_eda_seismic.ipynb](notebooks/01_eda_seismic.ipynb). Make it understandable on its own and save refreshed inline outputs; do not generate a separate Markdown EDA report.
- Read [HOSPITAL_BUILDING_DATA.md](docs/HOSPITAL_BUILDING_DATA.md) when working with building characteristics or joining the HCAI datasets. It documents field definitions, missing values, identifier types, and header differences.
- Keep building EDA and its findings in [02_eda_hospital_building.ipynb](notebooks/02_eda_hospital_building.ipynb), following the same notebook-only approach with refreshed inline outputs.

Keep project scope and dataset explanations in these documents. Update the relevant document when decisions change rather than duplicating its contents here.

## Working with data

- Preserve source files in `data/raw/`. Perform cleaning and transformations in code, and write derived datasets to `data/processed/`.
- Follow the current phase's validation requirements in `PROJECT_SCOPE.md`; recheck join keys and coverage when inputs change.
- Document filtering decisions and their effect on the modeling population in accordance with `PROJECT_SCOPE.md`.
- Keep documentation links consistent with the actual file layout when files move.

## Engineering guidelines

- Keep code modular. Prefer small functions and modules with clear responsibilities over large scripts that mix loading, cleaning, validation, modeling, and presentation.
- Prefer readable and maintainable code over clever or highly condensed implementations.
- Keep docstrings and inline comments concise. Document intent, assumptions, or non-obvious behavior rather than restating what the code already expresses.
- Prefer simple solutions before introducing abstractions, frameworks, or additional dependencies.
- Avoid adding dependencies unless they provide a clear benefit that cannot reasonably be achieved with the existing stack.
- Maintain project metadata, the supported Python version, and dependencies in [pyproject.toml](pyproject.toml). Keep dependency declarations in one place and add build or tool configuration when implementation requires it.
- Separate data ingestion, transformation, validation, feature engineering, modeling, and evaluation where practical.
- Do not hard-code dataset-specific values, paths, thresholds, or mappings when they are likely to change; centralize reusable configuration instead.
- Preserve existing behavior unless a change is intentional. Update or add tests when behavior changes.
- Validate assumptions at data boundaries. Fail clearly when required columns, identifiers, schemas, or expected relationships are invalid rather than silently continuing.
- Avoid target leakage. Treat feature eligibility as a modeling decision and consult the project documentation before introducing seismic assessment fields as predictors.
- Prefer deterministic and reproducible transformations. Set random seeds where randomness affects experiments or evaluation.
- Do not optimize prematurely. Establish a correct and understandable implementation before improving performance or introducing additional complexity.
- Keep exploratory analysis separate from reusable pipeline code. Promote logic from notebooks into tested modules once it becomes part of the workflow.
- Keep project documentation synchronized with implementation changes. Update the relevant files under `docs/`, `README.md`, and `AGENTS.md` when behavior, scope, data sources, assumptions, workflows, or repository structure change.
- Do not duplicate the same information across documentation files. Update the canonical document and adjust links or summaries elsewhere as needed.
- Treat documentation updates as part of completing a change, not as a separate optional task.
- Before finishing a change, check whether it affects documented commands, file paths, schemas, modeling assumptions, validation rules, or project scope.
