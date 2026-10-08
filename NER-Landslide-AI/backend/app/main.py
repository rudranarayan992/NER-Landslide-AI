from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Query
from pydantic import BaseModel

from backend.app.config import NER_STATES
from backend.app.enums import SystemStatus
from backend.app.ml_module_status import get_ml_module_status, check_training_readiness
from backend.app.risk_engine_status import get_risk_engine_status, get_risk_prerequisites, calculate_risk
from backend.app.field_reports_service import (
    submit_field_report, get_field_reports, get_field_report,
    review_field_report, get_field_report_statistics
)
from backend.app.alert_engine import get_alert_engine_status, get_alerts, get_active_alerts
from backend.app.infrastructure_services import (
    get_roads_status, get_villages_status, get_routes_status,
    get_road_segments, get_villages, analyze_route, get_route_alternatives
)
from backend.app.data_readiness_status import (
    get_system_status, get_data_sources_status, get_processing_status,
    get_ml_risk_status, get_system_readiness_report
)
from backend.app.llm_assistant import query_assistant
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


# ============================================================================
# SYSTEM STATUS & READINESS ENDPOINTS
# ============================================================================

@app.get("/api/system-status")
def get_complete_system_status() -> dict:
    """Get complete system status for all components"""
    return get_system_status()


@app.get("/api/data-readiness")
def get_data_readiness() -> dict:
    """Get data sources readiness status"""
    return get_data_sources_status()


@app.get("/api/data-status")
def get_data_status_summary() -> dict:
    """Get summary of data status (alias for data-readiness)"""
    return get_data_sources_status()


@app.get("/api/processing-status")
def get_processing_pipeline_status() -> dict:
    """Get processing pipeline status"""
    return get_processing_status()


@app.get("/api/system-readiness-report")
def get_system_readiness_document() -> dict:
    """Get complete system readiness report for leadership/review"""
    return get_system_readiness_report()


# ============================================================================
# ML MODULE ENDPOINTS
# ============================================================================

@app.get("/api/ml/status")
def get_ml_status() -> dict:
    """Get ML module status - NOT TRAINED until data available"""
    return get_ml_module_status()


@app.get("/api/ml/training-readiness")
def get_ml_training_readiness() -> dict:
    """Check if ML training is ready - returns BLOCKED"""
    return check_training_readiness()


# ============================================================================
# RISK ENGINE ENDPOINTS
# ============================================================================

@app.get("/api/risk/status")
def get_risk_status() -> dict:
    """Get risk engine status - BLOCKED until ML trained"""
    return get_risk_engine_status()


@app.get("/api/risk/prerequisites")
def get_risk_prerequisites_list() -> dict:
    """Get list of prerequisites for risk calculation"""
    return get_risk_prerequisites()


@app.get("/api/risk/location/{location_id}")
def get_location_risk(location_id: str) -> dict:
    """Get risk for a specific location - returns BLOCKED"""
    return calculate_risk(location_id, location_id)


# ============================================================================
# FIELD REPORTS ENDPOINTS
# ============================================================================

@app.get("/api/field-reports/status")
def get_field_reports_workflow_status() -> dict:
    """Get field reports workflow status"""
    return {
        "status": "OPERATIONAL",
        "component": "FIELD_REPORTS",
        "message": "Field report submission and review workflow is operational",
        "workflow_stages": ["SUBMITTED", "UNDER_REVIEW", "VERIFIED", "REJECTED"],
        "statistics": get_field_report_statistics(),
    }


@app.get("/api/field-reports")
def list_field_reports(status: str | None = Query(default=None)) -> dict:
    """Get all field reports, optionally filtered by status"""
    return get_field_reports(status=status)


@app.get("/api/field-reports/{report_id}")
def get_specific_field_report(report_id: str) -> dict:
    """Get a specific field report"""
    return get_field_report(report_id)


@app.post("/api/field-reports")
def submit_new_field_report(data: dict) -> dict:
    """Submit a new field report"""
    return submit_field_report(
        location_name=data.get("location_name"),
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        description=data.get("description"),
        reporter_name=data.get("reporter_name"),
        reporter_contact=data.get("reporter_contact"),
        photo_url=data.get("photo_url"),
        evidence_notes=data.get("evidence_notes"),
        observations=data.get("observations"),
    )


@app.put("/api/field-reports/{report_id}/review")
def review_submitted_field_report(report_id: str, data: dict) -> dict:
    """Review and update a field report"""
    return review_field_report(
        report_id=report_id,
        action=data.get("action"),  # VERIFY, REJECT, INCONCLUSIVE
        reviewed_by=data.get("reviewed_by"),
        review_notes=data.get("review_notes"),
        linked_event_id=data.get("linked_event_id"),
    )


# ============================================================================
# ALERT ENGINE ENDPOINTS
# ============================================================================

@app.get("/api/alerts/status")
def get_alert_engine_status_endpoint() -> dict:
    """Get alert engine status - BLOCKED until risk operational"""
    return get_alert_engine_status()


@app.get("/api/alerts")
def list_alerts() -> dict:
    """Get all alerts"""
    return get_alerts()


@app.get("/api/alerts/active")
def list_active_alerts() -> dict:
    """Get active alerts"""
    return get_active_alerts()


# ============================================================================
# INFRASTRUCTURE SERVICES ENDPOINTS
# ============================================================================

@app.get("/api/roads/status")
def get_roads_service_status() -> dict:
    """Get roads service status"""
    return get_roads_status()


@app.get("/api/roads")
def list_road_segments(state: str | None = Query(default=None)) -> dict:
    """Get road segments, optionally filtered by state"""
    return get_road_segments(state=state)


@app.get("/api/roads/{road_id}/risk")
def get_road_risk_assessment(road_id: str) -> dict:
    """Get risk assessment for a road - returns BLOCKED"""
    return {
        "road_id": road_id,
        "status": "BLOCKED",
        "message": "Road risk calculation blocked - risk engine not operational",
    }


@app.get("/api/villages/status")
def get_villages_service_status() -> dict:
    """Get villages service status"""
    return get_villages_status()


@app.get("/api/villages")
def list_villages(state: str | None = Query(default=None)) -> dict:
    """Get villages, optionally filtered by state"""
    return get_villages(state=state)


@app.get("/api/villages/{village_id}/exposure")
def get_village_exposure_assessment(village_id: str) -> dict:
    """Get exposure assessment for a village - returns BLOCKED"""
    return {
        "village_id": village_id,
        "status": "BLOCKED",
        "message": "Village exposure assessment blocked - risk engine not operational",
    }


@app.get("/api/routes/status")
def get_routes_service_status() -> dict:
    """Get routes service status"""
    return get_routes_status()


@app.post("/api/routes/analyze")
def analyze_route_endpoint(data: dict) -> dict:
    """Analyze a route for risk - returns BLOCKED"""
    return analyze_route(
        origin=data.get("origin"),
        destination=data.get("destination"),
    )


@app.post("/api/routes/alternatives")
def get_route_alternatives_endpoint(data: dict) -> dict:
    """Get alternative routes with risk comparison - returns BLOCKED"""
    return get_route_alternatives(
        origin=data.get("origin"),
        destination=data.get("destination"),
    )


@app.get("/api/routes/calculate")
def calculate_route_endpoint(from_location: str = Query(...), to_location: str = Query(...)) -> dict:
    """Calculate route between two locations"""
    return get_route_alternatives(
        origin=from_location,
        destination=to_location,
    )


# ============================================================================
# LLM ASSISTANT ENDPOINT
# ============================================================================

@app.post("/api/assistant/query")
def query_llm_assistant(data: dict) -> dict:
    """Query LLM assistant about system and data status"""
    question = data.get("question", "")
    if not question:
        return {
            "error": "No question provided",
            "message": "Please provide a 'question' field in the request",
        }
    
    return query_assistant(question)


@app.get("/api/assistant/status")
def get_assistant_status() -> dict:
    """Get LLM assistant status"""
    return {
        "component": "LLM_ASSISTANT",
        "status": "OPERATIONAL",
        "capabilities": [
            "Query historical landslide data",
            "Explain data availability status",
            "Clarify why components are blocked",
            "Report system readiness",
            "Distinguish OBSERVED vs HISTORICAL vs CALCULATED vs PREDICTED vs UNKNOWN",
        ],
        "important_note": "Assistant provides honest answers based on verified data without fabricating missing observations",
        "endpoint": "POST /api/assistant/query with {'question': 'your question'}",
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

# ============================================================================
# LOCATION INTELLIGENCE & WARNING-STYLE ENDPOINTS
# ============================================================================

@app.get("/api/location/{lat}/{lon}")
def get_location_payload(lat: float, lon: float) -> dict:
    """Return a location intelligence payload with honest status handling."""
    return {
        "status": "BLOCKED",
        "message": "CURRENT PREDICTIVE RISK UNAVAILABLE. Verified environmental datasets and a validated ML model are required before current location risk can be calculated.",
        "location": {
            "latitude": lat,
            "longitude": lon,
            "state": "AWAITING VERIFIED SOURCE DATA",
            "district": "AWAITING VERIFIED SOURCE DATA",
            "village": "AWAITING VERIFIED SOURCE DATA",
            "administrative_hierarchy": "AWAITING VERIFIED SOURCE DATA",
        },
        "infrastructure": {
            "nearest_road": "AWAITING VERIFIED SOURCE DATA",
            "road_id": "AWAITING VERIFIED SOURCE DATA",
            "road_class": "AWAITING VERIFIED SOURCE DATA",
            "road_connectivity": "AWAITING VERIFIED SOURCE DATA",
            "nearest_village": "AWAITING VERIFIED SOURCE DATA",
            "distance_to_village_km": "AWAITING VERIFIED SOURCE DATA",
            "nearby_infrastructure": "AWAITING VERIFIED SOURCE DATA",
        },
        "historical_landslide_intelligence": {
            "historical_landslide_count_nearby": "AWAITING VERIFIED SOURCE DATA",
            "historical_landslide_density": "AWAITING VERIFIED SOURCE DATA",
            "nearest_historical_landslide": "AWAITING VERIFIED SOURCE DATA",
            "distance_to_nearest_historical_landslide_km": "AWAITING VERIFIED SOURCE DATA",
            "source": "GSI HISTORICAL LANDSLIDE DATA",
            "status": "VERIFIED",
        },
        "environment": {
            "status": "AWAITING_VERIFIED_DATA",
            "rainfall_1h": "AWAITING VERIFIED SOURCE DATA",
            "rainfall_24h": "AWAITING VERIFIED SOURCE DATA",
            "rainfall_3d": "AWAITING VERIFIED SOURCE DATA",
            "rainfall_7d": "AWAITING VERIFIED SOURCE DATA",
            "rainfall_30d": "AWAITING VERIFIED SOURCE DATA",
            "temperature": "AWAITING VERIFIED SOURCE DATA",
            "humidity": "AWAITING VERIFIED SOURCE DATA",
            "wind": "AWAITING VERIFIED SOURCE DATA",
            "soil_moisture": "AWAITING VERIFIED SOURCE DATA",
            "soil_properties": "AWAITING VERIFIED SOURCE DATA",
            "dem_elevation": "AWAITING VERIFIED SOURCE DATA",
            "slope": "AWAITING VERIFIED SOURCE DATA",
            "aspect": "AWAITING VERIFIED SOURCE DATA",
            "ndvi": "AWAITING VERIFIED SOURCE DATA",
            "land_cover": "AWAITING VERIFIED SOURCE DATA",
            "distance_to_stream_m": "AWAITING VERIFIED SOURCE DATA",
            "drainage_density": "AWAITING VERIFIED SOURCE DATA",
            "flow_accumulation": "AWAITING VERIFIED SOURCE DATA",
        },
        "soil": {
            "status": "AWAITING_VERIFIED_DATA",
            "soil_type": "AWAITING VERIFIED SOURCE DATA",
            "soil_classification": "AWAITING VERIFIED SOURCE DATA",
            "texture": "AWAITING VERIFIED SOURCE DATA",
            "sand_percent": "NOT AVAILABLE",
            "silt_percent": "NOT AVAILABLE",
            "clay_percent": "NOT AVAILABLE",
            "organic_matter": "NOT AVAILABLE",
            "bulk_density": "NOT AVAILABLE",
            "permeability": "NOT AVAILABLE",
            "available_water_capacity": "NOT AVAILABLE",
            "soil_depth": "NOT AVAILABLE",
            "soil_moisture": "AWAITING VERIFIED SOURCE DATA",
            "source_dataset": "AWAITING VERIFIED SOURCE DATA",
            "dataset_version": "AWAITING VERIFIED SOURCE DATA",
            "resolution": "AWAITING VERIFIED SOURCE DATA",
        },
        "terrain": {
            "status": "AWAITING_VERIFIED_DATA",
            "elevation": "AWAITING VERIFIED SOURCE DATA",
            "slope": "AWAITING VERIFIED SOURCE DATA",
            "aspect": "AWAITING VERIFIED SOURCE DATA",
            "curvature": "AWAITING VERIFIED SOURCE DATA",
            "relief": "AWAITING VERIFIED SOURCE DATA",
            "flow_accumulation": "AWAITING VERIFIED SOURCE DATA",
            "distance_to_stream_m": "AWAITING VERIFIED SOURCE DATA",
            "drainage_density": "AWAITING VERIFIED SOURCE DATA",
            "note": "Terrain factors are model inputs / susceptibility indicators. They do not independently confirm a landslide.",
        },
        "rainfall": {
            "status": "AWAITING_VERIFIED_DATA",
            "source": "AWAITING VERIFIED SOURCE DATA",
            "observation_time": "AWAITING VERIFIED SOURCE DATA",
            "quality": "MISSING",
            "values": {
                "1h": "AWAITING VERIFIED SOURCE DATA",
                "24h": "AWAITING VERIFIED SOURCE DATA",
                "3d": "AWAITING VERIFIED SOURCE DATA",
                "7d": "AWAITING VERIFIED SOURCE DATA",
                "30d": "AWAITING VERIFIED SOURCE DATA",
            },
        },
        "prediction": {
            "status": "BLOCKED",
            "risk": "BLOCKED",
            "probability": None,
            "prediction_horizon": "AWAITING VERIFIED MODEL",
            "model_version": "AWAITING VERIFIED MODEL",
            "model_type": "AWAITING VERIFIED MODEL",
            "validation_status": "UNAVAILABLE",
            "inputs": ["DEM", "Rainfall", "Soil", "Weather", "Land cover", "Historical landslides", "Hydrology"],
        },
        "warning": {
            "status": "BLOCKED",
            "level": "BLOCKED",
            "reason": "Validated environmental observations and ML/risk model are not yet available.",
        },
        "provenance": {
            "status": "PARTIAL",
            "source": "GSI historical landslide records and verified administrative / infrastructure data only",
            "data_set": "VERIFIED HISTORICAL DATASET",
            "dataset_version": "AVAILABLE",
            "acquisition_time": "N/A",
            "processing_time": "N/A",
            "resolution": "N/A",
            "crs": "EPSG:4326",
            "verification_status": "VERIFIED FOR HISTORICAL DATA ONLY",
        },
    }


@app.get("/api/location-intelligence")
def get_location_intelligence_endpoint(lat: float = Query(...), lon: float = Query(...)) -> dict:
    """Client-friendly alias for location intelligence payload."""
    return get_location_payload(lat=lat, lon=lon)


@app.get("/api/environment")
def get_environment_status() -> dict:
    return {
        "status": "AWAITING_VERIFIED_DATA",
        "message": "Current environmental values are unavailable until verified source data is ingested.",
        "data": None,
    }


@app.get("/api/terrain")
def get_terrain_status() -> dict:
    return {
        "status": "AWAITING_VERIFIED_DATA",
        "message": "Terrain factors are available as model inputs only after verified DEM/terrain datasets are supplied.",
        "data": None,
    }


@app.get("/api/soil")
def get_soil_status() -> dict:
    return {
        "status": "AWAITING_VERIFIED_DATA",
        "message": "Soil data is not yet available from a verified source.",
        "data": None,
    }


@app.get("/api/rainfall")
def get_rainfall_status() -> dict:
    return {
        "status": "AWAITING_VERIFIED_DATA",
        "message": "Rainfall data is not yet available from a verified source.",
        "data": None,
    }


@app.get("/api/hydrology")
def get_hydrology_status() -> dict:
    return {
        "status": "AWAITING_VERIFIED_DATA",
        "message": "Hydrology information is not yet available from a verified source.",
        "data": None,
    }


@app.get("/api/landcover")
def get_landcover_status() -> dict:
    return {
        "status": "AWAITING_VERIFIED_DATA",
        "message": "Land cover data is not yet available from a verified source.",
        "data": None,
    }


@app.get("/api/risk/explanation")
def get_risk_explanation() -> dict:
    return {
        "status": "BLOCKED",
        "message": "Model explanation unavailable because predictive model is not operational.",
        "primary_contributing_factors": [],
        "data": None,
    }


@app.get("/api/risk/location")
def get_location_risk_status() -> dict:
    return {
        "status": "BLOCKED",
        "location": None,
        "risk": "BLOCKED",
        "message": "CURRENT PREDICTIVE RISK UNAVAILABLE. Verified environmental datasets and a validated ML model are required before current predictive risk can be calculated.",
        "data": None,
    }


@app.get("/api/risk/roads")
def get_roads_risk_status() -> dict:
    return {
        "status": "BLOCKED",
        "message": "Road risk analysis is blocked until validated hazard/risk outputs exist.",
        "data": None,
    }


@app.get("/api/risk/villages")
def get_villages_risk_status() -> dict:
    return {
        "status": "BLOCKED",
        "message": "Village exposure analysis is blocked until validated hazard/risk outputs exist.",
        "data": None,
    }


@app.get("/api/risk/routes")
def get_routes_risk_status() -> dict:
    return {
        "status": "BLOCKED",
        "message": "Route risk analysis is blocked until validated hazard/risk outputs exist.",
        "data": None,
    }


@app.get("/api/alerts/history")
def get_alerts_history() -> dict:
    return {
        "status": "OPERATIONAL",
        "message": "No verified automated alert history is available yet.",
        "alerts": [],
    }


@app.get("/api/provenance")
def get_provenance_status() -> dict:
    return {
        "status": "PARTIAL",
        "message": "Historical datasets have verified provenance. Environmental and model provenance are unavailable until source data and model validation exist.",
        "data": {
            "source": "GSI historical landslide records",
            "verification_status": "VERIFIED",
            "dataset_version": "AVAILABLE",
            "crs": "EPSG:4326",
            "quality": "VERIFIED FOR HISTORICAL DATA ONLY",
            "warning": "Additional environmental provenance remains pending verified source data.",
        },
    }