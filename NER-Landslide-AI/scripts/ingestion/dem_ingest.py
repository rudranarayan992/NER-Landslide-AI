from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.ingestion.base_ingest import (
    PROJECT_ROOT,
    dataset_status_from_result,
    unavailable_dataset_summary,
    utc_now_iso,
)

DEM_ROOT = PROJECT_ROOT / "data" / "raw" / "dem"


def scan_dem_files() -> list[Path]:
    if not DEM_ROOT.exists():
        return []
    return sorted(DEM_ROOT.rglob("*"))


def ingest_dem() -> dict[str, Any]:
    files = scan_dem_files()
    raster_files = [p for p in files if p.suffix.lower() in {".tif", ".tiff", ".asc", ".img", ".vrt", ".nc"}]
    if not raster_files:
        return unavailable_dataset_summary(
            "dem",
            source="local_dem",
            note="DEM dataset not available in data/raw/dem; no verified raster source was found.",
        )

    rows = [{
        "dataset_id": p.stem,
        "source": "local_dem",
        "resolution": "unknown",
        "crs": "EPSG:4326",
        "bounds": None,
        "file_path": str(p),
        "download_date": None,
        "checksum": None,
        "data_status": "OBSERVED",
        "source_provenance": "OBSERVED",
        "created_at": utc_now_iso(),
    } for p in raster_files]
    status = dataset_status_from_result(rows, files_found=len(raster_files), invalid=0)
    return {
        "dataset": "dem",
        "source": "local_dem",
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
    print(ingest_dem())
