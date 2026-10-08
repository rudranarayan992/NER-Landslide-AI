import React from 'react';

interface Feature {
  type: 'Feature';
  id: string | number;
  properties: Record<string, any>;
  geometry: {
    type: string;
    coordinates: any[];
  };
}

interface SelectedFeatureData {
  type: string;
  data: Feature | null;
}

interface InfoPanelProps {
  selectedFeature: SelectedFeatureData | null;
}

const fieldValue = (value: unknown) => {
  if (value === null || value === undefined || value === '') return '—';
  if (typeof value === 'number') return Number.isFinite(value) ? value.toString() : '—';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
};

const unavailable = 'AWAITING VERIFIED SOURCE DATA';

const renderStatusPill = (status: string, tone: 'green' | 'amber' | 'red' | 'slate' = 'slate') => {
  const palette = {
    green: 'border-emerald-600/60 bg-emerald-500/10 text-emerald-200',
    amber: 'border-amber-600/60 bg-amber-500/10 text-amber-200',
    red: 'border-rose-600/60 bg-rose-500/10 text-rose-200',
    slate: 'border-slate-600/70 bg-slate-800/80 text-slate-200',
  };

  return (
    <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[9px] uppercase tracking-[0.18em] ${palette[tone]}`}>
      {status}
    </span>
  );
};

export function InfoPanel({ selectedFeature }: InfoPanelProps) {
  const renderContent = () => {
    if (!selectedFeature || !selectedFeature.data) {
      return (
        <div className="p-6 text-center text-slate-400">
          <p className="text-[11px] uppercase tracking-[0.2em] text-cyan-300">Location Intelligence</p>
          <p className="mt-3 text-sm text-slate-300">Click a feature to inspect its location and historical context.</p>
          <div className="mt-4 rounded border border-slate-700 bg-slate-900/60 p-3 text-left">
            <p className="text-[9px] uppercase tracking-[0.18em] text-amber-300">Current Risk</p>
            <p className="mt-2 text-xs text-slate-200">BLOCKED — Verified environmental data and a validated ML model are required.</p>
          </div>
        </div>
      );
    }

    const feature = selectedFeature.data;
    const props = feature.properties || {};
    const coords = feature.geometry?.coordinates || [];
    const lat = Array.isArray(coords) && coords.length >= 2 ? Number(coords[1]) : null;
    const lon = Array.isArray(coords) && coords.length >= 2 ? Number(coords[0]) : null;

    const getTypeLabel = () => {
      switch (selectedFeature.type) {
        case 'landslide': return 'Historical Landslide Event';
        case 'state': return 'Administrative Boundary';
        case 'village': return 'Village / Local Settlement';
        case 'road': return 'Road Feature';
        default: return 'GIS Feature';
      }
    };

    const nameValue = props.name || props.event_id || props.village || props.state || props.state_name || props.road_name || 'Unnamed Feature';
    const locationInfo = [
      { label: 'Latitude', value: lat !== null && Number.isFinite(lat) ? lat.toFixed(5) : unavailable },
      { label: 'Longitude', value: lon !== null && Number.isFinite(lon) ? lon.toFixed(5) : unavailable },
      { label: 'State', value: props.state || props.state_name || unavailable },
      { label: 'District', value: props.district || unavailable },
      { label: 'Village / locality', value: props.village || props.village_name || unavailable },
      { label: 'Administrative hierarchy', value: props.administrative_hierarchy || 'AWAITING VERIFIED SOURCE DATA' },
    ];

    return (
      <div className="space-y-4">
        <div className="panel-header px-4 py-3 border-b border-slate-700/80 bg-slate-900/50">
          <p className="text-[10px] uppercase tracking-[0.18em] text-cyan-300">LOCATION INTELLIGENCE</p>
          <div className="mt-2 flex items-center justify-between gap-3">
            <p className="text-lg font-semibold text-white">{nameValue}</p>
            {renderStatusPill('CURRENT RISK BLOCKED', 'amber')}
          </div>
        </div>

        <div className="px-4 py-3 space-y-3">
          <div className="rounded border border-slate-700 bg-slate-900/60 p-3">
            <p className="text-[9px] uppercase tracking-[0.2em] text-cyan-300">A. LOCATION</p>
            <div className="mt-3 space-y-2">
              {locationInfo.map((item) => (
                <div key={item.label} className="flex justify-between gap-3 text-xs">
                  <span className="text-slate-400">{item.label}</span>
                  <span className="text-right text-slate-100">{item.value}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded border border-slate-700 bg-slate-900/60 p-3">
            <p className="text-[9px] uppercase tracking-[0.2em] text-cyan-300">B. INFRASTRUCTURE</p>
            <div className="mt-3 space-y-2 text-xs">
              <div className="flex justify-between gap-3"><span className="text-slate-400">Nearest road</span><span className="text-right text-slate-100">{props.road_name || unavailable}</span></div>
              <div className="flex justify-between gap-3"><span className="text-slate-400">Road ID</span><span className="text-right text-slate-100">{props.road_id || unavailable}</span></div>
              <div className="flex justify-between gap-3"><span className="text-slate-400">Road class</span><span className="text-right text-slate-100">{props.road_class || unavailable}</span></div>
              <div className="flex justify-between gap-3"><span className="text-slate-400">Road connectivity</span><span className="text-right text-slate-100">{props.road_connectivity || unavailable}</span></div>
              <div className="flex justify-between gap-3"><span className="text-slate-400">Nearest village</span><span className="text-right text-slate-100">{props.village || props.village_name || unavailable}</span></div>
              <div className="flex justify-between gap-3"><span className="text-slate-400">Distance to village</span><span className="text-right text-slate-100">{props.distance_to_village_km || unavailable}</span></div>
            </div>
          </div>

          <div className="rounded border border-slate-700 bg-slate-900/60 p-3">
            <p className="text-[9px] uppercase tracking-[0.2em] text-cyan-300">C. HISTORICAL LANDSLIDE INTELLIGENCE</p>
            <div className="mt-3 space-y-2 text-xs">
              <div className="flex justify-between gap-3"><span className="text-slate-400">Historical landslide count nearby</span><span className="text-right text-slate-100">{props.historical_count || unavailable}</span></div>
              <div className="flex justify-between gap-3"><span className="text-slate-400">Historical density</span><span className="text-right text-slate-100">{props.density || unavailable}</span></div>
              <div className="flex justify-between gap-3"><span className="text-slate-400">Nearest historical event</span><span className="text-right text-slate-100">{props.nearest_event || unavailable}</span></div>
              <div className="flex justify-between gap-3"><span className="text-slate-400">Distance</span><span className="text-right text-slate-100">{props.distance_to_nearest_event_km || unavailable}</span></div>
              <div className="mt-2 rounded border border-emerald-600/30 bg-emerald-500/5 p-2 text-[10px] text-emerald-100">
                SOURCE: GSI HISTORICAL LANDSLIDE DATA
              </div>
            </div>
          </div>

          <div className="rounded border border-slate-700 bg-slate-900/60 p-3">
            <p className="text-[9px] uppercase tracking-[0.2em] text-cyan-300">D. CURRENT ENVIRONMENT</p>
            <div className="mt-3 space-y-2 text-xs">
              <div className="flex justify-between gap-3"><span className="text-slate-400">Rainfall 1h</span><span className="text-right text-slate-100">{unavailable}</span></div>
              <div className="flex justify-between gap-3"><span className="text-slate-400">Rainfall 24h</span><span className="text-right text-slate-100">{unavailable}</span></div>
              <div className="flex justify-between gap-3"><span className="text-slate-400">Rainfall 3d</span><span className="text-right text-slate-100">{unavailable}</span></div>
              <div className="flex justify-between gap-3"><span className="text-slate-400">Rainfall 7d</span><span className="text-right text-slate-100">{unavailable}</span></div>
              <div className="flex justify-between gap-3"><span className="text-slate-400">DEM / slope</span><span className="text-right text-slate-100">{unavailable}</span></div>
              <div className="flex justify-between gap-3"><span className="text-slate-400">Soil / moisture</span><span className="text-right text-slate-100">{unavailable}</span></div>
              <div className="flex justify-between gap-3"><span className="text-slate-400">Hydrology / land cover</span><span className="text-right text-slate-100">{unavailable}</span></div>
            </div>
          </div>

          <div className="rounded border border-slate-700 bg-slate-900/60 p-3">
            <p className="text-[9px] uppercase tracking-[0.2em] text-cyan-300">LANDSLIDE PREDICTION</p>
            <div className="mt-3 flex items-center justify-between gap-3">
              <span className="text-slate-400 text-xs">Status</span>
              {renderStatusPill('BLOCKED', 'red')}
            </div>
            <p className="mt-2 text-[10px] text-slate-300 leading-relaxed">
              Predictive landslide risk is unavailable because verified environmental inputs and a validated ML model are not yet available.
            </p>
          </div>

          <div className="rounded border border-slate-700 bg-slate-900/60 p-3">
            <p className="text-[9px] uppercase tracking-[0.2em] text-cyan-300">WHY THIS LOCATION?</p>
            <p className="mt-2 text-[10px] text-slate-300 leading-relaxed">
              Model explanation unavailable because predictive model is not operational.
            </p>
          </div>

          <div className="rounded border border-slate-700 bg-slate-900/60 p-3">
            <p className="text-[9px] uppercase tracking-[0.2em] text-cyan-300">PROVENANCE</p>
            <div className="mt-3 text-[10px] text-slate-300 leading-relaxed">
              <p>Source: GSI historical landslide data and verified administrative infrastructure.</p>
              <p className="mt-1">Verification status: VERIFIED FOR HISTORICAL DATA ONLY</p>
              <p className="mt-1">Additional environmental provenance: AWAITING VERIFIED SOURCE DATA</p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 text-slate-100">
      <div className="px-4 py-3 border-b border-slate-700/80 bg-slate-950/80">
        <h2 className="text-[11px] uppercase tracking-[0.2em] text-cyan-300">LOCATION INTELLIGENCE</h2>
      </div>
      <div className="flex-1 overflow-y-auto">{renderContent()}</div>
    </div>
  );
}
