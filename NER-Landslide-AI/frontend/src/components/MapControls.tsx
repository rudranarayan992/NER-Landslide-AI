import React from 'react';
import maplibregl from 'maplibre-gl';

interface MapControlsProps {
  map: maplibregl.Map | null;
}

export function MapControls({ map }: MapControlsProps) {
  const handleZoomIn = () => {
    if (map) map.zoomIn();
  };

  const handleZoomOut = () => {
    if (map) map.zoomOut();
  };

  const handleHome = () => {
    if (map) {
      map.flyTo({
        center: [93.5, 26.5],
        zoom: 6,
        duration: 1000,
      });
    }
  };

  const handleFullscreen = () => {
    if (map?.getContainer()?.requestFullscreen) {
      map.getContainer().requestFullscreen();
    }
  };

  const handleLocate = () => {
    if (navigator.geolocation && map) {
      navigator.geolocation.getCurrentPosition((position) => {
        const { longitude, latitude } = position.coords;
        map.flyTo({
          center: [longitude, latitude],
          zoom: 12,
          duration: 1000,
        });
      });
    }
  };

  const handleMeasure = () => {
    alert('Distance/Area measurement tool coming soon');
  };

  return (
    <div className="flex items-center gap-1">
      <button
        onClick={handleZoomIn}
        className="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-700 hover:text-gray-900 font-bold text-lg"
        title="Zoom in"
      >
        +
      </button>
      <button
        onClick={handleZoomOut}
        className="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-700 hover:text-gray-900 font-bold text-lg"
        title="Zoom out"
      >
        −
      </button>
      <button
        onClick={handleHome}
        className="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-700 hover:text-gray-900"
        title="Reset map to initial view"
      >
        ⌂
      </button>
      <button
        onClick={handleLocate}
        className="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-700 hover:text-gray-900"
        title="Show your location"
      >
        📍
      </button>
      <button
        onClick={handleMeasure}
        className="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-700 hover:text-gray-900"
        title="Measure distance/area"
      >
        📏
      </button>
      <button
        onClick={handleFullscreen}
        className="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-700 hover:text-gray-900"
        title="Fullscreen"
      >
        ⛶
      </button>
    </div>
  );
}
