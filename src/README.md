# Project notebook guide (01–05)

This repository is organised as a short analysis pipeline. The notebooks build progressively from raw source data to a simple PV-vs-MIDAS correlation workflow. Each notebook saves outputs to `data/outputs/...` and expects the project structure used by the earlier notebooks.

Key conventions used throughout:
- Paths are relative to the repository root, with notebook code run from the `src/` directory.
- MIDAS files live under `data/inputs/MIDAS202607/...`
- Generated data products are saved under `data/outputs/...`
- The notebooks work best when run in order: 01 → 02 → 03 → 04 → 05

## 01 — Project setup and data inventory
Purpose:
- Establish the project structure, data folders, and references to the main sources.
- Review the available datasets before analysis starts.

What it does:
- Confirms the repository layout and file locations.
- Identifies the PV and meteorological input sources.
- Sets the groundwork for subsequent notebooks by defining paths and common variables.

Why it matters:
- This is the “entry point” for anyone who needs to understand where the input files come from and where the outputs should be written.

Continue from here:
- Move to 02 to define the geography (GSP regions, maps, and physical reference points).
- If you need to inspect raw inputs first, review the `data/inputs/` folders before running the next notebook.

## 02 — GSP regions, mapping, and spatial reference setup
Purpose:
- Load the Great Britain GSP polygon data and prepare a spatial baseline.
- Identify a reference point or centroid for each GSP region.

What it does:
- Reads the geometry and attributes for GSP regions.
- Selects a specific GSP (for example, ABHA1 or another region) for analysis.
- Produces plots of region boundaries and reference points.
- Projects data into a suitable CRS (for example, EPSG:27700 for GB).
- Prepares the spatial context needed for distance calculations.

Why it matters:
- 05 later relies on knowing how near a MIDAS station is to a GSP region.
- This notebook creates the map and point geometry used in the correlation workflow.

Continue from here:
- Use the selected GSP geometry as the anchor for the station-distance calculations in 05.
- If a new GSP is required, reuse the same code pattern without reworking the analysis logic.

## 03 — PV_Live extraction and GSP time series
Purpose:
- Pull PV generation time series from the PV_Live API for one or more GSPs.
- Convert the raw fetched data into a clean dataframe ready for alignment with weather data.

What it does:
- Calls the PV_Live API.
- Extracts generation values and metadata.
- Stores the raw JSON response as a dataframe.
- May save a GSP capacity and spatial reference dataset to `data/outputs/reference_data/`.
- Builds a daily or period-specific PV time series for later comparison.

Why it matters:
- This notebook creates the “target” series for the correlation analysis.
- It is the source of the observed PV output used in notebook 05.

Continue from here:
- The resulting PV time series is used directly in 05.
- If new GSP IDs are needed, rerun the same API pull with different parameters.

## 04 — MIDAS metadata, station selection, and radiation extraction
Purpose:
- Load MIDAS station metadata and the hourly/daily radiation files.
- Filter the data to a target period and prepare a clean radiation dataset.

What it does:
- Reads MIDAS metadata and station locations.
- Finds all annual radiation files for the relevant year(s).
- Chooses the highest-quality QC version for each station/year.
- Parses the raw file preamble and identifies the real observation table.
- Selects only native hourly observations and excludes 23:59 daily summary rows from the canonical analysis dataset.
- Saves:
  - `data/outputs/MIDAS202607/midas_2024_hourly_radiation.csv`
  - `data/outputs/MIDAS202607/midas_2024_all_rows_radiation.csv`

Why it matters:
- This is the main data-preparation step for the meteorological side of the project.
- It ensures the weather records are not corrupted by daily summary rows or inconsistent metadata.

Continue from here:
- Notebook 05 consumes the cleaned MIDAS output directly.
- If you need to expand to a longer or different time period, update the date range in this notebook and rerun the export.

## 05 — PV and MIDAS correlation analysis
Purpose:
- Compare PV generation against nearby MIDAS irradiance records.
- Build a simple correlation workflow and visualise the relationship.

What it does:
- Selects a GSP region and nearby MIDAS stations.
- Computes station-to-GSP distances.
- Pulls the closest MIDAS records for the target period.
- Converts MIDAS irradiation from kJ/m² to W/m² as needed.
- Aligns PV and irradiance time series on the same datetime index.
- Averages several nearby station records into a composite weather proxy.
- Computes Pearson correlation and produces scatter/time-series plots.

Why it matters:
- This notebook is the first modelling step that links output-side data (PV_Live) with weather-side data (MIDAS).
- It demonstrates the basic pattern for later work: station selection, alignment, normalisation, and correlation.

Continue from here:
- Extend the analysis to multiple GSPs or multiple months/years.
- Replace the simple average-of-nearest-stations approach with weighted averages, distance decay models, or a fuller regression pipeline.
- Use the saved hourly MIDAS CSV as the canonical input for broader analysis.

## Recommended workflow for a new analyst
1. Start with 01 to understand folder structure and expected outputs.
2. Run 02 to define the GSP geography and reference points.
3. Run 03 to obtain PV_Live generation for the GSP(s) of interest.
4. Run 04 to prepare the MIDAS radiation dataset for the same period.
5. Run 05 to conduct the first correlation analysis and inspect the map/time-series diagnostics.
6. If the project is extended, continue from the saved CSVs rather than rerunning earlier notebooks unnecessarily.

## Important outputs to keep
- `data/outputs/reference_data/`
  - GSP region files, capacity tables, and geometry exports
- `data/outputs/MIDAS202607/`
  - canonical 2024 hourly MIDAS dataset
  - full raw-period MIDAS export
- `data/inputs/MIDAS202607/`
  - source MIDAS meteorological data
- `data/inputs/...` and `data/outputs/...` used by the PV_Live API workflow

## Practical note
The code assumes the repository is kept in a consistent structure and that notebooks are run from the `src/` directory. If you are continuing a project from a notebook midway through the sequence, start by checking which outputs already exist, then move to the next notebook that depends on them.

## Data source map: MIDAS vs AWS near-live vs GSP/PV outturn

This project is mixing three different kinds of data, and they are not interchangeable.

### 1) MIDAS: historical meteorological archive
What it is:
- MIDAS = Met Office Integrated Data Archive System.
- This is the historical weather station archive used for station-based observations such as temperature, rainfall, pressure, and radiation.
- For this project, the important MIDAS files are the radiation observations under `data/inputs/MIDAS202607/...`.

What this means in practice:
- MIDAS is the source of the historical irradiance time series used in notebooks 04 and 05.
- It is a station archive, not a live operational feed.
- It is not refreshed in near-real time; it is a historical dataset that is usually delivered in periodic updates or annual/monthly batches.

Typical fields in this project:
- `ob_end_time`
- `glbl_irad_amt`
- `direct_irad`
- station metadata such as latitude/longitude
- QC version folders such as `qc-version-1`, `qc-version-2`, etc.

Why it matters:
- MIDAS is the weather-side input for a comparison against PV output.
- A lot of the notebook logic is there to parse raw MIDAS CSVs, choose the highest QC version, and remove summary rows like 23:59 daily totals.

Useful references:
- Met Office climate/data archive: https://www.metoffice.gov.uk/research/climate/maps-and-data
- MIDAS Open / historical station data: https://www.metoffice.gov.uk/research/climate/maps-and-data/uk-and-regional-series

### 2) AWS-hosted near-live dataset
What it is:
- This refers to the more recent, near-live operational dataset that is hosted in AWS and used for recent generation/outturn-type analysis.
- It is not the same as MIDAS.
- It is generally a live or near-live operational source, designed for recent monitoring and analysis rather than long historical weather reconstruction.

What this means in practice:
- The AWS-hosted dataset is the “recent operational” side of the project, often used when we are looking at recent days/weeks/months rather than the historical archive.
- Some notebooks may refer to this as “the AWS data” or “near-live data”; it is separate from MIDAS and should not be confused with the historical station data.

Why it matters:
- The AWS dataset is not the primary source for meteorological station comparison in the project.
- It is mostly relevant to recent operational analysis or quick investigations of recent GSP output or near-live status.

### 3) GSP regions and PV outturn/generation data
What it is:
- GSP = Grid Supply Point. These are regional electricity zones in Great Britain.
- The region polygons used in the project are geospatial boundary files for the GSP areas.
- PV outturn / generation data is the actual recorded generation for those GSP areas.

Where this data comes from:
- GSP region geometry and reference data:
  - generated/used in the project as local spatial reference data, saved under `data/outputs/reference_data/`
  - these are linked to the GSP regions used for mapping and distance calculations
- PV outturn / generation:
  - PV_Live API: https://api.pvlive.uk/pvlive/api/v4
  - this is the live / recent output feed used to get generation data by GSP
  - the project reads `generation_mw` and related metadata from this API

Useful references:
- PV_Live / NESO data portal: https://www.neso.energy/data-portal/pv-live
- PV_Live API docs / endpoint examples: https://api.pvlive.uk/

Important distinction:
- The GSP polygons are spatial geography.
- The PV output is operational electricity generation.
- MIDAS is weather data.
- These are separate data products serving different roles in the project.

## Which notebooks use which source?

### 01
- project setup and high-level data inventory
- usually explains which folders exist and what the project depends on
- no major data analysis yet

### 02
- geometric / spatial notebook
- uses GSP region polygons and map geometry
- prepares the spatial reference context for nearest-station selection and distance calculations

### 03
- PV_Live retrieval and GSP generation time series
- uses the PV_Live API for generation data
- uses GSP metadata / capacity / geometry

### 04
- MIDAS station metadata and radiation extraction
- uses historical MIDAS weather files
- teaches how to parse raw MIDAS CSVs and prepare a clean hourly dataset

### 05
- correlation work between GSP/PV output and MIDAS irradiance
- combines:
  - PV_Live generation data
  - GSP region geometry
  - nearby MIDAS stations
- this is where the historical weather and operational generation are deliberately aligned

## Short version
- MIDAS = historical weather station archive
- AWS near-live = recent operational data; not the same as MIDAS
- GSP/PV outturn = regional electricity generation data from PV_Live / GSP definitions
- notebooks 03 and 05 are primarily about PV / GSP data
- notebooks 04 and 05 are primarily about MIDAS weather data

## Recommended note to keep in each notebook
At the top of any notebook that reads weather or generation data, add a small block like:

```python
# DATA SOURCE NOTE
# - MIDAS = historical Met Office weather archive (station observations)
# - AWS near-live = recent operational dataset; not the same as MIDAS
# - PV outturn = PV_Live API generation data by GSP
# - GSP geometry = project geospatial definitions for regional supply points
```