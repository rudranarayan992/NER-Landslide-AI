from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Query
from pydantic import BaseModel

from backend.app.config import NER_STATES
from scripts.ingestion.administrative_ingest import ingest_administrative_boundaries
from scripts.ingestion.base_ingest import bbox_filter_geojson, feature_collection
from scripts.ingestion.geology_ingest import ingest_geology
from scripts.ingestion.gsi_ingest import ingest_gsi_landslides
from scripts.ingestion.lgd_villages_ingest import ingest_lgd_villages
from scripts.ingestion.roads_ingest import ingest_roads
from scripts.ingestion.environmental_foundation import (
    get_all_datasets,
    calculate_phase_7_readiness,
)
from scripts.ingestion.feature_engineering_foundation import get_feature_engineering_report

app = FastAPI(title="NER Landslide AI API", version="0.1.0")


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


def _parse_bbox(raw: str | list[float] | None) -> tuple[float, float, float, float] | None:
    if raw is None:
        return None
    if isinstance(raw, list):
        values = raw
    else:
        values = [part.strip() for part in str(raw).split(",") if part.strip()]
    if len(values) != 4:
        return None
    try:
        return tuple(float(value) for value in values)
    except ValueError:
        return None


def _json_feature_from_record(record: dict[str, Any], *, key: str) -> dict[str, Any] | None:
    geometry = record.get("geometry")
    if geometry is None:
        return None
    if hasattr(geometry, "geom_type"):
        try:
            from shapely.geometry import mapping

            geom_json = mapping(geometry)
        except Exception:
            geom_json = None
    elif isinstance(geometry, dict):
        geom_json = geometry
    else:
        return None
    if geom_json is None:
        return None
    return {
        "type": "Feature",
        "id": record.get("source_id") or record.get("road_id") or record.get(key) or record.get("id"),
        "properties": {k: v for k, v in record.items() if k != "geometry"},
        "geometry": geom_json,
    }


def _geojson_from_rows(rows: list[dict[str, Any]], *, state: str | None = None, bbox: tuple[float, float, float, float] | None = None) -> dict[str, Any]:
    features: list[dict[str, Any]] = []
    for record in rows:
        if state and str(record.get("state") or "").strip() != state:
            continue
        feature = _json_feature_from_record(record, key="id")
        if feature is not None:
            features.append(feature)
    payload = feature_collection(features)
    if bbox is not None:
        payload = bbox_filter_geojson(payload, bbox)
    return payload


def _blocked_payload(resource: str, *, reason: str | None = None) -> dict[str, Any]:
    message = reason or f"{resource} is blocked until verified source data and validation are available."
    return {
        "status": "BLOCKED",
        "resource": resource,
        "message": message,
        "data_status": "UNAVAILABLE",
    }


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="ner-landslide-ai", version="0.1.0")


@app.get("/api/health")
def health_api() -> dict:
    return {
        "status": "ok",
        "service": "ner-landslide-ai",
        "version": "0.1.0",
        "environment": "development",
        "states": list(NER_STATES),
        "message": "Phase 1 backend is running without ML or fabricated datasets.",
    }


@app.get("/api/states")
def get_states() -> dict:
    return {"states": list(NER_STATES), "count": len(NER_STATES), "message": "Approved NER states for this project."}


@app.get("/api/districts")
def get_districts() -> dict:
    return {"districts": [], "count": 0, "message": "No data ingested yet."}


@app.get("/api/villages")
def get_villages(state: str | None = Query(default=None), bbox: str | list[float] | None = Query(default=None)) -> dict:
    rows = ingest_lgd_villages().get("rows", [])
    return _geojson_from_rows(rows, state=state, bbox=_parse_bbox(bbox))


@app.get("/api/landslides")
def get_landslides(state: str | None = Query(default=None), bbox: str | list[float] | None = Query(default=None)) -> dict:
    rows = ingest_gsi_landslides().get("rows", [])
    return _geojson_from_rows(rows, state=state, bbox=_parse_bbox(bbox))


@app.get("/api/roads")
def get_roads(state: str | None = Query(default=None), bbox: str | list[float] | None = Query(default=None)) -> dict:
    rows = ingest_roads().get("rows", [])
    return _geojson_from_rows(rows, state=state, bbox=_parse_bbox(bbox))


@app.get("/api/geology")
def get_geology(state: str | None = Query(default=None), bbox: str | list[float] | None = Query(default=None)) -> dict:
    rows = ingest_geology().get("rows", [])
    return _geojson_from_rows(rows, state=state, bbox=_parse_bbox(bbox))


@app.get("/api/landslides/{event_id}")
def get_landslide_by_id(event_id: str) -> dict:
    return {"event_id": event_id, "message": "No matching landslide event found yet."}


@app.get("/api/risk")
def get_risk() -> dict:
    return {"risk": [], "message": "No risk model outputs available yet."}


@app.get("/api/risk/location")
def get_risk_for_location() -> dict:
    return {"location": None, "risk": None, "message": "No location data has been ingested yet."}


@app.get("/api/features")
def get_features() -> dict:
    return _blocked_payload(
        "feature_engineering",
        reason="FEATURE ENGINEERING BLOCKED — requires verified Phase 3–6 datasets and provenance before a training feature set can be created.",
    )


@app.get("/api/features/location")
def get_feature_location() -> dict:
    return _blocked_payload(
        "feature_extraction",
        reason="FEATURE EXTRACTION BLOCKED — no verified spatially aligned training dataset is available.",
    )


@app.get("/api/models")
def get_models() -> dict:
    return _blocked_payload(
        "model_registry",
        reason="MODEL REGISTRY BLOCKED — no verified training dataset or model version exists yet.",
    )


@app.get("/api/models/{model_id}")
def get_model_by_id(model_id: str) -> dict:
    return _blocked_payload(
        "model",
        reason=f"Model {model_id} is unavailable until a validated training dataset and model artifact exist.",
    )


@app.get("/api/predictions")
def get_predictions() -> dict:
    return _blocked_payload(
        "predictions",
        reason="MODEL PREDICTIONS BLOCKED — no validated training dataset or inference pipeline is available.",
    )


@app.get("/api/road-segments")
def get_road_segments() -> dict:
    return _blocked_payload(
        "road_segments",
        reason="ROAD SEGMENT RISK BLOCKED — verified road network and hazard/risk layers are not yet available.",
    )


@app.get("/api/village-exposure")
def get_village_exposure() -> dict:
    return _blocked_payload(
        "village_exposure",
        reason="VILLAGE EXPOSURE BLOCKED — village spatial geometry or exposure data is not available for NER coverage.",
    )


@app.get("/api/alerts")
def get_alerts() -> dict:
    return _blocked_payload(
        "alerts",
        reason="ALERT SYSTEM BLOCKED — current validated risk outputs and alert thresholds are not yet available.",
    )


@app.post("/api/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: str) -> dict:
    return _blocked_payload(
        "alert_acknowledgement",
        reason=f"Alert {alert_id} cannot be acknowledged until the alert engine and validated risk pipeline exist.",
    )


@app.get("/api/field-reports")
def get_field_reports() -> dict:
    return {
        "status": "BLOCKED",
        "resource": "field_reports",
        "reports": [],
        "message": "FIELD REPORT WORKFLOW BLOCKED — real verified field report ingestion and review workflow is not yet implemented.",
        "data_status": "UNAVAILABLE",
    }


@app.get("/api/field-reports/{report_id}")
def get_field_report(report_id: str) -> dict:
    return _blocked_payload(
        "field_report",
        reason=f"Field report {report_id} is unavailable until a verified submission and review workflow exists.",
    )


@app.put("/api/field-reports/{report_id}/review")
def review_field_report(report_id: str) -> dict:
    return _blocked_payload(
        "field_report_review",
        reason=f"Field report {report_id} review is blocked until the validation workflow is implemented.",
    )


@app.post("/api/route-risk")
def route_risk() -> dict:
    return _blocked_payload(
        "route_risk",
        reason="ROUTE RISK BLOCKED — verified road network, modeled hazard, and route cost functions are not available.",
    )


@app.post("/api/predict")
def predict() -> dict:
    return _blocked_payload(
        "prediction_inference",
        reason="Prediction inference is not implemented until a validated model, real feature set, and current environmental data are available.",
    )


@app.post("/api/image/analyze")
def analyze_image() -> dict:
    return {"status": "BLOCKED", "resource": "image_analysis", "message": "Image AI module is not implemented yet."}


@app.post("/api/field-report")
def submit_field_report() -> dict:
    return {
        "status": "BLOCKED",
        "resource": "field_report_submission",
        "message": "FIELD REPORT SUBMISSION BLOCKED — the verified submission and review workflow is not implemented.",
        "data_status": "UNAVAILABLE",
    }


@app.get("/api/data-sources")
def get_data_sources() -> dict:
    return {
        "sources": [
            ingest_administrative_boundaries(),
            ingest_lgd_villages(),
            ingest_roads(),
            ingest_gsi_landslides(),
            ingest_geology(),
        ],
        "count": 5,
        "message": "Local NER datasets discovered through Phase 5 ingestion support.",
    }


@app.get("/api/environmental-datasets")
def get_environmental_datasets() -> dict:
    """
    Get status of all environmental datasets
    Phase 6 Environmental Data Foundation
    NO FABRICATED DATA — returns actual dataset status
    """
    all_datasets = get_all_datasets()
    dataset_list = [d.to_dict() for d in all_datasets]

    verified_count = sum(1 for d in all_datasets if d.status == "VERIFIED")
    partial_count = sum(1 for d in all_datasets if d.status == "PARTIAL")
    awaiting_count = sum(1 for d in all_datasets if d.status == "AWAITING_VERIFIED_SOURCE_DATA")

    return {
        "phase": 6,
        "name": "Environmental Data Foundation",
        "total_datasets": len(all_datasets),
        "verified_count": verified_count,
        "partial_count": partial_count,
        "awaiting_count": awaiting_count,
        "datasets": dataset_list,
        "message": "Phase 6 datasets scanned. AWAITING_VERIFIED_SOURCE_DATA indicates data not yet obtained. NO FABRICATED DATA.",
    }


@app.get("/api/phase-7-readiness")
def get_phase_7_readiness() -> dict:
    """
    Phase 7 Readiness Check
    Determines if Feature Engineering can proceed
    Returns BLOCKED if critical environmental data is missing
    """
    env_readiness = calculate_phase_7_readiness()
    feature_report = get_feature_engineering_report()

    phase_7_status = env_readiness["status"]
    if feature_report["phase_7_status"] == "BLOCKED":
        phase_7_status = "BLOCKED"

    return {
        "phase": 7,
        "name": "Feature Engineering",
        "overall_status": phase_7_status,
        "environmental_readiness": env_readiness,
        "feature_readiness": {
            "required_features": feature_report["required_features"],
            "optional_features": feature_report["optional_features"],
        },
        "message": f"Phase 7 is {phase_7_status}. Environmental data availability: {env_readiness['message']}",
    }

@app.get("/api/layers")
def get_layers() -> dict:
    """GIS Layer status endpoint for map interface"""
    layers = [
        {
            "id": "landslides",
            "name": "Historical Landslide Events",
            "group": "LANDSLIDES",
            "status": "available",
            "description": "33,904 verified historical landslide events from GSI",
            "color": "#c0392b",
            "count": 33904,
        },
        {
            "id": "landslides-heatmap",
            "name": "Historical Density Heatmap",
            "group": "LANDSLIDES",
            "status": "available",
            "description": "Spatial density clustering of historical events (NOT current risk)",
            "color": "#bd2d1f",
        },
        {
            "id": "state-boundaries",
            "name": "State Boundaries",
            "group": "ADMINISTRATIVE",
            "status": "available",
            "description": "Administrative boundaries of NER states",
            "color": "#2c3e50",
        },
        {
            "id": "roads",
            "name": "Road Network",
            "group": "INFRASTRUCTURE",
            "status": "available",
            "description": "Primary and secondary road network",
            "color": "#95a5a6",
        },
        {
            "id": "villages",
            "name": "Villages & Settlements",
            "group": "INFRASTRUCTURE",
            "status": "available",
            "description": "Populated villages in the NER region",
            "color": "#3498db",
        },
        {
            "id": "dem",
            "name": "Digital Elevation Model",
            "group": "TERRAIN",
            "status": "awaiting",
            "description": "AWAITING VERIFIED SOURCE DATA",
        },
        {
            "id": "slope",
            "name": "Slope Analysis",
            "group": "TERRAIN",
            "status": "blocked",
            "description": "BLOCKED — requires DEM and processing",
        },
        {
            "id": "rainfall",
            "name": "Rainfall Distribution",
            "group": "RAINFALL",
            "status": "awaiting",
            "description": "AWAITING VERIFIED SOURCE DATA",
        },
        {
            "id": "soil",
            "name": "Soil Properties",
            "group": "SOIL",
            "status": "awaiting",
            "description": "AWAITING VERIFIED SOURCE DATA",
        },
        {
            "id": "geology",
            "name": "Geological Map",
            "group": "GEOLOGY",
            "status": "awaiting",
            "description": "AWAITING VERIFIED SOURCE DATA",
        },
        {
            "id": "susceptibility",
            "name": "Susceptibility Map",
            "group": "LANDSLIDES",
            "status": "blocked",
            "description": "BLOCKED — requires Phase 7 feature engineering",
        },
        {
            "id": "hazard",
            "name": "Hazard Assessment",
            "group": "RISK",
            "status": "blocked",
            "description": "BLOCKED — requires Phase 8 ML model training",
        },
        {
            "id": "risk",
            "name": "Risk Map (Final)",
            "group": "RISK",
            "status": "blocked",
            "description": "BLOCKED — requires Phase 9 risk engine",
        },
    ]

    available_count = sum(1 for l in layers if l["status"] == "available")
    awaiting_count = sum(1 for l in layers if l["status"] == "awaiting")
    blocked_count = sum(1 for l in layers if l["status"] == "blocked")

    return {
        "total_layers": len(layers),
        "available": available_count,
        "awaiting": awaiting_count,
        "blocked": blocked_count,
        "layers": layers,
    }


@app.get("/api/search")
def search(q: str = Query(..., min_length=1)) -> dict:
    """Search for locations: states, districts, villages, landslide IDs"""
    query_lower = q.lower().strip()
    results = []

    # Search states
    for state in NER_STATES:
        if query_lower in state.lower():
            results.append({
                "type": "state",
                "name": state,
                "center": [26.5, 93.5],  # NER region center
                "zoom": 6,
            })

    # Search villages
    try:
        villages = ingest_lgd_villages().get("rows", [])
        for v in villages[:50]:  # Limit results
            if query_lower in str(v.get("village", "")).lower():
                if hasattr(v.get("geometry"), "geom_type"):
                    from shapely.geometry import mapping
                    coords = list(mapping(v["geometry"])["coordinates"])
                else:
                    coords = v.get("geometry", {}).get("coordinates", [])

                if coords:
                    results.append({
                        "type": "village",
                        "name": v.get("village", "Unknown"),
                        "center": coords,
                        "zoom": 12,
                    })
    except Exception:
        pass

    return {"query": q, "results": results[:20]}