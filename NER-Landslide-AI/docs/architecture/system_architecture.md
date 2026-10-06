# NER Landslide AI Architecture

## Overview

This project is designed as a real-data-first monitoring and early-warning foundation for the North Eastern Region (NER) of India. The system focuses on landslide hazard monitoring, GIS-enriched contextualization, and future ML-driven risk modeling once data sources are available and validated.

## Design principles

- Real data only: no fabricated landslide records or environmental measurements.
- Raw data preservation: never overwrite original downloaded files.
- Provenance tracking: store source, license, timestamp, and file hash information.
- Modularity: each data source has a dedicated collector.
- CRS discipline: all transformations must be explicit and documented.
- Separation of concerns: image AI is isolated from environmental risk prediction.
- Avoid overclaiming: probability outputs are not treated as validated chance-of-landslide percentages.

## Core layers

### 1. Data acquisition

The collection layer stores raw files under `data/raw/` by data type. Each collector is a standalone module within `pipelines/collect/` and logs failures and validation results.

### 2. Data validation and provenance

The validation layer checks file existence, metadata completeness, and file-type suitability. Provenance metadata is maintained for every ingested dataset.

### 3. Processing and GIS integration

The GIS pipeline later clips boundaries, validates coordinates, creates landslide points, derives terrain features, performs spatial joins, and aligns rainfall, soil, geology, and infrastructure features.

### 4. Database and storage

The `database/schema` files define the PostGIS schema for administrative, environmental, and prediction tables. Each table uses a geometry column where relevant.

### 5. Backend API

The FastAPI API exposes health and registry/data endpoints. It is intentionally a skeleton until datasets are loaded.

### 6. Frontend dashboard

The React + TypeScript + Vite dashboard provides a green-and-dark-green environmental monitoring layout. It is intentionally a UI scaffold and not a connected analytics dashboard yet.

### 7. ML and image AI

The repository prepares a structure for later model work, but development is intentionally deferred until real, validated datasets exist.

## Standard data sources

The project supports the following categories:
- administrative boundaries
- landslide inventories
- rainfall time series / gridded data
- soil
- geology
- DEM / terrain
- satellite imagery
- land cover
- hydrology
- roads and infrastructure
- villages and settlements
- field reports

## CRS guidance

Use a consistent geodetic reference system and document it. The default config sets:
- input / general display: EPSG:4326
- target projected CRS: EPSG:32646

If a dataset arrives in another CRS, the transformation and reason for reprojection must be recorded in a processing log or metadata document.

## Current status

This repository is intentionally in the first stage and contains the project foundation, collection cycle templates, and startup health check, without implementing ML training or fake results.
