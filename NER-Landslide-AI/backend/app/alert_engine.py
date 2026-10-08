"""
Alert Engine
Implements alert schema: BLOCKED until validated risk exists
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from backend.app.enums import AlertStatus, SystemStatus


@dataclass
class Alert:
    """Alert record"""
    alert_id: str
    location_id: str
    location_name: str
    latitude: float
    longitude: float
    severity: str  # VERY_LOW, LOW, MODERATE, HIGH, VERY_HIGH (would be from risk score)
    timestamp: datetime
    reason: str
    supporting_dataset: str
    model_version: Optional[str]
    status: AlertStatus
    verification_status: str  # UNVERIFIED, UNDER_VERIFICATION, VERIFIED
    created_at: datetime = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "location_id": self.location_id,
            "location_name": self.location_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat(),
            "reason": self.reason,
            "supporting_dataset": self.supporting_dataset,
            "model_version": self.model_version,
            "status": self.status.value,
            "verification_status": self.verification_status,
            "created_at": self.created_at.isoformat(),
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "acknowledged_by": self.acknowledged_by,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }


class AlertEngine:
    """Alert engine - demonstrates architecture while showing BLOCKED status"""
    
    def __init__(self):
        self.status = SystemStatus.BLOCKED
        self.alerts: Dict[str, Alert] = {}
        self.next_alert_id = 1
    
    def get_status(self) -> Dict[str, Any]:
        """Get alert engine status"""
        return {
            "component": "ALERT_ENGINE",
            "status": self.status.value,
            "message": self._get_status_message(),
            "blocking_reasons": [
                "Risk engine not operational (Phase 9 not complete)",
                "No validated hazard probability maps available",
                "Cannot generate alerts without risk output",
                "Alert thresholds not calibrated",
                "No real-time risk updates available",
            ],
            "total_alerts": len(self.alerts),
            "alerts_by_status": self._get_alerts_by_status(),
        }
    
    def _get_status_message(self) -> str:
        return (
            "ALERT ENGINE BLOCKED — Cannot generate operational alerts. "
            "Requires: (1) Risk engine producing risk scores, (2) Alert thresholds calibrated, "
            "(3) Real-time environmental data stream. "
            "Current status: Awaiting Phase 9 risk engine completion."
        )
    
    def _get_alerts_by_status(self) -> Dict[str, int]:
        """Count alerts by status"""
        counts = {}
        for status in AlertStatus:
            count = sum(1 for a in self.alerts.values() if a.status == status)
            if count > 0:
                counts[status.value] = count
        return counts
    
    def create_demonstration_alert(
        self,
        location_name: str,
        latitude: float,
        longitude: float,
    ) -> Optional[Alert]:
        """
        Create a DEMONSTRATION alert for system showcase
        Marked as UNVERIFIED because it's synthetic for demo purposes
        """
        alert_id = f"ALERT_DEMO_{self.next_alert_id:06d}"
        self.next_alert_id += 1
        
        alert = Alert(
            alert_id=alert_id,
            location_id=f"LOC_{int(latitude*1000)}_{int(longitude*1000)}",
            location_name=location_name,
            latitude=latitude,
            longitude=longitude,
            severity="DEMONSTRATION",  # Not a real severity class
            timestamp=datetime.now(),
            reason="DEMONSTRATION ONLY - Not a real alert",
            supporting_dataset="SYNTHETIC_DATA",
            model_version="NONE",
            status=AlertStatus.DISMISSED,
            verification_status="DEMONSTRATION",
            created_at=datetime.now(),
        )
        
        self.alerts[alert_id] = alert
        return alert
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return [a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE]
    
    def get_all_alerts(self) -> List[Alert]:
        """Get all alerts"""
        return list(self.alerts.values())
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> Optional[Alert]:
        """Acknowledge an alert"""
        alert = self.alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            alert.acknowledged_by = acknowledged_by
        return alert
    
    def resolve_alert(self, alert_id: str) -> Optional[Alert]:
        """Mark alert as resolved"""
        alert = self.alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
        return alert


# Global alert engine
_alert_engine = AlertEngine()


def get_alert_engine_status() -> Dict[str, Any]:
    """Get alert engine status"""
    return _alert_engine.get_status()


def get_alerts() -> Dict[str, Any]:
    """Get all alerts"""
    all_alerts = _alert_engine.get_all_alerts()
    return {
        "status": "BLOCKED",
        "component": "ALERT_ENGINE",
        "total_alerts": len(all_alerts),
        "alerts": [a.to_dict() for a in all_alerts],
        "message": "ALERT ENGINE BLOCKED — No validated risk outputs available for alert generation",
        "data_status": "UNAVAILABLE",
    }


def get_active_alerts() -> Dict[str, Any]:
    """Get active alerts"""
    active = _alert_engine.get_active_alerts()
    return {
        "status": "BLOCKED",
        "component": "ALERT_ENGINE",
        "active_alerts": len(active),
        "alerts": [a.to_dict() for a in active],
        "message": "No active alerts - Alert engine is not operational",
    }


def acknowledge_alert(alert_id: str, acknowledged_by: str) -> Dict[str, Any]:
    """Acknowledge an alert"""
    alert = _alert_engine.acknowledge_alert(alert_id, acknowledged_by)
    if alert:
        return {
            "status": "OK",
            "alert": alert.to_dict(),
            "message": f"Alert {alert_id} acknowledged",
        }
    return {
        "status": "NOT_FOUND",
        "message": f"Alert {alert_id} not found",
    }


def create_demonstration_alert(
    location_name: str,
    latitude: float,
    longitude: float,
) -> Dict[str, Any]:
    """Create a demonstration alert (for UI/UX testing only)"""
    alert = _alert_engine.create_demonstration_alert(location_name, latitude, longitude)
    return {
        "status": "OK",
        "alert": alert.to_dict(),
        "warning": "THIS IS A DEMONSTRATION ALERT - NOT BASED ON REAL RISK CALCULATION",
        "message": f"Demonstration alert created for {location_name}",
    }
