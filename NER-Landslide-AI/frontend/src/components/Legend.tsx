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
        color: '#c0392b',
        description: '33,904 verified events (NOT current risk)',
      });
    }

    if (visibleLayers.has('landslides-heatmap') && heatmapEnabled) {
      items.push({
        label: '⬚ Historical Density Heatmap',
        color: '#bd2d1f',
        description: 'Spatial clustering of historical events (past occurrence)',
      });
    }

    if (visibleLayers.has('state-boundaries')) {
      items.push({
        label: '─ State Boundaries',
        color: '#2c3e50',
        description: 'Administrative state boundaries of NER region',
      });
    }

    if (visibleLayers.has('roads')) {
      items.push({
        label: '─ Road Network',
        color: '#95a5a6',
        description: 'Primary and secondary road network',
      });
    }

    if (visibleLayers.has('villages')) {
      items.push({
        label: '● Villages & Settlements',
        color: '#3498db',
        description: 'Populated villages in the region',
      });
    }

    return items;
  };

  const items = getLegendItems();

  if (items.length === 0) {
    return (
      <div className="text-xs text-gray-500">
        <p className="font-semibold">No layers enabled</p>
        <p className="mt-1">Enable layers from the left panel to view legend</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <p className="font-bold text-sm text-gray-900">Map Legend</p>
      <div className="space-y-2">
        {items.map((item, idx) => (
          <div key={idx} className="flex items-start gap-2">
            <div
              className="w-3 h-3 rounded-full flex-shrink-0 mt-1"
              style={{ backgroundColor: item.color }}
            />
            <div>
              <p className="text-xs font-semibold text-gray-900">{item.label}</p>
              <p className="text-xs text-gray-600">{item.description}</p>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-3 p-2 bg-amber-50 border border-amber-200 rounded text-xs text-amber-900">
        <p className="font-semibold">⚠ Important Note</p>
        <p className="mt-1">
          Historical data shows PAST occurrences. Current risk assessment requires verified environmental data (DEM, rainfall, soil) not yet available.
        </p>
      </div>
    </div>
  );
}
