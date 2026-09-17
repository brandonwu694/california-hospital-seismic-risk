# Seismic Ratings and Collapse Probabilities of California Hospitals

This guide summarizes the supplied package metadata and includes the complete detailed data dictionary, with observations from the current data snapshot used in this project. Source links in [DATA_SOURCES.md](DATA_SOURCES.md#seismic-ratings-and-collapse-probabilities) are recorded from the supplied package. This snapshot was the most up-to-date data available from the publisher at the time of review (September 14, 2026).

## Purpose and coverage

The dataset describes California general acute care hospital buildings, including structural and nonstructural seismic ratings, modeled collapse probabilities, and facility locations. It is a point-in-time snapshot, not a history of earthquakes or changes in building condition.

The current data snapshot contains 4,690 records, 423 distinct facility IDs, and 56 counties. Records also include proposed buildings, equipment yards, tanks, and other campus structures; not every row represents an operating hospital building.

## Project files

| File | Purpose |
| --- | --- |
| `data/raw/seismic-ratings-and-collapse-probabilities-of-california-hospitals-.csv` | Main CSV, relative to the repository root: 15 columns covering facility and building identity, status, ratings, collapse scores, and location. Downloaded separately using the data source instructions. |
| [Data sources](DATA_SOURCES.md#seismic-ratings-and-collapse-probabilities) | Publisher and citation details, license information, source links, project file locations, and review details. |

The [complete data dictionary](#detailed-data-dictionary) is included below. Store the main CSV in `data/raw/`; it is excluded from Git. Follow [Getting the data](DATA_SOURCES.md#getting-the-data) after cloning. [DATA_SOURCES.md](DATA_SOURCES.md#seismic-ratings-and-collapse-probabilities) provides the source and citation details. This guide contains the field definitions and interpretation notes.

## Provenance

- **Publisher:** Department of Health Care Access and Information, Office of Statewide Hospital Planning and Development/Seismic Compliance Unit.
- **Suggested citation from the package:** Department of Health Care Access and Information, Structural and Nonstructural Performance Categories and Collapse Probability of General Acute Care Hospital Buildings.
- **Contact:** seismiccomplianceunit@hcai.ca.gov.
- **Coverage:** California; county, city, and location point.
- **Snapshot date:** the source filename contains `09032026`, suggesting September 3, 2026. The package does not separately specify a snapshot date or download date.
- **Update frequency:** recorded as `other`; no specific schedule is supplied.
- **License:** recorded as `Terms of Use`; the package does not supply the actual terms or a dedicated license URL.
- **Limitations:** the field contains only the placeholder `Limitations`, so it provides no substantive guidance.
- **Secondary sources:** recorded as `None`.

### Source and related links

The seismic dataset’s section in [DATA_SOURCES.md](DATA_SOURCES.md#seismic-ratings-and-collapse-probabilities) contains the original data and dictionary downloads, HCAI ratings list, seismic safety program, facility detail page, and Licensed Facility Cross-Walk. The crosswalk is referenced by the publisher for linking HCAI facility IDs with IDs from other departments, such as CDPH.

## Interpreting the main fields

| Fields | Meaning and use |
| --- | --- |
| `Perm ID`, `Facility Name` | Facility identifier and name. Multiple records can belong to one facility; keep IDs as text for joins. |
| `Building Nbr`, `Building Name` | Building identifier and name. `Building Nbr` is unique across the current data snapshot. |
| `County Code`, `City` | Facility geography. `County Code` combines the county number and name. |
| `Building Status` | Indicates use or structure status. Select statuses appropriate to the analysis; 3,183 rows in the current data snapshot have the exact value `OSHPD 1-In Service`. |
| `SPC Rating` | Structural Performance Category. The dictionary describes SPC 1 as significant collapse risk and SPC 5 as reasonably capable of providing services after strong shaking. An `s` suffix indicates an unverified SPC rating. |
| `HCAI NPC Rating` | Nonstructural Performance Category, addressing architectural, mechanical, and electrical systems, components, and equipment. The dictionary describes implications for evacuation and continued operation. |
| `2007 Hazus Score (%)`, `2010 Hazus Score (%)` | Modeled collapse probabilities conditional on specified design-level ground motion occurring at the site. The years refer to model versions, not observation years. These are not annual collapse probabilities. |
| `AB 1882 Notice` | Explanatory seismic notice supplied for some buildings. Consult the detailed dictionary for its descriptions. |
| `Latitude`, `Longitude` | Coordinates of the facility where the building is located, not necessarily the individual building. |
| `Count` | Always `1` in this snapshot. Summing it counts records, not distinct hospitals. |

## Related building dataset

The [Hospital Building Data guide](HOSPITAL_BUILDING_DATA.md) describes height, stories, design code, completion year, and building portal links for the same buildings. The current snapshots match one-to-one across all 4,690 records using `Perm ID` and `Building Nbr`, with agreement across all 12 shared columns after normalizing the SPC headers. See [joining guidance](HOSPITAL_BUILDING_DATA.md#joining-with-the-seismic-dataset) for header differences, identifier types, and checks to repeat for future snapshots.

## Detailed data dictionary

The following table reproduces all 15 entries from the publisher’s dictionary CSV, including the original types, labels, wording, and spelling. The empty description for `City` is also preserved. These source definitions supplement the interpretation notes above. The original CSV used Windows-1252 (`cp1252`) encoding; its contents are now consolidated here.

| Column | Type | Label | Description |
| --- | --- | --- | --- |
| County Code | Text | County Code | County Number and County Name.  County numbers are assigned to each California county from 1 - 58 in alphabetical order. |
| Perm ID | Text | Perm ID | Unique Facility Identification Number established by HCAI Facilities Development Division; aslo referred to as “Perm ID” in other datasets. |
| Facility Name | Text | Facility Name | Name of the General Acute Care Hospital. |
| City | Text | City |  |
| Building Nbr | Text | Building Number | Unique Building Number assigned by HCAI Facilities Development Division to a seismically separate building on a hospital campus. |
| Building Name | Text | Building Name | Building name provided to HCAI by the Facility. |
| Building Status | Text | Building Status | Statuses include "In Service" for buildings that are currently in use and "Under Construction" for buildings currently under construction.  Other statuses are used to identify buildings that may be located in general acute care facility but do not provide general acute care services. |
| SPC Rating | Text | SPC Rating | Seismic ratings for the building's primary structure are expressed as a Structural Performance Category; SPC ratings range from 1 to 5 with SPC 1 assigned to buildings posing significant risk of collapse following a strong earthquake and SPC 5 assigned to buildings reasonably capable of providing services to the public following a strong earthquake. Where SPC ratings have not been verified by the Department of Health Care Access and Information (HCAI), the rating index is followed by the letter 's'.  N/A = Not Applicable and  NYA = Not Yet Available. |
| 2007 Hazus Score (%) | Numeric | 2007 Hazus Score (%) | The Multi-Hazard Loss Estimation Technology (HAZUS) program is used to determine the Probability of Collapse of the building; expressed as a percentage, this number reflects the likelihood of the building to collapse when ground motions of a given design acceleration occur at the building site - 2007 version. |
| 2010 Hazus Score (%) | Numeric | 2010 Hazus Score (%) | The Multi-Hazard Loss Estimation Technology (HAZUS) program is used to determine the Probability of Collapse of the building; expressed as a percentage, this number reflects the likelihood of the building to collapse when ground motions of a given design acceleration occur at the building site; the 2010 version uses additional building parameters to determine the collapse probability. Buildings located directly on faults are assigned probability of -50%. |
| HCAI NPC Rating | Text | HCAI NPC Rating | Seismic ratings for anchorage and bracing of the building's architectural, mechanical, electrical systems, components and equipment are expressed as a Nonstructural Performance Category; NPC ratings range from 1 to 5 with NPC 1 assigned to buildings where the safe and orderly evacuation following a strong earthquake cannot be assured and NPC 5 assigned to buildings capable of continued operation for 72 hours without any power, water and sewer services following a strong ground motion.    N/A = Not Applicable and  NYA = Not Yet Available. |
| AB 1882 Notice | Text | AB 1882 Notice | Buildings which do not meet seismic safety regulations (SPC-2) are identified as “These buildings do not significantly jeopardize life, but may not be repairable or functional following an earthquake”. Buidings which do meet seismic safety regulations (SPC-5/NPC-5) are identified as “Earthquake Resilient”. |
| Latitude | Numeric | Latitude | Latitude of facility where building is located |
| Longitude | Numeric | Longitude | Longitude of facility where building is located |
| Count | Numeric | Count | Column to facilitate counting of filtered rows |

## Loading and analysis notes

See the [EDA notebook](../notebooks/01_eda_seismic.ipynb) for per-column missingness, numeric and rating distributions, identifier checks, city inconsistencies, and cleanup findings that informed the current pipeline. The notebook contains the analysis and its saved inline results.

- The main CSV decodes using Windows-1252 (`cp1252`).
- The main CSV header contains a trailing space in `SPC Rating `. Strip header whitespace when loading, while preserving the source file.
- The package schema declares every main-table field as a string. Parse coordinates and collapse scores into numeric values explicitly where needed.
- Preserve rating values as text. Values include `N/A`, `3s`, `4D`, `3R`, and `4D-L1`; the supplied dictionary does not fully explain every variant. It defines `N/A` as not applicable and `NYA` as not yet available.
- Only 403 rows have a 2007 Hazus score and 295 have a 2010 score. These counts may overlap. Blank scores are missing values, not zero collapse risk.
- The dictionary documents `-50` as a special 2010 Hazus value for buildings directly on faults. No negative Hazus scores occur in the current data snapshot; if encountered in later data, do not interpret that marker as a literal probability.
- Facility coordinates repeat across building records. Aggregate by `Perm ID` when counting or mapping hospitals, with an explicit rule for summarizing building-level ratings.
