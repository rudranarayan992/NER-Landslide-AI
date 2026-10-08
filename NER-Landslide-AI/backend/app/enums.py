"""
System status enums - centralized status model for all components
"""

from enum import Enum
from typing import Literal


class SystemStatus(str, Enum):
    """Central system component status enum"""
    VERIFIED = "VERIFIED"  # Real, validated data/component
    OPERATIONAL = "OPERATIONAL"  # Working end-to-end
    PARTIAL = "PARTIAL"  # Partially implemented
    AWAITING_DATA = "AWAITING_DATA"  # Implemented but waiting for verified data
    BLOCKED = "BLOCKED"  # Cannot proceed, documented scientific reason


class ComponentType(str, Enum):
    """Component types in the system"""
    DATA_SOURCE = "data_source"
    PROCESSING = "processing"
    ML = "machine_learning"
    RISK = "risk"
    USER_INTERFACE = "user_interface"
    API = "api"


class FeatureAvailability(str, Enum):
    """Feature availability status"""
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"


class MLModelStatus(str, Enum):
    """ML model lifecycle status"""
    NOT_TRAINED = "NOT_TRAINED"
    TRAINING = "TRAINING"
    VALIDATION = "VALIDATION"
    READY = "READY"
    DEPRECATED = "DEPRECATED"


class RiskStatus(str, Enum):
    """Risk calculation status"""
    BLOCKED = "BLOCKED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    CALCULATED = "CALCULATED"
    OUTDATED = "OUTDATED"


class FieldReportStatus(str, Enum):
    """Field report workflow status"""
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class AlertStatus(str, Enum):
    """Alert status"""
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"
    CANCELLED = "CANCELLED"


# Type aliases for cleaner code
StatusValue = Literal["VERIFIED", "OPERATIONAL", "PARTIAL", "AWAITING_DATA", "BLOCKED"]
