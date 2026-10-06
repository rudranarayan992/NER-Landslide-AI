#!/usr/bin/env python3
"""
Integration Tests for GIS Application
Verifies all components work correctly
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_gsi_landslides_loading():
    """Test: GSI landslide data loads correctly"""
    try:
        from scripts.ingestion.gsi_ingest import ingest_gsi_landslides
        
        result = ingest_gsi_landslides()
        assert result is not None, "GSI ingest returned None"
        
        rows = result.get("rows", [])
        assert len(rows) > 0, f"No GSI rows returned, got: {len(rows)}"
        
        # Check record structure
        first_record = rows[0]
        assert "geometry" in first_record, "Missing geometry in record"
        
        print(f"✓ GSI Landslides: {len(rows)} records loaded")
        return True, len(rows)
        
    except Exception as e:
        print(f"✗ GSI Landslides failed: {str(e)}")
        return False, str(e)


def test_villages_loading():
    """Test: LGD villages load correctly"""
    try:
        from scripts.ingestion.lgd_villages_ingest import ingest_lgd_villages
        
        result = ingest_lgd_villages()
        assert result is not None, "Village ingest returned None"
        
        rows = result.get("rows", [])
        print(f"✓ LGD Villages: {len(rows)} records loaded")
        return True, len(rows)
        
    except Exception as e:
        print(f"✗ LGD Villages failed: {str(e)}")
        return False, str(e)


def test_roads_loading():
    """Test: Road network loads correctly"""
    try:
        from scripts.ingestion.roads_ingest import ingest_roads
        
        result = ingest_roads()
        assert result is not None, "Roads ingest returned None"
        
        rows = result.get("rows", [])
        print(f"✓ Roads: {len(rows)} records loaded")
        return True, len(rows)
        
    except Exception as e:
        print(f"✗ Roads failed: {str(e)}")
        return False, str(e)


def test_administrative_loading():
    """Test: Administrative boundaries load"""
    try:
        from scripts.ingestion.administrative_ingest import ingest_administrative_boundaries
        
        result = ingest_administrative_boundaries()
        assert result is not None, "Admin ingest returned None"
        
        rows = result.get("rows", [])
        print(f"✓ Administrative: {len(rows)} records loaded")
        return True, len(rows)
        
    except Exception as e:
        print(f"✗ Administrative failed: {str(e)}")
        return False, str(e)


def test_environmental_foundation():
    """Test: Environmental foundation provides dataset status"""
    try:
        from scripts.ingestion.environmental_foundation import get_all_datasets
        
        datasets = get_all_datasets()
        assert len(datasets) > 0, "No datasets returned"
        
        # Check dataset structure
        for ds in datasets:
            assert hasattr(ds, 'name'), "Dataset missing name"
            assert hasattr(ds, 'status'), "Dataset missing status"
        
        verified = sum(1 for d in datasets if d.status == "VERIFIED")
        awaiting = sum(1 for d in datasets if d.status == "AWAITING_VERIFIED_SOURCE_DATA")
        blocked = sum(1 for d in datasets if d.status == "BLOCKED")
        
        print(f"✓ Environmental Foundation: {len(datasets)} datasets")
        print(f"  ├─ Verified: {verified}")
        print(f"  ├─ Awaiting: {awaiting}")
        print(f"  └─ Blocked: {blocked}")
        return True, len(datasets)
        
    except Exception as e:
        print(f"✗ Environmental Foundation failed: {str(e)}")
        return False, str(e)


def test_feature_engineering_report():
    """Test: Feature engineering schema available"""
    try:
        from scripts.ingestion.feature_engineering_foundation import get_feature_engineering_report
        
        report = get_feature_engineering_report()
        assert report is not None, "Report returned None"
        
        required = report.get("required_features", [])
        optional = report.get("optional_features", [])
        status = report.get("phase_7_status")
        
        print(f"✓ Feature Engineering Report:")
        print(f"  ├─ Required features: {len(required)}")
        print(f"  ├─ Optional features: {len(optional)}")
        print(f"  └─ Phase 7 status: {status}")
        return True, report
        
    except Exception as e:
        print(f"✗ Feature Engineering Report failed: {str(e)}")
        return False, str(e)


def test_ner_states_config():
    """Test: NER states are configured"""
    try:
        from backend.app.config import NER_STATES
        
        assert len(NER_STATES) == 8, f"Expected 8 NER states, got {len(NER_STATES)}"
        
        expected = {'Assam', 'Meghalaya', 'Manipur', 'Mizoram', 
                   'Nagaland', 'Sikkim', 'Tripura', 'Arunachal Pradesh'}
        actual = set(NER_STATES)
        
        assert actual == expected, f"States mismatch. Got: {actual}"
        
        print(f"✓ NER States configured: {', '.join(sorted(NER_STATES))}")
        return True, NER_STATES
        
    except Exception as e:
        print(f"✗ NER States config failed: {str(e)}")
        return False, str(e)


def test_component_files_exist():
    """Test: All GIS components exist"""
    components = [
        "frontend/src/components/GISMap.tsx",
        "frontend/src/components/LayerPanel.tsx",
        "frontend/src/components/InfoPanel.tsx",
        "frontend/src/components/MapControls.tsx",
        "frontend/src/components/SearchBox.tsx",
        "frontend/src/components/Legend.tsx",
    ]
    
    all_exist = True
    for comp in components:
        path = project_root / comp
        exists = path.exists()
        status = "✓" if exists else "✗"
        size = path.stat().st_size if exists else 0
        print(f"  {status} {comp} ({size} bytes)")
        all_exist = all_exist and exists
    
    if all_exist:
        print(f"✓ All GIS components present")
        return True, components
    else:
        print(f"✗ Some components missing")
        return False, components


def test_api_endpoints_defined():
    """Test: All required API endpoints defined"""
    try:
        main_py = project_root / "backend/app/main.py"
        assert main_py.exists(), "main.py not found"
        
        content = main_py.read_text()
        
        endpoints = [
            "/api/landslides",
            "/api/villages",
            "/api/roads",
            "/api/layers",
            "/api/search",
            "/api/environmental-datasets",
            "/api/phase-7-readiness",
        ]
        
        missing = []
        for ep in endpoints:
            if ep not in content:
                missing.append(ep)
                print(f"  ✗ {ep}")
            else:
                print(f"  ✓ {ep}")
        
        if not missing:
            print(f"✓ All API endpoints defined")
            return True, endpoints
        else:
            print(f"✗ Missing endpoints: {missing}")
            return False, missing
            
    except Exception as e:
        print(f"✗ API endpoints check failed: {str(e)}")
        return False, str(e)


def test_maplibre_gl_installed():
    """Test: MapLibre GL is in dependencies"""
    try:
        package_json = project_root / "frontend/package.json"
        assert package_json.exists(), "package.json not found"
        
        content = json.loads(package_json.read_text())
        deps = content.get("dependencies", {})
        
        has_maplibre = "maplibre-gl" in deps
        version = deps.get("maplibre-gl", "NOT FOUND")
        
        if has_maplibre:
            print(f"✓ MapLibre GL {version} in dependencies")
            return True, version
        else:
            print(f"✗ MapLibre GL not found in dependencies")
            return False, "Not installed"
            
    except Exception as e:
        print(f"✗ MapLibre check failed: {str(e)}")
        return False, str(e)


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("  NER Landslide AI - Integration Test Suite")
    print("="*60 + "\n")
    
    tests = [
        ("GIS Components", test_component_files_exist),
        ("MapLibre GL", test_maplibre_gl_installed),
        ("API Endpoints", test_api_endpoints_defined),
        ("NER States Config", test_ner_states_config),
        ("GSI Landslides", test_gsi_landslides_loading),
        ("LGD Villages", test_villages_loading),
        ("Roads", test_roads_loading),
        ("Administrative", test_administrative_loading),
        ("Environmental Foundation", test_environmental_foundation),
        ("Feature Engineering", test_feature_engineering_report),
    ]
    
    print("\nRunning tests:\n")
    results = []
    
    for name, test_func in tests:
        print(f"\n[{name}]")
        success, data = test_func()
        results.append((name, success, data))
    
    # Summary
    print("\n" + "="*60)
    print("  TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for name, success, data in results:
        status = "PASS" if success else "FAIL"
        print(f"  [{status}] {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED - Application ready")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed - Check errors above")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
