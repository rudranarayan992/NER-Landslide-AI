from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from backend.app.config import NER_STATES
from scripts.ingestion.base_ingest import (
    PROJECT_ROOT,
    dataset_status_from_result,
    deduplicate_records,
    file_sha256,
    is_valid_ner_state,
    normalize_state_name,
    utc_now_iso,
)

ADMINISTRATIVE_ROOT = PROJECT_ROOT / "data" / "raw" / "administrative"


def scan_administrative_sources() -> list[Path]:
    files: list[Path] = []
    for suffix in (".xls", ".xlsx", ".csv", ".geojson", ".gpkg", ".shp"):
        files.extend(sorted(ADMINISTRATIVE_ROOT.rglob(f"*{suffix}")))
    return files


def _extract_rows_from_excel(path: Path, *, state_name: str) -> list[dict[str, Any]]:
    df = pd.read_excel(path, header=None, dtype=str, keep_default_na=False)
    records: list[dict[str, Any]] = []
    for row_index, row in df.iterrows():
        cells = [str(cell).strip() for cell in row.tolist()]
        lowered = " ".join(cells).lower()
        if not any(token in lowered for token in ("district", "village", "block", "subdistrict", "state")):
            continue
        district = ""
        subdistrict = ""
        village = ""
        for idx, cell in enumerate(cells):
            if "district" in cell.lower() and idx < len(cells):
                district = cells[idx + 1] if idx + 1 < len(cells) else ""
            if "subdistrict" in cell.lower() or "block" in cell.lower():
                subdistrict = cells[idx + 1] if idx + 1 < len(cells) else ""
            if "village" in cell.lower() and idx + 1 < len(cells):
                village = cells[idx + 1]
        if not any([district, subdistrict, village]):
            continue
        record = {
            "id": f"{state_name}:{path.stem}:{row_index}",
            "state": state_name,
            "district": district or "",
            "subdistrict": subdistrict or "",
            "village_name": village or "",
            "source": "administrative_xls",
            "source_id": f"{path.name}:{row_index}",
            "geometry": None,
            "geometry_status": "NOT_AVAILABLE",
            "data_status": "OBSERVED" if state_name in NER_STATES else "NOT_AVAILABLE",
            "created_at": utc_now_iso(),
            "updated_at": utc_now_iso(),
            "source_provenance": "OBSERVED",
            "checksum": file_sha256(path),
        }
        records.append(record)
    return records


def ingest_administrative_boundaries() -> dict[str, Any]:
    files = scan_administrative_sources()
    records: list[dict[str, Any]] = []
    if not files:
        return {
            "dataset": "administrative_boundaries",
            "source": "local_administrative_raw",
            "status": "DATA NOT FOUND",
            "records": 0,
            "valid_records": 0,
            "invalid_records": 0,
            "geometry_available": 0,
            "geometry_missing": 0,
            "states": [],
            "last_processed": utc_now_iso(),
        }

    seen: set[tuple[str | None, str | None, str | None, str | None]] = set()
    for path in files:
        if path.suffix.lower() in {".xls", ".xlsx"}:
            state_name = normalize_state_name(path.parent.name.replace("_", " "))
            if not state_name:
                state_name = "unknown"
            for record in _extract_rows_from_excel(path, state_name=state_name):
                key = (record.get("state"), record.get("district"), record.get("subdistrict"), record.get("village_name"))
                if key in seen:
                    continue
                seen.add(key)
                if is_valid_ner_state(record.get("state")):
                    records.append(record)
    deduped = deduplicate_records(records, ("state", "district", "subdistrict", "village_name"))
    valid = [record for record in deduped if is_valid_ner_state(record.get("state"))]
    invalid = len(deduped) - len(valid)
    status = dataset_status_from_result(valid, files_found=len(files), invalid=invalid)
    return {
        "dataset": "administrative_boundaries",
        "source": "local_administrative_raw",
        "status": status,
        "records": len(deduped),
        "valid_records": len(valid),
        "invalid_records": invalid,
        "geometry_available": sum(1 for item in deduped if item.get("geometry") is not None),
        "geometry_missing": sum(1 for item in deduped if item.get("geometry") is None),
        "states": sorted({normalize_state_name(item.get("state")) for item in deduped if item.get("state")}),
        "last_processed": utc_now_iso(),
        "rows": deduped,
    }


if __name__ == "__main__":
    print(ingest_administrative_boundaries())
