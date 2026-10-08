import React, { useState } from 'react';
import {
  Layers,
  Sparkles,
  Eye,
  Sliders,
  Download,
  CheckCircle2,
  AlertOctagon,
  TrendingDown,
  Globe,
  RefreshCw,
  Zap,
  Info,
  ChevronRight
} from 'lucide-react';

interface SatelliteAnalysisProps {
  onClose?: () => void;
}

export function SatelliteAnalysis({ onClose }: SatelliteAnalysisProps) {
  const [sliderPosition, setSliderPosition] = useState<number>(50);
  const [activeBand, setActiveBand] = useState<'rgb' | 'ndvi' | 'sar' | 'displacement'>('displacement');
  const [selectedRegion, setSelectedRegion] = useState<string>('gangtok');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  const regions = [
    { id: 'gangtok', name: 'Gangtok Zone 1 — East Sikkim', risk: 'CRITICAL', coords: '27.3389° N, 88.6138° E' },
    { id: 'tawang', name: 'Tawang Pass — Arunachal Pradesh', risk: 'HIGH', coords: '27.5833° N, 91.8667° E' },
    { id: 'shillong', name: 'Shillong Bypass — Meghalaya', risk: 'MEDIUM', coords: '25.5788° N, 91.8933° E' },
    { id: 'aizawl', name: 'Aizawl Slope 03 — Mizoram', risk: 'HIGH', coords: '23.7271° N, 92.7176° E' },
  ];

  const handleRunInference = () => {
    setIsProcessing(true);
    setTimeout(() => {
      setIsProcessing(false);
    }, 1200);
  };

  return (
    <div className="bg-slate-900 text-white rounded-2xl border border-slate-800 shadow-2xl overflow-hidden flex flex-col h-full max-h-[85vh]">
      {/* HEADER BAR */}
      <div className="bg-slate-950/80 border-b border-slate-800 px-6 py-4 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400">
            <Globe className="animate-spin-slow" size={22} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-extrabold text-white tracking-tight">
                Satellite AI Change Detection & Slope Instability
              </h2>
              <span className="bg-blue-500/20 text-blue-400 border border-blue-500/30 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">
                Sentinel-2 & InSAR AI
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              AN.E GUARDIANS Deep Learning Satellite Imagery Processor — 10m Resolution Optical & SAR Interferometry
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={handleRunInference}
            disabled={isProcessing}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-bold text-xs rounded-xl shadow-lg transition active:scale-95 disabled:opacity-50"
          >
            {isProcessing ? (
              <>
                <RefreshCw size={14} className="animate-spin" />
                <span>Processing Neural Pass...</span>
              </>
            ) : (
              <>
                <Sparkles size={14} />
                <span>Run Sentinel-2 AI Scan</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* MAIN CONTAINER */}
      <div className="flex-1 flex overflow-hidden">
        {/* LEFT CONTROLS PANEL */}
        <div className="w-80 border-r border-slate-800 bg-slate-950/50 p-5 flex flex-col space-y-5 overflow-y-auto">
          {/* REGION SELECTION */}
          <div>
            <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
              Target Observation Area
            </label>
            <div className="space-y-2">
              {regions.map((reg) => (
                <button
                  key={reg.id}
                  type="button"
                  onClick={() => setSelectedRegion(reg.id)}
                  className={`w-full text-left p-3 rounded-xl border text-xs transition flex flex-col justify-between ${
                    selectedRegion === reg.id
                      ? 'bg-blue-600/20 border-blue-500 text-white shadow-md'
                      : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:bg-slate-800/80 hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-center justify-between font-bold text-slate-100">
                    <span>{reg.name}</span>
                    <span
                      className={`text-[9px] px-2 py-0.5 rounded font-extrabold ${
                        reg.risk === 'CRITICAL'
                          ? 'bg-red-500/20 text-red-400 border border-red-500/40'
                          : reg.risk === 'HIGH'
                          ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                          : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/40'
                      }`}
                    >
                      {reg.risk}
                    </span>
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono mt-1">
                    {reg.coords}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* SATELLITE BAND FILTER */}
          <div>
            <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
              Spectral & Radar Layers
            </label>
            <div className="grid grid-cols-2 gap-2">
              {[
                { id: 'displacement', label: 'InSAR Displacement', icon: Zap },
                { id: 'rgb', label: 'True Color RGB', icon: Eye },
                { id: 'ndvi', label: 'NDVI Vegetation', icon: Layers },
                { id: 'sar', label: 'Sentinel-1 SAR', icon: Globe },
              ].map((band) => {
                const Icon = band.icon;
                const isActive = activeBand === band.id;
                return (
                  <button
                    key={band.id}
                    type="button"
                    onClick={() => setActiveBand(band.id as any)}
                    className={`p-2.5 rounded-xl border text-xs font-semibold flex items-center gap-2 transition ${
                      isActive
                        ? 'bg-cyan-500/20 border-cyan-400 text-cyan-300 shadow-sm'
                        : 'bg-slate-900 border-slate-800 text-slate-400 hover:bg-slate-800'
                    }`}
                  >
                    <Icon size={14} className={isActive ? 'text-cyan-400' : 'text-slate-500'} />
                    <span>{band.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* SATELLITE METRICS BREAKDOWN */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-3">
            <div className="flex items-center justify-between text-xs font-bold text-slate-300">
              <span>AI SCAN DIAGNOSTICS</span>
              <span className="text-[10px] text-emerald-400 font-mono">100% CONFIDENCE</span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between items-center text-slate-400">
                <span>Surface Slope Shift:</span>
                <span className="font-mono text-red-400 font-bold">+14.2 mm/yr</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                <div className="bg-red-500 h-full w-[78%]" />
              </div>

              <div className="flex justify-between items-center text-slate-400">
                <span>NDVI Canopy Loss:</span>
                <span className="font-mono text-amber-400 font-bold">-23.4%</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                <div className="bg-amber-500 h-full w-[54%]" />
              </div>

              <div className="flex justify-between items-center text-slate-400">
                <span>Soil Moisture Anomaly:</span>
                <span className="font-mono text-cyan-400 font-bold">+38% High Saturation</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                <div className="bg-cyan-400 h-full w-[88%]" />
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT IMAGE COMPARISON SLIDER VIEW */}
        <div className="flex-1 relative bg-black flex items-center justify-center overflow-hidden">
          {/* COMPARISON SLIDER CONTAINER */}
          <div className="relative w-full h-full select-none">
            {/* BEFORE IMAGE (Pre-Displacement Sentinel Pass) */}
            <div className="absolute inset-0 bg-slate-950 flex items-center justify-center">
              <div
                className="w-full h-full bg-cover bg-center transition-all duration-300 filter brightness-95 opacity-90"
                style={{
                  backgroundImage: `url('https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1600&q=80')`,
                }}
              />
              <div className="absolute top-4 left-4 bg-slate-950/80 border border-slate-700 text-slate-200 text-xs font-mono font-bold px-3 py-1 rounded-lg backdrop-blur-md">
                PRE-DISPLACEMENT (Sentinel-2 Pass: 2026-08-15)
              </div>
            </div>

            {/* AFTER IMAGE (Post-Displacement AI Overlay) */}
            <div
              className="absolute top-0 bottom-0 left-0 overflow-hidden border-r-2 border-cyan-400 shadow-2xl transition-all"
              style={{ width: `${sliderPosition}%` }}
            >
              <div
                className="absolute inset-0 w-full h-full bg-cover bg-center"
                style={{
                  backgroundImage: `url('https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1600&q=80')`,
                  width: '100vw',
                  maxWidth: 'none',
                }}
              />

              {/* HEATMAP / DISPLACEMENT OVERLAY GRAPHIC */}
              <div className="absolute inset-0 bg-gradient-to-tr from-red-600/40 via-amber-500/20 to-transparent mix-blend-overlay" />
              <div className="absolute top-1/3 left-1/4 h-64 w-64 rounded-full bg-red-600/30 blur-2xl animate-pulse" />

              <div className="absolute top-4 left-4 bg-red-950/90 border border-red-600 text-red-300 text-xs font-mono font-bold px-3 py-1 rounded-lg backdrop-blur-md flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-red-500 animate-ping" />
                <span>AI DISPLACEMENT OVERLAY (Pass: 2026-10-08)</span>
              </div>
            </div>

            {/* INTERACTIVE DRAG SLIDER CONTROL */}
            <input
              type="range"
              min="0"
              max="100"
              value={sliderPosition}
              onChange={(e) => setSliderPosition(Number(e.target.value))}
              className="absolute inset-0 opacity-0 cursor-ew-resize z-30 w-full h-full"
            />

            {/* VISUAL SLIDER BAR & KNOB */}
            <div
              className="absolute top-0 bottom-0 w-1 bg-cyan-400 z-20 pointer-events-none shadow-[0_0_15px_rgba(0,229,255,0.8)]"
              style={{ left: `${sliderPosition}%` }}
            >
              <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 h-10 w-10 rounded-full bg-cyan-400 text-slate-950 font-bold flex items-center justify-center shadow-lg border-2 border-white text-xs">
                <Sliders size={16} />
              </div>
            </div>

            {/* FOOTER INSTRUCTION OVERLAY */}
            <div className="absolute bottom-4 right-4 bg-slate-950/80 border border-slate-800 text-slate-400 text-xs font-medium px-4 py-2 rounded-xl backdrop-blur-md flex items-center gap-3">
              <span>Drag horizontal slider to compare baseline vs AI Sentinel satellite pass</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
