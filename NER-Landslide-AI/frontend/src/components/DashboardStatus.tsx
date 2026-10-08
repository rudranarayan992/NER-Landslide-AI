import React from 'react';
import { CheckCircle, AlertCircle, Clock } from 'lucide-react';

interface StatusItem {
  label: string;
  status: 'VERIFIED' | 'AVAILABLE' | 'AWAITING' | 'BLOCKED' | 'NOT_TRAINED';
  description: string;
  icon: 'check' | 'alert' | 'clock';
}

interface DashboardStatusProps {
  onClose?: () => void;
}

export function DashboardStatus({ onClose }: DashboardStatusProps) {
  const statusItems: StatusItem[] = [
    {
      label: 'GSI Historical Landslides',
      status: 'VERIFIED',
      description: '33,904 georeferenced events',
      icon: 'check',
    },
    {
      label: 'Roads Network',
      status: 'AVAILABLE',
      description: 'Verified where data exists',
      icon: 'check',
    },
    {
      label: 'Villages',
      status: 'AVAILABLE',
      description: 'Verified where data exists',
      icon: 'check',
    },
    {
      label: 'Environmental Data',
      status: 'AWAITING',
      description: 'Rainfall, soil, terrain, hydrology',
      icon: 'clock',
    },
    {
      label: 'ML Pipeline',
      status: 'NOT_TRAINED',
      description: 'Requires verified environmental data',
      icon: 'alert',
    },
    {
      label: 'Current Risk Layer',
      status: 'BLOCKED',
      description: 'Requires ML + environmental data',
      icon: 'alert',
    },
    {
      label: 'Automated Alerts',
      status: 'BLOCKED',
      description: 'Requires operational ML & validation',
      icon: 'alert',
    },
  ];

  const getStatusColor = (status: StatusItem['status']) => {
    switch (status) {
      case 'VERIFIED':
      case 'AVAILABLE':
        return 'border-emerald-600/60 bg-emerald-500/10 text-emerald-200';
      case 'AWAITING':
        return 'border-amber-600/60 bg-amber-500/10 text-amber-200';
      case 'BLOCKED':
      case 'NOT_TRAINED':
        return 'border-rose-600/60 bg-rose-500/10 text-rose-200';
      default:
        return 'border-slate-600/60 bg-slate-500/10 text-slate-200';
    }
  };

  const getIcon = (icon: StatusItem['icon']) => {
    switch (icon) {
      case 'check':
        return <CheckCircle size={16} />;
      case 'clock':
        return <Clock size={16} />;
      case 'alert':
        return <AlertCircle size={16} />;
      default:
        return null;
    }
  };

  return (
    <div className="fixed top-20 left-4 w-80 rounded-lg border border-slate-700/70 bg-slate-950/95 shadow-2xl backdrop-blur-sm z-30 max-h-[600px] overflow-y-auto">
      <div className="p-4 space-y-2 divide-y divide-slate-700/50">
        <h2 className="text-sm font-bold text-cyan-300 uppercase tracking-[0.14em] pb-3">System Status</h2>

        {statusItems.map((item, idx) => (
          <div key={idx} className="py-2">
            <div className="flex items-start gap-2 mb-1">
              <div className={`p-1 rounded border flex-shrink-0 mt-0.5 ${getStatusColor(item.status)}`}>
                {getIcon(item.icon)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <h3 className="font-semibold text-white text-[11px]">{item.label}</h3>
                  <span className={`text-[7px] font-bold uppercase rounded px-1 py-0.5 border whitespace-nowrap ${getStatusColor(item.status)}`}>
                    {item.status}
                  </span>
                </div>
                <p className="text-[10px] text-slate-400">{item.description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="border-t border-slate-700/50 px-4 py-3 bg-slate-900/60 text-[9px] text-slate-400">
        <p className="mb-1">
          <span className="text-cyan-300">System State:</span> Dashboard is operational for historical data exploration and field reporting.
        </p>
        <p>
          <span className="text-amber-300">Predictive Features:</span> Current risk assessment and automated warnings pending environmental data validation and ML model training.
        </p>
      </div>
    </div>
  );
}
