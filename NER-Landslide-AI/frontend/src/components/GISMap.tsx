import React, { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { LayerPanel } from './LayerPanel';
import { InfoPanel } from './InfoPanel';
import { MapControls } from './MapControls';
import { Legend } from './Legend';
import { SearchBox } from './SearchBox';
import { RouteSystem } from './RouteSystem';
import { AlertCenter } from './AlertCenter';
import { EnvironmentalPanel } from './EnvironmentalPanel';
import { DisasterAIAssistant } from './DisasterAIAssistant';
import { DashboardStatus } from './DashboardStatus';

interface Feature {
  type: 'Feature';
  id: string | number;
  properties: Record<string, any>;
  geometry: {
    type: string;
    coordinates: any[];
  };
}

interface SelectedFeature {
  type: string;
  data: Feature | null;
}

const BASEMAP_MAP: Record<string, string> = {
  street: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
  satellite: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
  topographic: 'https://a.tile.opentopomap.org/{z}/{x}/{y}.png',
  terrain: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
  hillshade: 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}.png',
};

export function GISMap() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [selectedFeature, setSelectedFeature] = useState<SelectedFeature | null>(null);
  const [visibleLayers, setVisibleLayers] = useState<Set<string>>(new Set([
    'landslides',
    'state-boundaries',
    'roads',
    'villages',
  ]));
  const [basemap, setBasemap] = useState<string>('street');
  const [heatmapEnabled, setHeatmapEnabled] = useState(true);
  const [showRouteSystem, setShowRouteSystem] = useState(false);
  const [showAlertCenter, setShowAlertCenter] = useState(false);
  const [showEnvironmentalPanel, setShowEnvironmentalPanel] = useState(false);
  const [showDisasterAI, setShowDisasterAI] = useState(false);
  const [showDashboardStatus, setShowDashboardStatus] = useState(false);

  const getBasemapStyle = (styleKey: string) => {
    const tileUrl = BASEMAP_MAP[styleKey] || BASEMAP_MAP.street;

    return JSON.stringify({
      version: 8,
      sources: {
        base: {
          type: 'raster',
          tiles: [tileUrl],
          tileSize: 256,
          attribution: '© OpenStreetMap contributors, © Esri, © Stadia Maps',
        },
      },
      layers: [{ id: 'base-layer', type: 'raster', source: 'base' }],
      glyphs: 'https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf',
      sprite: 'https://demotiles.maplibre.org/sprite',
    });
  };

  const addMapLayers = () => {
    if (!map.current?.isStyleLoaded()) return;

    if (!map.current.getSource('landslides')) {
      map.current.addSource('landslides', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] },
        cluster: true,
        clusterMaxZoom: 14,
        clusterRadius: 50,
      });

      map.current.addLayer({
        id: 'landslides-cluster',
        type: 'circle',
        source: 'landslides',
        filter: ['has', 'point_count'],
        paint: {
          'circle-color': '#f87171',
          'circle-radius': ['step', ['get', 'point_count'], 18, 5, 22, 10, 28],
          'circle-opacity': 0.8,
        },
      });

      map.current.addLayer({
        id: 'landslides-cluster-count',
        type: 'symbol',
        source: 'landslides',
        filter: ['has', 'point_count'],
        layout: {
          'text-field': ['get', 'point_count_abbreviated'],
          'text-size': 11,
          'text-font': ['Open Sans Regular'],
          'text-allow-overlap': true,
        },
        paint: { 'text-color': '#ffffff' },
      });

      map.current.addLayer({
        id: 'landslides',
        type: 'circle',
        source: 'landslides',
        filter: ['!', ['has', 'point_count']],
        paint: {
          'circle-color': '#dc2626',
          'circle-radius': 6,
          'circle-opacity': 0.9,
          'circle-stroke-color': '#fecaca',
          'circle-stroke-width': 1.5,
        },
      });
    }

    if (!map.current.getSource('landslides-heatmap')) {
      map.current.addSource('landslides-heatmap', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] },
      });

      map.current.addLayer({
        id: 'landslides-heatmap',
        type: 'heatmap',
        source: 'landslides-heatmap',
        maxzoom: 15,
        paint: {
          'heatmap-weight': 1,
          'heatmap-intensity': 1,
          'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 0, 2, 9, 18],
          'heatmap-opacity': 0.72,
          'heatmap-color': [
            'interpolate',
            ['linear'],
            ['heatmap-density'],
            0, '#ffffff00',
            0.2, '#fef3c7',
            0.4, '#fbbf24',
            0.6, '#f97316',
            0.8, '#ef4444',
            1, '#7f1d1d',
          ],
        },
      });
    }

    if (!map.current.getSource('state-boundaries')) {
      map.current.addSource('state-boundaries', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] },
      });
      map.current.addLayer({
        id: 'state-boundaries',
        type: 'line',
        source: 'state-boundaries',
        paint: {
          'line-color': '#38bdf8',
          'line-width': 1.5,
          'line-opacity': 0.75,
        },
      });
    }

    if (!map.current.getSource('villages')) {
      map.current.addSource('villages', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] },
      });
      map.current.addLayer({
        id: 'villages',
        type: 'circle',
        source: 'villages',
        paint: {
          'circle-radius': 4,
          'circle-color': '#7dd3fc',
          'circle-opacity': 0.8,
          'circle-stroke-color': '#e0f2fe',
          'circle-stroke-width': 1,
        },
      });
    }

    if (!map.current.getSource('roads')) {
      map.current.addSource('roads', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] },
      });
      map.current.addLayer({
        id: 'roads',
        type: 'line',
        source: 'roads',
        paint: {
          'line-color': '#cbd5e1',
          'line-width': 1.5,
          'line-opacity': 0.8,
        },
      });
    }

    Object.entries({
      landslides: 'visible',
      'landslides-cluster': 'visible',
      'landslides-cluster-count': 'visible',
      'landslides-heatmap': heatmapEnabled ? 'visible' : 'none',
      'state-boundaries': visibleLayers.has('state-boundaries') ? 'visible' : 'none',
      villages: visibleLayers.has('villages') ? 'visible' : 'none',
      roads: visibleLayers.has('roads') ? 'visible' : 'none',
    }).forEach(([layerId, vis]) => {
      try {
        if (map.current?.getLayer(layerId)) {
          map.current?.setLayoutProperty(layerId, 'visibility', vis as any);
        }
      } catch (error) {
        console.debug(`Layer ${layerId} not ready:`, error);
      }
    });
  };

  const addMapInteractions = () => {
    if (!map.current) return;

    map.current.on('click', 'landslides', (event) => {
      const feature = event.features?.[0] as Feature | undefined;
      if (feature) setSelectedFeature({ type: 'landslide', data: feature });
    });

    map.current.on('click', 'state-boundaries', (event) => {
      const feature = event.features?.[0] as Feature | undefined;
      if (feature) setSelectedFeature({ type: 'state', data: feature });
    });

    map.current.on('click', 'villages', (event) => {
      const feature = event.features?.[0] as Feature | undefined;
      if (feature) setSelectedFeature({ type: 'village', data: feature });
    });

    ['landslides', 'state-boundaries', 'villages', 'roads'].forEach((layerId) => {
      map.current?.on('mouseenter', layerId, () => {
        map.current!.getCanvas().style.cursor = 'pointer';
      });
      map.current?.on('mouseleave', layerId, () => {
        map.current!.getCanvas().style.cursor = '';
      });
    });
  };

  const loadLandslideData = async () => {
    if (!map.current?.isStyleLoaded()) return;

    try {
      const response = await fetch('/api/landslides');
      const data = await response.json();
      const source = map.current.getSource('landslides') as any;
      const densitySource = map.current.getSource('landslides-heatmap') as any;
      const features = data?.features || [];

      if (source) source.setData({ type: 'FeatureCollection', features });
      if (densitySource) densitySource.setData({ type: 'FeatureCollection', features });
    } catch (error) {
      console.error('Failed to load landslide data:', error);
    }
  };

  const loadVillageData = async () => {
    if (!map.current?.isStyleLoaded()) return;

    try {
      const response = await fetch('/api/villages');
      const data = await response.json();
      const source = map.current.getSource('villages') as any;
      if (source && data?.features) {
        source.setData({ type: 'FeatureCollection', features: data.features });
      }
    } catch (error) {
      console.error('Failed to load village data:', error);
    }
  };

  const loadRoadData = async () => {
    if (!map.current?.isStyleLoaded()) return;

    try {
      const response = await fetch('/api/roads');
      const data = await response.json();
      const source = map.current.getSource('roads') as any;
      if (source && data?.features) {
        source.setData({ type: 'FeatureCollection', features: data.features });
      }
    } catch (error) {
      console.error('Failed to load road data:', error);
    }
  };

  const loadAdministrativeData = async () => {
    if (!map.current?.isStyleLoaded()) return;

    try {
      const response = await fetch('/api/states');
      const data = await response.json();
      if (data?.states && map.current.getSource('state-boundaries')) {
        const source = map.current.getSource('state-boundaries') as any;
        if (source && Array.isArray(data.states)) {
          const features = data.states.map((state: string, index: number) => ({
            type: 'Feature',
            id: `state-${index}`,
            properties: { name: state, state_name: state, status: 'verified' },
            geometry: {
              type: 'Point',
              coordinates: [93.5 + index * 0.2, 26.5 + (index % 2 === 0 ? 0.5 : -0.5)],
            },
          }));
          source.setData({ type: 'FeatureCollection', features });
        }
      }
    } catch (error) {
      console.error('Failed to load state metadata:', error);
    }
  };

  useEffect(() => {
    if (!mapContainer.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: getBasemapStyle(basemap),
      center: [93.5, 26.5],
      zoom: 6,
      minZoom: 4,
      maxZoom: 18,
      pitch: 0,
      bearing: 0,
    });

    map.current.on('load', () => {
      setLoaded(true);
      addMapLayers();
      addMapInteractions();
    });

    return () => map.current?.remove();
  }, []);

  useEffect(() => {
    if (loaded) {
      loadLandslideData();
      loadAdministrativeData();
      loadVillageData();
      loadRoadData();
    }
  }, [loaded]);

  const changeBasemap = (newBasemap: string) => {
    setBasemap(newBasemap);
    if (map.current) {
      map.current.setStyle(getBasemapStyle(newBasemap));
      setTimeout(() => {
        if (map.current?.isStyleLoaded()) {
          addMapLayers();
          addMapInteractions();
        }
      }, 120);
    }
  };

  const toggleLayer = (layerId: string) => {
    if (!map.current?.isStyleLoaded()) return;
    const next = new Set(visibleLayers);
    if (next.has(layerId)) next.delete(layerId); else next.add(layerId);
    setVisibleLayers(next);

    try {
      if (map.current.getLayer(layerId)) {
        map.current.setLayoutProperty(layerId, 'visibility', next.has(layerId) ? 'visible' : 'none');
      }
    } catch (error) {
      console.error(`Failed to toggle layer ${layerId}:`, error);
    }
  };

  useEffect(() => {
    if (!map.current?.isStyleLoaded()) return;
    ['landslides', 'landslides-cluster', 'landslides-cluster-count', 'landslides-heatmap', 'state-boundaries', 'villages', 'roads'].forEach((layerId) => {
      if (map.current?.getLayer(layerId)) {
        const visible = layerId === 'landslides-heatmap' ? (heatmapEnabled && visibleLayers.has('landslides-heatmap')) : visibleLayers.has(layerId);
        map.current.setLayoutProperty(layerId, 'visibility', visible ? 'visible' : 'none');
      }
    });
  }, [visibleLayers, heatmapEnabled]);

  return (
    <div className="w-full h-screen flex flex-col bg-slate-950 text-slate-100 overflow-hidden">
      {/* PROFESSIONAL GIS HEADER WITH AN.E GUARDINAS BRANDING */}
      <div className="border-b border-slate-700/60 bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950 backdrop-blur-sm px-4 py-3 shadow-lg">
        <div className="flex items-center justify-between gap-6">
          {/* LEFT: NER APPLICATION TITLE */}
          <div className="flex-1 min-w-0">
            <h1 className="text-sm font-bold text-white tracking-tight">NER LANDSLIDE GUARD AI</h1>
            <p className="text-[11px] text-slate-400 mt-0.5">Landslide Risk Monitoring & Early Warning System</p>
          </div>

          {/* CENTER: SYSTEM STATUS BADGES */}
          <div className="flex items-center gap-2 px-4 py-2 bg-slate-800/50 rounded-lg border border-slate-700/50">
            <div className="flex items-center gap-1">
              <span className="text-[9px] uppercase tracking-[0.16em] text-slate-400">HISTORICAL DATA</span>
              <span className="rounded px-1.5 py-0.5 bg-emerald-500/20 border border-emerald-600/60 text-[8px] font-semibold text-emerald-200 uppercase">VERIFIED</span>
            </div>
            <span className="text-slate-600">|</span>
            <div className="flex items-center gap-1">
              <span className="text-[9px] uppercase tracking-[0.16em] text-slate-400">CURRENT RISK</span>
              <span className="rounded px-1.5 py-0.5 bg-red-500/20 border border-red-600/60 text-[8px] font-semibold text-red-200 uppercase">BLOCKED</span>
            </div>
            <span className="text-slate-600">|</span>
            <div className="flex items-center gap-1">
              <span className="text-[9px] uppercase tracking-[0.16em] text-slate-400">ML</span>
              <span className="rounded px-1.5 py-0.5 bg-red-500/20 border border-red-600/60 text-[8px] font-semibold text-red-200 uppercase">BLOCKED</span>
            </div>
            <span className="text-slate-600">|</span>
            <div className="flex items-center gap-1">
              <span className="text-[9px] uppercase tracking-[0.16em] text-slate-400">ALERTS</span>
              <span className="rounded px-1.5 py-0.5 bg-red-500/20 border border-red-600/60 text-[8px] font-semibold text-red-200 uppercase">BLOCKED</span>
            </div>
          </div>

          {/* RIGHT: AN.E GUARDINAS BRANDING */}
          <div className="text-right">
            <div className="text-xs font-semibold text-cyan-300 uppercase tracking-[0.14em]">AN.E GUARDINAS</div>
            <div className="text-[10px] text-slate-400 mt-1">Disaster Management</div>
          </div>
        </div>
      </div>

      {/* BASEMAP SELECTOR BAR */}
      <div className="flex items-center gap-2 px-4 py-2 border-b border-slate-700/60 bg-slate-950/80 backdrop-blur-sm">
        <span className="text-[9px] uppercase tracking-[0.16em] text-slate-400 font-semibold">Base:</span>
        <div className="flex items-center gap-1 rounded-md border border-slate-700/50 bg-slate-900/60 p-0.5">
          { [
            { key: 'street', label: 'STREET' },
            { key: 'satellite', label: 'SATELLITE' },
            { key: 'topographic', label: 'TOPO' },
            { key: 'terrain', label: 'TERRAIN' },
            { key: 'hillshade', label: 'HILLSHADE' },
          ].map(item => (
            <button
              key={item.key}
              type="button"
              onClick={() => changeBasemap(item.key)}
              title={`Switch to ${item.label} basemap`}
              className={`px-2.5 py-1 text-[8px] font-bold uppercase tracking-[0.14em] rounded transition-colors ${
                basemap === item.key
                  ? 'bg-cyan-500/80 text-slate-950 shadow-sm'
                  : 'text-slate-300 hover:bg-slate-700/60 hover:text-white'
              }`}
            >
              {item.label}
            </button>
          )) }
        </div>

        <div className="flex-1" />

        {/* ACTION BUTTONS */}
        <div className="flex items-center gap-1 rounded-md border border-slate-700/50 bg-slate-900/60 p-0.5">
          <button
            onClick={() => setShowDashboardStatus(!showDashboardStatus)}
            title="System status"
            className="px-2.5 py-1 text-[8px] font-bold uppercase tracking-[0.12em] rounded hover:bg-slate-700/60 text-slate-300 hover:text-white transition-colors"
          >
            STATUS
          </button>
          <button
            onClick={() => setShowRouteSystem(!showRouteSystem)}
            title="Route planner"
            className="px-2.5 py-1 text-[8px] font-bold uppercase tracking-[0.12em] rounded hover:bg-slate-700/60 text-slate-300 hover:text-white transition-colors"
          >
            ROUTE
          </button>
          <button
            onClick={() => setShowAlertCenter(!showAlertCenter)}
            title="View alerts"
            className="px-2.5 py-1 text-[8px] font-bold uppercase tracking-[0.12em] rounded hover:bg-slate-700/60 text-slate-300 hover:text-white transition-colors"
          >
            ALERTS
          </button>
          <button
            onClick={() => setShowEnvironmentalPanel(!showEnvironmentalPanel)}
            title="Environmental data"
            className="px-2.5 py-1 text-[8px] font-bold uppercase tracking-[0.12em] rounded hover:bg-slate-700/60 text-slate-300 hover:text-white transition-colors"
          >
            ENV
          </button>
          <button
            onClick={() => setShowDisasterAI(!showDisasterAI)}
            title="Ask Disaster AI"
            className="px-2.5 py-1 text-[8px] font-bold uppercase tracking-[0.12em] rounded hover:bg-slate-700/60 text-slate-300 hover:text-white transition-colors"
          >
            AI
          </button>
        </div>

        <div className="ml-2" />

        <SearchBox map={map.current} />
        <MapControls map={map.current} />
      </div>

      {/* MAIN GIS WORKSPACE: LEFT LAYER PANEL + MAP + RIGHT INFO PANEL */}
      <div className="flex-1 flex min-h-0 overflow-hidden">
        {/* LEFT: QGIS-STYLE LAYER PANEL */}
        <aside className="w-72 border-r border-slate-700/60 bg-slate-950/95 flex flex-col">
          <LayerPanel
            visibleLayers={visibleLayers}
            onToggleLayer={toggleLayer}
            onToggleHeatmap={() => setHeatmapEnabled(value => !value)}
            heatmapEnabled={heatmapEnabled}
          />
        </aside>

        {/* CENTER: MAPLIBRE MAP FILLS REMAINING SPACE */}
        <main className="relative flex-1 min-w-0 bg-slate-950 overflow-hidden">
          <div ref={mapContainer} className="w-full h-full" />

          {/* LEGEND CARD: BOTTOM-LEFT FLOATING */}
          <div className="absolute left-3 bottom-16 w-80 rounded-lg border border-slate-700/70 bg-slate-950/95 p-3 shadow-2xl backdrop-blur-sm z-10">
            <Legend visibleLayers={visibleLayers} heatmapEnabled={heatmapEnabled} />
          </div>
        </main>

        {/* RIGHT: LOCATION INTELLIGENCE INSPECTOR */}
        <aside className="w-80 border-l border-slate-700/60 bg-slate-950/95 flex flex-col overflow-hidden">
          <InfoPanel selectedFeature={selectedFeature} />
        </aside>
      </div>

      {/* BOTTOM STATUS BAR */}
      <div className="border-t border-slate-700/60 bg-slate-950/90 backdrop-blur-sm px-4 py-2 flex items-center justify-between text-[9px]">
        <div className="flex-1 min-w-0">
          <span className="text-slate-400 uppercase tracking-[0.12em] font-semibold">SYSTEM NOTICE:</span>
          <span className="text-slate-300 ml-2">Automated warning system is not operational. Current predictive risk is BLOCKED pending verified environmental data and ML model validation.</span>
        </div>
        <div className="flex-shrink-0 ml-4 flex items-center gap-2">
          <span className="text-slate-400 uppercase tracking-[0.12em]">STATUS:</span>
          <span className="text-emerald-300 font-semibold">ONLINE</span>
        </div>
      </div>

      {/* FLOATING PANELS */}
      {showDashboardStatus && <DashboardStatus onClose={() => setShowDashboardStatus(false)} />}
      {showRouteSystem && <RouteSystem map={map.current} onClose={() => setShowRouteSystem(false)} />}
      {showAlertCenter && <AlertCenter onClose={() => setShowAlertCenter(false)} />}
      {showEnvironmentalPanel && <EnvironmentalPanel onClose={() => setShowEnvironmentalPanel(false)} />}
      {showDisasterAI && <DisasterAIAssistant onClose={() => setShowDisasterAI(false)} selectedLocation={selectedFeature?.data?.properties?.name} />}
    </div>
  );
}
