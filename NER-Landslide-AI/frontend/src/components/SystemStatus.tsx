import React, { useEffect, useState } from 'react';
import { Roadmap } from './Roadmap';

interface SystemStatusResponse {
  status: string;
  message?: string;
  states?: string[];
}

interface DataSourcesResponse {
  sources: Array<{
    dataset: string;
    status: string;
    records?: number;
    valid_records?: number;
  }>;
  count?: number;
}

export function SystemStatus() {
  const [apiStatus, setApiStatus] = useState<SystemStatusResponse | null>(null);
  const [dataSources, setDataSources] = useState<DataSourcesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        setLoading(true);
        const [statusRes, sourcesRes] = await Promise.all([
          fetch('/api/health'),
          fetch('/api/data-sources'),
        ]);

        if (!statusRes.ok || !sourcesRes.ok) {
          throw new Error('Failed to fetch system status');
        }

        const status = await statusRes.json();
        const sources = await sourcesRes.json();

        setApiStatus(status);
        setDataSources(sources);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const phaseStatus = {
    '1': 'PARTIAL',
    '2': 'PARTIAL',
    '3': 'PARTIAL',
    '4': 'PARTIAL',
    '5': 'PARTIAL',
    '6': 'PARTIAL / IN PROGRESS',
    '7': 'BLOCKED',
    '8': 'BLOCKED',
    '9': 'BLOCKED',
    '10': 'BLOCKED',
    '11': 'BLOCKED',
    '12': 'BLOCKED',
    '13': 'BLOCKED',
    '14': 'BLOCKED',
    '15': 'BLOCKED',
  };

  const nerStates = [
    'Arunachal Pradesh',
    'Assam',
    'Manipur',
    'Meghalaya',
    'Mizoram',
    'Nagaland',
    'Sikkim',
    'Tripura',
  ];

  const dataAvailability = [
    { name: 'GSI Landslides', status: 'AVAILABLE / PARTIAL', source: 'Geological Survey of India' },
    { name: 'Administrative Data', status: 'AVAILABLE / PARTIAL', source: 'Local administrative files' },
    { name: 'DEM / Elevation', status: 'AWAITING VERIFIED DATA', source: 'Pending' },
    { name: 'Rainfall', status: 'AWAITING VERIFIED DATA', source: 'Pending' },
    { name: 'Weather', status: 'AWAITING VERIFIED DATA', source: 'Pending' },
    { name: 'Soil Moisture', status: 'AWAITING VERIFIED DATA', source: 'Pending' },
    { name: 'Hydrology', status: 'AWAITING VERIFIED DATA', source: 'Pending' },
    { name: 'Satellite', status: 'AWAITING VERIFIED DATA', source: 'Pending' },
    { name: 'Road Network', status: 'AWAITING VERIFIED DATA', source: 'Pending' },
    { name: 'Village Geometry', status: 'AWAITING VERIFIED DATA', source: 'Pending' },
    { name: 'ML Training Data', status: 'BLOCKED', source: 'Requires verified inputs' },
    { name: 'ML Model', status: 'BLOCKED', source: 'Requires training dataset' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-emerald-950 text-slate-50">
      {/* Header */}
      <header className="border-b border-emerald-700/40 bg-slate-950/60 backdrop-blur-md">
        <div className="mx-auto max-w-7xl px-6 py-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs uppercase tracking-widest text-emerald-400">Real-Data GIS Foundation</p>
              <h1 className="mt-2 text-3xl font-bold text-slate-50">NER Landslide AI</h1>
              <p className="mt-1 text-sm text-slate-400">
                AI-Based Early Warning & Landslide Risk Monitoring System — North Eastern Region
              </p>
            </div>
            <div className="rounded-lg border border-emerald-700/60 bg-emerald-950/50 px-4 py-3 text-right">
              <div className="text-xs uppercase tracking-widest text-emerald-300">System Status</div>
              <div className="mt-1 text-sm font-semibold text-emerald-200">DATA PLATFORM: PARTIAL</div>
              <div className="mt-1 text-xs text-slate-400">
                {loading ? 'Checking status...' : error ? 'Connection error' : 'Operational foundation'}
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-10">
        {/* System Overview */}
        <section className="mb-10">
          <h2 className="mb-4 text-xl font-semibold text-slate-50">System Overview</h2>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-5">
            {[
              { label: 'GIS Foundation', status: 'PARTIAL', color: 'emerald' },
              { label: 'Real Data', status: 'PARTIAL', color: 'emerald' },
              { label: 'ML Model', status: 'BLOCKED', color: 'red' },
              { label: 'Current Risk', status: 'BLOCKED', color: 'red' },
              { label: 'Early Warning', status: 'BLOCKED', color: 'red' },
            ].map((card) => (
              <div
                key={card.label}
                className={`rounded-lg border ${
                  card.color === 'emerald'
                    ? 'border-emerald-700/60 bg-emerald-950/30'
                    : 'border-red-700/40 bg-red-950/20'
                } p-4`}
              >
                <div className="text-xs uppercase tracking-wide text-slate-400">{card.label}</div>
                <div
                  className={`mt-2 text-lg font-bold ${
                    card.color === 'emerald' ? 'text-emerald-300' : 'text-red-300'
                  }`}
                >
                  {card.status}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Main Grid */}
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
          {/* Left Column: Map Placeholder and Statistics */}
          <div className="lg:col-span-2 space-y-8">
            {/* GIS Map */}
            <section className="rounded-lg border border-emerald-700/40 bg-slate-900/50 p-6">
              <h3 className="mb-4 text-lg font-semibold text-slate-50">GIS Map</h3>
              <div className="flex h-96 items-center justify-center rounded-lg border border-dashed border-emerald-700/30 bg-gradient-to-br from-slate-800 to-slate-900">
                <div className="text-center">
                  <p className="text-sm text-slate-400">
                    Interactive map with historical landslides and administrative boundaries
                  </p>
                  <p className="mt-2 text-xs text-slate-500">
                    Real GeoJSON data from verified sources — no fabricated layers
                  </p>
                </div>
              </div>
            </section>

            {/* Statistics */}
            <section className="rounded-lg border border-emerald-700/40 bg-slate-900/50 p-6">
              <h3 className="mb-4 text-lg font-semibold text-slate-50">NER Coverage</h3>
              <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                {nerStates.map((state) => (
                  <div key={state} className="rounded-lg border border-slate-700/50 bg-slate-800/30 p-3">
                    <div className="truncate text-xs font-semibold text-emerald-300">{state}</div>
                    <div className="mt-2 text-xs text-slate-400">
                      Phase 1–6: Partial
                      <br />
                      Phase 7+: Blocked
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* Historical Landslides */}
            <section className="rounded-lg border border-emerald-700/40 bg-slate-900/50 p-6">
              <h3 className="mb-4 text-lg font-semibold text-slate-50">Historical Landslide Inventory</h3>
              <div className="space-y-3">
                <div className="flex justify-between border-b border-slate-700/50 pb-2">
                  <span className="text-sm text-slate-400">Source</span>
                  <span className="text-sm font-semibold text-emerald-300">Geological Survey of India (GSI)</span>
                </div>
                <div className="flex justify-between border-b border-slate-700/50 pb-2">
                  <span className="text-sm text-slate-400">Status</span>
                  <span className="text-sm font-semibold text-emerald-300">AVAILABLE / PARTIAL</span>
                </div>
                <div className="flex justify-between border-b border-slate-700/50 pb-2">
                  <span className="text-sm text-slate-400">Data Format</span>
                  <span className="text-sm text-slate-300">Extracted CSV + GeoJSON</span>
                </div>
                <div className="flex justify-between pb-2">
                  <span className="text-sm text-slate-400">Verification</span>
                  <span className="text-sm text-yellow-300">Field-validated inventory</span>
                </div>
              </div>
            </section>
          </div>

          {/* Right Column: Status Panels */}
          <div className="space-y-8">
            {/* Data Availability */}
            <section className="rounded-lg border border-emerald-700/40 bg-slate-900/50 p-6">
              <h3 className="mb-4 text-lg font-semibold text-slate-50">Data Availability</h3>
              <div className="space-y-2">
                {dataAvailability.map((item) => (
                  <div
                    key={item.name}
                    className="rounded-lg border border-slate-700/30 bg-slate-800/30 p-3"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="text-xs font-semibold text-slate-300">{item.name}</div>
                        <div className="mt-1 text-xs text-slate-500">{item.source}</div>
                      </div>
                      <div
                        className={`ml-2 whitespace-nowrap rounded-full px-2 py-1 text-xs font-semibold ${
                          item.status === 'AVAILABLE / PARTIAL'
                            ? 'border border-emerald-600/60 bg-emerald-950/50 text-emerald-300'
                            : item.status === 'AWAITING VERIFIED DATA'
                              ? 'border border-yellow-600/60 bg-yellow-950/50 text-yellow-300'
                              : 'border border-red-600/60 bg-red-950/50 text-red-300'
                        }`}
                      >
                        {item.status}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* ML / AI Status */}
            <section className="rounded-lg border border-red-700/40 bg-red-950/20 p-6">
              <h3 className="mb-4 text-lg font-semibold text-slate-50">AI / ML Status</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <div className="text-xs uppercase tracking-wide text-slate-400">Feature Engineering</div>
                  <div className="mt-1 font-semibold text-red-300">BLOCKED</div>
                </div>
                <div>
                  <div className="text-xs uppercase tracking-wide text-slate-400">Training Dataset</div>
                  <div className="mt-1 font-semibold text-red-300">0 VERIFIED ROWS</div>
                </div>
                <div>
                  <div className="text-xs uppercase tracking-wide text-slate-400">Model Status</div>
                  <div className="mt-1 font-semibold text-red-300">NOT TRAINED</div>
                </div>
                <div>
                  <div className="text-xs uppercase tracking-wide text-slate-400">Validation</div>
                  <div className="mt-1 font-semibold text-red-300">NOT AVAILABLE</div>
                </div>
                <div className="mt-4 border-t border-red-700/30 pt-3">
                  <p className="text-xs leading-relaxed text-slate-400">
                    ML pipeline is blocked until verified terrain, rainfall, environmental, and training data are available.
                  </p>
                </div>
              </div>
            </section>

            {/* Risk Status */}
            <section className="rounded-lg border border-red-700/40 bg-red-950/20 p-6">
              <h3 className="mb-4 text-lg font-semibold text-slate-50">Risk Engine Status</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <div className="text-xs uppercase tracking-wide text-slate-400">Susceptibility</div>
                  <div className="mt-1 font-semibold text-red-300">NOT AVAILABLE</div>
                </div>
                <div>
                  <div className="text-xs uppercase tracking-wide text-slate-400">Current Risk</div>
                  <div className="mt-1 font-semibold text-red-300">NOT AVAILABLE</div>
                </div>
                <div>
                  <div className="text-xs uppercase tracking-wide text-slate-400">Calibration</div>
                  <div className="mt-1 font-semibold text-red-300">NOT AVAILABLE</div>
                </div>
                <div>
                  <div className="text-xs uppercase tracking-wide text-slate-400">Alerts</div>
                  <div className="mt-1 font-semibold text-red-300">NO VALIDATED ALERTS</div>
                </div>
              </div>
            </section>

            {/* Phase Status */}
            <section className="rounded-lg border border-slate-700/40 bg-slate-800/30 p-6">
              <h3 className="mb-4 text-lg font-semibold text-slate-50">Project Phases</h3>
              <div className="space-y-2 text-xs">
                {Object.entries(phaseStatus).map(([phase, status]) => (
                  <div key={phase} className="flex items-center justify-between">
                    <span className="text-slate-400">Phase {phase}</span>
                    <span
                      className={`rounded px-2 py-1 font-semibold ${
                        status === 'PARTIAL' || status === 'PARTIAL / IN PROGRESS'
                          ? 'border border-emerald-600/60 bg-emerald-950/40 text-emerald-300'
                          : status === 'BLOCKED'
                            ? 'border border-red-600/60 bg-red-950/30 text-red-300'
                            : 'border border-slate-600/60 bg-slate-800 text-slate-400'
                      }`}
                    >
                      {status}
                    </span>
                  </div>
                ))}
              </div>
            </section>
          </div>
        </div>

        {/* Data Provenance */}
        <section className="mt-10 rounded-lg border border-slate-700/40 bg-slate-900/50 p-6">
          <h3 className="mb-4 text-lg font-semibold text-slate-50">Data Provenance & Versioning</h3>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[
              {
                name: 'GSI Landslide Inventory',
                source: 'Geological Survey of India',
                version: 'Not yet versioned',
                status: 'AVAILABLE / PARTIAL',
              },
              {
                name: 'Administrative Boundaries',
                source: 'Local administrative files',
                version: 'Not yet versioned',
                status: 'AVAILABLE / PARTIAL',
              },
              {
                name: 'Training Dataset',
                source: 'Pending',
                version: 'N/A',
                status: 'BLOCKED',
              },
              {
                name: 'ML Model',
                source: 'Pending',
                version: 'N/A',
                status: 'BLOCKED',
              },
            ].map((item) => (
              <div
                key={item.name}
                className="rounded-lg border border-slate-700/30 bg-slate-800/30 p-4"
              >
                <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">{item.name}</div>
                <div className="mt-2 space-y-1 text-xs text-slate-400">
                  <div>
                    <span className="text-slate-500">Source:</span> {item.source}
                  </div>
                  <div>
                    <span className="text-slate-500">Version:</span> {item.version}
                  </div>
                  <div className="mt-2">
                    <span
                      className={`rounded-full px-2 py-1 font-semibold ${
                        item.status === 'AVAILABLE / PARTIAL'
                          ? 'border border-emerald-600/60 bg-emerald-950/40 text-emerald-300'
                          : 'border border-red-600/60 bg-red-950/30 text-red-300'
                      }`}
                    >
                      {item.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Information */}
        <section className="mt-10 rounded-lg border border-slate-700/40 bg-slate-900/50 p-6">
          <h3 className="mb-3 text-lg font-semibold text-slate-50">About This Project</h3>
          <div className="space-y-3 text-sm leading-relaxed text-slate-400">
            <p>
              The NER Landslide AI system is a scientifically defensible real-data GIS foundation under active development.
            </p>
            <p>
              <span className="text-emerald-300">✓ What exists:</span> Real GSI landslide inventory, administrative
              boundaries, and partial Phase 1–6 infrastructure.
            </p>
            <p>
              <span className="text-red-300">✗ What is blocked:</span> ML training (Phase 7–8), risk modeling (Phase
              9), real-time risk (Phase 10), road/village exposure (Phase 11–12), routing (Phase 13), alerts (Phase 14),
              and field reports (Phase 15).
            </p>
            <p>
              <span className="text-yellow-300">⚠ Why:</span> Verified DEM, rainfall, weather, soil, hydrology, and
              satellite data sources are not yet available. No scientific layer is fabricated.
            </p>
            <p className="mt-4 rounded-lg border border-emerald-700/40 bg-emerald-950/20 p-3 text-xs text-emerald-200">
              This dashboard reflects the actual repository state. Missing datasets are explicitly marked as unavailable.
              No fake risk scores, predictions, or environmental values are displayed.
            </p>
          </div>
        </section>

        {/* Roadmap */}
        <section className="mt-10">
          <Roadmap />
        </section>
      </main>

      {/* Footer */}
      <footer className="mt-10 border-t border-slate-800 bg-slate-950/70 py-6">
        <div className="mx-auto max-w-7xl px-6 text-center text-xs text-slate-500">
          <p>NER Landslide AI — Real-Data GIS Foundation for Landslide Early Warning & Risk Monitoring</p>
          <p className="mt-2">Phases 1–6: Partial | Phases 7–15: Blocked pending verified environmental data sources</p>
        </div>
      </footer>
    </div>
  );
}

export default SystemStatus;
