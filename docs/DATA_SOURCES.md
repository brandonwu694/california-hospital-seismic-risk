# Documentation for Datasets Used In This Project

This document records source links, attribution, license information, review details, and project files for each dataset. Dataset guides contain field definitions and interpretation notes.

## Getting the data

Data files are excluded from Git. A fresh clone contains `.gitkeep` files that preserve `data/raw/`, `data/interim/`, and `data/processed/`.

Download each main CSV using the source links in its dataset section below, and save it under the indicated path relative to the repository root:

| Dataset | Source | Local destination |
| --- | --- | --- |
| Seismic ratings and collapse probabilities | [Seismic source links](#seismic-source-links) | `data/raw/seismic-ratings-and-collapse-probabilities-of-california-hospitals-.csv` |
| Hospital building data | [Building source links](#building-source-links) | `data/raw/hospital-building-data-.csv` |

The publisher's download names include a date; use the destination filenames above and preserve the file contents. Prefer the recorded downloads when reproducing the documented snapshot. If a download is unavailable or a newer release is used, record the replacement source and review date, then recheck the documented row counts, missingness, and join coverage. The complete dictionaries are already included in the dataset guides.

## Adding a dataset

Add a section with the dataset’s title, a unique descriptive ID, a short description, publisher, citation, license information, and dated review notes. Include labeled source links, its expected data path, and a link to its guide. Keep detailed definitions and analysis notes in the dataset guide. Data paths are relative to the repository root; documentation links are relative to `docs/`.

## Seismic Ratings and Collapse Probabilities

California hospital building seismic ratings, modeled collapse probabilities, and facility locations, published by the Department of Health Care Access and Information (HCAI).

- **Dataset title:** Seismic Ratings and Collapse Probabilities of California Hospitals
- **Dataset ID:** `seismic-ratings-and-collapse-probabilities-of-california-hospitals`
- **Publisher:** Department of Health Care Access and Information, Office of Statewide Hospital Planning and Development/Seismic Compliance Unit
- **Citation:** Department of Health Care Access and Information, Structural and Nonstructural Performance Categories and Collapse Probability of General Acute Care Hospital Buildings
- **License:** Terms of Use. The supplied package does not include the actual terms or a dedicated license URL.
- **Review date:** 2026-09-14. The project maintainer confirmed this snapshot was the most up-to-date data available from the publisher at the time of review.

### Project files

- Main observations CSV: `data/raw/seismic-ratings-and-collapse-probabilities-of-california-hospitals-.csv` (repository root relative; downloaded separately).
- [Dataset guide](SEISMIC_DATA.md)
- [Complete data dictionary](SEISMIC_DATA.md#detailed-data-dictionary)

### Seismic source links

- [Original main CSV download](https://data.chhs.ca.gov/dataset/257fb4cd-7687-41b5-8ae9-0bc6e29aa28e/resource/8f804127-40f0-4b25-b303-982956c19b73/download/ca-hcai-seismic-ratings-and-collapse-probabilities-09032026.csv)
- [Original detailed dictionary download](https://data.chhs.ca.gov/dataset/257fb4cd-7687-41b5-8ae9-0bc6e29aa28e/resource/c075b694-aa9c-4ed1-8991-a06099db16b1/download/datadictionary-seismic-ratings-and-collapse-probabilities.csv)
- [HCAI SPC/NPC ratings list](https://hcai.ca.gov/document/spc-npc-ratings-list/)
- [HCAI seismic compliance and safety program](https://hcai.ca.gov/facilities/building-safety/seismic-compliance-and-safety/)
- [HCAI facility detail](https://hcai.ca.gov/facilities/building-safety/facility-detail/)
- [Licensed Facility Cross-Walk](https://data.chhs.ca.gov/dataset/licensed-facility-crosswalk)

## Hospital Building Data

Physical characteristics, design codes, completion years, structural seismic ratings, and building portal links for California hospital buildings. This dataset complements the seismic ratings and collapse probabilities dataset.

- **Dataset title:** Hospital Building Data
- **Dataset ID:** `hospital-building-data`
- **Publisher:** Department of Health Care Access and Information/Office of Statewide Hospital Planning and Development
- **Citation:** Department of Health Care Access and Information, Hospital Building Data
- **License:** Terms of Use. The supplied package does not include the actual terms or a dedicated license URL.
- **Review date:** 2026-09-14. The uploaded package and its join with the seismic dataset were checked; availability of a newer publisher release was not independently verified.

### Project files

- Main observations CSV: `data/raw/hospital-building-data-.csv` (repository root relative; downloaded separately).
- [Dataset guide](HOSPITAL_BUILDING_DATA.md)
- [Complete data dictionary](HOSPITAL_BUILDING_DATA.md#detailed-data-dictionary)
- [Joining with the seismic dataset](HOSPITAL_BUILDING_DATA.md#joining-with-the-seismic-dataset)

### Building source links

- [Hospital Building Data (CSV)](https://data.chhs.ca.gov/dataset/dab37323-5b23-492e-9328-3bcc93bd1335/resource/d97adf28-ebaf-4204-a29e-bb6bdb7f96b9/download/ca-hcai-hospital-building-data-09032026.csv)
- [Data Dictionary - Hospital Building Data](https://data.chhs.ca.gov/dataset/dab37323-5b23-492e-9328-3bcc93bd1335/resource/cefc10e5-5071-4ca4-8b03-2249caf0d294/download/datadictionary-hospital-building-data.csv)
- [HCAI seismic compliance and safety program](https://hcai.ca.gov/facilities/building-safety/seismic-compliance-and-safety/)
- [HCAI facility detail](https://hcai.ca.gov/facilities/building-safety/facility-detail/)
