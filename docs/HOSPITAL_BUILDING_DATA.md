# Hospital Building Data

This guide summarizes the supplied package metadata and includes the complete detailed data dictionary, with observations from the current data snapshot used in this project. Source links are recorded in [DATA_SOURCES.md](DATA_SOURCES.md#hospital-building-data).

## Purpose and coverage

The dataset describes California general acute care hospital buildings, including height, number of stories, the building code used for design, code year, completion year, and structural seismic ratings. Each record also includes a building portal URL and facility coordinates. It is a point-in-time snapshot.

The current data snapshot contains 4,690 records, 423 distinct facility IDs, and 56 counties. Each `Building Nbr` is unique. Records include proposed buildings, equipment yards, tanks, and other campus structures; not every row represents an operating hospital building. There are 3,183 records with the exact status `OSHPD 1-In Service`.

## Project files

| File | Purpose |
| --- | --- |
| `data/raw/hospital-building-data-.csv` | Main CSV, relative to the repository root: 18 columns covering facility and building identity, status, physical characteristics, design code, completion year, ratings, and location. Downloaded separately using the data source instructions. |
| [Data sources](DATA_SOURCES.md#hospital-building-data) | Publisher, citation, license information, source links, review details, and project file locations. |
| [Seismic dataset guide](SEISMIC_DATA.md) | Definitions and interpretation of the complementary NPC ratings and Hazus collapse probabilities. |

The [complete data dictionary](#detailed-data-dictionary) is included below. Store both observation CSVs in `data/raw/` with their original contents; they are excluded from Git. Follow [Getting the data](DATA_SOURCES.md#getting-the-data) after cloning.

## Provenance

- **Publisher:** Department of Health Care Access and Information/Office of Statewide Hospital Planning and Development.
- **Suggested citation from the package:** Department of Health Care Access and Information, Hospital Building Data.
- **Contact:** seismiccomplianceunit@hcai.ca.gov.
- **Coverage:** California; county, city, and location point.
- **Snapshot date:** the source filename contains `09032026`, suggesting September 3, 2026. The package does not separately specify a snapshot date or download date.
- **Update frequency:** recorded as `biweekly`. The package does not clarify the interval or provide a publication schedule.
- **License:** recorded as `Terms of Use`; the package does not supply the actual terms or a dedicated license URL.
- **Limitations:** the field contains only the placeholder `Limitations`, so it provides no substantive guidance.
- **Secondary sources:** the package field is blank.
- **Review:** the uploaded files and their relationship to the seismic dataset were checked on September 14, 2026. This review did not independently establish whether the publisher has a newer release.

## Interpreting the main fields

| Fields | Meaning and use |
| --- | --- |
| `Perm ID`, `Facility Name` | Facility identifier and name. Multiple building records belong to one facility. Treat the identifier as text when joining datasets. |
| `Building Nbr`, `Building Name` | Identifier for a seismically separate building and its facility-provided name. |
| `County Code`, `City` | Facility geography; county code combines the county number and name. |
| `Building Status` | Identifies use or structure status. Select statuses appropriate to the analysis before counting operating buildings. |
| `SPC Rating *` | Structural Performance Category. Preserve category labels and suffixes as text. The detailed dictionary calls this field `SPC Rating*`, without the space before the asterisk. |
| `Building URL` | Link to the building page in the HCAI/OSHPD eServices Portal, including access to related construction projects. |
| `Height (ft)`, `Stories` | Building height in feet and number of stories, where available. Missing values do not mean zero. |
| `Building Code`, `Building Code Year` | Design code and its associated edition year. The code year is not the building’s completion year. |
| `Year Completed` | Building completion year. A blank value does not by itself establish that a building is unfinished. |
| `AB 1882 Notice` | Publisher-provided seismic notice for some buildings; consult the source definition below. |
| `Latitude`, `Longitude` | Coordinates of the facility where the building is located, not necessarily the individual building. |
| `Count` | Always `1` in this snapshot. Summing it counts records, not distinct facilities. |

## Joining with the seismic dataset

Use `Perm ID` and `Building Nbr` together as the join key. In the current snapshots, all 4,690 records match one-to-one, with no unmatched records or duplicate key pairs. All 12 shared columns agree after normalizing the SPC headers. This agreement should be checked again when either snapshot is updated.

The building dataset adds `Building URL`, `Height (ft)`, `Stories`, `Building Code`, `Building Code Year`, and `Year Completed`. The seismic dataset adds `HCAI NPC Rating`, `2007 Hazus Score (%)`, and `2010 Hazus Score (%)`.

Normalize the building CSV’s `SPC Rating *` and the seismic CSV’s `SPC Rating ` (which has a trailing space) to the same analysis column name. Load `Perm ID` consistently as text in both datasets, even though the building dictionary declares it numeric. Keep the raw files unchanged and join through the validated [cleaning pipeline](CLEANING_PIPELINE.md). The pipeline checks key uniqueness, unmatched records, and agreement of shared fields before publishing the integrated table. Avoid joining on facility name or coordinates, which can repeat across buildings.

## Detailed data dictionary

The following table reproduces all 18 entries from the publisher’s dictionary CSV, including the original types, labels, wording, and spelling. These source definitions supplement the interpretation notes above. The original dictionary used Windows-1252 (`cp1252`) encoding; its contents are consolidated here.

| Column | Type | Label | Description |
| --- | --- | --- | --- |
| County Code | Text | County Code | County number (set by State of California) and County Name |
| Perm ID | Numeric | Perm ID | Facility number per Facilities Development Division |
| Facility Name | Text | Facility Name | Name of the General Acute Care Hospital |
| City | Text | City | City |
| Building Nbr | Text | Building Nbr | Unique building number assigned to seismically separate building in a hospital campus. |
| Building Name | Text | Building Name | Building name provided by the Facility. |
| Building Status | Text | Building Status | If currently in service, status is "In Service". If under construction, status is "Under Construction". Other statuses are used to identify buildings that may be located in general acute care facility but do not provide general acute care services. |
| SPC Rating* | Text | SPC Rating* | Structural Performance Category used to rate the building structure, can be 1 to 5, “s” is added where the rating is not confirmed by HCAI.  SPC 1 is assigned to buildings that may be at risk of collapse in a strong earthquake and SPC 5 is assigned to buildings reasonably capable of providing services to the public following strong ground motion.  N/A = Not Applicable and NYA = Not Yet Available. |
| Building URL | Text | Building URL | A URL that oens the page associated with Building Nbr in the eServices Portal which provides access to related projects being constructed in the building. |
| Height (ft) | Numeric | Height (ft) | Height in feet for the building where available |
| Stories | Numeric | Stories | Number of stories in the building where available. |
| Building Code | Text | Building Code | The building code that was used to design the building where available. |
| Building Code Year | Numeric | Building Code Year | The year associated with the building code that was used to design the building (where available). |
| Year Completed | Numeric | Year Completed | The year that building was completed. Typically, the year the building is completed is later than the building code year. |
| AB 1882 Notice | Text | AB 1882 Notice | Buildings which do not meet seismic safety regulations (SPC-2) are identified as “These buildings do not significantly jeopardize life, but may not be repairable or functional following an earthquake”. Buidings which do meet seismic safety regulations (SPC-5/NPC-5) are identified as “Earthquake Resilient”. |
| Latitude | Numeric | Latitude | Latitude of facility where building is located |
| Longitude | Numeric | Longitude | Longitude of facility where building is located |
| Count | Numeric | Count | Column to facilitate counting of filtered rows |

## Loading and analysis notes

See the [building EDA notebook](../notebooks/02_eda_hospital_building.ipynb) for per-column missingness, physical characteristics, code/completion-year checks, identifier consistency, and cleanup findings that informed the current pipeline, with saved inline results.

- The main CSV decodes using Windows-1252 (`cp1252`).
- Preserve IDs and SPC ratings as text. `N/A` means not applicable, and `NYA` means not yet available according to the dictionary; do not treat category labels as numeric ratings.
- The package schema declares `Perm ID`, height, stories, code year, completion year, latitude, longitude, and count as numeric. Other columns are strings. Treat `Perm ID` as an identifier when loading, and parse measurement fields explicitly while preserving missing values.
- `Building Code` has 80 `Unknown` values and no blanks. Unknown code information is distinct from a known code edition.
- Facility coordinates repeat across building records. Group by `Perm ID` when counting facilities, and state how building characteristics are summarized.

| Field | Blank records in the current snapshot |
| --- | ---: |
| `Height (ft)` | 2,361 |
| `Stories` | 1,074 |
| `Building Code Year` | 80 |
| `Year Completed` | 889 |

These counts describe missing values in separate columns and may overlap. Do not replace blanks with zero or infer building age from the code year.
