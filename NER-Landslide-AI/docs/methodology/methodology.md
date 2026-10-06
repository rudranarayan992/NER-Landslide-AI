# Methodology Overview

## Phase 1: Foundation and data collection pipeline

This phase establishes the project structure, metadata conventions, validation rules, and collection modules needed to ingest real data. It deliberately avoids model training and synthetic datasets.

## Phase 2: Data acquisition and validation

Real datasets for NER will be collected from authoritative sources and stored in raw datasets under `data/raw/`. Metadata and checksums are tracked so that provenance is preserved throughout the data lifecycle.

## Phase 3: GIS processing

Once real datasets are available, the GIS pipeline will:
- clip to NER boundaries
- filter to relevant states and district boundaries
- validate coordinates
- derive terrain features
- match rainfall and soil data to points or polygons
- associate roads, villages, and waterways
- generate standardized analytical datasets

## Phase 4: ML dataset preparation

The ML pipeline will create a training dataset in Parquet format. The target field will be binary: 0 for no observed landslide and 1 for observed landslide. Spatial and temporal validation will be used instead of random splits.

## Phase 5: Evaluation and calibration

The evaluation framework will include precision, recall, F1, PR-AUC, ROC-AUC, confusion matrices, calibration curves, and minority-class recall tracking.

## Phase 6: Operational deployment

After sufficient real data collection and validation, the system can be extended with the risk API, route-risk service, and frontend visualizations.
