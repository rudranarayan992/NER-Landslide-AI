# Quick Start Guide - NER Landslide AI GIS

## 🚀 Start Application (2 terminals)

### Terminal 1: Backend
```bash
cd c:\Users\rudra\Desktop\hackthon-2026\NER-Landslide-AI\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
✓ Runs on http://localhost:8000
✓ API docs at http://localhost:8000/docs

### Terminal 2: Frontend
```bash
cd c:\Users\rudra\Desktop\hackthon-2026\NER-Landslide-AI\frontend
npm run dev
```
✓ Opens http://localhost:5173 automatically

## 📊 What You See

### On Map Load
- **Historical Landslide Events:** 33,904 verified GSI points
- **Clustered display** for performance
- **State boundaries** showing NER region
- **Basemap selector** (top right)

### Left Panel - Layer Control
```
✓ AVAILABLE (ready to view):
  - Historical Landslide Events (33,904)
  - Historical Density Heatmap
  - State Boundaries
  - Road Network
  - Villages

⏳ AWAITING DATA (in progress):
  - Digital Elevation Model (DEM)
  - Rainfall Distribution
  - Soil Properties
  - Geological Map
  - Water Bodies

🔒 BLOCKED (waiting for Phase 7+):
  - Slope Analysis
  - Hazard Assessment
  - Risk Maps
  - Current Risk Alerts
```

### Right Panel - Feature Info
- Click any map feature
- See coordinates, properties
- View data source & verification status

## 🎮 Map Controls

| Button | Action |
|--------|--------|
| `+` | Zoom in |
| `−` | Zoom out |
| `⌂` | Reset to NER region |
| `📍` | Go to your location |
| `📏` | Measure distance/area |
| `⛶` | Fullscreen mode |

## 🔍 Search Bar (Top)

Type to search:
- State name: "Assam", "Meghalaya", "Manipur", etc.
- Village name: "Cherrapunji", "Itanagar", etc.
- Auto-flyTo on result click

## 📍 Key Features

### Historical Density Layer
- Shows spatial clustering of past events
- Red = high historical density
- Yellow = low historical density
- **NOT current risk** (clearly labeled)

### Feature Inspector
Click any feature to see:
```
Landslide Event:
  - Event ID
  - Date occurred
  - State/District
  - Type of movement
  - Trigger (rainfall/earthquake/construction)
  - Data source (GSI)

Village:
  - Village name
  - Population
  - Coordinates
  - District

State:
  - State name
  - Boundaries
  - Administrative info
```

## 📈 Data Status

### Phase 1-6: ✓ COMPLETE
- Historical data ingested
- Environmental foundation created
- Feature schema defined
- Backend APIs operational

### Phase 7: 🔒 BLOCKED
**Requires:** Verified DEM, rainfall, soil, hydrology data

### Phase 8+: 🔒 BLOCKED
**Requires:** Phase 7 completion + ML training data

## 🔗 API Endpoints

```bash
# Get historical landslides (GeoJSON)
curl http://localhost:8000/api/landslides

# Search locations
curl "http://localhost:8000/api/search?q=Assam"

# Get layer status
curl http://localhost:8000/api/layers

# Phase 7 readiness check
curl http://localhost:8000/api/phase-7-readiness

# Environmental datasets
curl http://localhost:8000/api/environmental-datasets
```

## ⚠️ Important Notes

1. **Historical ≠ Risk**
   - Heatmap shows WHERE events happened (past)
   - NOT WHERE they will happen (future)
   - Risk assessment blocked until Phase 7 complete

2. **No Fabricated Data**
   - All coordinates from real GSI database
   - No synthetic values or predictions
   - Blocked layers show reason (transparent)

3. **Why Things Are Blocked**
   - DEM needed for slope/aspect/curvature
   - Rainfall needed for trigger modeling
   - Soil data needed for susceptibility
   - ML model needed for risk calculation

## 🛠️ Troubleshooting

### Map Won't Load
- ✓ Ensure backend running (http://localhost:8000/health)
- ✓ Check browser console for errors
- ✓ Try clearing cache (Ctrl+Shift+Delete)

### Data Not Showing
- ✓ Check /api/landslides returns data
- ✓ Verify layer is enabled (left panel)
- ✓ Check zoom level (zoom in if needed)

### Search Not Working
- ✓ Verify backend API is running
- ✓ Check network tab in browser DevTools
- ✓ Try simpler search (full state name)

### Performance Issues
- ✓ Zoom in to reduce point density
- ✓ Disable heatmap if slow
- ✓ Check browser tab memory usage

## 📱 Browser Support

- Chrome 90+ ✓
- Firefox 88+ ✓
- Safari 14+ ✓
- Edge 90+ ✓

## 🎯 Verification Checklist

```
After starting both terminals:

☐ Backend responds: curl http://localhost:8000/health
☐ Frontend loads: http://localhost:5173
☐ Map visible with base layer
☐ 33,904 landslide points display as clusters
☐ Can zoom in to see individual points
☐ Historical Density heatmap works
☐ Layer panel shows all groups
☐ Feature click shows info panel
☐ Search box responds
☐ Basemap selector works
```

## 📊 Data Files Location

```
data/
├── raw/
│   ├── landslides/          # GSI historical data
│   ├── administrative/       # State/district boundaries
│   ├── villages/             # LGD village data
│   └── roads/                # Road network
├── processed/                # Ingested data caches
└── training/                 # (empty - Phase 7 blocker)

backend/app/
├── main.py                  # FastAPI endpoints
└── models.py                # PostGIS database schema
```

## 🚦 Next Actions

### To View Historical Data
1. Start both terminals (backend + frontend)
2. Open http://localhost:5173
3. Map loads with 33,904 events
4. Use layers panel to toggle visibility
5. Click features to inspect

### To Enable Phase 7
1. Obtain verified environmental data (DEM, rainfall, soil)
2. Ingest using `scripts/ingestion/`
3. Run `verify_gis_deployment.py`
4. Check `/api/phase-7-readiness`

### To Enable Risk Prediction
1. Complete Phase 7 (feature engineering)
2. Collect training dataset (landslide/non-landslide labels)
3. Train ML model using `ml/training/`
4. Validate performance metrics
5. Deploy Phase 9 risk engine

---

**Status:** ✓ Professional GIS Application Ready
**Data:** ✓ 33,904 Historical Events Available
**Risk Assessment:** 🔒 Blocked (awaiting environmental data)
