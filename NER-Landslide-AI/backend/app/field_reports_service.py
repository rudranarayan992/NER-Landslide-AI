"""
Field Reports Service
Real field report workflow: SUBMITTED → UNDER_REVIEW → VERIFIED/REJECTED
Important: A field report is OBSERVATION/REPORT, not automatically a confirmed landslide
"""

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from backend.app.enums import FieldReportStatus


@dataclass
class FieldReport:
    """Complete field report record"""
    report_id: str
    location_name: str
    latitude: float
    longitude: float
    timestamp: datetime
    description: str
    reporter_name: str
    reporter_contact: Optional[str] = None
    photo_url: Optional[str] = None
    evidence_notes: Optional[str] = None
    observations: Dict[str, Any] = field(default_factory=dict)  # Flexible observation data
    
    # Workflow status
    status: FieldReportStatus = FieldReportStatus.SUBMITTED
    submitted_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    verification_status: Optional[str] = None  # VERIFIED, REJECTED, INCONCLUSIVE
    
    # Linking to landslide event (if verified to match existing event)
    linked_landslide_event_id: Optional[str] = None
    confidence_of_link: Optional[float] = None  # 0-1, how certain is the link
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        data["timestamp"] = self.timestamp.isoformat()
        data["submitted_at"] = self.submitted_at.isoformat() if self.submitted_at else None
        data["reviewed_at"] = self.reviewed_at.isoformat() if self.reviewed_at else None
        return data
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'FieldReport':
        """Create FieldReport from dictionary"""
        return FieldReport(
            report_id=data["report_id"],
            location_name=data["location_name"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            description=data["description"],
            reporter_name=data["reporter_name"],
            reporter_contact=data.get("reporter_contact"),
            photo_url=data.get("photo_url"),
            evidence_notes=data.get("evidence_notes"),
            observations=data.get("observations", {}),
            status=FieldReportStatus[data.get("status", "SUBMITTED")],
            submitted_at=datetime.fromisoformat(data["submitted_at"]) if data.get("submitted_at") else None,
            reviewed_by=data.get("reviewed_by"),
            reviewed_at=datetime.fromisoformat(data["reviewed_at"]) if data.get("reviewed_at") else None,
            review_notes=data.get("review_notes"),
            verification_status=data.get("verification_status"),
            linked_landslide_event_id=data.get("linked_landslide_event_id"),
            confidence_of_link=data.get("confidence_of_link"),
        )


class FieldReportService:
    """Manage field reports - real workflow without fabrication"""
    
    def __init__(self):
        self.reports: Dict[str, FieldReport] = {}
        self.next_report_id = 1
    
    def submit_report(
        self,
        location_name: str,
        latitude: float,
        longitude: float,
        description: str,
        reporter_name: str,
        reporter_contact: Optional[str] = None,
        photo_url: Optional[str] = None,
        evidence_notes: Optional[str] = None,
        observations: Optional[Dict[str, Any]] = None,
    ) -> FieldReport:
        """Submit a new field report"""
        report_id = f"FIELD_REPORT_{self.next_report_id:06d}"
        self.next_report_id += 1
        
        report = FieldReport(
            report_id=report_id,
            location_name=location_name,
            latitude=latitude,
            longitude=longitude,
            timestamp=datetime.now(),
            description=description,
            reporter_name=reporter_name,
            reporter_contact=reporter_contact,
            photo_url=photo_url,
            evidence_notes=evidence_notes,
            observations=observations or {},
            status=FieldReportStatus.SUBMITTED,
            submitted_at=datetime.now(),
        )
        
        self.reports[report_id] = report
        return report
    
    def get_report(self, report_id: str) -> Optional[FieldReport]:
        """Get a field report by ID"""
        return self.reports.get(report_id)
    
    def get_all_reports(
        self,
        status: Optional[FieldReportStatus] = None,
        state: Optional[str] = None,
    ) -> List[FieldReport]:
        """Get all field reports, optionally filtered"""
        reports = list(self.reports.values())
        
        if status:
            reports = [r for r in reports if r.status == status]
        
        return reports
    
    def update_report_status(
        self,
        report_id: str,
        new_status: FieldReportStatus,
        reviewed_by: Optional[str] = None,
        review_notes: Optional[str] = None,
        verification_status: Optional[str] = None,
        linked_landslide_event_id: Optional[str] = None,
        confidence: Optional[float] = None,
    ) -> Optional[FieldReport]:
        """Update field report status through review workflow"""
        report = self.reports.get(report_id)
        if not report:
            return None
        
        report.status = new_status
        report.reviewed_by = reviewed_by
        report.reviewed_at = datetime.now()
        report.review_notes = review_notes
        report.verification_status = verification_status
        report.linked_landslide_event_id = linked_landslide_event_id
        report.confidence_of_link = confidence
        
        return report
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get field report statistics"""
        total = len(self.reports)
        by_status = {}
        for status in FieldReportStatus:
            count = sum(1 for r in self.reports.values() if r.status == status)
            by_status[status.value] = count
        
        verified_count = sum(
            1 for r in self.reports.values()
            if r.status == FieldReportStatus.VERIFIED
        )
        
        linked_count = sum(
            1 for r in self.reports.values()
            if r.linked_landslide_event_id is not None
        )
        
        return {
            "total_reports": total,
            "by_status": by_status,
            "verified_reports": verified_count,
            "linked_to_events": linked_count,
            "awaiting_review": by_status.get(FieldReportStatus.UNDER_REVIEW.value, 0),
        }
    
    def clear_all(self) -> None:
        """Clear all reports (for testing)"""
        self.reports.clear()
        self.next_report_id = 1


# Global field report service
_field_report_service = FieldReportService()


def submit_field_report(
    location_name: str,
    latitude: float,
    longitude: float,
    description: str,
    reporter_name: str,
    **kwargs
) -> Dict[str, Any]:
    """Submit a new field report"""
    report = _field_report_service.submit_report(
        location_name=location_name,
        latitude=latitude,
        longitude=longitude,
        description=description,
        reporter_name=reporter_name,
        **kwargs
    )
    return {
        "status": "SUCCESS",
        "report": report.to_dict(),
        "message": f"Field report {report.report_id} submitted for review",
    }


def get_field_reports(
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """Get all field reports"""
    filter_status = None
    if status:
        try:
            filter_status = FieldReportStatus[status.upper()]
        except KeyError:
            pass
    
    reports = _field_report_service.get_all_reports(status=filter_status)
    return {
        "status": "OK",
        "count": len(reports),
        "reports": [r.to_dict() for r in reports],
        "message": "Field reports returned (observation data, not automatically verified)",
    }


def get_field_report(report_id: str) -> Dict[str, Any]:
    """Get a specific field report"""
    report = _field_report_service.get_report(report_id)
    if not report:
        return {"status": "NOT_FOUND", "message": f"Report {report_id} not found"}
    
    return {
        "status": "OK",
        "report": report.to_dict(),
    }


def review_field_report(
    report_id: str,
    action: str,  # VERIFY, REJECT, INCONCLUSIVE
    reviewed_by: str,
    review_notes: Optional[str] = None,
    linked_event_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Review and update field report status"""
    report = _field_report_service.get_report(report_id)
    if not report:
        return {"status": "NOT_FOUND", "message": f"Report {report_id} not found"}
    
    if action == "VERIFY":
        new_status = FieldReportStatus.VERIFIED
        verification_status = "VERIFIED"
    elif action == "REJECT":
        new_status = FieldReportStatus.REJECTED
        verification_status = "REJECTED"
    else:
        new_status = FieldReportStatus.UNDER_REVIEW
        verification_status = "INCONCLUSIVE"
    
    updated = _field_report_service.update_report_status(
        report_id=report_id,
        new_status=new_status,
        reviewed_by=reviewed_by,
        review_notes=review_notes,
        verification_status=verification_status,
        linked_landslide_event_id=linked_event_id,
    )
    
    return {
        "status": "OK",
        "report": updated.to_dict(),
        "message": f"Field report {report_id} reviewed: {verification_status}",
    }


def get_field_report_statistics() -> Dict[str, Any]:
    """Get field report statistics"""
    return _field_report_service.get_statistics()
