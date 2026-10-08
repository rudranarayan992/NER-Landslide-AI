import React, { useState } from 'react';
import { ChevronDown, X } from 'lucide-react';

interface EnvironmentalData {
  rainfall: { value1h?: number; value24h?: number; value72h?: number; value7d?: number; timestamp?: string };
  soil: { type?: string; moisture?: number; properties?: string; timestamp?: string };
  terrain: { elevation?: number; slope?: number; aspect?: string; curvature?: number; timestamp?: string };
  hydrology: { distanceToStream?: number; drainage?: string; flowAccumulation?: number; timestamp?: string };
  satellite: { landcover?: string; ndvi?: number; change?: string; timestamp?: string };
}

interface EnvironmentalPanelProps {
  onClose: () => void;
}

export function EnvironmentalPanel({ onClose }: EnvironmentalPanelProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['rainfall', 'soil', 'terrain'])
  );

  const toggleSection = (section: string) => {
    const next = new Set(expandedSections);
    if (next.has(section)) next.delete(section); else next.add(section);
    setExpandedSections(next);
  };

  const unavailable = 'AWAITING VERIFIED SOURCE DATA';

  const envData: EnvironmentalData = {
    rainfall: { value1h: undefined, value24h: undefined },
    soil: { type: undefined },
    terrain: { elevation: undefined },
    hydrology: { distanceToStream: undefined },
    satellite: { ndvi: undefined },
  };

  const DataField = ({ label, value }: { label: string; value?: number | string }) => (
    <div className="flex items-center justify-between py-1 text-[10px] border-b border-slate-700/30 last:border-0">
      <span className="text-slate-400">{label}</span>
      <span className="text-slate-200 font-medium">
        {value !== undefined && value !== null ? String(value) : unavailable}
      </span>
    </div>
  );

  const Section = ({ 
    id, 
    title, 
    children, 
    status = 'awaiting' 
  }: { 
    id: string; 
    title: string; 
    children: React.ReactNode; 
    status?: 'available' | 'awaiting' | 'blocked';
  }) => {
    const statusColor = {
      available: 'text-emerald-400',
      awaiting: 'text-amber-400',
      blocked: 'text-rose-400',
    }[status];

    const expanded = expandedSections.has(id);

    return (
      <div className="border-b border-slate-700/50 last:border-0">
        <button
          onClick={() => toggleSection(id)}
          className="w-full flex items-center justify-between p-3 hover:bg-slate-900/60 transition-colors"
        >
          <div className="flex items-center gap-2">
            <ChevronDown
              size={14}
              className={`text-slate-500 transition-transform ${expanded ? 'rotate-180' : ''}`}
            />
            <h3 className="text-sm font-semibold text-white uppercase tracking-[0.12em]">{title}</h3>
            <span className={`text-[8px] font-semibold uppercase tracking-[0.1em] ${statusColor}`}>
              {status === 'available' ? '✓ AVAILABLE' : status === 'blocked' ? '✗ BLOCKED' : '⏳ AWAITING'}
            </span>
          </div>
        </button>
        {expanded && (
          <div className="px-3 pb-3 space-y-1 bg-slate-900/30">
            {children}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="fixed bottom-4 left-4 w-96 rounded-lg border border-slate-700/70 bg-slate-950/95 shadow-2xl backdrop-blur-sm z-20 flex flex-col max-h-[600px]">
      {/* HEADER */}
      <div className="flex items-center justify-between p-3 border-b border-slate-700/50">
        <h2 className="text-sm font-bold text-cyan-300 uppercase tracking-[0.14em]">Environmental Conditions</h2>
        <button
          onClick={onClose}
          className="p-1 hover:bg-slate-700/60 rounded transition-colors"
        >
          <X size={16} className="text-slate-400" />
        </button>
      </div>

      {/* SECTIONS */}
      <div className="flex-1 overflow-y-auto divide-y divide-slate-700/50">
        <Section id="rainfall" title="Rainfall" status="awaiting">
          <DataField label="1-Hour Total" value={envData.rainfall.value1h} />
          <DataField label="24-Hour Total" value={envData.rainfall.value24h} />
          <DataField label="72-Hour Total" value={envData.rainfall.value72h} />
          <DataField label="7-Day Total" value={envData.rainfall.value7d} />
          <div className="text-[9px] text-slate-400 mt-2 pt-2 border-t border-slate-700/30">
            Dataset: IMERG • CRS: WGS84 • Provider: NASA GSFC
          </div>
        </Section>

        <Section id="soil" title="Soil" status="awaiting">
          <DataField label="Soil Type" value={envData.soil.type} />
          <DataField label="Soil Moisture" value={envData.soil.moisture} />
          <DataField label="Soil Properties" value={envData.soil.properties} />
          <div className="text-[9px] text-slate-400 mt-2 pt-2 border-t border-slate-700/30">
            Dataset: ISRIC • CRS: WGS84 • Verification: AWAITING
          </div>
        </Section>

        <Section id="terrain" title="Terrain" status="awaiting">
          <DataField label="Elevation (m)" value={envData.terrain.elevation} />
          <DataField label="Slope (°)" value={envData.terrain.slope} />
          <DataField label="Aspect" value={envData.terrain.aspect} />
          <DataField label="Curvature" value={envData.terrain.curvature} />
          <div className="text-[9px] text-slate-400 mt-2 pt-2 border-t border-slate-700/30">
            Dataset: USGS DEM 30m • CRS: WGS84 • Provider: OpenTopo
          </div>
        </Section>

        <Section id="hydrology" title="Hydrology" status="awaiting">
          <DataField label="Distance to Stream (m)" value={envData.hydrology.distanceToStream} />
          <DataField label="Drainage" value={envData.hydrology.drainage} />
          <DataField label="Flow Accumulation" value={envData.hydrology.flowAccumulation} />
          <div className="text-[9px] text-slate-400 mt-2 pt-2 border-t border-slate-700/30">
            Dataset: HydroSHEDS • CRS: WGS84 • Provider: USGS
          </div>
        </Section>

        <Section id="satellite" title="Satellite / Remote Sensing" status="awaiting">
          <DataField label="Land Cover" value={envData.satellite.landcover} />
          <DataField label="NDVI Index" value={envData.satellite.ndvi} />
          <DataField label="Change Detection" value={envData.satellite.change} />
          <div className="text-[9px] text-slate-400 mt-2 pt-2 border-t border-slate-700/30">
            Dataset: Sentinel-2 • CRS: WGS84 • Provider: ESA Copernicus
          </div>
        </Section>
      </div>

      {/* STATUS */}
      <div className="border-t border-slate-700/50 p-2 bg-slate-900/60 text-[9px] text-slate-400">
        <span className="text-amber-300">ℹ</span> Environmental data is <span className="font-semibold text-amber-300">AWAITING VERIFIED SOURCE DATA</span>
      </div>
    </div>
  );
}
