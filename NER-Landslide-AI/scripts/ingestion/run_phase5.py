from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.ingestion.administrative_ingest import ingest_administrative_boundaries
from scripts.ingestion.dem_ingest import ingest_dem
from scripts.ingestion.geology_ingest import ingest_geology
from scripts.ingestion.gsi_ingest import ingest_gsi_landslides
from scripts.ingestion.lgd_villages_ingest import ingest_lgd_villages
from scripts.ingestion.roads_ingest import ingest_roads
from scripts.ingestion.soil_ingest import ingest_soil


def run_phase5() -> dict[str, Any]:
    pipelines = [
        ("administrative_boundaries", ingest_administrative_boundaries),
        ("lgd_villages", ingest_lgd_villages),
        ("roads", ingest_roads),
        ("gsi_landslides", ingest_gsi_landslides),
        ("dem", ingest_dem),
        ("soil", ingest_soil),
        ("geology", ingest_geology),
    ]
    summary = {
        "phase": "5",
        "datasets": {},
        "available_datasets": [],
        "missing_datasets": [],
        "status": "completed",
    }

    for name, func in pipelines:
        result = func()
        summary["datasets"][name] = result
        if result.get("status") == "DATA NOT FOUND":
            summary["missing_datasets"].append(name)
        else:
            summary["available_datasets"].append(name)

    return summary


if __name__ == "__main__":
    result = run_phase5()
    print(json.dumps(result, indent=2, ensure_ascii=False))
