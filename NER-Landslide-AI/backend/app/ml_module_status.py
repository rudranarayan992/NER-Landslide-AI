"""
ML Module Status and Configuration
Reports model training/validation/prediction status
WITHOUT fabricating accuracy, predictions, or pretending to be trained
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any
from backend.app.enums import MLModelStatus, SystemStatus


@dataclass
class FeatureSchema:
    """Feature definition for model training"""
    name: str
    data_type: str
    source_dataset: str
    description: str
    availability: str  # AVAILABLE, UNAVAILABLE, PARTIAL


@dataclass
class ModelMetadata:
    """Model version and metadata"""
    model_id: str
    version: str
    status: MLModelStatus
    created_at: Optional[datetime] = None
    trained_at: Optional[datetime] = None
    last_validated_at: Optional[datetime] = None
    algorithm: Optional[str] = None
    input_features: Optional[list[str]] = None
    output_shape: Optional[tuple] = None
    framework: str = "scikit-learn"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "version": self.version,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "trained_at": self.trained_at.isoformat() if self.trained_at else None,
            "last_validated_at": self.last_validated_at.isoformat() if self.last_validated_at else None,
            "algorithm": self.algorithm,
            "input_features": self.input_features,
            "output_shape": self.output_shape,
            "framework": self.framework,
        }


@dataclass
class TrainingDatasetStatus:
    """Status of training dataset availability"""
    required_features: list[str]
    available_features: list[str]
    missing_features: list[str]
    total_samples: int
    verified_samples: int
    coverage_percentage: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MLModuleStatus:
    """Central ML module status tracker"""
    
    def __init__(self):
        self.overall_status = SystemStatus.BLOCKED
        self.models: Dict[str, ModelMetadata] = {}
        self.training_data_status: Optional[TrainingDatasetStatus] = None
        self.last_checked = datetime.now()
        
    def get_status(self) -> Dict[str, Any]:
        """Get complete ML module status"""
        return {
            "component": "ML_MODULE",
            "status": self.overall_status.value,
            "message": self._get_status_message(),
            "models": {k: v.to_dict() for k, v in self.models.items()},
            "training_data": self.training_data_status.to_dict() if self.training_data_status else None,
            "blocking_reasons": self._get_blocking_reasons(),
            "last_checked": self.last_checked.isoformat(),
        }
    
    def _get_status_message(self) -> str:
        if self.overall_status == SystemStatus.BLOCKED:
            return (
                "ML MODULE BLOCKED — No validated training dataset exists. "
                "Environmental data (DEM, rainfall, soil, geology) must be verified first. "
                "Once Phase 7 feature engineering produces validated spatially-aligned features, "
                "model training can begin."
            )
        elif self.overall_status == SystemStatus.AWAITING_DATA:
            return (
                "ML MODULE AWAITING DATA — Training pipeline ready, "
                "waiting for verified feature dataset from Phase 7."
            )
        elif self.overall_status == SystemStatus.PARTIAL:
            return "ML MODULE PARTIAL — Some models trained, others awaiting validation."
        else:
            return "ML MODULE OPERATIONAL"
    
    def _get_blocking_reasons(self) -> list[str]:
        return [
            "No verified environmental training dataset exists (Phase 7 not complete)",
            "Cannot train landslide prediction model without validated feature set",
            "Missing verified DEM, rainfall, soil, geology data for feature engineering",
            "Field reports insufficient for supervised learning (raw data, not verified observations)",
            "Cross-validation requires spatial hold-out test regions (not established)",
        ]
    
    def register_model(self, model_id: str, metadata: ModelMetadata) -> None:
        """Register a model version"""
        self.models[model_id] = metadata
    
    def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        """Get model metadata"""
        return self.models.get(model_id)


# Global ML module status
_ml_module = MLModuleStatus()


def get_ml_module_status() -> Dict[str, Any]:
    """Get current ML module status"""
    return _ml_module.get_status()


def register_model(model_id: str, metadata: ModelMetadata) -> None:
    """Register a new model"""
    _ml_module.register_model(model_id, metadata)


def check_training_readiness() -> Dict[str, Any]:
    """Check if training dataset is ready"""
    return {
        "status": "BLOCKED",
        "training_ready": False,
        "reason": "No verified training dataset available",
        "required_steps": [
            "1. Verify environmental data sources (DEM, rainfall, soil, geology)",
            "2. Align all spatial datasets to common grid/projection",
            "3. Create training features for all verified landslide events",
            "4. Establish train/validation/test splits with spatial hold-out",
            "5. Validate feature distributions match expected environmental conditions",
            "6. Only then: begin model training",
        ],
        "current_blocker": "Phase 7 feature engineering not complete",
    }
