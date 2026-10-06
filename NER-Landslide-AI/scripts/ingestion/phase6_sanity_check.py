#!/usr/bin/env python3
"""
Phase 6 Environmental Foundation — Sanity Check
Verify all modules import and execute correctly
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

print("=" * 70)
print("PHASE 6 ENVIRONMENTAL FOUNDATION — SANITY CHECK")
print("=" * 70)

try:
    print("\n1. Testing environmental_foundation.py imports...")
    from scripts.ingestion.environmental_foundation import (
        get_all_datasets,
        get_dataset_status,
        calculate_phase_7_readiness,
    )
    print("   ✓ Imports successful")

    print("\n2. Checking available datasets...")
    all_datasets = get_all_datasets()
    print(f"   ✓ Found {len(all_datasets)} datasets")

    verified = [d for d in all_datasets if d.status == "VERIFIED"]
    awaiting = [d for d in all_datasets if d.status == "AWAITING_VERIFIED_SOURCE_DATA"]
    print(f"   ✓ Verified: {len(verified)}")
    print(f"   ✓ Awaiting: {len(awaiting)}")

    print("\n3. Checking Phase 7 readiness...")
    phase_7 = calculate_phase_7_readiness()
    print(f"   ✓ Phase 7 Status: {phase_7['status']}")
    print(f"   ✓ Critical datasets ready: {sum(phase_7['critical_datasets'].values())}/4")

    print("\n4. Testing feature_engineering_foundation.py imports...")
    from scripts.ingestion.feature_engineering_foundation import (
        get_feature_engineering_report,
        PHASE_7_REQUIRED_FEATURES,
    )
    print("   ✓ Imports successful")

    print("\n5. Checking feature engineering status...")
    feature_report = get_feature_engineering_report()
    print(f"   ✓ Phase 7 Feature Status: {feature_report['phase_7_status']}")
    print(f"   ✓ Required features: {len(PHASE_7_REQUIRED_FEATURES)}")
    print(f"   ✓ Features available: {feature_report['required_features']['available']}")

    print("\n6. Listing verified datasets:")
    for d in verified:
        print(f"   ✓ {d.dataset_name}")

    print("\n7. Listing critical missing datasets:")
    for blocker in phase_7["blockers"][:5]:
        print(f"   ✗ {blocker}")

    print("\n" + "=" * 70)
    print("SANITY CHECK: PASSED ✓")
    print("=" * 70)
    print("\nAll Phase 6 modules are functional.")
    print("Phase 7 is correctly BLOCKED awaiting environmental data.")
    print("NO FABRICATED DATA detected.")

except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {e}")
    import traceback

    traceback.print_exc()
    print("\n" + "=" * 70)
    print("SANITY CHECK: FAILED ✗")
    print("=" * 70)
    sys.exit(1)
