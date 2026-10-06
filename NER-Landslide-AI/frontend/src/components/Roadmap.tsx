import React from 'react';

export interface RoadmapPhase {
  phase: number;
  name: string;
  status: 'COMPLETED' | 'PARTIAL' | 'IN PROGRESS' | 'BLOCKED' | 'NOT STARTED';
  description: string;
}

const phases: RoadmapPhase[] = [
  { phase: 1, name: 'Project Foundation & GIS Setup', status: 'PARTIAL', description: 'Database schema, PostGIS, FastAPI backend' },
  { phase: 2, name: 'Data Infrastructure & Validation', status: 'PARTIAL', description: 'Validation pipelines, data quality checks' },
  { phase: 3, name: 'NER Boundary & Administrative Data', status: 'PARTIAL', description: 'State/district/village boundaries' },
  { phase: 4, name: 'Landslide Inventory (GSI)', status: 'PARTIAL', description: 'Historical GSI landslide extraction and ingestion' },
  { phase: 5, name: 'Real NER GIS Data Ingestion', status: 'PARTIAL', description: 'Administrative, roads, villages, geology ingestion' },
  { phase: 6, name: 'Terrain & Environmental Foundation', status: 'IN PROGRESS', description: 'DEM, rainfall, soil, hydrology framework (blocked on data)' },
  { phase: 7, name: 'Feature Engineering & Training Dataset', status: 'BLOCKED', description: 'Requires verified Phase 3–6 datasets' },
  { phase: 8, name: 'Machine Learning Model Development', status: 'BLOCKED', description: 'Requires Phase 7 training dataset' },
  { phase: 9, name: 'Risk Model & Calibration', status: 'BLOCKED', description: 'Requires Phase 8 validated model' },
  { phase: 10, name: 'Dynamic Real-Time Risk Engine', status: 'BLOCKED', description: 'Requires validated model + current data' },
  { phase: 11, name: 'Road Segment Risk & Exposure', status: 'BLOCKED', description: 'Requires verified road network + risk layer' },
  { phase: 12, name: 'Village/Settlement Exposure', status: 'BLOCKED', description: 'Requires verified village geometry + risk layer' },
  { phase: 13, name: 'Route-Risk Analysis', status: 'BLOCKED', description: 'Requires routing network + hazard data' },
  { phase: 14, name: 'Alerts & Early Warning Engine', status: 'BLOCKED', description: 'Requires validated current-risk outputs' },
  { phase: 15, name: 'Field Reports & Human Validation', status: 'BLOCKED', description: 'Requires verified submission/review workflow' },
];

export function Roadmap() {
  const statusColors = {
    COMPLETED: 'border-emerald-600/60 bg-emerald-950/40 text-emerald-300',
    PARTIAL: 'border-emerald-600/60 bg-emerald-950/40 text-emerald-300',
    'IN PROGRESS': 'border-yellow-600/60 bg-yellow-950/40 text-yellow-300',
    BLOCKED: 'border-red-600/60 bg-red-950/30 text-red-300',
    'NOT STARTED': 'border-slate-600/60 bg-slate-800/30 text-slate-400',
  };

  return (
    <div className="rounded-lg border border-slate-700/40 bg-slate-900/50 p-6">
      <h3 className="mb-6 text-lg font-semibold text-slate-50">Project Roadmap (Phases 1–15)</h3>
      <div className="space-y-3">
        {phases.map((p) => (
          <div
            key={p.phase}
            className={`rounded-lg border ${
              statusColors[p.status]
            } p-4 transition-all hover:shadow-lg`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full border border-current text-xs font-bold">
                    {p.phase}
                  </div>
                  <div>
                    <h4 className="font-semibold text-slate-50">{p.name}</h4>
                    <p className="mt-1 text-xs text-slate-400">{p.description}</p>
                  </div>
                </div>
              </div>
              <div className={`ml-4 whitespace-nowrap rounded-full border px-3 py-1 text-xs font-semibold ${statusColors[p.status]}`}>
                {p.status}
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-6 rounded-lg border border-slate-700/40 bg-slate-800/20 p-4 text-xs leading-relaxed text-slate-400">
        <p className="font-semibold text-slate-300">Legend:</p>
        <p className="mt-2">
          <span className="text-emerald-300">PARTIAL:</span> Foundation infrastructure exists; data or full implementation incomplete.
        </p>
        <p className="mt-1">
          <span className="text-yellow-300">IN PROGRESS:</span> Active development; awaiting verified source data or validation.
        </p>
        <p className="mt-1">
          <span className="text-red-300">BLOCKED:</span> Requires prerequisites from earlier phases; cannot proceed without verified data.
        </p>
      </div>
    </div>
  );
}
