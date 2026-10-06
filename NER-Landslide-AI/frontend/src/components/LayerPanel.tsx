import React from 'react';
import { ChevronDown, Eye, EyeOff } from 'lucide-react';

interface LayerPanelProps {
  visibleLayers: Set<string>;
  onToggleLayer: (layerId: string) => void;
  onToggleHeatmap: () => void;
  heatmapEnabled: boolean;
}

const LAYER_GROUPS = [
  {
    name: 'BASE MAPS',
    layers: [
      { id: 'osm-streets', name: 'Street Map', status: 'available' },
      { id: 'osm-light', name: 'Light Map', status: 'available' },
    ]
  },
  {
    name: 'ADMINISTRATIVE',
    layers: [
      { id: 'state-boundaries', name: 'State Boundaries', status: 'available' },
      { id: 'district-boundaries', name: 'District Boundaries', status: 'awaiting' },
      { id: 'taluk-boundaries', name: 'Taluk Boundaries', status: 'awaiting' },
    ]
  },
  {
    name: 'LANDSLIDES',
    layers: [
      { id: 'landslides', name: 'Historical Events (33,904)', status: 'available' },
      { id: 'landslides-heatmap', name: 'Historical Density', status: 'available' },
      { id: 'susceptibility', name: 'Susceptibility Map', status: 'blocked' },
    ]
  },
  {
    name: 'TERRAIN',
    layers: [
      { id: 'dem', name: 'Digital Elevation Model', status: 'awaiting' },
      { id: 'slope', name: 'Slope Analysis', status: 'blocked' },
      { id: 'aspect', name: 'Aspect Analysis', status: 'blocked' },
    ]
  },
  {
    name: 'RAINFALL & CLIMATE',
    layers: [
      { id: 'rainfall', name: 'Rainfall Distribution', status: 'awaiting' },
      { id: 'weather', name: 'Current Weather', status: 'awaiting' },
      { id: 'monsoon', name: 'Monsoon Tracking', status: 'blocked' },
    ]
  },
  {
    name: 'SOIL & GEOLOGY',
    layers: [
      { id: 'soil', name: 'Soil Properties', status: 'awaiting' },
      { id: 'geology', name: 'Geological Map', status: 'awaiting' },
      { id: 'lithology', name: 'Lithology', status: 'blocked' },
    ]
  },
  {
    name: 'HYDROLOGY',
    layers: [
      { id: 'rivers', name: 'River Network', status: 'awaiting' },
      { id: 'water-bodies', name: 'Water Bodies', status: 'awaiting' },
      { id: 'drainage', name: 'Drainage Analysis', status: 'blocked' },
    ]
  },
  {
    name: 'REMOTE SENSING',
    layers: [
      { id: 'ndvi', name: 'Vegetation Index (NDVI)', status: 'awaiting' },
      { id: 'landcover', name: 'Land Cover Classification', status: 'awaiting' },
      { id: 'forest-density', name: 'Forest Density', status: 'awaiting' },
    ]
  },
  {
    name: 'INFRASTRUCTURE',
    layers: [
      { id: 'roads', name: 'Road Network', status: 'available' },
      { id: 'villages', name: 'Villages & Settlements', status: 'available' },
      { id: 'hospitals', name: 'Hospitals & Clinics', status: 'awaiting' },
      { id: 'schools', name: 'Schools', status: 'awaiting' },
    ]
  },
  {
    name: 'RISK & HAZARD',
    layers: [
      { id: 'hazard', name: 'Hazard Assessment', status: 'blocked' },
      { id: 'exposure', name: 'Exposure Analysis', status: 'blocked' },
      { id: 'vulnerability', name: 'Vulnerability Index', status: 'blocked' },
      { id: 'risk', name: 'Risk Map (Final)', status: 'blocked' },
    ]
  },
  {
    name: 'ALERTS & WARNINGS',
    layers: [
      { id: 'alerts', name: 'Active Alerts', status: 'blocked' },
      { id: 'warnings', name: 'Warnings', status: 'blocked' },
      { id: 'incidents', name: 'Recent Incidents', status: 'awaiting' },
    ]
  },
];

export function LayerPanel({ visibleLayers, onToggleLayer, onToggleHeatmap, heatmapEnabled }: LayerPanelProps) {
  const [expandedGroups, setExpandedGroups] = React.useState<Set<string>>(
    new Set(['LANDSLIDES', 'ADMINISTRATIVE', 'INFRASTRUCTURE'])
  );

  const toggleGroup = (groupName: string) => {
    const newExpanded = new Set(expandedGroups);
    if (newExpanded.has(groupName)) {
      newExpanded.delete(groupName);
    } else {
      newExpanded.add(groupName);
    }
    setExpandedGroups(newExpanded);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available':
        return 'text-green-600';
      case 'awaiting':
        return 'text-amber-600';
      case 'blocked':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'available':
        return '✓ Available';
      case 'awaiting':
        return '⏳ Awaiting Data';
      case 'blocked':
        return '🔒 Blocked';
      default:
        return status;
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <h2 className="text-lg font-bold text-gray-900">Map Layers</h2>
        <p className="text-xs text-gray-500 mt-1">Click to toggle layer visibility</p>
      </div>

      <div className="flex-1 overflow-y-auto">
        {LAYER_GROUPS.map((group) => (
          <div key={group.name} className="border-b border-gray-100">
            <button
              onClick={() => toggleGroup(group.name)}
              className="w-full px-4 py-3 flex items-center gap-2 hover:bg-gray-50 transition-colors"
            >
              <ChevronDown
                size={16}
                className={`transform transition-transform ${
                  expandedGroups.has(group.name) ? '' : '-rotate-90'
                }`}
              />
              <span className="font-semibold text-sm text-gray-900 flex-1 text-left">
                {group.name}
              </span>
            </button>

            {expandedGroups.has(group.name) && (
              <div className="bg-gray-50 border-t border-gray-100">
                {group.layers.map((layer) => (
                  <div
                    key={layer.id}
                    className="px-4 py-2 flex items-center gap-2 hover:bg-gray-100 transition-colors"
                  >
                    <button
                      onClick={() => onToggleLayer(layer.id)}
                      className="flex-shrink-0 p-1 hover:bg-gray-200 rounded"
                    >
                      {visibleLayers.has(layer.id) ? (
                        <Eye size={16} className="text-blue-600" />
                      ) : (
                        <EyeOff size={16} className="text-gray-400" />
                      )}
                    </button>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-gray-900 truncate">
                        {layer.name}
                      </p>
                      <p className={`text-xs ${getStatusColor(layer.status)}`}>
                        {getStatusLabel(layer.status)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="text-xs text-gray-600">
          <p className="font-semibold mb-2">Legend</p>
          <ul className="space-y-1">
            <li>✓ Data Available (33,904 events)</li>
            <li>⏳ Awaiting Data (in progress)</li>
            <li>🔒 Blocked (dependencies not met)</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
