import React, { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { LayerPanel } from './LayerPanel';
import { InfoPanel } from './InfoPanel';
import { MapControls } from './MapControls';
import { Legend } from './Legend';
import { SearchBox } from './SearchBox';

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

export function GISMap() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [selectedFeature, setSelectedFeature] = useState<SelectedFeature | null>(null);
  const [visibleLayers, setVisibleLayers] = useState<Set<string>>(new Set([
    'osm-streets',
    'landslides',
    'state-boundaries',
  ]));
  const [basemap, setBasemap] = useState<string>('osm-streets');
  const [heatmapEnabled, setHeatmapEnabled] = useState(false);

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: getBasemapStyle('osm-streets'),
      center: [93.5, 26.5], // NER region center
      zoom: 6,
      pitch: 0,
      bearing: 0,
    });

    map.current.on('load', () => {
      setLoaded(true);
      addMapLayers();
      addMapInteractions();
    });

    return () => {
      map.current?.remove();
    };
  }, []);

  const getBasemapStyle = (style: string): string => {
    const styles: Record<string, string> = {
      'osm-streets': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
      'osm-light': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    };

    // Using OpenStreetMap raster tiles style
    return JSON.stringify({
      version: 8,
      sources: {
        'osm-tiles': {
          type: 'raster',
          tiles: [style === 'osm-streets' || style === 'osm-light' 
            ? 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
            : 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
          tileSize: 256,
          attribution: '© OpenStreetMap contributors'
        }
      },
      layers: [{
        id: 'osm-background',
        type: 'raster',
        source: 'osm-tiles',
      }]
    });
  };

  const changeBasemap = (newBasemap: string) => {
    setBasemap(newBasemap);
    if (map.current) {
      map.current.setStyle(getBasemapStyle(newBasemap));
      // Re-add layers after style change
      setTimeout(() => {
        if (map.current?.isStyleLoaded()) {
          addMapLayers();
          addMapInteractions();
        }
      }, 100);
    }
  };

  const addMapLayers = () => {
    if (!map.current?.isStyleLoaded()) return;

    // Historical landslides GeoJSON source
    if (!map.current.getSource('landslides')) {
      map.current.addSource('landslides', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: []
        },
        cluster: true,
        clusterMaxZoom: 14,
        clusterRadius: 50,
      });

      // Landslide cluster layer
      map.current.addLayer({
        id: 'landslides-cluster',
        type: 'circle',
        source: 'landslides',
        filter: ['has', 'point_count'],
        paint: {
          'circle-color': '#e74c3c',
          'circle-radius': [
            'step',
            ['get', 'point_count'],
            20,
            5,
            25,
            10,
            30,
          ],
          'circle-opacity': 0.8,
        },
      });

      // Cluster labels
      map.current.addLayer({
        id: 'landslides-cluster-count',
        type: 'symbol',
        source: 'landslides',
        filter: ['has', 'point_count'],
        layout: {
          'text-field': '{point_count_abbreviated}',
          'text-font': ['Open Sans Regular'],
          'text-size': 12,
          'text-allow-overlap': true,
        },
        paint: {
          'text-color': 'white',
        },
      });

      // Individual landslide points
      map.current.addLayer({
        id: 'landslides',
        type: 'circle',
        source: 'landslides',
        filter: ['!', ['has', 'point_count']],
        paint: {
          'circle-color': '#c0392b',
          'circle-radius': 6,
          'circle-opacity': 0.8,
          'circle-stroke-width': 2,
          'circle-stroke-color': '#e74c3c',
        },
      });
    }

    // Heatmap layer for historical landslide density
    if (!map.current.getSource('landslides-heatmap')) {
      map.current.addSource('landslides-heatmap', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: []
        }
      });

      map.current.addLayer({
        id: 'landslides-heatmap',
        type: 'heatmap',
        source: 'landslides-heatmap',
        maxzoom: 15,
        paint: {
          'heatmap-weight': 1,
          'heatmap-intensity': 1,
          'heatmap-color': [
            'interpolate',
            ['linear'],
            ['heatmap-density'],
            0, '#ffffcc',
            0.2, '#ffeda0',
            0.4, '#fed976',
            0.6, '#feb24c',
            0.8, '#fd8d3c',
            1, '#bd2d1f',
          ],
          'heatmap-radius': [
            'interpolate',
            ['linear'],
            ['zoom'],
            0, 2,
            9, 20,
          ],
          'heatmap-opacity': 0.7,
        },
      }, basemap === 'satellite' ? 'landslides' : undefined);
    }

    // State boundaries
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
          'line-color': '#2c3e50',
          'line-width': 2,
          'line-opacity': 0.6,
        },
      });
    }

    // Village points
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
          'circle-color': '#3498db',
          'circle-opacity': 0.6,
        },
      });
    }

    // Roads
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
          'line-color': '#95a5a6',
          'line-width': 2,
          'line-opacity': 0.5,
        },
      });
    }
  };

  const addMapInteractions = () => {
    if (!map.current) return;

    // Click on landslide
    map.current.on('click', 'landslides', (e) => {
      if (e.features && e.features[0]) {
        setSelectedFeature({
          type: 'landslide',
          data: e.features[0] as Feature,
        });
      }
    });

    map.current.on('click', 'state-boundaries', (e) => {
      if (e.features && e.features[0]) {
        setSelectedFeature({
          type: 'state',
          data: e.features[0] as Feature,
        });
      }
    });

    map.current.on('click', 'villages', (e) => {
      if (e.features && e.features[0]) {
        setSelectedFeature({
          type: 'village',
          data: e.features[0] as Feature,
        });
      }
    });

    // Change cursor on hover
    ['landslides', 'state-boundaries', 'villages'].forEach(layerId => {
      map.current?.on('mouseenter', layerId, () => {
        if (map.current) map.current.getCanvas().style.cursor = 'pointer';
      });
      map.current?.on('mouseleave', layerId, () => {
        if (map.current) map.current.getCanvas().style.cursor = '';
      });
    });
  };

  const loadLandslideData = async () => {
    if (!map.current?.isStyleLoaded()) return;

    try {
      const response = await fetch('/api/landslides');
      const data = await response.json();

      if (data.features) {
        const source = map.current.getSource('landslides') as any;
        const heatmapSource = map.current.getSource('landslides-heatmap') as any;

        if (source) {
          source.setData({
            type: 'FeatureCollection',
            features: data.features,
          });
        }

        if (heatmapSource) {
          heatmapSource.setData({
            type: 'FeatureCollection',
            features: data.features,
          });
        }
      }
    } catch (error) {
      console.error('Failed to load landslide data:', error);
    }
  };

  const loadAdministrativeData = async () => {
    if (!map.current?.isStyleLoaded()) return;

    try {
      const response = await fetch('/api/states');
      const data = await response.json();
      // State boundaries would come from a separate endpoint
    } catch (error) {
      console.error('Failed to load administrative data:', error);
    }
  };

  const loadVillageData = async () => {
    if (!map.current?.isStyleLoaded()) return;

    try {
      const response = await fetch('/api/villages');
      const data = await response.json();

      if (data.features) {
        const source = map.current.getSource('villages') as any;
        if (source) {
          source.setData({
            type: 'FeatureCollection',
            features: data.features,
          });
        }
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

      if (data.features) {
        const source = map.current.getSource('roads') as any;
        if (source) {
          source.setData({
            type: 'FeatureCollection',
            features: data.features,
          });
        }
      }
    } catch (error) {
      console.error('Failed to load road data:', error);
    }
  };

  // Load data when map is loaded
  useEffect(() => {
    if (loaded) {
      loadLandslideData();
      loadAdministrativeData();
      loadVillageData();
      loadRoadData();
    }
  }, [loaded]);

  // Toggle layer visibility
  const toggleLayer = (layerId: string) => {
    if (!map.current?.isStyleLoaded()) return;

    const newVisible = new Set(visibleLayers);
    if (newVisible.has(layerId)) {
      newVisible.delete(layerId);
    } else {
      newVisible.add(layerId);
    }
    setVisibleLayers(newVisible);

    try {
      map.current.setLayoutProperty(
        layerId,
        'visibility',
        newVisible.has(layerId) ? 'visible' : 'none'
      );
    } catch (error) {
      console.error(`Failed to toggle layer ${layerId}:`, error);
    }
  };

  return (
    <div className="w-full h-screen flex flex-col bg-gray-50">
      {/* Header with tools */}
      <div className="bg-white shadow-sm border-b border-gray-200 p-3 flex items-center gap-3">
        <SearchBox map={map.current} />
        <div className="flex-1" />
        <select
          value={basemap}
          onChange={(e) => changeBasemap(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="osm-streets">Street</option>
          <option value="osm-light">Light</option>
        </select>
        <MapControls map={map.current} />
      </div>

      {/* Main content area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Layer Panel */}
        <div className="w-64 bg-white border-r border-gray-200 overflow-y-auto shadow-sm">
          <LayerPanel
            visibleLayers={visibleLayers}
            onToggleLayer={toggleLayer}
            onToggleHeatmap={() => setHeatmapEnabled(!heatmapEnabled)}
            heatmapEnabled={heatmapEnabled}
          />
        </div>

        {/* Center: Map */}
        <div className="flex-1 relative">
          <div ref={mapContainer} className="w-full h-full" />
          {/* Legend overlay */}
          <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg p-4 max-w-xs max-h-48 overflow-y-auto">
            <Legend
              visibleLayers={visibleLayers}
              heatmapEnabled={heatmapEnabled}
            />
          </div>
        </div>

        {/* Right: Info Panel */}
        <div className="w-72 bg-white border-l border-gray-200 overflow-y-auto shadow-sm">
          <InfoPanel selectedFeature={selectedFeature} />
        </div>
      </div>
    </div>
  );
}
