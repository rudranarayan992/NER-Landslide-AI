#!/usr/bin/env python3
"""
Phase 7 Readiness Check
Determines if Phase 7 (Feature Engineering) can proceed
Returns BLOCKED if critical environmental datasets are missing
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from scripts.ingestion.environmental_foundation import (
    calculate_phase_7_readiness,
    save_dataset_inventory,
    get_all_datasets,
)
from scripts.ingestion.feature_engineering_foundation import get_feature_engineering_report

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
METADATA_DIR = DATA_DIR / "metadata"


def run_readiness_check() -> dict:
    """
    Comprehensive Phase 7 readiness check
    Returns dictionary with status and details
    """
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    # Get dataset inventory
    all_datasets = get_all_datasets()

    # Check dataset availability
    verified_datasets = [d for d in all_datasets if d.status == "VERIFIED"]
    partial_datasets = [d for d in all_datasets if d.status == "PARTIAL"]
    awaiting_datasets = [d for d in all_datasets if d.status == "AWAITING_VERIFIED_SOURCE_DATA"]
    blocked_datasets = [d for d in all_datasets if d.status == "BLOCKED"]

    # Get Phase 7 readiness from environmental perspective
    phase_7_env_readiness = calculate_phase_7_readiness()

    # Get Phase 7 readiness from feature perspective
    feature_report = get_feature_engineering_report()

    # Determine final Phase 7 status
    phase_7_status = phase_7_env_readiness["status"]
    if feature_report["phase_7_status"] == "BLOCKED":
        phase_7_status = "BLOCKED"

    # Compile blockers
    blockers = []
    blockers.extend(phase_7_env_readiness.get("blockers", []))
    blockers.extend([
        f"Feature '{f['feature_name']}' requires {f['source_dataset']} (unavailable)"
        for f in feature_report["required_features"]["features"]
        if f["availability"] != "AVAILABLE"
    ])

    report = {
        "timestamp": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "phase": 7,
        "name": "Feature Engineering Foundation",
        "overall_status": phase_7_status,
        "dataset_summary": {
            "total_datasets": len(all_datasets),
            "verified": len(verified_datasets),
            "partial": len(partial_datasets),
            "awaiting": len(awaiting_datasets),
            "blocked": len(blocked_datasets),
        },
        "verified_datasets": [d.dataset_id for d in verified_datasets],
        "partial_datasets": [d.dataset_id for d in partial_datasets],
        "awaiting_datasets": [d.dataset_id for d in awaiting_datasets],
        "blockers": blockers,
        "critical_missing": phase_7_env_readiness["blockers"],
        "required_features": {
            "total": feature_report["required_features"]["total"],
            "available": feature_report["required_features"]["available"],
            "missing": feature_report["required_features"]["missing"],
        },
        "optional_features": {
            "total": feature_report["optional_features"]["total"],
            "available": feature_report["optional_features"]["available"],
            "missing": feature_report["optional_features"]["missing"],
        },
        "message": f"Phase 7 {phase_7_status}: {phase_7_env_readiness['message']}",
        "next_steps": [
            "Obtain verified DEM from USGS/SRTM/Copernicus",
            "Obtain rainfall time series from IMD/CHIRPS/NASA MERRA",
            "Obtain soil properties from SoilGrids/ISRIC/Indian Soil Survey",
            "Obtain hydrological network from HydroSHEDS/OSM",
            "Once datasets are verified, update data_sources.yaml and run Phase 6 validation",
            "Then Phase 7 feature engineering can proceed",
        ] if phase_7_status == "BLOCKED" else [
            "Phase 7 feature engineering can proceed with available data",
            "Build training feature matrix from available datasets",
            "Handle missing values according to feature definitions",
            "Create training dataset for Phase 8 ML model training",
        ],
    }

    return report


def main():
    """Run readiness check and save results"""
    print("=" * 60)
    print("PHASE 7 READINESS CHECK")
    print("=" * 60)

    # Save dataset inventory
    print("\nScanning datasets...")
    inventory_path = save_dataset_inventory()
    print(f"Dataset inventory saved to: {inventory_path}")

    # Run readiness check
    print("Running Phase 7 readiness check...")
    report = run_readiness_check()

    # Save report
    report_path = METADATA_DIR / "phase_7_readiness.json"
    with report_path.open("w") as f:
        json.dump(report, f, indent=2)
    print(f"Readiness report saved to: {report_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Overall Status: {report['overall_status']}")
    print(f"\nDatasets:")
    print(f"  Verified:  {report['dataset_summary']['verified']}")
    print(f"  Partial:   {report['dataset_summary']['partial']}")
    print(f"  Awaiting:  {report['dataset_summary']['awaiting']}")
    print(f"\nFeatures:")
    print(f"  Required available: {report['required_features']['available']}/{report['required_features']['total']}")
    print(f"  Optional available: {report['optional_features']['available']}/{report['optional_features']['total']}")

    if report["blockers"]:
        print(f"\nBlockers ({len(report['blockers'])}):")
        for blocker in report["blockers"][:5]:  # Show first 5
            print(f"  - {blocker}")
        if len(report["blockers"]) > 5:
            print(f"  ... and {len(report['blockers']) - 5} more")

    print(f"\nNext Steps:")
    for i, step in enumerate(report["next_steps"][:3], 1):
        print(f"  {i}. {step}")

    print("\n" + "=" * 60)
    print(f"Status: Phase 7 is {report['overall_status']}")
    print("=" * 60)

    # Exit with appropriate code
    sys.exit(0 if report["overall_status"] == "READY" else 1)


if __name__ == "__main__":
    main()
