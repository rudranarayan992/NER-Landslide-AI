import React, { useMemo, useState } from 'react';
import maplibregl from 'maplibre-gl';
import { Compass, Crosshair, Expand, LocateFixed, Map, Minus, Navigation, Plus, Route, Ruler, Search } from 'lucide-react';

interface MapControlsProps {
  map: maplibregl.Map | null;
  mode: 'gis' | 'travel';
  onToggleMode: () => void;
  basemap: string;
  onBasemapChange: (style: string) => void;
}

const STYLE_OPTIONS = [
  { key: 'street', label: 'Street' },
  { key: 'satellite', label: 'Satellite' },
  { key: 'topographic', label: 'Topographic' },
  { key: 'terrain', label: 'Terrain' },
  { key: 'hillshade', label: 'Hillshade' },
];

export function MapControls({ map, mode, onToggleMode, basemap, onBasemapChange }: MapControlsProps) {
  const [measureMode, setMeasureMode] = useState(false);
  const [identifyMode, setIdentifyMode] = useState(false);
  const [locationStatus, setLocationStatus] = useState<'idle' | 'success' | 'unavailable'>('idle');
  const [showStyleMenu, setShowStyleMenu] = useState(false);

  const handleZoomIn = () => map?.zoomIn();
  const handleZoomOut = () => map?.zoomOut();

  const handleHome = () => {
    if (map) {
      map.flyTo({ center: [93.5, 26.5], zoom: 6, duration: 1000 });
      setIdentifyMode(false);
      setMeasureMode(false);
    }
  };

  const handleFullscreen = () => {
    const container = map?.getContainer();
    if (container && 'requestFullscreen' in container) {
      (container as any).requestFullscreen?.();
    }
  };

  const handleLocate = () => {
    if (!navigator.geolocation) {
      setLocationStatus('unavailable');
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { longitude, latitude, accuracy } = position.coords;
        if (map) {
          map.flyTo({ center: [longitude, latitude], zoom: 12, duration: 1000 });
        }
        setLocationStatus('success');
        console.info('GPS accuracy:', accuracy, 'm');
      },
      () => setLocationStatus('unavailable')
    );
  };

  const handleIdentify = () => {
    setIdentifyMode((value) => !value);
    setMeasureMode(false);
  };

  const handleMeasure = () => {
    setMeasureMode((value) => !value);
    setIdentifyMode(false);
    if (map) {
      map.getCanvas().style.cursor = measureMode ? '' : 'crosshair';
    }
  };

  const controls = useMemo(
    () => [
      { key: 'zoom-in', label: <Plus size={14} />, action: handleZoomIn, title: 'Zoom in' },
      { key: 'zoom-out', label: <Minus size={14} />, action: handleZoomOut, title: 'Zoom out' },
      { key: 'locate', label: <Crosshair size={14} />, action: handleLocate, title: 'Current location' },
      { key: 'compass', label: <Compass size={14} />, action: handleHome, title: 'Reset view' },
      { key: 'identify', label: <Search size={14} />, action: handleIdentify, title: 'Identify', active: identifyMode },
      { key: 'measure', label: <Ruler size={14} />, action: handleMeasure, title: 'Measure', active: measureMode },
      { key: 'fullscreen', label: <Expand size={14} />, action: handleFullscreen, title: 'Fullscreen' },
      { key: 'route', label: <Route size={14} />, action: onToggleMode, title: 'Toggle travel mode' },
    ],
    [identifyMode, measureMode, map, mode]
  );

  return (
    <div className="flex items-center gap-2 relative">
      <div className="flex items-center gap-1 rounded-xl border border-slate-700 bg-slate-900/90 p-1 shadow-lg">
        {controls.map((control) => (
          <button
            key={control.key}
            type="button"
            onClick={control.action}
            title={control.title}
            className={`flex h-8 w-8 items-center justify-center rounded-md transition-colors ${
              control.active
                ? 'bg-cyan-400 text-slate-950'
                : 'text-slate-200 hover:bg-slate-800 hover:text-white'
            }`}
          >
            {control.label}
          </button>
        ))}
      </div>

      <div className="relative">
        <button
          type="button"
          onClick={() => setShowStyleMenu((value) => !value)}
          className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-900/90 px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-slate-100 shadow-lg"
        >
          <Map size={14} className="text-cyan-300" />
          {STYLE_OPTIONS.find((item) => item.key === basemap)?.label || 'Street'}
        </button>

        {showStyleMenu && (
          <div className="absolute right-0 top-full mt-2 w-44 rounded-xl border border-slate-700 bg-slate-900/95 p-1.5 shadow-2xl z-40">
            {STYLE_OPTIONS.map((option) => (
              <button
                key={option.key}
                type="button"
                onClick={() => {
                  onBasemapChange(option.key);
                  setShowStyleMenu(false);
                }}
                className={`flex w-full items-center justify-between rounded-md px-2.5 py-2 text-left text-[10px] font-semibold uppercase tracking-[0.12em] ${
                  basemap === option.key ? 'bg-cyan-500/20 text-cyan-200' : 'text-slate-200 hover:bg-slate-800'
                }`}
              >
                <span>{option.label}</span>
                {basemap === option.key && <span className="h-2 w-2 rounded-full bg-cyan-400" />}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="rounded-xl border border-slate-700 bg-slate-900/90 px-2.5 py-2 text-[9px] font-semibold uppercase tracking-[0.12em] text-slate-100 shadow-lg">
        {locationStatus === 'success' ? 'YOU ARE HERE' : locationStatus === 'unavailable' ? 'LOCATION UNAVAILABLE' : 'GPS READY'}
      </div>
    </div>
  );
}
