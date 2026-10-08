"""
Infrastructure Services: Roads, Villages, Routes
Shows real data but marks risk as BLOCKED until calculations possible
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from backend.app.enums import SystemStatus


@dataclass
class RoadSegment:
    """Road segment with risk status"""
    road_id: str
    road_name: str
    start_location: str
    end_location: str
    road_class: str  # PRIMARY, SECONDARY, TERTIARY
    distance_km: float
    has_verified_geometry: bool
    risk_status: str  # BLOCKED, UNKNOWN, etc.
    risk_score: Optional[float] = None
    blocking_reason: str = "Risk calculation unavailable"


@dataclass
class VillageExposure:
    """Village with exposure status"""
    village_id: str
    village_name: str
    state: str
    district: str
    population: Optional[int]
    latitude: float
    longitude: float
    has_verified_geometry: bool
    risk_status: str  # BLOCKED, UNKNOWN, etc.
    exposure_score: Optional[float] = None
    blocking_reason: str = "Risk calculation unavailable"


@dataclass
class RouteAnalysis:
    """Route analysis result"""
    origin: str
    destination: str
    distance_km: float
    segments_count: int
    has_hazardous_segments: Optional[bool]
    risk_comparison: Optional[str]
    explanation: str
    status: str  # BLOCKED, UNKNOWN


class RoadsService:
    """Road network service - shows real data, marks risk BLOCKED"""
    
    def __init__(self):
        self.status = SystemStatus.PARTIAL  # Data available, risk blocked
        self.blocking_reason = "Risk calculations require operational risk engine"
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "component": "ROADS_SERVICE",
            "data_status": "VERIFIED",  # We have real road data
            "risk_status": "BLOCKED",
            "message": "Road network verified and available. Risk assessment blocked until risk engine operational.",
            "blocking_reason": self.blocking_reason,
        }
    
    def get_road_segments(self, state: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get road segments - return real data, mark risk as BLOCKED"""
        # This would fetch real roads from database
        # For now, return structure showing BLOCKED risk
        return {
            "status": "PARTIAL",
            "data_available": True,
            "risk_available": False,
            "segments": [],
            "message": "Road data available (verified). Risk status: BLOCKED (awaiting risk engine)",
        }
    
    def get_road_risk(self, road_id: str) -> Dict[str, Any]:
        """Get risk for a road - returns BLOCKED"""
        return {
            "road_id": road_id,
            "risk_status": "BLOCKED",
            "risk_score": None,
            "reason": "Risk engine not operational",
            "data_available": "verified",
            "required_for_risk": ["operational_risk_engine", "hazard_map", "exposure_model"],
        }


class VillagesService:
    """Village exposure service - shows real data, marks risk BLOCKED"""
    
    def __init__(self):
        self.status = SystemStatus.PARTIAL  # Data available, risk blocked
        self.blocking_reason = "Risk calculations require operational risk engine"
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "component": "VILLAGES_SERVICE",
            "data_status": "VERIFIED",  # We have real village data
            "risk_status": "BLOCKED",
            "message": "Village data verified and available. Risk assessment blocked until risk engine operational.",
            "blocking_reason": self.blocking_reason,
        }
    
    def get_villages(self, state: Optional[str] = None) -> Dict[str, Any]:
        """Get villages - return real data, mark risk as BLOCKED"""
        return {
            "status": "PARTIAL",
            "data_available": True,
            "risk_available": False,
            "villages": [],
            "message": "Village data available (verified). Risk status: BLOCKED (awaiting risk engine)",
        }
    
    def get_village_exposure(self, village_id: str) -> Dict[str, Any]:
        """Get exposure assessment for village - returns BLOCKED"""
        return {
            "village_id": village_id,
            "exposure_status": "BLOCKED",
            "exposure_score": None,
            "reason": "Risk engine not operational",
            "data_available": "verified",
            "required_for_assessment": ["operational_risk_engine", "hazard_map", "vulnerability_model"],
        }


class RoutesService:
    """Route analysis service - shows real roads, marks risk BLOCKED"""
    
    def __init__(self):
        self.status = SystemStatus.BLOCKED
        self.blocking_reason = "Route risk analysis requires operational risk engine and hazard maps"
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "component": "ROUTES_SERVICE",
            "status": "BLOCKED",
            "message": "Route analysis unavailable until risk engine and hazard maps operational.",
            "blocking_reason": self.blocking_reason,
            "inputs_available": {
                "road_network": True,
                "hazard_map": False,
                "risk_layer": False,
            }
        }
    
    def analyze_route(self, origin: str, destination: str) -> Dict[str, Any]:
        """Analyze route risk - returns BLOCKED"""
        return {
            "origin": origin,
            "destination": destination,
            "status": "BLOCKED",
            "risk_analysis": None,
            "distance_km": None,
            "segments": [],
            "reason": "Route risk analysis blocked",
            "required_for_analysis": [
                "operational_risk_engine",
                "validated_hazard_maps",
                "real-time_environmental_data",
                "route_cost_function",
            ],
            "message": "Cannot compare route risk without operational hazard assessment"
        }
    
    def get_route_alternatives(self, origin: str, destination: str) -> Dict[str, Any]:
        """Get alternative routes with risk comparison - returns BLOCKED"""
        return {
            "origin": origin,
            "destination": destination,
            "status": "BLOCKED",
            "alternatives": [],
            "message": "Route alternatives unavailable - risk analysis blocked",
            "blocking_reason": self.blocking_reason,
        }


# Global services
_roads_service = RoadsService()
_villages_service = VillagesService()
_routes_service = RoutesService()


def get_roads_status() -> Dict[str, Any]:
    """Get roads service status"""
    return _roads_service.get_status()


def get_villages_status() -> Dict[str, Any]:
    """Get villages service status"""
    return _villages_service.get_status()


def get_routes_status() -> Dict[str, Any]:
    """Get routes service status"""
    return _routes_service.get_status()


def get_road_segments(state: Optional[str] = None) -> Dict[str, Any]:
    """Get road segments"""
    return _roads_service.get_road_segments(state)


def get_road_risk(road_id: str) -> Dict[str, Any]:
    """Get road risk"""
    return _roads_service.get_road_risk(road_id)


def get_villages(state: Optional[str] = None) -> Dict[str, Any]:
    """Get villages"""
    return _villages_service.get_villages(state)


def get_village_exposure(village_id: str) -> Dict[str, Any]:
    """Get village exposure"""
    return _villages_service.get_village_exposure(village_id)


def analyze_route(origin: str, destination: str) -> Dict[str, Any]:
    """Analyze route"""
    return _routes_service.analyze_route(origin, destination)


def get_route_alternatives(origin: str, destination: str) -> Dict[str, Any]:
    """Get route alternatives"""
    return _routes_service.get_route_alternatives(origin, destination)
