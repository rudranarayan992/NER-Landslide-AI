#!/usr/bin/env python3
"""
Data Manifest Generator
Scans data directories and generates machine-readable manifest
Shows what data exists and what is missing
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

from scripts.ingestion.environmental_foundation import (
    get_all_datasets,
    get_dataset_status,
    save_dataset_inventory,
    METADATA_DIR,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"


def generate_data_manifest() -> dict:
    """Generate comprehensive data manifest"""
    ensure_manifest_dir()

    all_datasets = get_all_datasets()

    manifest = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project": "NER Landslide AI",
        "phase": 6,
        "description": "Environmental Data Foundation - Real Dataset Manifest",
        "scientific_note": "NO FABRICATED DATA. Only datasets actually present in repository are listed.",
        "summary": {
            "total_datasets": len(all_datasets),
            "verified": sum(1 for d in all_datasets if d.status == "VERIFIED"),
            "partial": sum(1 for d in all_datasets if d.status == "PARTIAL"),
            "awaiting": sum(1 for d in all_datasets if d.status == "AWAITING_VERIFIED_SOURCE_DATA"),
            "blocked": sum(1 for d in all_datasets if d.status == "BLOCKED"),
        },
        "datasets": {},
        "phase_7_blockers": [],
    }

    # Organize by category
    by_category = {}
    for dataset in all_datasets:
        if dataset.category not in by_category:
            by_category[dataset.category] = []
        by_category[dataset.category].append(dataset)

    for category, datasets in sorted(by_category.items()):
        manifest["datasets"][category] = [
            {
                "dataset_id": d.dataset_id,
                "dataset_name": d.dataset_name,
                "provider": d.provider,
                "status": d.status,
                "verification_status": d.verification_status,
                "local_path": d.local_path,
                "file_count": d.file_count,
                "total_size_bytes": d.total_size_bytes,
                "total_size_mb": round(d.total_size_bytes / 1024 / 1024, 2) if d.total_size_bytes > 0 else 0,
                "coverage": d.coverage,
                "spatial_resolution": d.spatial_resolution,
                "crs": d.crs,
                "data_quality": d.data_quality,
                "ingestion_status": d.ingestion_status,
                "required_for_phase": d.required_for_phase,
                "notes": d.notes,
            }
            for d in datasets
        ]

        # Add Phase 7 blockers
        for dataset in datasets:
            if (
                dataset.status == "AWAITING_VERIFIED_SOURCE_DATA"
                and dataset.required_for_phase == 7
            ):
                manifest["phase_7_blockers"].append(
                    f"{dataset.dataset_name} ({dataset.dataset_id}) — required for Phase 7"
                )

    return manifest


def ensure_manifest_dir() -> None:
    """Create manifest directory"""
    METADATA_DIR.mkdir(parents=True, exist_ok=True)


def save_manifest(manifest: dict) -> Path:
    """Save manifest to JSON file"""
    ensure_manifest_dir()
    manifest_path = METADATA_DIR / "data_manifest.json"

    with manifest_path.open("w") as f:
        json.dump(manifest, f, indent=2)

    return manifest_path


def print_manifest_summary(manifest: dict) -> None:
    """Print human-readable manifest summary"""
    print("\n" + "=" * 70)
    print("DATA MANIFEST — NER LANDSLIDE AI")
    print("=" * 70)

    summary = manifest["summary"]
    print(
        f"\nTotal Datasets: {summary['total_datasets']}\n"
        f"  Verified:   {summary['verified']}\n"
        f"  Partial:    {summary['partial']}\n"
        f"  Awaiting:   {summary['awaiting']}\n"
        f"  Blocked:    {summary['blocked']}\n"
    )

    print("DATASETS BY CATEGORY:")
    print("-" * 70)

    for category, datasets in sorted(manifest["datasets"].items()):
        print(f"\n{category.upper().replace('_', ' ')} ({len(datasets)} dataset{'s' if len(datasets) != 1 else ''}):")
        for dataset in datasets:
            status_icon = {
                "VERIFIED": "✓",
                "PARTIAL": "◐",
                "AWAITING_VERIFIED_SOURCE_DATA": "✗",
                "BLOCKED": "⊘",
                "NOT_AVAILABLE": "✗",
            }.get(dataset["status"], "?")

            size_str = (
                f"{dataset['total_size_mb']} MB"
                if dataset["total_size_bytes"] > 0
                else "(empty)"
            )

            print(
                f"  {status_icon} {dataset['dataset_name']:<40} "
                f"[{dataset['provider'][:20]}...] "
                f"{size_str}"
            )

    if manifest["phase_7_blockers"]:
        print("\n" + "-" * 70)
        print("PHASE 7 BLOCKERS (Critical Missing Data):")
        for blocker in manifest["phase_7_blockers"]:
            print(f"  ✗ {blocker}")

    print("\n" + "=" * 70)
    print("Scientific Integrity Note: NO FABRICATED DATA")
    print("Datasets marked 'AWAITING_VERIFIED_SOURCE_DATA' do NOT exist in repository")
    print("=" * 70 + "\n")


def main():
    """Generate and display manifest"""
    print("Generating data manifest...")
    manifest = generate_data_manifest()

    # Save manifest
    manifest_path = save_manifest(manifest)
    print(f"Manifest saved to: {manifest_path}")

    # Also save inventory
    inventory_path = save_dataset_inventory()
    print(f"Inventory saved to: {inventory_path}")

    # Print summary
    print_manifest_summary(manifest)

    return manifest_path


if __name__ == "__main__":
    main()
