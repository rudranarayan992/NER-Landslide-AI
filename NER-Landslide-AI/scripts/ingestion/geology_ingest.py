from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.ingestion.base_ingest import PROJECT_ROOT, dataset_status_from_result, utc_now_iso

GEOLOGY_ROOT = PROJECT_ROOT / "data" / "raw" / "geology"


def scan_geology_files() -> list[Path]:
    if not GEOLOGY_ROOT.exists():
        return []
    return sorted(GEOLOGY_ROOT.rglob("*"))


def ingest_geology() -> dict[str, Any]:
    files = scan_geology_files()
    geology_files = [p for p in files if p.suffix.lower() in {".geojson", ".gpkg", ".shp", ".json", ".csv"}]
    if not geology_files:
        return {
            "dataset": "geology",
            "source": "local_geology",
            "status": "DATA NOT FOUND",
            "records": 0,
            "valid_records": 0,
            "invalid_records": 0,
            "geometry_available": 0,
            "geometry_missing": 0,
            "states": [],
            "last_processed": utc_now_iso(),
        }

    rows = [{
        "dataset_id": p.stem,
        "source": "local_geology",
        "lithology": None,
        "formation": None,
        "geological_age": None,
        "faults": None,
        "lineaments": None,
        "geometry": None,
        "data_status": "OBSERVED",
        "source_provenance": "OBSERVED",
        "created_at": utc_now_iso(),
    } for p in geology_files]
    status = dataset_status_from_result(rows, files_found=len(geology_files), invalid=0)
    return {
        "dataset": "geology",
        "source": "local_geology",
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
    print(ingest_geology())
