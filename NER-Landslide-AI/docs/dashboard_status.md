# NER Landslide AI — Complete Project Status Dashboard

## Dashboard Overview

The NER Landslide AI status dashboard is a professional scientific GIS monitoring interface that accurately represents the real state of the partially implemented real-data landslide monitoring foundation.

**Key Principle:** The dashboard displays actual implemented functionality and explicitly marks all unavailable scientific datasets and blocked phases. No fake risk scores, predictions, or environmental values are synthesized or displayed.

---

## What the Dashboard Shows

### 1. System Overview Cards
- **GIS Foundation:** PARTIAL — core infrastructure exists
- **Real Data:** PARTIAL — GSI landslides and administrative data available
- **ML Model:** BLOCKED — no training dataset or validated model exists
- **Current Risk:** BLOCKED — requires validated model + current environmental data
- **Early Warning:** BLOCKED — requires validated risk engine and thresholds

### 2. Main GIS Map
- Central interactive component
- Ready to display real GeoJSON features from the backend
- Placeholder state shows intent; actual data layers render when backend provides it
- No fake heatmaps or synthetic risk visualizations

### 3. Real Data Sections

#### Historical Landslide Inventory (GSI)
- **Status:** AVAILABLE / PARTIAL
- **Source:** Geological Survey of India field-validated inventory
- **Data Format:** Extracted CSV + GeoJSON points
- **Coverage:** Available for NER states (incomplete per state)
- **Verification:** Field-validated entries with location, date, type, trigger information

#### Administrative Data
- **Status:** AVAILABLE / PARTIAL
- **Source:** Local administrative files and boundaries
- **Coverage:** State, district, village boundaries
- **Status:** Existing but not fully versioned

### 4. Data Availability Panel
Comprehensive inventory of all 12 major datasets with honest status:

**Available:**
- GSI Landslides (AVAILABLE / PARTIAL)
- Administrative Data (AVAILABLE / PARTIAL)

**Awaiting Verified Data:**
- DEM / Elevation
- Rainfall
- Weather Station Data
- Soil Moisture
- Hydrology / Drainage
- Satellite Imagery
- Road Network (verified geometry)
- Village Geometry (verified polygons)

**Blocked (Waiting on Prerequisites):**
- ML Training Dataset (needs feature engineering)
- ML Model (needs training data)
- Current Risk Layer (needs model + current data)

### 5. AI/ML Status Panel
Clearly states the hard facts:
- **Feature Engineering:** BLOCKED
- **Training Dataset:** 0 VERIFIED ROWS
- **Model Status:** NOT TRAINED
- **Validation:** NOT AVAILABLE
- **Calibration:** NOT AVAILABLE
- **Alerts:** NO VALIDATED ALERTS

Explanation: "ML pipeline is blocked until verified terrain, rainfall, environmental, and training data are available."

### 6. Risk Engine Status
- **Susceptibility:** NOT AVAILABLE
- **Current Dynamic Risk:** NOT AVAILABLE
- **Calibration:** NOT AVAILABLE
- **Alerts:** NO VALIDATED ALERTS

Message: "Validated risk predictions will appear after verified environmental data and a validated ML model are available."

### 7. NER State Coverage
Lists all 8 NER states with honest status for each:
- Arunachal Pradesh: Phases 1–6 Partial / Phases 7+ Blocked
- Assam: Phases 1–6 Partial / Phases 7+ Blocked
- (etc. for all 8 states)

### 8. Project Phases Panel
15-phase roadmap showing actual status:
- Phases 1–6: PARTIAL (foundation exists, data incomplete)
- Phase 6: PARTIAL / IN PROGRESS (environmental framework, awaiting real data)
- Phases 7–15: BLOCKED (prerequisites not satisfied)

Color coding:
- **Emerald:** PARTIAL / IN PROGRESS (foundation work ongoing)
- **Yellow:** IN PROGRESS (active development)
- **Red:** BLOCKED (dependencies not available)

### 9. Data Provenance & Versioning
For each major dataset shows:
- Name
- Source
- Version (when unavailable, explicitly states "Not yet versioned")
- Status

Examples:
- GSI Landslide Inventory: Source = Geological Survey of India | Version = Not yet versioned | Status = AVAILABLE / PARTIAL
- Training Dataset: Source = Pending | Version = N/A | Status = BLOCKED

### 10. About This Project Section
Honest communication of the project's actual state:
- What exists (real data sources and GIS foundation)
- What is blocked (ML, risk modeling, current risk, routing, alerts, field reports)
- Why (missing verified environmental data sources)
- Commitment to scientific integrity (no fake data)

---

## Frontend Components

### `SystemStatus.tsx` (Main Component)
The primary dashboard container that:
- Fetches system status from `/api/health`
- Fetches data sources from `/api/data-sources`
- Renders all dashboard sections
- Handles loading and error states
- Displays real data when available

### `LayerControl.tsx` (Layer Management)
Grouped layer controls for:
- Administrative layers (NER boundary, states, districts, villages)
- Landslide layers (GSI historical events)
- Terrain layers (elevation, slope, aspect, curvature — all unavailable)
- Environment layers (rainfall, weather, soil moisture, hydrology — all unavailable)
- Risk layers (susceptibility, current risk — all unavailable)
- Route analysis layers
- Alert layers

Only layers with actual backend data are enabled; unavailable layers show "awaiting data" state.

### `Roadmap.tsx` (Project Progress)
15-phase roadmap component showing:
- Phase number
- Phase name
- Actual status (COMPLETED / PARTIAL / IN PROGRESS / BLOCKED / NOT STARTED)
- Description of what each phase requires
- Visual color coding
- Legend explaining status definitions

---

## Backend Integration

The dashboard connects to these actual API endpoints:

### Health & Status
- `GET /api/health` — returns system status
- `GET /api/states` — returns approved NER states

### Real Data
- `GET /api/landslides` — returns GSI historical landslides (real data)
- `GET /api/roads` — returns road network (if available)
- `GET /api/villages` — returns village data (if available)
- `GET /api/geology` — returns geological data (if available)
- `GET /api/data-sources` — returns complete data source inventory with statuses

### Blocked Endpoints (Return BLOCKED Status)
- `GET /api/features` — feature engineering blocked
- `GET /api/models` — model registry blocked
- `GET /api/predictions` — predictions blocked
- `GET /api/risk` — risk layer blocked
- `GET /api/road-segments` — road risk blocked
- `GET /api/village-exposure` — village exposure blocked
- `GET /api/alerts` — alert system blocked
- `GET /api/field-reports` — field report workflow blocked

All blocked endpoints return explicit status messages rather than fake data.

---

## Visual Design

**Color Palette:**
- **Slate:** Primary background and neutral text
- **Emerald:** Available data, partial progress, operational elements
- **Red:** Blocked components, unavailable data
- **Yellow:** In-progress, warnings
- **Dark theme:** Professional, serious monitoring interface

**Layout:**
- Clean, readable typography
- Professional GIS-style interface
- Clear hierarchy and information architecture
- Responsive grid layout (desktop/tablet/mobile)
- No unnecessary animations or gaming-style effects

---

## How to Run

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Development server:**
   ```bash
   npm run dev
   ```
   Opens at http://localhost:5173

3. **Production build:**
   ```bash
   npm run build
   ```
   Creates optimized bundle in `dist/`

4. **Start backend (in separate terminal):**
   ```bash
   cd backend
   python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Open dashboard:**
   http://localhost:5173

---

## Key Features

### 1. No Fabricated Data
- Real GSI landslides display when backend provides them
- Missing datasets explicitly marked as "DATASET NOT AVAILABLE"
- No fake risk scores or probabilities
- No synthetic environmental values
- No made-up alerts or warnings

### 2. Scientific Honesty
- Every data source lists its origin and status
- Blocked phases remain visually distinct from working phases
- Explains why each phase is blocked
- Shows exact prerequisites for unblocking each phase

### 3. Real-Time API Connection
- Dashboard respects actual backend responses
- Handles API errors gracefully
- Shows loading states during data fetch
- Updates every 30 seconds

### 4. Professional UX
- Readable typography and spacing
- Logical information hierarchy
- Accessible color contrast
- Professional GIS styling

### 5. Responsive Design
- Works on desktop (recommended)
- Tablet-friendly layout
- Mobile considerations (stacked layout)

---

## Limitations & Future Work

### Current Limitations
1. Map is a placeholder; full MapLibre integration requires real tile data
2. Statistics calculated from actual API responses (may show zeros for blocked layers)
3. No real-time alerts (blocked until alert engine is implemented)
4. No route analysis (blocked until routing network + risk layers exist)
5. No field report UI (blocked until review workflow is implemented)

### To Unblock Phase 7 (Feature Engineering)
1. Acquire verified DEM/terrain source
2. Acquire verified rainfall source
3. Acquire verified soil/hydrology sources
4. Create spatially aligned training dataset
5. Document feature provenance and validation strategy
6. Run tests to confirm no temporal/spatial leakage

### To Unblock Phase 8+ (ML & Risk)
- Complete Phase 7 validation
- Train and validate model with proper spatial/temporal splits
- Calibrate model outputs
- Build current-risk pipeline with verified environmental data
- Implement alert thresholds based on validated methodology

---

## Files Created/Modified

**Created:**
- `frontend/src/components/SystemStatus.tsx` — Main dashboard component
- `frontend/src/components/LayerControl.tsx` — Layer management UI
- `frontend/src/components/Roadmap.tsx` — 15-phase roadmap visualization

**Modified:**
- `frontend/src/main.tsx` — Updated to use new SystemStatus component
- `backend/app/main.py` — Added blocked-status endpoints for Phases 7–15

---

## Testing

### Unit Tests (to be added)
- Component rendering
- API error handling
- Data transformation
- Empty states

### Integration Tests
- Backend API connectivity
- Real data display from GSI endpoint
- Blocked endpoint behavior
- Layer toggle state management

### Build Test
```bash
npm run build
```
Should complete without errors and create optimized production bundle.

---

## Project Status Summary

**PHASES 1–6:** PARTIAL (foundation infrastructure and real GSI/administrative data available)
**PHASE 6:** IN PROGRESS (environmental framework established; awaiting verified DEM/rainfall/soil/hydrology sources)
**PHASES 7–15:** BLOCKED (all dependent on successful Phase 6 + verified training data)

**Real Data Currently Available:**
- GSI historical landslide inventory (33,904 field-validated events)
- Administrative boundaries (states, districts, villages)
- Existing ingestion infrastructure for roads, geology, DEM, soil

**Missing for ML/Risk Phases:**
- Verified DEM and terrain derivatives
- Verified rainfall / weather observations
- Verified soil moisture data
- Verified hydrology / drainage layers
- Verified satellite imagery / indices
- Verified route network with complete attributes
- Verified village geometry for exposure analysis

**Scientific Rule:**
No phase will be marked COMPLETE unless its actual implementation, real data, validation, and testing verify it works correctly. Blocked phases remain blocked until prerequisites are satisfied.

---

## Questions / Issues

For questions about:
- **Why is Phase X blocked?** → See the Phases section; each blocked phase shows its prerequisites
- **Where is the risk model?** → Not implemented (Phase 8–9 blocked); requires training data from Phase 7
- **Why no current risk scores?** → No validated model or current environmental data (Phases 7, 10 blocked)
- **Can I get alerts?** → Alert engine is blocked until current-risk pipeline is validated (Phase 14 blocked on Phase 10)
- **Why no route-risk analysis?** → Blocked until verified road network + validated risk layer exist (Phase 13 blocked)

All blocked components have explicit error messages in the dashboard explaining the exact reason.

---

**Dashboard Created:** October 5, 2026
**Project Status:** Real-data GIS foundation + partial Phase 1–6 implementation
**Data Integrity:** All missing datasets explicitly marked unavailable; no scientific values fabricated
