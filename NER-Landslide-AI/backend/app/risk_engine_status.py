"""
Risk Engine Status and Interface
Demonstrates risk calculation architecture WITHOUT fabricating risk scores
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any, List
from backend.app.enums import RiskStatus, SystemStatus


@dataclass
class HazardAssessment:
    """Hazard component of risk calculation"""
    hazard_type: str
    probability: Optional[float]  # None until model trained
    magnitude: Optional[float]
    spatial_extent: Optional[str]
    data_source: str
    status: str  # UNAVAILABLE, CALCULATED
    confidence: Optional[float] = None


@dataclass
class ExposureAssessment:
    """Exposure component: what is at risk"""
    feature_type: str  # roads, villages, agriculture, etc.
    count: int
    area_km2: Optional[float]
    population: Optional[int]
    data_source: str
    status: str  # VERIFIED, PARTIAL


@dataclass
class VulnerabilityAssessment:
    """Vulnerability component: how susceptible is exposure to hazard"""
    community_type: str
    building_vulnerability_factor: Optional[float]  # None until assessed
    critical_infrastructure_present: bool
    historical_losses: int
    data_source: str
    status: str  # PARTIAL, AWAITING_DATA


@dataclass
class RiskCalculation:
    """Risk = Hazard × Exposure × Vulnerability"""
    location_id: str
    location_name: str
    hazard: HazardAssessment
    exposure: ExposureAssessment
    vulnerability: VulnerabilityAssessment
    risk_score: Optional[float]  # None if blocking conditions exist
    risk_class: Optional[str]  # None if blocking conditions exist
    timestamp: datetime
    model_version: Optional[str]
    status: RiskStatus
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "location_id": self.location_id,
            "location_name": self.location_name,
            "hazard": asdict(self.hazard),
            "exposure": asdict(self.exposure),
            "vulnerability": asdict(self.vulnerability),
            "risk_score": self.risk_score,
            "risk_class": self.risk_class,
            "timestamp": self.timestamp.isoformat(),
            "model_version": self.model_version,
            "status": self.status.value,
        }


class RiskEngineStatus:
    """Central risk engine status tracker"""
    
    def __init__(self):
        self.overall_status = SystemStatus.BLOCKED
        self.blocking_reasons = [
            "Hazard model not trained (Phase 8 ML not complete)",
            "Environmental feature dataset incomplete (Phase 7 not complete)",
            "Vulnerability assessment not validated",
            "Exposure-vulnerability interaction parameters unknown",
        ]
        self.last_checked = datetime.now()
    
    def get_status(self) -> Dict[str, Any]:
        """Get risk engine status"""
        return {
            "component": "RISK_ENGINE",
            "status": self.overall_status.value,
            "message": self._get_status_message(),
            "blocking_reasons": self.blocking_reasons,
            "architectural_requirements": self._get_architectural_requirements(),
            "last_checked": self.last_checked.isoformat(),
        }
    
    def _get_status_message(self) -> str:
        return (
            "RISK ENGINE BLOCKED — Cannot calculate current landslide risk. "
            "Prerequisites: (1) ML model trained on verified environmental features, "
            "(2) Hazard probability maps generated, (3) Exposure/vulnerability assessed. "
            "Currently at: Stage requires Phase 7-8 environmental/ML completion."
        )
    
    def _get_architectural_requirements(self) -> Dict[str, Any]:
        return {
            "input_hazard_model": {
                "type": "trained_ml_classifier",
                "status": "NOT_TRAINED",
                "required_features": [
                    "elevation", "slope", "aspect", "rainfall_24h", "rainfall_7d",
                    "soil_type", "geology", "distance_to_stream", "land_cover"
                ]
            },
            "input_exposure_data": {
                "roads": {"status": "VERIFIED", "records": "5000+"},
                "villages": {"status": "VERIFIED", "records": "10000+"},
                "agriculture": {"status": "AWAITING_DATA"},
                "urban_areas": {"status": "PARTIAL"}
            },
            "input_vulnerability_parameters": {
                "building_vulnerability": {"status": "AWAITING_DATA"},
                "social_vulnerability": {"status": "AWAITING_DATA"},
                "historical_loss_functions": {"status": "PARTIAL"}
            },
            "calculation_interface": {
                "method": "Hazard × Exposure × Vulnerability",
                "output_grid_resolution_m": 30,
                "risk_classes": ["VERY_LOW", "LOW", "MODERATE", "HIGH", "VERY_HIGH"],
                "confidence_thresholds": {"high": 0.8, "moderate": 0.6, "low": 0.4}
            }
        }
    
    def calculate_risk(self, location_id: str, location_name: str) -> RiskCalculation:
        """Calculate risk for a location - returns BLOCKED status"""
        return RiskCalculation(
            location_id=location_id,
            location_name=location_name,
            hazard=HazardAssessment(
                hazard_type="landslide",
                probability=None,
                magnitude=None,
                spatial_extent=None,
                data_source="ML_MODEL_NOT_TRAINED",
                status="UNAVAILABLE",
            ),
            exposure=ExposureAssessment(
                feature_type="roads_and_villages",
                count=0,
                area_km2=None,
                population=None,
                data_source="VERIFIED",
                status="VERIFIED",
            ),
            vulnerability=VulnerabilityAssessment(
                community_type="rural",
                building_vulnerability_factor=None,
                critical_infrastructure_present=False,
                historical_losses=0,
                data_source="UNKNOWN",
                status="AWAITING_DATA",
            ),
            risk_score=None,
            risk_class=None,
            timestamp=datetime.now(),
            model_version=None,
            status=RiskStatus.BLOCKED,
        )


# Global risk engine status
_risk_engine = RiskEngineStatus()


def get_risk_engine_status() -> Dict[str, Any]:
    """Get current risk engine status"""
    return _risk_engine.get_status()


def calculate_risk(location_id: str, location_name: str) -> Dict[str, Any]:
    """Attempt to calculate risk - will return BLOCKED status"""
    result = _risk_engine.calculate_risk(location_id, location_name)
    return result.to_dict()


def get_risk_prerequisites() -> Dict[str, Any]:
    """Get list of what must be completed before risk can be calculated"""
    return {
        "status": "BLOCKED",
        "prerequisites": [
            {
                "phase": 7,
                "task": "Feature Engineering",
                "requirement": "Create spatially-aligned features from verified environmental datasets",
                "status": "NOT_STARTED",
            },
            {
                "phase": 8,
                "task": "ML Model Training",
                "requirement": "Train hazard probability model on validated features",
                "status": "NOT_STARTED",
            },
            {
                "phase": 8.5,
                "task": "Model Validation",
                "requirement": "Validate model performance on held-out spatial regions",
                "status": "NOT_STARTED",
            },
            {
                "phase": 9,
                "task": "Risk Engine Integration",
                "requirement": "Integrate trained model with exposure/vulnerability data",
                "status": "READY",
            },
        ],
        "current_blocker": "Phases 7-8 not complete. Cannot calculate risk without trained model and verified features.",
    }
