from __future__ import annotations

from typing import Any

from scripts.ingestion.base_ingest import unavailable_dataset_summary
from scripts.ingestion.dem_ingest import ingest_dem
from scripts.ingestion.soil_ingest import ingest_soil


def run_phase6() -> dict[str, Any]:
    """Registry of Phase 6 terrain and environmental datasets.

    This repository does not contain verified raw DEM, rainfall, weather, soil moisture,
    hydrology, or satellite sources for the North East Region. We therefore register the
    current status as unavailable rather than fabricating inference or synthetic data.
    """
    datasets = {
        "dem": ingest_dem(),
        "terrain_derivatives": unavailable_dataset_summary(
            "terrain_derivatives",
            source="local_terrain",
            note="Terrain derivatives (slope, aspect, TWI, curvature, roughness) are not available; no verified DEM source exists yet.",
        ),
        "rainfall": unavailable_dataset_summary(
            "rainfall",
            source="local_rainfall",
            note="Rainfall and meteorological time series are not available in data/raw/rainfall; no verified source files were found.",
        ),
        "weather": unavailable_dataset_summary(
            "weather",
            source="local_weather",
            note="Weather observations and IMD-style station data are not available in this repository.",
        ),
        "soil": ingest_soil(),
        "soil_moisture": unavailable_dataset_summary(
            "soil_moisture",
            source="local_soil_moisture",
            note="Soil moisture observations are not available; no verified remote or local dataset has been attached.",
        ),
        "hydrology": unavailable_dataset_summary(
            "hydrology",
            source="local_hydrology",
            note="Hydrological drainage and river network datasets are not available in data/raw/hydrology; no verified source files were found.",
        ),
        "satellite": unavailable_dataset_summary(
            "satellite",
            source="local_satellite",
            note="Satellite imagery and derived indices are not available in data/raw/satellite; no verified remote source has been configured.",
        ),
    }

    summary = {
        "phase": "6",
        "status": "completed",
        "datasets": datasets,
        "available_datasets": [name for name, result in datasets.items() if result.get("status") not in {"DATA NOT FOUND", "DATASET NOT AVAILABLE — AWAITING VERIFIED SOURCE DATA."}],
        "missing_datasets": [name for name, result in datasets.items() if result.get("status") in {"DATA NOT FOUND", "DATASET NOT AVAILABLE — AWAITING VERIFIED SOURCE DATA."}],
        "message": "Phase 6 is limited to verified terrain/environment foundation; unavailable datasets remain explicitly marked as unpopulated.",
    }
    return summary


if __name__ == "__main__":
    import json

    print(json.dumps(run_phase6(), indent=2, ensure_ascii=False))
