"""
Phase 6-7 Feature Engineering Foundation
Defines feature schema but returns DATA_NOT_AVAILABLE when source datasets are missing
NO FABRICATED DATA
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Optional
from enum import Enum

import numpy as np

from scripts.ingestion.environmental_foundation import (
    get_dataset_status,
    calculate_phase_7_readiness,
)


class FeatureAvailability(str, Enum):
    """Feature availability status"""

    AVAILABLE = "AVAILABLE"
    DATA_NOT_AVAILABLE = "DATA_NOT_AVAILABLE"
    AWAITING_SOURCE_DATA = "AWAITING_SOURCE_DATA"
    NOT_COMPUTED = "NOT_COMPUTED"


@dataclass
class FeatureDefinition:
    """Definition of a feature that will be used in ML training"""

    feature_id: str
    feature_name: str
    feature_group: str  # terrain, rainfall, soil, etc.
    description: str
    source_dataset: str  # Which dataset provides this feature
    calculation: str  # How it is calculated
    units: str
    temporal_window: str | None  # e.g., "24h", "7d", "static"
    spatial_resolution: str
    crs: str
    required_for_phase: int
    null_handling: str  # how to handle missing values
    availability: FeatureAvailability = FeatureAvailability.DATA_NOT_AVAILABLE

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "feature_name": self.feature_name,
            "feature_group": self.feature_group,
            "description": self.description,
            "source_dataset": self.source_dataset,
            "calculation": self.calculation,
            "units": self.units,
            "temporal_window": self.temporal_window,
            "spatial_resolution": self.spatial_resolution,
            "crs": self.crs,
            "required_for_phase": self.required_for_phase,
            "null_handling": self.null_handling,
            "availability": self.availability.value,
        }


# ==================================================
# TERRAIN FEATURES (require DEM)
# ==================================================

ELEVATION = FeatureDefinition(
    feature_id="terrain_elevation",
    feature_name="Elevation",
    feature_group="terrain",
    description="Height above sea level at location",
    source_dataset="dem",
    calculation="DEM value at point location (meters)",
    units="meters",
    temporal_window="static",
    spatial_resolution="30-90m (depends on DEM source)",
    crs="EPSG:4326",
    required_for_phase=7,
    null_handling="Remove from training; mark as nodata in production",
)

SLOPE = FeatureDefinition(
    feature_id="terrain_slope",
    feature_name="Slope",
    feature_group="terrain",
    description="Gradient of terrain surface",
    source_dataset="dem",
    calculation="Computed from DEM using gradient/derivative",
    units="degrees",
    temporal_window="static",
    spatial_resolution="30-90m (depends on DEM source)",
    crs="EPSG:4326",
    required_for_phase=7,
    null_handling="Remove from training; interpolate in production",
)

ASPECT = FeatureDefinition(
    feature_id="terrain_aspect",
    feature_name="Aspect",
    feature_group="terrain",
    description="Direction of slope (North=0°, East=90°, etc.)",
    source_dataset="dem",
    calculation="Computed from DEM gradient direction",
    units="degrees (0-360)",
    temporal_window="static",
    spatial_resolution="30-90m (depends on DEM source)",
    crs="EPSG:4326",
    required_for_phase=7,
    null_handling="Remove from training; interpolate in production",
)

CURVATURE = FeatureDefinition(
    feature_id="terrain_curvature",
    feature_name="Curvature",
    feature_group="terrain",
    description="Curvature of terrain surface (concave/convex)",
    source_dataset="dem",
    calculation="Second derivative of DEM (Laplacian)",
    units="1/meters",
    temporal_window="static",
    spatial_resolution="30-90m (depends on DEM source)",
    crs="EPSG:4326",
    required_for_phase=7,
    null_handling="Remove from training; interpolate in production",
)

FLOW_ACCUMULATION = FeatureDefinition(
    feature_id="terrain_flow_accumulation",
    feature_name="Flow Accumulation",
    feature_group="terrain",
    description="Number of upslope cells draining through a cell",
    source_dataset="dem",
    calculation="D8 or D-infinity flow direction algorithm",
    units="cell count",
    temporal_window="static",
    spatial_resolution="30-90m (depends on DEM source)",
    crs="EPSG:4326",
    required_for_phase=7,
    null_handling="Log-transform; remove zeros from training",
)

# ==================================================
# RAINFALL FEATURES (require rainfall time series)
# ==================================================

RAINFALL_24H = FeatureDefinition(
    feature_id="rainfall_24h",
    feature_name="24-hour Rainfall",
    feature_group="rainfall",
    description="Total precipitation in previous 24 hours",
    source_dataset="rainfall",
    calculation="Sum of hourly/daily rainfall observations",
    units="millimeters (mm)",
    temporal_window="24h",
    spatial_resolution="0.05° (CHIRPS) or station-based",
    crs="EPSG:4326",
    required_for_phase=7,
    null_handling="For training: use sentinel value; in production: use last available observation",
)

RAINFALL_3D = FeatureDefinition(
    feature_id="rainfall_3d",
    feature_name="3-day Rainfall",
    feature_group="rainfall",
    description="Total precipitation in previous 3 days",
    source_dataset="rainfall",
    calculation="Sum of daily rainfall observations (3-day window)",
    units="millimeters (mm)",
    temporal_window="3 days",
    spatial_resolution="0.05° (CHIRPS) or station-based",
    crs="EPSG:4326",
    required_for_phase=7,
    null_handling="For training: use sentinel value; in production: cumulative from available days",
)

RAINFALL_7D = FeatureDefinition(
    feature_id="rainfall_7d",
    feature_name="7-day Rainfall",
    feature_group="rainfall",
    description="Total precipitation in previous 7 days",
    source_dataset="rainfall",
    calculation="Sum of daily rainfall observations (7-day window)",
    units="millimeters (mm)",
    temporal_window="7 days",
    spatial_resolution="0.05° (CHIRPS) or station-based",
    crs="EPSG:4326",
    required_for_phase=7,
    null_handling="For training: use sentinel value; in production: cumulative from available days",
)

RAINFALL_30D = FeatureDefinition(
    feature_id="rainfall_30d",
    feature_name="30-day Rainfall",
    feature_group="rainfall",
    description="Total precipitation in previous 30 days",
    source_dataset="rainfall",
    calculation="Sum of daily rainfall observations (30-day window)",
    units="millimeters (mm)",
    temporal_window="30 days",
    spatial_resolution="0.05° (CHIRPS) or station-based",
    crs="EPSG:4326",
    required_for_phase=7,
    null_handling="For training: use sentinel value; in production: cumulative from available days",
)

RAINFALL_INTENSITY = FeatureDefinition(
    feature_id="rainfall_intensity",
    feature_name="Rainfall Intensity",
    feature_group="rainfall",
    description="Hourly/daily rainfall rate (mm/hour or mm/day)",
    source_dataset="rainfall",
    calculation="Peak hourly or daily rainfall rate",
    units="millimeters per hour or per day",
    temporal_window="24h (or sub-daily)",
    spatial_resolution="0.05° (CHIRPS) or station-based",
    crs="EPSG:4326",
    required_for_phase=7,
    null_handling="For training: remove or use sentinel; in production: compute from available data",
)

# ==================================================
# SOIL FEATURES (require soil properties dataset)
# ==================================================

SOIL_TYPE = FeatureDefinition(
    feature_id="soil_type",
    feature_name="Soil Type",
    feature_group="soil",
    description="Categorical soil classification (clay, silt, sand, etc.)",
    source_dataset="soil",
    calculation="Classification from soil survey or SoilGrids",
    units="categorical (encoded)",
    temporal_window="static",
    spatial_resolution="250m (SoilGrids) or variable",
    crs="EPSG:4326",
    required_for_phase=7,
    null_handling="For training: remove from feature set or use majority class; in production: use nearest neighbor",
)

SOIL_DEPTH = FeatureDefinition(
    feature_id="soil_depth",
    feature_name="Soil Depth",
    feature_group="soil",
    description="Effective soil thickness / regolith depth",
    source_dataset="soil",
    calculation="From soil survey or proxy from relief/age",
    units="centimeters (cm)",
    temporal_window="static",
    spatial_resolution="250m (SoilGrids) or variable",
    crs="EPSG:4326",
    required_for_phase=7,
    null_handling="For training: remove or use mean; in production: use default estimate",
)

SOIL_COHESION = FeatureDefinition(
    feature_id="soil_cohesion",
    feature_name="Soil Cohesion",
    feature_group="soil",
    description="Soil shear strength parameter (c)",
    source_dataset="soil",
    calculation="Inferred from soil type and properties (typically 5-50 kPa for regolith)",
    units="kilopascals (kPa)",
    temporal_window="static",
    spatial_resolution="Variable",
    crs="EPSG:4326",
    required_for_phase=7,
    null_handling="For training: use pedotransfer function or mean; in production: use default by soil type",
)

SOIL_FRICTION_ANGLE = FeatureDefinition(
    feature_id="soil_friction_angle",
    feature_name="Soil Friction Angle",
    feature_group="soil",
    description="Soil shear strength parameter (φ)",
    source_dataset="soil",
    calculation="Inferred from soil type (typically 20-40° for regolith)",
    units="degrees",
    temporal_window="static",
    spatial_resolution="Variable",
    crs="EPSG:4326",
    required_for_phase=7,
    null_handling="For training: use pedotransfer function or mean; in production: use default by soil type",
)

# ==================================================
# HYDROLOGY FEATURES (require drainage/hydrology dataset)
# ==================================================

DISTANCE_TO_STREAM = FeatureDefinition(
    feature_id="hydrology_distance_to_stream",
    feature_name="Distance to Stream",
    feature_group="hydrology",
    description="Euclidean distance to nearest stream or water body",
    source_dataset="hydrology",
    calculation="Computed using spatial distance from drainage network",
    units="meters",
    temporal_window="static",
    spatial_resolution="30m (from HydroSHEDS or DEM)",
    crs="EPSG:4326",
    required_for_phase=7,
    null_handling="For training: remove far-field locations; in production: cap at max distance",
)

DRAINAGE_DENSITY = FeatureDefinition(
    feature_id="hydrology_drainage_density",
    feature_name="Drainage Density",
    feature_group="hydrology",
    description="Length of streams per unit area in a neighborhood",
    source_dataset="hydrology",
    calculation="Total stream length / area within moving window",
    units="1/kilometers",
    temporal_window="static",
    spatial_resolution="Variable (depends on window size)",
    crs="EPSG:4326",
    required_for_phase=7,
    null_handling="For training: compute at standardized scale; in production: same",
)

# ==================================================
# LAND COVER FEATURES (optional, require land cover dataset)
# ==================================================

LAND_COVER_CLASS = FeatureDefinition(
    feature_id="landcover_class",
    feature_name="Land Cover Type",
    feature_group="land_cover",
    description="Categorical land cover (forest, agriculture, urban, water, etc.)",
    source_dataset="landcover",
    calculation="Classification from ESA WorldCover or Copernicus",
    units="categorical (encoded)",
    temporal_window="annual",
    spatial_resolution="10m (ESA WorldCover)",
    crs="EPSG:4326",
    required_for_phase=7,
    null_handling="For training: remove or use majority class; in production: use nearest neighbor",
)

VEGETATION_INDEX = FeatureDefinition(
    feature_id="landcover_vegetation_index",
    feature_name="Vegetation Index (NDVI)",
    feature_group="land_cover",
    description="Normalized Difference Vegetation Index (proxy for vegetation health)",
    source_dataset="satellite",
    calculation="(NIR - Red) / (NIR + Red) from multispectral imagery",
    units="unitless (-1 to +1)",
    temporal_window="seasonal",
    spatial_resolution="10-30m (Sentinel-2/Landsat)",
    crs="EPSG:4326",
    required_for_phase=7,
    null_handling="For training: use seasonal mean; in production: use latest observation",
)

# ==================================================
# FEATURE SETS
# ==================================================

PHASE_7_REQUIRED_FEATURES = [
    ELEVATION,
    SLOPE,
    ASPECT,
    CURVATURE,
    FLOW_ACCUMULATION,
    RAINFALL_24H,
    RAINFALL_3D,
    RAINFALL_7D,
    RAINFALL_30D,
    SOIL_TYPE,
    SOIL_DEPTH,
    DISTANCE_TO_STREAM,
    LAND_COVER_CLASS,
]

PHASE_7_OPTIONAL_FEATURES = [
    RAINFALL_INTENSITY,
    SOIL_COHESION,
    SOIL_FRICTION_ANGLE,
    DRAINAGE_DENSITY,
    VEGETATION_INDEX,
]


def check_feature_availability(feature: FeatureDefinition) -> FeatureAvailability:
    """
    Check if a feature can be computed based on available datasets
    Returns DATA_NOT_AVAILABLE if source dataset is missing
    """
    source_status = get_dataset_status(feature.source_dataset)
    if source_status is None:
        return FeatureAvailability.DATA_NOT_AVAILABLE

    if source_status.status in ("VERIFIED", "PARTIAL"):
        return FeatureAvailability.AVAILABLE
    elif source_status.status == "AWAITING_VERIFIED_SOURCE_DATA":
        return FeatureAvailability.AWAITING_SOURCE_DATA
    else:
        return FeatureAvailability.DATA_NOT_AVAILABLE


def compute_feature_stub(
    feature: FeatureDefinition, location: tuple[float, float]
) -> tuple[float | None, FeatureAvailability]:
    """
    Stub function for computing a feature at a location
    Returns (value, availability_status)
    NO FABRICATED VALUES — returns None if data is not available
    """
    availability = check_feature_availability(feature)

    if availability == FeatureAvailability.AVAILABLE:
        # Placeholder: actual computation requires real data
        # For now, return None until real data is available
        return None, availability

    # Data not available
    return None, availability


def get_feature_engineering_report() -> dict[str, Any]:
    """Generate a report on feature engineering status"""
    required_available = sum(
        1
        for f in PHASE_7_REQUIRED_FEATURES
        if check_feature_availability(f) == FeatureAvailability.AVAILABLE
    )
    required_total = len(PHASE_7_REQUIRED_FEATURES)

    optional_available = sum(
        1
        for f in PHASE_7_OPTIONAL_FEATURES
        if check_feature_availability(f) == FeatureAvailability.AVAILABLE
    )
    optional_total = len(PHASE_7_OPTIONAL_FEATURES)

    return {
        "phase": 7,
        "name": "Feature Engineering",
        "required_features": {
            "total": required_total,
            "available": required_available,
            "missing": required_total - required_available,
            "features": [
                {
                    "feature_id": f.feature_id,
                    "feature_name": f.feature_name,
                    "availability": check_feature_availability(f).value,
                    "source_dataset": f.source_dataset,
                }
                for f in PHASE_7_REQUIRED_FEATURES
            ],
        },
        "optional_features": {
            "total": optional_total,
            "available": optional_available,
            "missing": optional_total - optional_available,
            "features": [
                {
                    "feature_id": f.feature_id,
                    "feature_name": f.feature_name,
                    "availability": check_feature_availability(f).value,
                    "source_dataset": f.source_dataset,
                }
                for f in PHASE_7_OPTIONAL_FEATURES
            ],
        },
        "phase_7_status": "READY"
        if required_available == required_total
        else "BLOCKED",
        "message": "Phase 7 feature engineering BLOCKED until verified environmental datasets are available."
        if required_available < required_total
        else "Phase 7 features can be computed with available data.",
        "phase_7_readiness": calculate_phase_7_readiness(),
    }


if __name__ == "__main__":
    report = get_feature_engineering_report()
    print("Phase 7 Feature Engineering Report:")
    print(f"Status: {report['phase_7_status']}")
    print(f"Required features available: {report['required_features']['available']}/{report['required_features']['total']}")
    print(f"Optional features available: {report['optional_features']['available']}/{report['optional_features']['total']}")
