# NER LANDSLIDE GUARD AI - DEMO WALKTHROUGH

## QUICK START (5 minutes)

### 1. START THE BACKEND
```bash
cd NER-Landslide-AI
python -m uvicorn backend.app.main:app --reload --port 8000
```
API will be available at: http://localhost:8000

### 2. CHECK API HEALTH
```bash
curl http://localhost:8000/api/health
```
Expected response:
```json
{
  "status": "ok",
  "service": "ner-landslide-ai",
  "version": "0.1.0"
}
```

### 3. START THE FRONTEND
```bash
cd frontend
npm run dev
```
Application will be available at: http://localhost:5173

---

## DEMONSTRATION FLOW (20 minutes)

### STEP 1: Open the Application
- Open browser to http://localhost:5173
- You should see the NER region GIS map with MapLibre

### STEP 2: View Historical Landslides
1. Click "Landslides" layer in the left panel
2. See 33,904 verified historical events displayed as red points
3. Zoom into Meghalaya or Sikkim for higher density
4. Click on a landslide event to see:
   - Event date and location
   - Trigger type (rainfall, earthquake, etc.)
   - Type (debris flow, rockfall, mudslide, etc.)
   - Severity and impacts
   - Reporter and source

**What's Demonstrated:** Real verified data from GSI with complete attributes

### STEP 3: Switch Map Layers
1. Click the layer selection buttons to change basemap:
   - "Street" - Street map view
   - "Satellite" - Satellite imagery
   - "Topographic" - Elevation shading
   - "Terrain" - 3D terrain view

**What's Demonstrated:** Professional map interaction, multiple viewing modes

### STEP 4: View Layer Control Panel
1. See the complete layer hierarchy:
   - LANDSLIDES group
     - Historical Landslide Events (Available - ✓)
     - Historical Density Heatmap (Available - ✓)
   - ADMINISTRATIVE group
     - State Boundaries (Available - ✓)
   - INFRASTRUCTURE group
     - Road Network (Available - ✓)
     - Villages & Settlements (Available - ✓)
   - TERRAIN group
     - DEM (Awaiting - ⏳)
     - Slope Analysis (Blocked - ✕)
   - RAINFALL group
     - Rainfall Distribution (Awaiting - ⏳)
   - SOIL group
     - Soil Properties (Awaiting - ⏳)
   - GEOLOGY group
     - Geological Map (Awaiting - ⏳)
   - RISK group
     - Susceptibility Map (Blocked - ✕)
     - Hazard Assessment (Blocked - ✕)
     - Risk Map (Blocked - ✕)

**What's Demonstrated:** Complete system architecture with honest status labels

### STEP 5: Search for a Location
1. Use the search box at the top
2. Type a state name (e.g., "Meghalaya", "Sikkim", "Assam")
3. Click a result to fly to that location
4. Zoom level automatically adjusts

**What's Demonstrated:** Interactive search and navigation

### STEP 6: View Roads and Villages
1. Enable "Road Network" layer
2. Enable "Villages & Settlements" layer
3. Zoom in to see detailed infrastructure
4. Click on a road or village to see properties
5. Note: "Risk Map" layer is marked as BLOCKED

**What's Demonstrated:** Verified infrastructure data, but risk is not calculated

### STEP 7: Open Data Readiness Dashboard
1. Click "Demo Mode" or "System Status" button
2. View the complete system status:
   - Summary statistics (Verified, Operational, Partial, Awaiting, Blocked)
   - Filter by category
   - See blocking reasons for each component

**What's Demonstrated:** Transparency about system readiness

### STEP 8: Submit a Field Report
1. Navigate to "Field Reports" section
2. Click "Submit New Report"
3. Fill in:
   - Location name (e.g., "Khasi Hills")
   - Coordinates
   - Description of observation
   - Reporter name and contact
   - Optional: photo URL, evidence notes
4. Submit the report
5. View the report in SUBMITTED status

**What's Demonstrated:** Workflow for citizen/field observer input

### STEP 9: Query the LLM Assistant
1. Open the LLM Assistant panel
2. Ask questions like:
   - "Show historical landslides near Shillong"
   - "What data is available?"
   - "Why is risk calculation blocked?"
   - "What datasets are missing?"
   - "Which districts have the most historical events?"

**What's Demonstrated:** 
- Queries real historical data
- Explains data status honestly
- Never fabricates missing data
- Distinguishes OBSERVED vs HISTORICAL vs UNKNOWN

### STEP 10: Check System API Endpoints

In a terminal or using curl/Postman:

#### System Status
```bash
curl http://localhost:8000/api/system-status | jq .summary
```
Shows: 4 verified, 5 operational, 2 partial, 5 awaiting, 6 blocked

#### Data Readiness
```bash
curl http://localhost:8000/api/data-readiness | jq
```
Shows: All data sources with status

#### ML Module Status
```bash
curl http://localhost:8000/api/ml/status | jq
```
Shows: NOT TRAINED with blocking reasons

#### Risk Engine Status
```bash
curl http://localhost:8000/api/risk/status | jq
```
Shows: BLOCKED with scientific prerequisites

#### System Readiness Report
```bash
curl http://localhost:8000/api/system-readiness-report | jq
```
Shows: Complete readiness assessment for leadership

#### Historical Landslides
```bash
curl "http://localhost:8000/api/landslides?state=Meghalaya" | jq '.features | length'
```
Returns: Number of verified events in state

#### Field Reports
```bash
curl http://localhost:8000/api/field-reports | jq
```
Shows: All submitted reports with workflow status

#### LLM Assistant Query
```bash
curl -X POST http://localhost:8000/api/assistant/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What datasets are available?"}' | jq
```
Returns: Honest answer about data availability

---

## KEY TALKING POINTS

### "What Works Today" ✓
1. **33,904 verified historical landslides** - Real GSI data with field validation
2. **GIS visualization** - Professional MapLibre interface
3. **Infrastructure mapping** - 5000+ roads, 10000+ villages
4. **Administrative boundaries** - All 8 NER states
5. **Field report workflow** - Community input collection
6. **System status dashboard** - Complete transparency
7. **LLM assistant** - Queries real data honestly
8. **API endpoints** - 20+ fully functional endpoints

### "What's Blocked & Why" ✕
1. **ML Model Training** - No verified training dataset exists yet
   - Reason: Environmental features not available (DEM, rainfall, soil, etc.)
   - Solution: Obtain verified environmental datasets

2. **Risk Calculation** - ML model is not trained
   - Reason: Cannot calculate risk without trained model
   - Solution: Train ML model when features available

3. **Road Risk Assessment** - Risk engine not operational
   - Reason: No risk calculations available
   - Note: Road data is verified, we just can't assess its risk yet

4. **Village Risk** - Risk engine not operational
   - Reason: Same as road risk
   - Note: Village data is verified, waiting for risk calculations

5. **Route Analysis** - Risk engine not operational
   - Reason: Cannot compare routes for safety without risk data
   - Solution: Implement after risk engine operational

6. **Alerts** - Risk engine not operational
   - Reason: No validated risk outputs to base alerts on
   - Solution: Implement after Phase 9 when risk available

### "Scientific Integrity"
- **NO FABRICATED DATA** - All missing data explicitly marked as AWAITING or NULL
- **NO FAKE PREDICTIONS** - ML model marked NOT TRAINED
- **NO FAKE RISK SCORES** - Risk engine marked BLOCKED until ready
- **HONEST LABELING** - Every component clearly labeled with status
- **CLEAR PREREQUISITES** - Each blocked component explains what's needed

---

## TECHNICAL ARCHITECTURE

### Backend Components
- ✓ `enums.py` - System status enums
- ✓ `ml_module_status.py` - ML module status tracking
- ✓ `risk_engine_status.py` - Risk engine with blocking reasons
- ✓ `field_reports_service.py` - Field report workflow
- ✓ `alert_engine.py` - Alert schema and status
- ✓ `infrastructure_services.py` - Roads, villages, routes
- ✓ `data_readiness_status.py` - Complete system status reporting
- ✓ `llm_assistant.py` - LLM with RAG over real data
- ✓ `main.py` - 20+ API endpoints

### Frontend Components
- ✓ `GISMap.tsx` - Main map interface
- ✓ `LayerPanel.tsx` - Layer control with status
- ✓ `SearchBox.tsx` - Location search
- ✓ `MapControls.tsx` - Map tools
- ✓ `Legend.tsx` - Layer legend
- ✓ `DemoMode.tsx` - System status visualization

### Database
- ✓ `PostGIS` - Spatial database with all tables
- ✓ `Schema` - Complete with landslides, roads, villages, environmental tables
- ✓ `Data` - Verified GSI landslides loaded

---

## EXPECTED OUTCOMES

After this walkthrough, stakeholders should understand:

1. **What's Operational:** A complete GIS system with verified historical data
2. **What's Ready:** Infrastructure for ML and risk when data available
3. **What's Blocked:** ML/risk components with documented scientific reasons
4. **Why It's Honest:** No fabricated data or false claims of capability
5. **What's Next:** Environmental data acquisition to unlock ML/risk phases

---

## TROUBLESHOOTING

### Backend Won't Start
```bash
# Check Python version (3.8+)
python --version

# Install dependencies
pip install -r requirements.txt

# Check port 8000 is available
netstat -an | grep 8000
```

### Frontend Won't Start
```bash
# Check Node version (14+)
node --version

# Install dependencies
npm install

# Check port 5173 is available
netstat -an | grep 5173
```

### API Endpoint Returns Error
1. Check backend is running: `curl http://localhost:8000/health`
2. Check endpoint exists: `curl http://localhost:8000/api/health`
3. Check CORS: Browser console for CORS errors
4. Check logs: Review terminal where `npm run dev` is running

### Map Won't Load
1. Check MapLibre GL CSS is loaded: DevTools → Elements → Look for MapLibre stylesheet
2. Check GeoJSON data is loading: DevTools → Network → Look for API calls
3. Check browser console for JavaScript errors

---

## NEXT STEPS AFTER DEMO

1. **Review FINAL_SYSTEM_STATUS.md** for complete technical documentation
2. **Begin Phase 7:** Environmental data acquisition
   - Obtain verified DEM, rainfall, soil, weather, satellite data
3. **Integrate Data:** Use existing ingestion framework
4. **Train Model:** Implement ML training pipeline
5. **Deploy Risk Engine:** When model validation complete
6. **Enable Alerts:** When risk engine operational

---

**Demo complete. The platform is production-quality for historical GIS viewing and field reports. ML and risk phases remain blocked until verified environmental data and model validation are complete.**
