import React, { useState } from 'react';
import { MapPin, Navigation, Clock, AlertTriangle, X } from 'lucide-react';

interface Route {
  id: string;
  name: string;
  distance: number;
  duration?: number;
  historicalLandslides: number;
  roadSegments: string[];
  verifiedClosures: string[];
}

interface RouteSystemProps {
  map: any;
  onClose: () => void;
}

export function RouteSystem({ map, onClose }: RouteSystemProps) {
  const [from, setFrom] = useState('');
  const [to, setTo] = useState('');
  const [routes, setRoutes] = useState<Route[]>([]);
  const [selectedRoute, setSelectedRoute] = useState<string | null>(null);
  const [showResults, setShowResults] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleCalculateRoute = async () => {
    if (!from || !to) return;
    
    setLoading(true);
    try {
      // Fetch route data from backend
      const response = await fetch(`/api/routes/calculate?from=${from}&to=${to}`);
      const data = await response.json();
      setRoutes(data.routes || []);
      setShowResults(true);
    } catch (error) {
      console.error('Route calculation failed:', error);
      setRoutes([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed right-4 top-32 w-96 rounded-lg border border-slate-700/70 bg-slate-950/95 p-4 shadow-2xl backdrop-blur-sm z-20 max-h-[600px] flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-bold text-cyan-300 uppercase tracking-[0.14em]">Route Planner</h2>
        <button
          onClick={onClose}
          className="p-1 hover:bg-slate-700/60 rounded transition-colors"
        >
          <X size={16} className="text-slate-400" />
        </button>
      </div>

      {!showResults ? (
        <div className="space-y-3">
          <div>
            <label className="block text-[10px] uppercase tracking-[0.12em] text-slate-400 mb-1">From</label>
            <input
              type="text"
              value={from}
              onChange={(e) => setFrom(e.target.value)}
              placeholder="Current location"
              className="w-full px-2 py-1.5 bg-slate-900/60 border border-slate-700/50 rounded text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/60"
            />
          </div>

          <div>
            <label className="block text-[10px] uppercase tracking-[0.12em] text-slate-400 mb-1">To</label>
            <input
              type="text"
              value={to}
              onChange={(e) => setTo(e.target.value)}
              placeholder="Destination"
              className="w-full px-2 py-1.5 bg-slate-900/60 border border-slate-700/50 rounded text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/60"
            />
          </div>

          <button
            onClick={handleCalculateRoute}
            disabled={loading || !from || !to}
            className="w-full py-2 bg-cyan-600/80 hover:bg-cyan-500/80 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded text-sm uppercase transition-colors"
          >
            {loading ? 'Calculating...' : 'Calculate Route'}
          </button>
        </div>
      ) : (
        <div className="space-y-3 overflow-y-auto flex-1">
          {routes.length === 0 ? (
            <div className="text-center py-4 text-slate-400">
              <p className="text-sm">No routes found</p>
            </div>
          ) : (
            routes.map((route) => (
              <div
                key={route.id}
                onClick={() => setSelectedRoute(route.id)}
                className={`p-3 rounded-lg border transition-colors cursor-pointer ${
                  selectedRoute === route.id
                    ? 'bg-cyan-500/20 border-cyan-500/60'
                    : 'bg-slate-900/60 border-slate-700/50 hover:border-slate-600/60'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-white text-sm">{route.name}</h3>
                  <span className="text-[9px] text-slate-400">
                    {(route.distance / 1000).toFixed(1)} km
                  </span>
                </div>

                <div className="space-y-1 text-[10px] text-slate-300 mb-2">
                  {route.duration && (
                    <div className="flex items-center gap-1">
                      <Clock size={12} className="text-slate-500" />
                      <span>{Math.round(route.duration / 60)} min</span>
                    </div>
                  )}
                  <div className="flex items-center gap-1">
                    <AlertTriangle size={12} className="text-amber-400" />
                    <span>{route.historicalLandslides} historical events nearby</span>
                  </div>
                </div>

                {route.verifiedClosures.length > 0 && (
                  <div className="text-[9px] text-rose-300 bg-rose-500/10 rounded px-2 py-1 border border-rose-600/30">
                    ⚠ {route.verifiedClosures.length} verified closure{route.verifiedClosures.length > 1 ? 's' : ''}
                  </div>
                )}
              </div>
            ))
          )}

          <button
            onClick={() => setShowResults(false)}
            className="w-full mt-3 py-1.5 text-sm text-slate-300 hover:text-white border border-slate-700/50 rounded transition-colors"
          >
            Back
          </button>
        </div>
      )}
    </div>
  );
}
