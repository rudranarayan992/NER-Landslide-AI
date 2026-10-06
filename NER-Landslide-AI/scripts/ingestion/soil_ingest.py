from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.ingestion.base_ingest import (
    PROJECT_ROOT,
    dataset_status_from_result,
    unavailable_dataset_summary,
    utc_now_iso,
)

SOIL_ROOT = PROJECT_ROOT / "data" / "raw" / "soil"


def scan_soil_files() -> list[Path]:
    if not SOIL_ROOT.exists():
        return []
    return sorted(SOIL_ROOT.rglob("*"))


def ingest_soil() -> dict[str, Any]:
    files = scan_soil_files()
    soil_files = [p for p in files if p.suffix.lower() in {".tif", ".tiff", ".nc", ".geojson", ".gpkg", ".shp", ".csv"}]
    if not soil_files:
        return unavailable_dataset_summary(
            "soil",
            source="local_soil",
            note="Soil and soil-moisture dataset not available in data/raw/soil; no verified source files were found.",
        )

    rows = [{
        "dataset_id": p.stem,
        "source": "local_soil",
        "sand": None,
        "silt": None,
        "clay": None,
        "bulk_density": None,
        "organic_carbon": None,
        "ph": None,
        "soil_depth": None,
        "soil_moisture": None,
        "file_path": str(p),
        "data_status": "OBSERVED",
        "source_provenance": "OBSERVED",
        "created_at": utc_now_iso(),
    } for p in soil_files]
    status = dataset_status_from_result(rows, files_found=len(soil_files), invalid=0)
    return {
        "dataset": "soil",
        "source": "local_soil",
        "status": status,
        "records": len(rows),
        "valid_records": len(rows),
        "invalid_records": 0,
        "geometry_available": 0,
        "geometry_missing": len(rows),
        "states": [],
        "last_processed": utc_now_iso(),
        "rows": rows,
    }


if __name__ == "__main__":
    print(ingest_soil())
