from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from backend.app.config import NER_STATES

PROVENANCE_TYPES = {"OBSERVED", "DERIVED", "ENRICHED", "INFERRED", "NOT_AVAILABLE"}

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data"
MANIFEST_PATH = DATA_ROOT / "manifests" / "data_quality_report.json"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_state_name(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    for state in NER_STATES:
        if text.lower() == state.lower():
            return state
    return text


def is_valid_ner_state(value: Any) -> bool:
    return normalize_state_name(value) in NER_STATES


def geometry_status_from_geometry(geometry: Any) -> str:
    if geometry is None:
        return "NOT_AVAILABLE"
    if getattr(geometry, "is_empty", False):
        return "NOT_AVAILABLE"
    return "AVAILABLE"


def validate_geometry_in_ner(geometry: Any, *, state_name: Any | None = None) -> tuple[bool, str]:
    if geometry is None:
        return False, "geometry_not_available"
    if getattr(geometry, "is_empty", False):
        return False, "geometry_empty"
    if state_name is not None:
        normalized = normalize_state_name(state_name)
        if normalized not in NER_STATES:
            return False, "state_outside_ner"
    return True, "geometry_valid"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def list_dataset_files(root: Path | str, suffixes: Iterable[str]) -> list[Path]:
    base = Path(root)
    if not base.exists():
        return []
    suffixes_lower = {str(s).lower() for s in suffixes}
    matches: list[Path] = []
    for path in sorted(base.rglob("*")):
        if path.is_file() and path.suffix.lower().lstrip(".") in suffixes_lower:
            matches.append(path)
    return matches


def ensure_manifest_directory() -> Path:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    return MANIFEST_PATH


def dataset_status_from_result(records: list[dict[str, Any]], *, missing: bool = False, invalid: int = 0, files_found: int = 0) -> str:
    if missing and not records:
        return "DATA NOT FOUND"
    if not files_found and not records:
        return "DATA NOT FOUND"
    if invalid and records:
        return "DATA PARTIAL"
    if records:
        return "DATA AVAILABLE"
    if invalid:
        return "DATA INVALID"
    return "DATA NOT FOUND"


def deduplicate_records(records: Iterable[Mapping[str, Any]], key_fields: Iterable[str]) -> list[dict[str, Any]]:
    unique: dict[tuple[Any, ...], dict[str, Any]] = {}
    for record in records:
        key = tuple(record.get(field) for field in key_fields)
        if key not in unique:
            unique[key] = dict(record)
    return list(unique.values())


def feature_collection(features: Iterable[dict[str, Any]] | None = None, **metadata: Any) -> dict[str, Any]:
    payload = {"type": "FeatureCollection", "features": list(features or [])}
    if metadata:
        payload.update(metadata)
    return payload


def bbox_filter_geojson(payload: Mapping[str, Any], bbox: tuple[float, float, float, float] | None) -> dict[str, Any]:
    if bbox is None:
        return dict(payload)
    min_x, min_y, max_x, max_y = bbox
    features = []
    for feature in payload.get("features", []):
        geometry = feature.get("geometry")
        if not geometry:
            continue
        coords = geometry.get("coordinates")
        if not coords:
            continue
        if isinstance(coords, list) and len(coords) >= 2:
            x = coords[0]
            y = coords[1]
            if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                if min_x <= x <= max_x and min_y <= y <= max_y:
                    features.append(feature)
    return feature_collection(features, count=len(features), bbox=list(bbox))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def empty_summary(dataset: str, *, source: str = "local") -> dict[str, Any]:
    return {
        "dataset": dataset,
        "source": source,
        "records": 0,
        "valid_records": 0,
        "invalid_records": 0,
        "geometry_available": 0,
        "geometry_missing": 0,
        "states": [],
        "last_processed": utc_now_iso(),
        "status": "DATA NOT FOUND",
    }


def unavailable_dataset_summary(
    dataset: str,
    *,
    source: str = "local",
    note: str | None = None,
    states: list[str] | None = None,
) -> dict[str, Any]:
    message = note or "DATASET NOT AVAILABLE — AWAITING VERIFIED SOURCE DATA."
    return {
        "dataset": dataset,
        "source": source,
        "records": 0,
        "valid_records": 0,
        "invalid_records": 0,
        "geometry_available": 0,
        "geometry_missing": 0,
        "states": states or [],
        "last_processed": utc_now_iso(),
        "status": "DATASET NOT AVAILABLE — AWAITING VERIFIED SOURCE DATA.",
        "message": message,
        "data_status": "NOT_AVAILABLE",
        "source_provenance": "NOT_AVAILABLE",
    }
