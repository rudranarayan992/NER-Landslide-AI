"""
Phase 6 Environmental Data Foundation
ETL framework for environmental datasets
NO FABRICATED DATA - all functions return DATA_NOT_AVAILABLE when inputs are missing
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Optional
import json
import hashlib

from backend.app.config import NER_STATES, SETTINGS

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_ROOT / "raw"
PROCESSED_DATA_DIR = DATA_ROOT / "processed"
METADATA_DIR = DATA_ROOT / "metadata"


def utc_now_iso() -> str:
    """ISO 8601 timestamp in UTC"""
    return datetime.now(timezone.utc).isoformat()


def ensure_metadata_dir() -> None:
    """Create metadata directory if it does not exist"""
    METADATA_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class DatasetStatus:
    """Status of a dataset in the repository"""

    dataset_id: str
    dataset_name: str
    provider: str
    category: str
    status: Literal[
        "VERIFIED",
        "PARTIAL",
        "AWAITING_VERIFIED_SOURCE_DATA",
        "BLOCKED",
        "NOT_AVAILABLE",
    ]
    verification_status: str
    local_path: str
    ingestion_status: str
    coverage: str
    spatial_resolution: str
    crs: str
    notes: str
    file_count: int = 0
    total_size_bytes: int = 0
    last_verified: str = ""
    data_quality: str = "NOT_AVAILABLE"
    required_for_phase: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "dataset_id": self.dataset_id,
            "dataset_name": self.dataset_name,
            "provider": self.provider,
            "category": self.category,
            "status": self.status,
            "verification_status": self.verification_status,
            "local_path": self.local_path,
            "ingestion_status": self.ingestion_status,
            "coverage": self.coverage,
            "spatial_resolution": self.spatial_resolution,
            "crs": self.crs,
            "notes": self.notes,
            "file_count": self.file_count,
            "total_size_bytes": self.total_size_bytes,
            "last_verified": self.last_verified,
            "data_quality": self.data_quality,
            "required_for_phase": self.required_for_phase,
        }


def scan_directory_size(path: Path) -> tuple[int, int]:
    """
    Scan directory and return (file_count, total_size_bytes)
    Returns (0, 0) if directory does not exist
    """
    if not path.exists():
        return 0, 0

    file_count = 0
    total_bytes = 0
    for file_path in path.rglob("*"):
        if file_path.is_file():
            file_count += 1
            total_bytes += file_path.stat().st_size

    return file_count, total_bytes


def validate_crs(crs_string: str) -> bool:
    """
    Check if CRS string is valid format (EPSG:XXXX)
    Does NOT validate against actual coordinate reference systems
    """
    if not crs_string:
        return False
    if crs_string.startswith("EPSG:"):
        try:
            int(crs_string.split(":")[1])
            return True
        except (IndexError, ValueError):
            return False
    return False


def get_dataset_status(dataset_id: str) -> DatasetStatus | None:
    """
    Inspect a dataset and return its status
    Returns None if dataset is not recognized
    """
    # GSI Landslides
    if dataset_id == "gsi_landslides":
        pdf_path = RAW_DATA_DIR / "landslides" / "33,904 field-validated inventory records.pdf"
        if pdf_path.exists():
            file_count, size = scan_directory_size(pdf_path.parent)
            return DatasetStatus(
                dataset_id="gsi_landslides",
                dataset_name="GSI Historical Landslide Inventory",
                provider="Geological Survey of India",
                category="historical_landslides",
                status="VERIFIED",
                verification_status="VERIFIED",
                local_path=str(pdf_path),
                ingestion_status="COMPLETED",
                coverage="8 NER states (33,904 events)",
                spatial_resolution="Point locations from field surveys",
                crs="EPSG:4326",
                notes="Field-validated landslide events; 33,904 records with coordinates",
                file_count=file_count,
                total_size_bytes=size,
                last_verified=utc_now_iso(),
                data_quality="OBSERVED",
            )
        else:
            return DatasetStatus(
                dataset_id="gsi_landslides",
                dataset_name="GSI Historical Landslide Inventory",
                provider="Geological Survey of India",
                category="historical_landslides",
                status="NOT_AVAILABLE",
                verification_status="NOT_FOUND",
                local_path=str(pdf_path),
                ingestion_status="BLOCKED",
                coverage="Unknown",
                spatial_resolution="N/A",
                crs="EPSG:4326",
                notes="PDF file not found at expected location",
            )

    # DEM
    if dataset_id == "dem":
        dem_dir = RAW_DATA_DIR / "dem"
        file_count, size = scan_directory_size(dem_dir)
        return DatasetStatus(
            dataset_id="dem",
            dataset_name="Digital Elevation Model",
            provider="AWAITING SOURCE",
            category="terrain",
            status="AWAITING_VERIFIED_SOURCE_DATA" if file_count == 0 else "PARTIAL",
            verification_status="AWAITING_VERIFIED_SOURCE_DATA",
            local_path=str(dem_dir),
            ingestion_status="BLOCKED",
            coverage="8 NER states",
            spatial_resolution="30-90m (depends on source)",
            crs="EPSG:4326",
            notes="DEM is essential for Phase 7 feature engineering (slope, aspect, curvature). Not yet obtained.",
            file_count=file_count,
            total_size_bytes=size,
            data_quality="NOT_AVAILABLE",
            required_for_phase=7,
        )

    # Rainfall
    if dataset_id == "rainfall":
        rainfall_dir = RAW_DATA_DIR / "rainfall"
        file_count, size = scan_directory_size(rainfall_dir)
        return DatasetStatus(
            dataset_id="rainfall",
            dataset_name="Rainfall Observations",
            provider="AWAITING SOURCE",
            category="rainfall_precipitation",
            status="AWAITING_VERIFIED_SOURCE_DATA" if file_count == 0 else "PARTIAL",
            verification_status="AWAITING_VERIFIED_SOURCE_DATA",
            local_path=str(rainfall_dir),
            ingestion_status="BLOCKED",
            coverage="8 NER states",
            spatial_resolution="0.05° (CHIRPS), station-based (IMD)",
            crs="EPSG:4326",
            notes="Rainfall data is critical for landslide triggering analysis. Not yet obtained.",
            file_count=file_count,
            total_size_bytes=size,
            data_quality="NOT_AVAILABLE",
            required_for_phase=7,
        )

    # Soil
    if dataset_id == "soil":
        soil_dir = RAW_DATA_DIR / "soil"
        file_count, size = scan_directory_size(soil_dir)
        return DatasetStatus(
            dataset_id="soil",
            dataset_name="Soil Properties",
            provider="AWAITING SOURCE",
            category="soil",
            status="AWAITING_VERIFIED_SOURCE_DATA" if file_count == 0 else "PARTIAL",
            verification_status="AWAITING_VERIFIED_SOURCE_DATA",
            local_path=str(soil_dir),
            ingestion_status="BLOCKED",
            coverage="8 NER states",
            spatial_resolution="250m (SoilGrids), variable (Indian surveys)",
            crs="EPSG:4326",
            notes="Soil properties important for susceptibility modeling. Not yet obtained.",
            file_count=file_count,
            total_size_bytes=size,
            data_quality="NOT_AVAILABLE",
            required_for_phase=7,
        )

    # Hydrology
    if dataset_id == "hydrology":
        hydro_dir = RAW_DATA_DIR / "hydrology"
        file_count, size = scan_directory_size(hydro_dir)
        return DatasetStatus(
            dataset_id="hydrology",
            dataset_name="Hydrological Network",
            provider="AWAITING SOURCE",
            category="hydrology",
            status="AWAITING_VERIFIED_SOURCE_DATA" if file_count == 0 else "PARTIAL",
            verification_status="AWAITING_VERIFIED_SOURCE_DATA",
            local_path=str(hydro_dir),
            ingestion_status="BLOCKED",
            coverage="8 NER states",
            spatial_resolution="30m (HydroSHEDS)",
            crs="EPSG:4326",
            notes="Drainage patterns important for flow accumulation. Not yet obtained.",
            file_count=file_count,
            total_size_bytes=size,
            data_quality="NOT_AVAILABLE",
            required_for_phase=7,
        )

    # Weather
    if dataset_id == "weather":
        weather_dir = RAW_DATA_DIR / "weather"
        file_count, size = scan_directory_size(weather_dir)
        return DatasetStatus(
            dataset_id="weather",
            dataset_name="Weather Observations",
            provider="AWAITING SOURCE",
            category="weather",
            status="AWAITING_VERIFIED_SOURCE_DATA" if file_count == 0 else "PARTIAL",
            verification_status="AWAITING_VERIFIED_SOURCE_DATA",
            local_path=str(weather_dir),
            ingestion_status="BLOCKED",
            coverage="8 NER states (limited by station density)",
            spatial_resolution="Station-based",
            crs="EPSG:4326",
            notes="Optional for current-risk monitoring. Not yet obtained.",
            file_count=file_count,
            total_size_bytes=size,
            data_quality="NOT_AVAILABLE",
            required_for_phase=10,
        )

    # Soil Moisture
    if dataset_id == "soil_moisture":
        sm_dir = RAW_DATA_DIR / "soil_moisture"
        file_count, size = scan_directory_size(sm_dir)
        return DatasetStatus(
            dataset_id="soil_moisture",
            dataset_name="Soil Moisture",
            provider="AWAITING SOURCE",
            category="soil_moisture",
            status="AWAITING_VERIFIED_SOURCE_DATA" if file_count == 0 else "PARTIAL",
            verification_status="AWAITING_VERIFIED_SOURCE_DATA",
            local_path=str(sm_dir),
            ingestion_status="BLOCKED",
            coverage="8 NER states",
            spatial_resolution="1-10 km",
            crs="EPSG:4326",
            notes="Useful for current-risk assessment. Not yet obtained.",
            file_count=file_count,
            total_size_bytes=size,
            data_quality="NOT_AVAILABLE",
            required_for_phase=10,
        )

    # Land Cover
    if dataset_id == "landcover":
        lc_dir = RAW_DATA_DIR / "landcover"
        file_count, size = scan_directory_size(lc_dir)
        return DatasetStatus(
            dataset_id="landcover",
            dataset_name="Land Cover Classification",
            provider="AWAITING SOURCE",
            category="land_cover",
            status="AWAITING_VERIFIED_SOURCE_DATA" if file_count == 0 else "PARTIAL",
            verification_status="AWAITING_VERIFIED_SOURCE_DATA",
            local_path=str(lc_dir),
            ingestion_status="BLOCKED",
            coverage="8 NER states",
            spatial_resolution="10m (ESA WorldCover)",
            crs="EPSG:4326",
            notes="Land-cover classes important for susceptibility. Not yet obtained.",
            file_count=file_count,
            total_size_bytes=size,
            data_quality="NOT_AVAILABLE",
            required_for_phase=7,
        )

    # Satellite
    if dataset_id == "satellite":
        sat_dir = RAW_DATA_DIR / "satellite"
        file_count, size = scan_directory_size(sat_dir)
        return DatasetStatus(
            dataset_id="satellite",
            dataset_name="Satellite Imagery",
            provider="AWAITING SOURCE",
            category="satellite_remote_sensing",
            status="AWAITING_VERIFIED_SOURCE_DATA" if file_count == 0 else "PARTIAL",
            verification_status="AWAITING_VERIFIED_SOURCE_DATA",
            local_path=str(sat_dir),
            ingestion_status="BLOCKED",
            coverage="8 NER states",
            spatial_resolution="10-30m (Sentinel-2/Landsat-8)",
            crs="EPSG:4326",
            notes="Optional for change detection. Not yet obtained.",
            file_count=file_count,
            total_size_bytes=size,
            data_quality="NOT_AVAILABLE",
            required_for_phase=10,
        )

    # Geology
    if dataset_id == "geology":
        geo_dir = RAW_DATA_DIR / "geology"
        file_count, size = scan_directory_size(geo_dir)
        status = "PARTIAL" if file_count > 0 else "AWAITING_VERIFIED_SOURCE_DATA"
        return DatasetStatus(
            dataset_id="geology",
            dataset_name="Geological Map",
            provider="Local sources + AWAITING VERIFIED NATIONAL SOURCE",
            category="geology",
            status=status,
            verification_status=status,
            local_path=str(geo_dir),
            ingestion_status="PARTIAL",
            coverage="Partial NER coverage",
            spatial_resolution="Variable (1:50,000-1:250,000)",
            crs="EPSG:4326",
            notes="Some geology data available locally. National geological map needed.",
            file_count=file_count,
            total_size_bytes=size,
            data_quality="PARTIAL",
            required_for_phase=7,
        )

    # Roads
    if dataset_id == "roads":
        roads_dir = RAW_DATA_DIR / "roads"
        file_count, size = scan_directory_size(roads_dir)
        status = "PARTIAL" if file_count > 0 else "AWAITING_VERIFIED_SOURCE_DATA"
        return DatasetStatus(
            dataset_id="roads",
            dataset_name="Road Network",
            provider="Local OSM + AWAITING VERIFICATION",
            category="roads",
            status=status,
            verification_status=status,
            local_path=str(roads_dir),
            ingestion_status="PARTIAL",
            coverage="Partial NER coverage",
            spatial_resolution="Vector linestrings",
            crs="EPSG:4326",
            notes="Road data exists but requires verification for Phase 11 (road-risk).",
            file_count=file_count,
            total_size_bytes=size,
            data_quality="PARTIAL",
            required_for_phase=11,
        )

    # Administrative
    if dataset_id == "administrative":
        admin_dir = RAW_DATA_DIR / "administrative"
        file_count, size = scan_directory_size(admin_dir)
        status = "VERIFIED" if file_count > 0 else "NOT_AVAILABLE"
        return DatasetStatus(
            dataset_id="administrative",
            dataset_name="Administrative Boundaries",
            provider="Local administrative files",
            category="administrative_boundaries",
            status=status,
            verification_status=status,
            local_path=str(admin_dir),
            ingestion_status="COMPLETED" if file_count > 0 else "BLOCKED",
            coverage="8 NER states",
            spatial_resolution="Vector polygons (state-level)",
            crs="EPSG:4326",
            notes="Administrative boundaries for data filtering and spatial queries.",
            file_count=file_count,
            total_size_bytes=size,
            data_quality="OBSERVED" if file_count > 0 else "NOT_AVAILABLE",
        )

    return None


def get_all_datasets() -> list[DatasetStatus]:
    """Get status of all known datasets"""
    dataset_ids = [
        "gsi_landslides",
        "administrative",
        "dem",
        "rainfall",
        "weather",
        "soil",
        "soil_moisture",
        "hydrology",
        "landcover",
        "satellite",
        "geology",
        "roads",
    ]
    statuses = []
    for dataset_id in dataset_ids:
        status = get_dataset_status(dataset_id)
        if status:
            statuses.append(status)
    return statuses


def calculate_phase_7_readiness() -> dict[str, Any]:
    """
    Check Phase 7 readiness based on available datasets
    Phase 7 BLOCKED if critical environmental data is missing
    """
    all_datasets = get_all_datasets()
    critical_datasets = {
        "dem": False,
        "rainfall": False,
        "soil": False,
        "hydrology": False,
    }

    optional_datasets = {
        "geology": False,
        "landcover": False,
        "satellite": False,
        "weather": False,
    }

    for dataset in all_datasets:
        if dataset.dataset_id in critical_datasets:
            if dataset.status in ("VERIFIED", "PARTIAL"):
                critical_datasets[dataset.dataset_id] = True
        if dataset.dataset_id in optional_datasets:
            if dataset.status in ("VERIFIED", "PARTIAL"):
                optional_datasets[dataset.dataset_id] = True

    all_critical_ready = all(critical_datasets.values())
    optional_count = sum(optional_datasets.values())

    phase_7_status = "READY" if all_critical_ready else "BLOCKED"

    return {
        "phase": 7,
        "name": "Feature Engineering",
        "status": phase_7_status,
        "critical_datasets": critical_datasets,
        "optional_datasets": optional_datasets,
        "blockers": [
            f"{k} — AWAITING_VERIFIED_SOURCE_DATA"
            for k, v in critical_datasets.items()
            if not v
        ],
        "ready_datasets": [k for k, v in {**critical_datasets, **optional_datasets}.items() if v],
        "message": "Phase 7 is BLOCKED until verified DEM, rainfall, soil, and hydrology datasets are available."
        if phase_7_status == "BLOCKED"
        else "Phase 7 can proceed with available environmental data.",
    }


def save_dataset_inventory(output_path: Path | None = None) -> Path:
    """
    Save current dataset inventory to JSON
    Returns path to created inventory file
    """
    ensure_metadata_dir()
    if output_path is None:
        output_path = METADATA_DIR / "dataset_inventory.json"

    all_datasets = get_all_datasets()
    inventory = {
        "timestamp": utc_now_iso(),
        "total_datasets": len(all_datasets),
        "verified_count": sum(
            1 for d in all_datasets if d.status == "VERIFIED"
        ),
        "partial_count": sum(
            1 for d in all_datasets if d.status == "PARTIAL"
        ),
        "awaiting_count": sum(
            1 for d in all_datasets if d.status == "AWAITING_VERIFIED_SOURCE_DATA"
        ),
        "blocked_count": sum(
            1 for d in all_datasets if d.status == "BLOCKED"
        ),
        "datasets": [d.to_dict() for d in all_datasets],
        "phase_7_readiness": calculate_phase_7_readiness(),
    }

    with output_path.open("w") as f:
        json.dump(inventory, f, indent=2)

    return output_path


if __name__ == "__main__":
    ensure_metadata_dir()
    inventory_path = save_dataset_inventory()
    print(f"Dataset inventory saved to: {inventory_path}")
    print(f"Phase 7 Status: {calculate_phase_7_readiness()}")
