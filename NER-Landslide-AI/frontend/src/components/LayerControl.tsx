import React from 'react';

interface LayerControlProps {
  visibleLayers: Record<string, boolean>;
  onLayerToggle: (layerId: string) => void;
}

export function LayerControl({ visibleLayers, onLayerToggle }: LayerControlProps) {
  const layerGroups = [
    {
      name: 'Administrative',
      layers: [
        { id: 'ner_boundary', name: 'NER Boundary', available: true },
        { id: 'state_boundaries', name: 'State Boundaries', available: true },
        { id: 'districts', name: 'Districts', available: false },
      ],
    },
    {
      name: 'Landslide',
      layers: [
        { id: 'gsi_landslides', name: 'Historical GSI Landslides', available: true },
      ],
    },
    {
      name: 'Terrain',
      layers: [
        { id: 'elevation', name: 'Elevation (DEM)', available: false },
        { id: 'slope', name: 'Slope', available: false },
        { id: 'aspect', name: 'Aspect', available: false },
      ],
    },
    {
      name: 'Environment',
      layers: [
        { id: 'rainfall', name: 'Rainfall', available: false },
        { id: 'weather', name: 'Weather', available: false },
        { id: 'soil_moisture', name: 'Soil Moisture', available: false },
      ],
    },
    {
      name: 'Risk',
      layers: [
        { id: 'susceptibility', name: 'Susceptibility', available: false },
        { id: 'current_risk', name: 'Current Risk', available: false },
      ],
    },
  ];

  return (
    <div className="rounded-lg border border-slate-700/40 bg-slate-900/50 p-4">
      <h3 className="mb-4 font-semibold text-slate-50">Map Layers</h3>
      <div className="space-y-4">
        {layerGroups.map((group) => (
          <div key={group.name}>
            <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-400">{group.name}</h4>
            <div className="mt-2 space-y-2">
              {group.layers.map((layer) => (
                <label key={layer.id} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={visibleLayers[layer.id] || false}
                    onChange={() => onLayerToggle(layer.id)}
                    disabled={!layer.available}
                    className="h-4 w-4 rounded border-slate-600 bg-slate-800 text-emerald-600 disabled:opacity-50"
                  />
                  <span className={`text-sm ${layer.available ? 'text-slate-300' : 'text-slate-600'}`}>
                    {layer.name}
                    {!layer.available && (
                      <span className="ml-1 text-xs text-slate-600">(awaiting data)</span>
                    )}
                  </span>
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
