import React, { useState } from 'react';
import { AlertTriangle, Info, Clock, MapPin, X, Filter } from 'lucide-react';

interface Alert {
  id: string;
  type: 'HISTORICAL' | 'OBSERVATION' | 'MODEL' | 'OFFICIAL' | 'ROAD_CLOSURE' | 'FIELD_REPORT';
  title: string;
  description: string;
  location: string;
  distance?: number;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  timestamp: string;
  status: 'ACTIVE' | 'RESOLVED' | 'ARCHIVED';
  source: string;
}

interface AlertCenterProps {
  onClose: () => void;
}

export function AlertCenter({ onClose }: AlertCenterProps) {
  const [selectedCategory, setSelectedCategory] = useState<Alert['type'] | 'ALL'>('ALL');
  const [alerts, setAlerts] = useState<Alert[]>([
    {
      id: '1',
      type: 'HISTORICAL',
      title: 'Historical Landslide Information Ahead',
      description: 'GSI recorded 12 historical landslide events in the region.',
      location: 'NH-27, Meghalaya',
      distance: 2.4,
      severity: 'LOW',
      timestamp: '2024-01-15T10:30:00Z',
      status: 'ACTIVE',
      source: 'GSI Historical Database',
    },
    {
      id: '2',
      type: 'FIELD_REPORT',
      title: 'Verified Field Observation',
      description: 'Visible ground cracks observed on road shoulder.',
      location: 'NH-44, Arunachal Pradesh',
      distance: 5.2,
      severity: 'MEDIUM',
      timestamp: '2024-01-14T15:45:00Z',
      status: 'ACTIVE',
      source: 'Field Team Report',
    },
  ]);

  const getSeverityColor = (severity: Alert['severity']) => {
    switch (severity) {
      case 'CRITICAL': return 'bg-red-500/20 border-red-600/60 text-red-200';
      case 'HIGH': return 'bg-orange-500/20 border-orange-600/60 text-orange-200';
      case 'MEDIUM': return 'bg-amber-500/20 border-amber-600/60 text-amber-200';
      case 'LOW': return 'bg-blue-500/20 border-blue-600/60 text-blue-200';
      default: return 'bg-slate-500/20 border-slate-600/60 text-slate-200';
    }
  };

  const getSeverityIcon = (severity: Alert['severity']) => {
    if (severity === 'CRITICAL' || severity === 'HIGH') return <AlertTriangle size={14} />;
    return <Info size={14} />;
  };

  const getTypeLabel = (type: Alert['type']) => {
    switch (type) {
      case 'HISTORICAL': return '📚 Historical';
      case 'OBSERVATION': return '👁 Observation';
      case 'MODEL': return '🤖 Model Warning';
      case 'OFFICIAL': return '📢 Official';
      case 'ROAD_CLOSURE': return '🚫 Road Closure';
      case 'FIELD_REPORT': return '📋 Field Report';
      default: return type;
    }
  };

  const filteredAlerts = selectedCategory === 'ALL' 
    ? alerts 
    : alerts.filter(a => a.type === selectedCategory);

  const categories: (Alert['type'] | 'ALL')[] = ['ALL', 'HISTORICAL', 'OBSERVATION', 'MODEL', 'OFFICIAL', 'ROAD_CLOSURE', 'FIELD_REPORT'];

  return (
    <div className="fixed bottom-4 right-4 w-96 rounded-lg border border-slate-700/70 bg-slate-950/95 shadow-2xl backdrop-blur-sm z-20 flex flex-col max-h-[500px]">
      {/* HEADER */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700/50">
        <h2 className="text-sm font-bold text-cyan-300 uppercase tracking-[0.14em]">Alert Center</h2>
        <button
          onClick={onClose}
          className="p-1 hover:bg-slate-700/60 rounded transition-colors"
        >
          <X size={16} className="text-slate-400" />
        </button>
      </div>

      {/* FILTER */}
      <div className="flex items-center gap-1 p-2 border-b border-slate-700/50 overflow-x-auto">
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-2 py-1 text-[9px] font-semibold uppercase rounded whitespace-nowrap transition-colors ${
              selectedCategory === cat
                ? 'bg-cyan-500/80 text-slate-950'
                : 'text-slate-400 hover:text-slate-200 bg-slate-700/20 hover:bg-slate-700/40'
            }`}
          >
            {cat === 'ROAD_CLOSURE' ? 'CLOSURE' : cat}
          </button>
        ))}
      </div>

      {/* ALERTS LIST */}
      <div className="flex-1 overflow-y-auto">
        {filteredAlerts.length === 0 ? (
          <div className="p-4 text-center text-slate-400">
            <p className="text-sm">No alerts in this category</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-700/30">
            {filteredAlerts.map((alert) => (
              <div key={alert.id} className="p-3 hover:bg-slate-900/60 transition-colors">
                <div className="flex items-start gap-2 mb-2">
                  <div className={`p-1 rounded border flex-shrink-0 ${getSeverityColor(alert.severity)}`}>
                    {getSeverityIcon(alert.severity)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-white text-sm truncate">{alert.title}</h3>
                      <span className={`text-[8px] font-bold uppercase rounded px-1.5 py-0.5 border flex-shrink-0 ${getSeverityColor(alert.severity)}`}>
                        {alert.severity}
                      </span>
                    </div>
                    <p className="text-[10px] text-slate-300 line-clamp-2 mb-1">{alert.description}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 text-[9px] text-slate-400 mb-1">
                  <div className="flex items-center gap-1">
                    <MapPin size={12} />
                    <span className="truncate">{alert.location}</span>
                  </div>
                  {alert.distance && (
                    <span className="text-slate-500">
                      {alert.distance.toFixed(1)} km away
                    </span>
                  )}
                </div>

                <div className="flex items-center justify-between text-[9px] text-slate-500">
                  <span>{getTypeLabel(alert.type)}</span>
                  <span>{alert.source}</span>
                </div>

                <div className="flex items-center gap-1 mt-2 text-[8px] text-slate-400">
                  <Clock size={10} />
                  <span>{new Date(alert.timestamp).toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* STATUS NOTICE */}
      <div className="border-t border-slate-700/50 p-2 bg-slate-900/60 text-[9px] text-slate-400">
        <span className="text-amber-300">⚠</span> Automated alerts currently <span className="font-semibold text-rose-300">BLOCKED</span>
      </div>
    </div>
  );
}
