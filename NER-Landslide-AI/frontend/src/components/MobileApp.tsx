import React, { useState, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { MapPin, Navigation, AlertTriangle, FileText, Menu } from 'lucide-react';

interface MobileAppProps {
  isMobile: boolean;
}

export function MobileApp({ isMobile }: MobileAppProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const [activeTab, setActiveTab] = useState<'map' | 'routes' | 'alerts' | 'report' | 'more'>('map');
  const [userLocation, setUserLocation] = useState<{ lat: number; lon: number } | null>(null);
  const [currentRoad, setCurrentRoad] = useState<string | null>(null);
  const [showMenu, setShowMenu] = useState(false);

  React.useEffect(() => {
    if (!isMobile || !mapContainer.current) return;

    if (!map.current) {
      map.current = new maplibregl.Map({
        container: mapContainer.current,
        style: {
          version: 8,
          sources: {
            base: {
              type: 'raster',
              tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
              tileSize: 256,
            },
          },
          layers: [{ id: 'base', type: 'raster', source: 'base' }],
          glyphs: 'https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf',
        },
        center: [93.5, 26.5],
        zoom: 6,
      });
    }

    // Request location permission
    if (navigator.geolocation) {
      navigator.geolocation.watchPosition((position) => {
        const { latitude, longitude } = position.coords;
        setUserLocation({ lat: latitude, lon: longitude });

        if (map.current) {
          map.current.flyTo({ center: [longitude, latitude], zoom: 14 });
        }
      });
    }

    return () => {
      // Keep map alive for mobile
    };
  }, [isMobile]);

  if (!isMobile) return null;

  return (
    <div className="fixed inset-0 bg-slate-950 flex flex-col z-50">
      {/* HEADER */}
      <div className="bg-slate-900/95 border-b border-slate-700/60 p-3 flex items-center justify-between">
        <div>
          <h1 className="text-sm font-bold text-cyan-300 uppercase">NER Landslide Guard</h1>
          <p className="text-[10px] text-slate-400">Disaster Management</p>
        </div>
        <button
          onClick={() => setShowMenu(!showMenu)}
          className="p-2 hover:bg-slate-700/60 rounded transition-colors"
        >
          <Menu size={20} className="text-slate-300" />
        </button>
      </div>

      {/* SEARCH / ROUTE INPUT */}
      <div className="bg-slate-950/80 border-b border-slate-700/60 p-3">
        <input
          type="text"
          placeholder="Where are you going?"
          className="w-full px-3 py-2 bg-slate-900/60 border border-slate-700/50 rounded text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/60"
        />
      </div>

      {/* MAP */}
      <div className="flex-1 relative overflow-hidden">
        <div ref={mapContainer} className="w-full h-full" />

        {/* GPS MARKER */}
        {userLocation && (
          <div className="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 w-4 h-4 bg-cyan-500 rounded-full border-2 border-white shadow-lg" />
        )}
      </div>

      {/* ROAD INTELLIGENCE CARD */}
      {currentRoad && (
        <div className="bg-slate-900/95 border-t border-slate-700/60 p-3">
          <div className="flex items-start gap-2 mb-2">
            <MapPin size={16} className="text-cyan-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-white text-sm">Current Road</h3>
              <p className="text-[11px] text-slate-300">{currentRoad}</p>
            </div>
          </div>
          <div className="text-[10px] text-slate-400 space-y-1">
            <p>
              <span className="text-amber-300">Historical Exposure:</span> 2 events nearby
            </p>
            <p>
              <span className="text-rose-300">Current Risk:</span> <span className="font-semibold">BLOCKED</span>
            </p>
          </div>
        </div>
      )}

      {/* MOBILE NAVIGATION TABS */}
      <div className="border-t border-slate-700/60 bg-slate-950/95 flex items-center justify-around p-0">
        {[
          { id: 'map', label: 'MAP', icon: '🗺️' },
          { id: 'routes', label: 'ROUTES', icon: '🛣️' },
          { id: 'alerts', label: 'ALERTS', icon: '⚠️' },
          { id: 'report', label: 'REPORT', icon: '📋' },
          { id: 'more', label: 'MORE', icon: '⋯' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex-1 py-3 text-center border-t-2 transition-colors ${
              activeTab === tab.id
                ? 'border-cyan-500 text-cyan-300 bg-slate-900/60'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <div className="text-lg">{tab.icon}</div>
            <div className="text-[8px] font-semibold uppercase mt-0.5">{tab.label}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
