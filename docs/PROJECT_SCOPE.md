# Project Scope

## 1. Project Goal

Build a multi-source seismic risk modeling system for California hospitals.

The project will combine hospital building characteristics, existing seismic assessments, and eventually earthquake-specific hazard data to estimate how vulnerable individual hospital buildings are and how their risk changes under different earthquake scenarios.

The goal is not simply to compare machine learning models. Machine learning will be one component of a broader data system involving:

- data integration
- feature engineering
- seismic vulnerability modeling
- geospatial analysis
- earthquake scenario modeling
- model interpretation
- risk visualization

A longer-term goal is to support questions such as:

> Which California hospital buildings are most vulnerable to earthquake damage?

and eventually:

> How would the expected risk to California hospitals change under an earthquake centered in Los Angeles versus Orange County?

---

## 2. Core Concept

The project separates three related concepts:

### Vulnerability

How susceptible is a hospital building to earthquake damage based on its intrinsic characteristics?

Examples:

- year completed
- number of stories
- building height
- building code
- structural characteristics

Vulnerability should remain approximately constant between earthquake scenarios unless the building itself changes.

### Exposure

How strongly is a hospital affected by a particular earthquake?

Examples:

- earthquake magnitude
- earthquake location
- earthquake depth
- distance to rupture or epicenter
- expected ground motion at the hospital location

Exposure changes between earthquake scenarios.

### Consequence

How important would the loss or reduced functionality of the hospital be?

Possible future features:

- number of beds
- emergency department capacity
- patient volume
- population served
- nearby alternative hospitals

The long-term conceptual model is:

`Risk = f(Vulnerability, Exposure, Consequence)`

Consequence is outside the initial project scope.

---

## 3. Initial Data Sources

### 3.1 HCAI Seismic Ratings and Collapse Probabilities

Publisher:
California Department of Health Care Access and Information (HCAI)

Purpose:
Provides existing seismic assessments for California hospital buildings.

Important fields include:

- `Perm ID`
- `Facility Name`
- `Building Nbr`
- `Building Name`
- `Building Status`
- `SPC Rating`
- `2007 Hazus Score (%)`
- `2010 Hazus Score (%)`
- `HCAI NPC Rating`
- `AB 1882 Notice`
- `Latitude`
- `Longitude`

This dataset primarily represents the **seismic assessment / outcome side** of the project.

See the [seismic data guide](SEISMIC_DATA.md) for field definitions and interpretation notes, and [data sources](DATA_SOURCES.md#seismic-ratings-and-collapse-probabilities) for provenance and downloads.

### 3.2 HCAI Hospital Building Data

Publisher:
California Department of Health Care Access and Information (HCAI)

Purpose:
Provides physical and design characteristics of individual hospital buildings.

Potentially useful fields include:

- year completed
- number of stories
- building height
- building code
- building status
- facility and building identifiers

This dataset primarily represents the **predictor / building-characteristics side** of the project.

See the [hospital building data guide](HOSPITAL_BUILDING_DATA.md) for field definitions and [data sources](DATA_SOURCES.md#hospital-building-data) for provenance and downloads.

### Expected Join

The datasets are expected to be joined primarily using:

- `Perm ID`
- `Building Nbr`

The uniqueness and reliability of these keys must be validated before modeling.

The current snapshot comparison is documented in the [joining guidance](HOSPITAL_BUILDING_DATA.md#joining-with-the-seismic-dataset). Repeat those checks as part of the implemented pipeline and whenever inputs change.

---

## 4. Unit of Analysis

The intended unit of analysis is:

> One seismically separate hospital building.

A hospital facility may therefore contain multiple records.

For example, one hospital may contain:

- original hospital building
- emergency department addition
- west wing
- radiology building
- utility structures
- tanks
- equipment structures

The modeling population must be defined carefully before training.

---

## 5. Modeling Population

Not every HCAI building record should automatically be included.

Examples requiring review include:

- proposed buildings
- equipment yards
- water tanks
- fuel tanks
- sheds
- canopies
- buildings no longer providing general acute care

Initial modeling should focus on buildings that are relevant to active hospital operations.

The exact inclusion/exclusion rules should be documented after inspecting the available building statuses and building types.

Do not silently remove records.

Every filtering rule should have a documented reason.

---

## 6. Phase 1 — Build the Integrated Dataset

Implementation details and current validation behavior are documented in the [cleaning and integration pipeline guide](CLEANING_PIPELINE.md).

### Objective

Create a validated building-level dataset combining physical building information with seismic assessment information.

### Tasks

1. Load both HCAI datasets.
2. Standardize column names and missing-value representations.
3. Inspect candidate keys.
4. Test uniqueness of `Perm ID + Building Nbr`.
5. Join the datasets.
6. Calculate join coverage.
7. Investigate unmatched records.
8. Identify duplicate records.
9. Review building statuses and building types.
10. Define the modeling population.
11. Separate predictor variables from seismic assessment variables.
12. Save a clean processed dataset.

### Important Validation

Document:

- number of rows before joining
- number of unique facilities
- number of unique buildings
- join success rate
- duplicated identifiers
- unmatched records
- records removed from the modeling population
- missingness in important features

### Expected Output

A modeling-ready dataset with approximately:

```text
facility_id
building_id
facility_name
building_name
year_completed
stories
height
building_code
...
target
```

This field list is illustrative. The final target definition and feature eligibility remain to be decided during implementation. Store the validated output in `data/processed/` and document the validation results listed above.
