import React, { useMemo, useState } from 'react';
import maplibregl from 'maplibre-gl';

interface MapControlsProps {
  map: maplibregl.Map | null;
}

export function MapControls({ map }: MapControlsProps) {
  const [measureMode, setMeasureMode] = useState(false);
  const [identifyMode, setIdentifyMode] = useState(false);

  const handleZoomIn = () => {
    if (map) map.zoomIn();
  };

  const handleZoomOut = () => {
    if (map) map.zoomOut();
  };

  const handleHome = () => {
    if (map) {
      map.flyTo({ center: [93.5, 26.5], zoom: 6, duration: 1000 });
      setIdentifyMode(false);
      setMeasureMode(false);
    }
  };

  const handleFullscreen = () => {
    const container = map?.getContainer();
    if (container && container.requestFullscreen) {
      container.requestFullscreen();
    }
  };

  const handleLocate = () => {
    if (!map || !navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition((position) => {
      const { longitude, latitude } = position.coords;
      map.flyTo({ center: [longitude, latitude], zoom: 12, duration: 1000 });
    });
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
      { key: 'zoom-in', label: '+', action: handleZoomIn, title: 'Zoom in' },
      { key: 'zoom-out', label: '−', action: handleZoomOut, title: 'Zoom out' },
      { key: 'home', label: 'HOME', action: handleHome, title: 'Reset to NER view' },
      { key: 'identify', label: 'IDENTIFY', action: handleIdentify, title: 'Toggle identify mode', active: identifyMode },
      { key: 'measure', label: 'MEASURE', action: handleMeasure, title: 'Toggle measuring', active: measureMode },
      { key: 'locate', label: 'LOCATE', action: handleLocate, title: 'Show my location' },
      { key: 'fullscreen', label: 'FULLSCREEN', action: handleFullscreen, title: 'Fullscreen map' },
    ],
    [identifyMode, measureMode, map]
  );

  return (
    <div className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-900/90 p-1 shadow-sm">
      {controls.map((control) => (
        <button
          key={control.key}
          type="button"
          onClick={control.action}
          title={control.title}
          className={`px-2.5 py-1.5 text-[9px] font-semibold uppercase tracking-[0.18em] transition-colors rounded ${
            control.active
              ? 'bg-cyan-400 text-slate-950'
              : 'text-slate-200 hover:bg-slate-800 hover:text-white'
          }`}
        >
          {control.label}
        </button>
      ))}
    </div>
  );
}
