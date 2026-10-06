from __future__ import annotations

from pathlib import Path
from typing import Any

import geopandas as gpd

from backend.app.config import NER_STATES
from scripts.ingestion.base_ingest import PROJECT_ROOT, dataset_status_from_result, deduplicate_records, file_sha256, is_valid_ner_state, normalize_state_name, utc_now_iso

ROADS_ROOT = PROJECT_ROOT / "data" / "raw" / "roads"


def scan_roads_sources() -> list[Path]:
    if not ROADS_ROOT.exists():
        return []
    suffixes = (".geojson", ".gpkg", ".shp", ".json")
    return [p for p in sorted(ROADS_ROOT.rglob("*")) if p.is_file() and p.suffix.lower() in suffixes]


def ingest_roads() -> dict[str, Any]:
    files = scan_roads_sources()
    if not files:
        return {
            "dataset": "roads",
            "source": "local_roads",
            "status": "DATA NOT FOUND",
            "records": 0,
            "valid_records": 0,
            "invalid_records": 0,
            "geometry_available": 0,
            "geometry_missing": 0,
            "states": [],
            "last_processed": utc_now_iso(),
        }

    records: list[dict[str, Any]] = []
    for path in files:
        try:
            frame = gpd.read_file(path)
        except Exception:
            continue
        for _, row in frame.iterrows():
            geometry = row.get("geometry")
            candidate_state = normalize_state_name(row.get("state") or row.get("STATE") or row.get("state_name") or path.parent.name.replace("_", " "))
            if not is_valid_ner_state(candidate_state):
                continue
            record = {
                "road_id": row.get("road_id") or row.get("osm_id") or f"{path.stem}:{len(records)}",
                "osm_id": row.get("osm_id") or row.get("OSM_ID") or "",
                "name": row.get("name") or row.get("road_name") or row.get("NAME") or "",
                "road_type": row.get("road_type") or row.get("highway") or row.get("CLASS") or "",
                "state": candidate_state,
                "district": row.get("district") or row.get("DISTRICT") or "",
                "geometry": geometry,
                "source": "osm_geofabrik",
                "source_id": f"{path.name}:{row.get('road_id') or row.get('osm_id') or 'row'}",
                "geometry_status": "AVAILABLE" if geometry is not None and not geometry.is_empty else "NOT_AVAILABLE",
                "data_status": "OBSERVED",
                "source_provenance": "OBSERVED",
                "checksum": file_sha256(path),
                "created_at": utc_now_iso(),
                "updated_at": utc_now_iso(),
            }
            records.append(record)

    deduped = deduplicate_records(records, ("road_id", "source_id", "state"))
    valid = [record for record in deduped if is_valid_ner_state(record.get("state"))]
    status = dataset_status_from_result(valid, files_found=len(files), invalid=max(0, len(deduped) - len(valid)))
    return {
        "dataset": "roads",
        "source": "local_roads",
        "status": status,
        "records": len(deduped),
        "valid_records": len(valid),
        "invalid_records": max(0, len(deduped) - len(valid)),
        "geometry_available": sum(1 for item in deduped if item.get("geometry") is not None),
        "geometry_missing": sum(1 for item in deduped if item.get("geometry") is None),
        "states": sorted({normalize_state_name(item.get("state")) for item in deduped if item.get("state")}),
        "last_processed": utc_now_iso(),
        "rows": deduped,
    }


if __name__ == "__main__":
    print(ingest_roads())
