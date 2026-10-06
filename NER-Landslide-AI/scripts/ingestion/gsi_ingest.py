from __future__ import annotations

import csv
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from backend.app.config import NER_STATES
from scripts.ingestion.base_ingest import PROJECT_ROOT, dataset_status_from_result, is_valid_ner_state, normalize_state_name, utc_now_iso

GSI_ROOT = PROJECT_ROOT / "data" / "raw" / "landslides"
GSI_PROCESSED = PROJECT_ROOT / "data" / "processed" / "landslides"


def find_gsi_pdf() -> Path | None:
    if not GSI_ROOT.exists():
        return None
    candidates = sorted(GSI_ROOT.rglob("*.pdf"))
    return candidates[0] if candidates else None


def parse_gsi_events() -> list[dict[str, Any]]:
    pdf_path = find_gsi_pdf()
    if pdf_path is None:
        return []

    csv_path = GSI_PROCESSED / "gsi_extracted" / f"{pdf_path.stem}_raw_extraction.csv"
    if not csv_path.exists():
        return []

    rows: list[dict[str, Any]] = []
    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row:
                continue
            state = normalize_state_name(row.get("raw_state") or row.get("state") or "")
            if state and not is_valid_ner_state(state):
                continue
            latitude = row.get("raw_latitude") or row.get("latitude")
            longitude = row.get("raw_longitude") or row.get("longitude")
            try:
                lat_value = float(latitude) if latitude not in (None, "", "NA", "N/A") else None
                lon_value = float(longitude) if longitude not in (None, "", "NA", "N/A") else None
            except (TypeError, ValueError):
                lat_value = None
                lon_value = None

            source_file = row.get("source_file") or pdf_path.name
            source_page = row.get("source_page") or row.get("page_number") or ""
            record = {
                "source_name": "GSI",
                "source_file": source_file,
                "source_page": source_page,
                "source_id": f"{source_file}:{source_page}:{(row.get('record_index') or row.get('page_number') or '0')}",
                "event_date": row.get("raw_date") or row.get("date") or None,
                "state": state,
                "district": (row.get("raw_district") or row.get("district") or "").strip(),
                "location": (row.get("raw_location") or row.get("location") or "").strip(),
                "latitude": lat_value,
                "longitude": lon_value,
                "geometry": None,
                "landslide_type": (row.get("raw_landslide_type") or row.get("landslide_type") or "").strip(),
                "trigger": (row.get("raw_trigger") or row.get("trigger") or "").strip(),
                "description": (row.get("raw_text") or row.get("description") or "").strip(),
                "data_status": "OBSERVED" if (lat_value is not None and lon_value is not None) else "NOT_AVAILABLE",
                "source_provenance": "OBSERVED",
                "created_at": utc_now_iso(),
                "updated_at": utc_now_iso(),
            }
            rows.append(record)
    return rows


def ingest_gsi_landslides() -> dict[str, Any]:
    rows = parse_gsi_events()
    valid_rows = [r for r in rows if r.get("state") in NER_STATES]
    invalid_rows = max(0, len(rows) - len(valid_rows))
    status = dataset_status_from_result(valid_rows, missing=(not rows), invalid=invalid_rows)
    return {
        "dataset": "gsi_landslides",
        "source": "gsi_pdf",
        "status": status,
        "records": len(rows),
        "valid_records": len(valid_rows),
        "invalid_records": invalid_rows,
        "geometry_available": sum(1 for r in rows if r.get("geometry") is not None),
        "geometry_missing": sum(1 for r in rows if r.get("geometry") is None),
        "states": sorted({normalize_state_name(r.get("state")) for r in rows if r.get("state")}),
        "last_processed": utc_now_iso(),
        "rows": valid_rows,
    }


if __name__ == "__main__":
    print(ingest_gsi_landslides())
