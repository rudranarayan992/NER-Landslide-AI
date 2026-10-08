import React from 'react';

interface Legend {
  label: string;
  color: string;
  description: string;
}

interface LegendProps {
  visibleLayers: Set<string>;
  heatmapEnabled: boolean;
}

export function Legend({ visibleLayers, heatmapEnabled }: LegendProps) {
  const getLegendItems = (): Legend[] => {
    const items: Legend[] = [];

    if (visibleLayers.has('landslides')) {
      items.push({
        label: '● Historical Landslide Events',
        color: '#dc2626',
        description: 'Real GSI historical observations',
      });
    }

    if (visibleLayers.has('landslides-heatmap') && heatmapEnabled) {
      items.push({
        label: '◆ Historical Landslide Density',
        color: '#ef4444',
        description: 'Density overlay — historical data only (NOT current risk)',
      });
    }

    if (visibleLayers.has('state-boundaries')) {
      items.push({
        label: '─ Administrative Boundaries',
        color: '#38bdf8',
        description: 'State and regional boundaries',
      });
    }

    if (visibleLayers.has('roads')) {
      items.push({
        label: '─ Road Network',
        color: '#cbd5e1',
        description: 'Infrastructure road segments',
      });
    }

    if (visibleLayers.has('villages')) {
      items.push({
        label: '● Villages & Settlements',
        color: '#7dd3fc',
        description: 'Villages and local settlements',
      });
    }

    return items;
  };

  const items = getLegendItems();

  return (
    <div className="space-y-3 text-slate-100">
      <p className="text-[10px] uppercase tracking-[0.18em] text-cyan-300 font-bold">LEGEND</p>

      {items.length > 0 ? (
        <div className="space-y-2.5 border-b border-slate-700/50 pb-3">
          {items.map((item, idx) => (
            <div key={idx} className="flex items-start gap-2">
              <div className="w-2.5 h-2.5 rounded-full mt-1.5 flex-shrink-0" style={{ backgroundColor: item.color }} />
              <div>
                <p className="text-[10px] font-semibold text-white">{item.label}</p>
                <p className="text-[9px] text-slate-400">{item.description}</p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-[9px] text-slate-400">
          <p>Enable layers from the left panel.</p>
        </div>
      )}

      <div className="space-y-2 border-b border-slate-700/50 pb-3">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold text-cyan-300 uppercase tracking-[0.12em]">Current Risk</span>
          <span className="inline-block px-1.5 py-0.5 rounded bg-red-500/20 border border-red-600/60 text-[8px] font-bold text-red-200 uppercase">BLOCKED</span>
        </div>
        <p className="text-[9px] text-slate-400">
          Requires: verified environmental data + validated ML model
        </p>
      </div>

      <div className="space-y-2 border-b border-slate-700/50 pb-3">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold text-cyan-300 uppercase tracking-[0.12em]">Road Risk</span>
          <span className="inline-block px-1.5 py-0.5 rounded bg-red-500/20 border border-red-600/60 text-[8px] font-bold text-red-200 uppercase">BLOCKED</span>
        </div>
        <p className="text-[9px] text-slate-400">
          Requires: validated road + hazard data
        </p>
      </div>

      <div>
        <p className="text-[9px] font-semibold text-amber-300 uppercase tracking-[0.12em] mb-1.5">Alert Levels</p>
        <div className="space-y-1 text-[9px]">
          <p className="text-slate-400">🔔 WATCH — ALERTS NOT OPERATIONAL</p>
          <p className="text-slate-400">⚠️ AUTOMATED ALERTS BLOCKED</p>
          <p className="text-slate-400">No real-time warnings available.</p>
        </div>
      </div>
    </div>
  );
}
