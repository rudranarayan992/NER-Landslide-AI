from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from backend.app.config import NER_STATES
from scripts.ingestion.base_ingest import PROJECT_ROOT, dataset_status_from_result, deduplicate_records, file_sha256, is_valid_ner_state, normalize_state_name, utc_now_iso

LGD_ROOT = PROJECT_ROOT / "data" / "raw" / "administrative" / "lgd_villages"


def scan_lgd_csvs() -> list[Path]:
    if not LGD_ROOT.exists():
        return []
    return sorted(LGD_ROOT.rglob("*.csv"))


def ingest_lgd_villages() -> dict[str, Any]:
    files = scan_lgd_csvs()
    if not files:
        return {
            "dataset": "lgd_villages",
            "source": "local_lgd_csv",
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
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                state = normalize_state_name(row.get("state") or row.get("State") or path.parent.name.replace("_", " "))
                if not is_valid_ner_state(state):
                    continue
                district = (row.get("district") or row.get("District") or "").strip()
                subdistrict = (row.get("subdistrict") or row.get("Subdistrict") or row.get("block") or row.get("Block") or "").strip()
                village_name = (row.get("village") or row.get("Village") or row.get("village_name") or row.get("Village Name") or "").strip()
                record = {
                    "lgd_code": (row.get("lgd_code") or row.get("LGD Code") or row.get("village_code") or row.get("Village Code") or "").strip(),
                    "village_name": village_name,
                    "district": district,
                    "subdistrict": subdistrict,
                    "state": state,
                    "source": "lgd_csv",
                    "source_id": f"{path.name}:{row.get('lgd_code') or row.get('LGD Code') or row.get('village_code') or row.get('Village Code') or 'row'}",
                    "geometry": None,
                    "geometry_status": "NOT_AVAILABLE",
                    "data_status": "OBSERVED",
                    "source_provenance": "OBSERVED",
                    "checksum": file_sha256(path),
                    "created_at": utc_now_iso(),
                    "updated_at": utc_now_iso(),
                }
                records.append(record)

    deduped = deduplicate_records(records, ("state", "district", "subdistrict", "village_name", "lgd_code"))
    valid = [record for record in deduped if is_valid_ner_state(record.get("state"))]
    status = dataset_status_from_result(valid, files_found=len(files), invalid=len(deduped) - len(valid))
    return {
        "dataset": "lgd_villages",
        "source": "local_lgd_csv",
        "status": status,
        "records": len(deduped),
        "valid_records": len(valid),
        "invalid_records": len(deduped) - len(valid),
        "geometry_available": sum(1 for item in deduped if item.get("geometry") is not None),
        "geometry_missing": sum(1 for item in deduped if item.get("geometry") is None),
        "states": sorted({normalize_state_name(item.get("state")) for item in deduped if item.get("state")}),
        "last_processed": utc_now_iso(),
        "rows": deduped,
    }


if __name__ == "__main__":
    print(ingest_lgd_villages())
