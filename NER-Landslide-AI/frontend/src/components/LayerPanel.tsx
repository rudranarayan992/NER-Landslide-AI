import React from 'react';
import { ChevronDown, Eye, EyeOff, ShieldAlert, Database } from 'lucide-react';

interface LayerPanelProps {
  visibleLayers: Set<string>;
  onToggleLayer: (layerId: string) => void;
  onToggleHeatmap: () => void;
  heatmapEnabled: boolean;
}

interface LayerItem {
  id: string;
  name: string;
  status: string;
  isBasemap?: boolean;
  isHeatmap?: boolean;
}

interface LayerGroup {
  name: string;
  layers: LayerItem[];
}

export function LayerPanel({ visibleLayers, onToggleLayer, onToggleHeatmap, heatmapEnabled }: LayerPanelProps) {
  const [expandedGroups, setExpandedGroups] = React.useState<Set<string>>(
    new Set(['Administrative', 'Landslides', 'Terrain', 'Rainfall', 'Soil', 'Hydrology', 'Roads', 'Villages'])
  );

  const toggleGroup = (groupName: string) => {
    const next = new Set(expandedGroups);
    if (next.has(groupName)) next.delete(groupName); else next.add(groupName);
    setExpandedGroups(next);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available': return 'text-emerald-400';
      case 'awaiting': return 'text-amber-400';
      case 'blocked': return 'text-rose-400';
      default: return 'text-slate-400';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'available': return 'AVAILABLE';
      case 'awaiting': return 'AWAITING DATA';
      case 'blocked': return 'BLOCKED';
      default: return status.toUpperCase();
    }
  };

  const LAYER_GROUPS: LayerGroup[] = [
    {
      name: 'Administrative',
      layers: [
        { id: 'state-boundaries', name: 'State Boundaries', status: 'available' },
        { id: 'district-boundaries', name: 'Districts', status: 'awaiting' },
      ],
    },
    {
      name: 'Landslides',
      layers: [
        { id: 'landslides', name: 'Historical Landslide Events', status: 'available' },
        { id: 'landslides-heatmap', name: 'Historical Density', status: 'available', isHeatmap: true },
        { id: 'susceptibility', name: 'Susceptibility Map', status: 'blocked' },
      ],
    },
    {
      name: 'Terrain',
      layers: [
        { id: 'dem', name: 'DEM / Elevation', status: 'awaiting' },
        { id: 'slope', name: 'Slope Analysis', status: 'awaiting' },
        { id: 'aspect', name: 'Aspect Analysis', status: 'awaiting' },
        { id: 'curvature', name: 'Curvature', status: 'awaiting' },
      ],
    },
    {
      name: 'Rainfall',
      layers: [
        { id: 'rainfall', name: 'Rainfall Distribution', status: 'awaiting' },
        { id: 'weather', name: 'Weather Monitoring', status: 'awaiting' },
      ],
    },
    {
      name: 'Soil',
      layers: [
        { id: 'soil', name: 'Soil Properties', status: 'awaiting' },
        { id: 'soil-moisture', name: 'Soil Moisture', status: 'awaiting' },
      ],
    },
    {
      name: 'Hydrology',
      layers: [
        { id: 'hydrology', name: 'Hydrology & Streams', status: 'awaiting' },
        { id: 'waterbodies', name: 'Water Bodies', status: 'awaiting' },
      ],
    },
    {
      name: 'Roads',
      layers: [
        { id: 'roads', name: 'Road Network', status: 'available' },
        { id: 'road-risk', name: 'Road Risk', status: 'blocked' },
      ],
    },
    {
      name: 'Villages',
      layers: [
        { id: 'villages', name: 'Villages & Settlements', status: 'available' },
        { id: 'village-risk', name: 'Village Exposure', status: 'blocked' },
      ],
    },
  ];

  return (
    <div className="gis-layer-panel h-full flex flex-col">
      {/* HEADER */}
      <div className="px-4 py-3 border-b border-slate-700/60 bg-slate-900/70 flex-shrink-0">
        <h2 className="text-sm font-bold uppercase tracking-[0.15em] text-cyan-300">GIS LAYERS</h2>
        <p className="mt-0.5 text-[9px] uppercase tracking-[0.12em] text-slate-400">Data Stack Selector</p>
      </div>

      {/* SCROLLABLE GROUPS */}
      <div className="flex-1 overflow-y-auto">
        {LAYER_GROUPS.map((group) => (
          <div key={group.name} className="border-b border-slate-700/40">
            {/* GROUP HEADER */}
            <button
              type="button"
              onClick={() => toggleGroup(group.name)}
              className="layer-group-header w-full"
            >
              <ChevronDown
                size={12}
                className={`transition-transform flex-shrink-0 text-slate-400 ${expandedGroups.has(group.name) ? '' : '-rotate-90'}`}
              />
              <span className="flex-1 text-left text-slate-200">{group.name}</span>
            </button>

            {/* GROUP ITEMS */}
            {expandedGroups.has(group.name) && (
              <div className="bg-slate-900/30 border-t border-slate-700/30">
                {group.layers.map((layer) => {
                  const disabled = layer.status !== 'available';
                  const isVisible = visibleLayers.has(layer.id);
                  const isHeatmap = (layer.isHeatmap === true);

                  return (
                    <div
                      key={layer.id}
                      className={`layer-item px-3 py-2 ${disabled ? 'opacity-70' : ''}`}
                    >
                      <button
                        type="button"
                        disabled={disabled}
                        onClick={() => {
                          if (isHeatmap) onToggleHeatmap();
                          else onToggleLayer(layer.id);
                        }}
                        className={`p-1 rounded transition ${
                          disabled ? 'text-slate-500 cursor-not-allowed' : 'text-cyan-400 hover:bg-slate-700/50'
                        }`}
                        title={disabled ? `${layer.name} unavailable` : `Toggle ${layer.name}`}
                      >
                        {isHeatmap ? (heatmapEnabled ? <Eye size={12} /> : <EyeOff size={12} />) : (isVisible ? <Eye size={12} /> : <EyeOff size={12} />)}
                      </button>

                      <div className="flex-1 min-w-0 ml-1">
                        <p className="text-[10px] font-medium text-slate-100 truncate">{layer.name}</p>
                        <p className={`text-[8px] uppercase tracking-[0.08em] font-semibold mt-0.5 ${getStatusColor(layer.status)}`}>
                          {getStatusLabel(layer.status)}
                        </p>
                      </div>

                      {layer.status === 'blocked' && <ShieldAlert size={11} className="text-rose-400 flex-shrink-0" />}
                      {layer.status === 'awaiting' && <Database size={11} className="text-amber-400 flex-shrink-0" />}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* FOOTER INFO */}
      <div className="border-t border-slate-700/60 px-3 py-2.5 bg-slate-900/50 flex-shrink-0 text-[8px] text-slate-400">
        <p className="uppercase tracking-[0.1em] font-semibold text-slate-300 mb-1">KEY</p>
        <p className="leading-snug">✓ AVAILABLE = Real dataset | ⏳ AWAITING = Pending verification | 🔒 BLOCKED = Dependency blocked</p>
      </div>
    </div>
  );
}
