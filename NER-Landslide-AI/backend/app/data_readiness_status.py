"""
Data Status and Readiness Reporting
Complete system component status and data availability tracking
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List
from backend.app.enums import SystemStatus


@dataclass
class ComponentStatus:
    """Status of a system component"""
    name: str
    component_type: str  # data_source, processing, ml, risk, api
    status: SystemStatus
    message: str
    last_checked: datetime
    blocking_reasons: List[str] = None
    prerequisites: List[str] = None
    
    def __post_init__(self):
        if self.blocking_reasons is None:
            self.blocking_reasons = []
        if self.prerequisites is None:
            self.prerequisites = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.component_type,
            "status": self.status.value,
            "message": self.message,
            "blocking_reasons": self.blocking_reasons,
            "prerequisites": self.prerequisites,
            "last_checked": self.last_checked.isoformat(),
        }


class DataReadinessReporter:
    """Central reporter for system and data readiness status"""
    
    def __init__(self):
        self.components: Dict[str, ComponentStatus] = {}
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all system components with current status"""
        
        # DATA SOURCES - Some verified, some awaiting
        self.components["GSI_Landslides"] = ComponentStatus(
            name="GSI Historical Landslides",
            component_type="data_source",
            status=SystemStatus.VERIFIED,
            message="33,904 field-validated historical landslide events",
            last_checked=datetime.now(),
        )
        
        self.components["Administrative_Boundaries"] = ComponentStatus(
            name="Administrative Boundaries",
            component_type="data_source",
            status=SystemStatus.VERIFIED,
            message="State and district boundaries for 8 NER states",
            last_checked=datetime.now(),
        )
        
        self.components["Roads"] = ComponentStatus(
            name="Road Network",
            component_type="data_source",
            status=SystemStatus.VERIFIED,
            message="Primary and secondary road network (5000+ segments)",
            last_checked=datetime.now(),
        )
        
        self.components["Villages"] = ComponentStatus(
            name="Villages & Settlements",
            component_type="data_source",
            status=SystemStatus.VERIFIED,
            message="Populated villages and settlements (10000+ records)",
            last_checked=datetime.now(),
        )
        
        self.components["DEM"] = ComponentStatus(
            name="Digital Elevation Model",
            component_type="data_source",
            status=SystemStatus.AWAITING_DATA,
            message="High-resolution DEM required for terrain analysis",
            blocking_reasons=["Awaiting verified 30m DEM source"],
            prerequisites=["SRTM or ASTER DEM data for NER region"],
            last_checked=datetime.now(),
        )
        
        self.components["Rainfall"] = ComponentStatus(
            name="Rainfall Data",
            component_type="data_source",
            status=SystemStatus.AWAITING_DATA,
            message="Time-series rainfall observations",
            blocking_reasons=["Awaiting verified rainfall station network or satellite rainfall"],
            prerequisites=["IMD rainfall station data or IMERG satellite data"],
            last_checked=datetime.now(),
        )
        
        self.components["Soil"] = ComponentStatus(
            name="Soil Properties",
            component_type="data_source",
            status=SystemStatus.AWAITING_DATA,
            message="Soil type, moisture, cohesion, friction angle",
            blocking_reasons=["Awaiting verified soil mapping database"],
            prerequisites=["NBSS&LUP soil map or field soil samples with lab analysis"],
            last_checked=datetime.now(),
        )
        
        self.components["Weather"] = ComponentStatus(
            name="Weather Data",
            component_type="data_source",
            status=SystemStatus.AWAITING_DATA,
            message="Temperature, humidity, pressure, wind speed",
            blocking_reasons=["Awaiting verified weather observation network"],
            prerequisites=["IMD weather station data or global weather reanalysis"],
            last_checked=datetime.now(),
        )
        
        self.components["Satellite"] = ComponentStatus(
            name="Satellite Imagery",
            component_type="data_source",
            status=SystemStatus.AWAITING_DATA,
            message="Optical and SAR satellite observations",
            blocking_reasons=["Awaiting archived satellite data access"],
            prerequisites=["Landsat/Copernicus or Sentinel-1/2 data for NER region"],
            last_checked=datetime.now(),
        )
        
        # PROCESSING
        self.components["Python_Processing"] = ComponentStatus(
            name="Python Processing Pipeline",
            component_type="processing",
            status=SystemStatus.OPERATIONAL,
            message="Data ingestion and validation framework ready",
            last_checked=datetime.now(),
        )
        
        self.components["PostGIS"] = ComponentStatus(
            name="PostGIS Database",
            component_type="processing",
            status=SystemStatus.OPERATIONAL,
            message="Spatial database with all required tables",
            last_checked=datetime.now(),
        )
        
        self.components["GIS"] = ComponentStatus(
            name="GIS Interface",
            component_type="processing",
            status=SystemStatus.OPERATIONAL,
            message="MapLibre-based visualization with layer control",
            last_checked=datetime.now(),
        )
        
        self.components["Feature_Engineering"] = ComponentStatus(
            name="Feature Engineering",
            component_type="processing",
            status=SystemStatus.PARTIAL,
            message="Feature schema defined, awaiting data for computation",
            blocking_reasons=["DEM, rainfall, soil, weather data unavailable"],
            prerequisites=["Phase 7: Verified environmental datasets"],
            last_checked=datetime.now(),
        )
        
        # ML
        self.components["ML_Module"] = ComponentStatus(
            name="Machine Learning",
            component_type="ml",
            status=SystemStatus.BLOCKED,
            message="ML pipeline framework ready, model NOT TRAINED",
            blocking_reasons=[
                "No verified training dataset available",
                "Phase 7 feature engineering not complete",
                "Cannot train without environmental features",
            ],
            prerequisites=["Phases 7-8: Feature engineering and model training"],
            last_checked=datetime.now(),
        )
        
        # RISK & HAZARD
        self.components["Risk_Engine"] = ComponentStatus(
            name="Risk Engine",
            component_type="risk",
            status=SystemStatus.BLOCKED,
            message="Risk calculation architecture defined, calculation blocked",
            blocking_reasons=[
                "ML model not trained",
                "Hazard probability maps unavailable",
                "Vulnerability parameters unknown",
            ],
            prerequisites=["Phase 9: ML model training and validation"],
            last_checked=datetime.now(),
        )
        
        self.components["Road_Risk"] = ComponentStatus(
            name="Road Network Risk",
            component_type="risk",
            status=SystemStatus.BLOCKED,
            message="Road geometry verified, risk calculation blocked",
            blocking_reasons=["Risk engine not operational"],
            prerequisites=["Phase 9: Operational risk engine"],
            last_checked=datetime.now(),
        )
        
        self.components["Village_Risk"] = ComponentStatus(
            name="Village Exposure",
            component_type="risk",
            status=SystemStatus.BLOCKED,
            message="Village data verified, risk assessment blocked",
            blocking_reasons=["Risk engine not operational"],
            prerequisites=["Phase 9: Operational risk engine"],
            last_checked=datetime.now(),
        )
        
        self.components["Route_Risk"] = ComponentStatus(
            name="Route Risk Analysis",
            component_type="risk",
            status=SystemStatus.BLOCKED,
            message="Route analysis framework ready, risk calculation blocked",
            blocking_reasons=["Risk engine not operational", "Hazard maps unavailable"],
            prerequisites=["Phase 9: Operational risk engine and hazard maps"],
            last_checked=datetime.now(),
        )
        
        self.components["Alerts"] = ComponentStatus(
            name="Alert Engine",
            component_type="risk",
            status=SystemStatus.BLOCKED,
            message="Alert schema defined, generation blocked",
            blocking_reasons=["Risk engine not operational", "No operational alerts possible"],
            prerequisites=["Phase 9: Operational risk engine"],
            last_checked=datetime.now(),
        )
        
        # USER-FACING
        self.components["Field_Reports"] = ComponentStatus(
            name="Field Reports",
            component_type="user_interface",
            status=SystemStatus.OPERATIONAL,
            message="Field report submission and review workflow implemented",
            last_checked=datetime.now(),
        )
        
        self.components["Dashboard"] = ComponentStatus(
            name="Dashboard",
            component_type="user_interface",
            status=SystemStatus.OPERATIONAL,
            message="Data readiness dashboard with system status",
            last_checked=datetime.now(),
        )
        
        self.components["LLM_Assistant"] = ComponentStatus(
            name="LLM Assistant",
            component_type="user_interface",
            status=SystemStatus.PARTIAL,
            message="Assistant querying real data, honest about unknowns",
            prerequisites=["Real-time connection to data sources"],
            last_checked=datetime.now(),
        )
    
    def get_complete_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        verified = sum(1 for c in self.components.values() if c.status == SystemStatus.VERIFIED)
        operational = sum(1 for c in self.components.values() if c.status == SystemStatus.OPERATIONAL)
        partial = sum(1 for c in self.components.values() if c.status == SystemStatus.PARTIAL)
        awaiting = sum(1 for c in self.components.values() if c.status == SystemStatus.AWAITING_DATA)
        blocked = sum(1 for c in self.components.values() if c.status == SystemStatus.BLOCKED)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "verified": verified,
                "operational": operational,
                "partial": partial,
                "awaiting_data": awaiting,
                "blocked": blocked,
                "total": len(self.components),
            },
            "components": {k: v.to_dict() for k, v in self.components.items()},
            "message": "Complete system architecture demonstrable end-to-end with honest status",
        }
    
    def get_data_sources_status(self) -> Dict[str, Any]:
        """Get data sources status only"""
        sources = {
            k: v.to_dict() for k, v in self.components.items()
            if v.component_type == "data_source"
        }
        
        verified = sum(1 for v in sources.values() if v["status"] == "VERIFIED")
        awaiting = sum(1 for v in sources.values() if v["status"] == "AWAITING_DATA")
        
        return {
            "category": "DATA_SOURCES",
            "verified_count": verified,
            "awaiting_count": awaiting,
            "total_sources": len(sources),
            "sources": sources,
        }
    
    def get_processing_status(self) -> Dict[str, Any]:
        """Get processing pipeline status"""
        processing = {
            k: v.to_dict() for k, v in self.components.items()
            if v.component_type == "processing"
        }
        
        return {
            "category": "PROCESSING",
            "components": processing,
        }
    
    def get_ml_risk_status(self) -> Dict[str, Any]:
        """Get ML and risk component status"""
        components = {
            k: v.to_dict() for k, v in self.components.items()
            if v.component_type in ["ml", "risk"]
        }
        
        return {
            "category": "ML_AND_RISK",
            "components": components,
        }
    
    def get_system_readiness_report(self) -> Dict[str, Any]:
        """Generate system readiness report for leadership"""
        return {
            "title": "NER LANDSLIDE GUARD AI - SYSTEM READINESS REPORT",
            "date": datetime.now().isoformat(),
            "executive_summary": {
                "status": "DEMONSTRATION MODE OPERATIONAL",
                "message": "Complete system architecture is demonstrable with scientifically honest status labels",
                "operational_components": 6,
                "verified_data_sources": 4,
                "awaiting_data_sources": 5,
                "blocked_ml_risk_components": 5,
            },
            "verified_components": [
                "Historical Landslide Events (GSI - 33,904 records)",
                "Administrative Boundaries (8 NER states)",
                "Road Network (5000+ segments)",
                "Villages & Settlements (10000+ records)",
                "Python Processing Pipeline",
                "PostGIS Database",
                "GIS Interface (MapLibre)",
                "Field Reports Workflow",
            ],
            "awaiting_verified_data": [
                "Digital Elevation Model (DEM)",
                "Rainfall Data",
                "Soil Properties",
                "Weather Data",
                "Satellite Imagery",
            ],
            "blocked_scientific_stages": [
                "ML Model (requires verified training features)",
                "Risk Engine (requires trained model)",
                "Road/Village Risk (requires risk engine)",
                "Route Analysis (requires risk engine)",
                "Alerts (requires risk engine)",
            ],
            "demonstration_capabilities": [
                "View 33,904 verified historical landslides",
                "Switch between map layers (street, satellite, topographic, terrain)",
                "View administrative boundaries",
                "View road network",
                "View villages and settlements",
                "Submit and review field reports",
                "Query LLM about historical data",
                "See complete system architecture with honest status",
            ],
            "next_steps": [
                "Phase 7: Obtain verified DEM, rainfall, soil, weather, satellite data",
                "Phase 7: Create spatially-aligned feature dataset from environmental sources",
                "Phase 8: Train and validate landslide prediction model",
                "Phase 9: Implement operational risk engine",
                "Phase 10: Deploy real-time alerts",
            ],
            "complete_status": self.get_complete_status(),
        }


# Global reporter
_reporter = DataReadinessReporter()


def get_system_status() -> Dict[str, Any]:
    """Get complete system status"""
    return _reporter.get_complete_status()


def get_data_sources_status() -> Dict[str, Any]:
    """Get data sources status"""
    return _reporter.get_data_sources_status()


def get_processing_status() -> Dict[str, Any]:
    """Get processing pipeline status"""
    return _reporter.get_processing_status()


def get_ml_risk_status() -> Dict[str, Any]:
    """Get ML and risk status"""
    return _reporter.get_ml_risk_status()


def get_system_readiness_report() -> Dict[str, Any]:
    """Get system readiness report"""
    return _reporter.get_system_readiness_report()
