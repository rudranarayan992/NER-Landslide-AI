import React from 'react';
import {
  ShieldCheck,
  Award,
  Cpu,
  Database,
  Globe,
  Users,
  CheckCircle,
  X,
  Target,
  FileCode,
  Sparkles
} from 'lucide-react';

interface TeamModalProps {
  onClose: () => void;
}

export function TeamModal({ onClose }: TeamModalProps) {
  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-3xl border border-slate-200 shadow-2xl w-full max-w-4xl overflow-hidden flex flex-col my-auto">
        {/* MODAL HEADER WITH LOGO EMBLEM */}
        <div className="bg-gradient-to-r from-slate-900 via-slate-850 to-blue-950 text-white p-6 relative overflow-hidden flex items-center justify-between">
          <div className="absolute right-0 top-0 bottom-0 w-1/2 opacity-15 pointer-events-none bg-[radial-gradient(#00E5FF_1px,transparent_1px)] [background-size:16px_16px]" />
          
          <div className="flex items-center gap-5 z-10">
            <div className="h-16 w-16 rounded-2xl bg-white p-2 shadow-lg border border-slate-200 flex items-center justify-center flex-shrink-0">
              <img src="/logo.svg" alt="AN.E GUARDIANS Logo" className="h-full w-full object-contain" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full bg-cyan-400/20 text-cyan-300 border border-cyan-400/30 text-[10px] font-extrabold uppercase tracking-widest">
                  SIH GROUP
                </span>
                <span className="text-slate-400 text-xs font-semibold">| Team Identity & Model Specs</span>
              </div>
              <h2 className="text-2xl font-black tracking-tight text-white mt-1">
                AN.E GUARDIANS
              </h2>
              <p className="text-xs font-semibold text-slate-300 tracking-wider uppercase mt-0.5">
                PROTECTING THE NORTH EAST — AI LANDSLIDE EARLY WARNING
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white hover:bg-slate-800/80 rounded-full transition z-10"
          >
            <X size={20} />
          </button>
        </div>

        {/* CONTENT BODY */}
        <div className="p-6 overflow-y-auto space-y-6 max-h-[75vh]">
          {/* MISSION BANNER */}
          <div className="bg-gradient-to-br from-blue-50 to-cyan-50 border border-blue-200 rounded-2xl p-5 flex items-start gap-4">
            <div className="h-10 w-10 rounded-xl bg-blue-600 text-white flex items-center justify-center font-bold flex-shrink-0 shadow-md">
              <Target size={22} />
            </div>
            <div>
              <h3 className="text-sm font-extrabold text-slate-900">
                Mission Statement: Protecting North East India with AI
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed mt-1">
                The North East Region (NER) of India suffers over 60% of the nation’s deadliest slope failures during monsoon seasons. Team <strong>AN.E GUARDIANS</strong> has built an end-to-end multi-modal Early Warning System combining Sentinel-2 satellite change detection, physics-based TRIGRS hydrological modeling, and in-situ IoT sensor networks to protect lives, highways, and critical infrastructure across all 8 North Eastern states.
              </p>
            </div>
          </div>

          {/* KEY INNOVATIONS & SPECIFICATIONS */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-slate-50 border border-slate-200 p-4 rounded-2xl">
              <div className="flex items-center gap-2 text-blue-700 font-extrabold text-xs mb-2">
                <Cpu size={16} />
                <span>AI / ML ARCHITECTURE</span>
              </div>
              <ul className="text-xs text-slate-700 space-y-1.5 font-medium">
                <li className="flex items-center gap-1.5">
                  <CheckCircle size={14} className="text-emerald-500" />
                  <span>XGBoost & Random Forest Ensembles</span>
                </li>
                <li className="flex items-center gap-1.5">
                  <CheckCircle size={14} className="text-emerald-500" />
                  <span>AUC-ROC Accuracy: <strong>0.942</strong></span>
                </li>
                <li className="flex items-center gap-1.5">
                  <CheckCircle size={14} className="text-emerald-500" />
                  <span>UNet Sentinel Satellite Segmenter</span>
                </li>
              </ul>
            </div>

            <div className="bg-slate-50 border border-slate-200 p-4 rounded-2xl">
              <div className="flex items-center gap-2 text-indigo-700 font-extrabold text-xs mb-2">
                <Globe size={16} />
                <span>SATELLITE & GIS PIPELINE</span>
              </div>
              <ul className="text-xs text-slate-700 space-y-1.5 font-medium">
                <li className="flex items-center gap-1.5">
                  <CheckCircle size={14} className="text-emerald-500" />
                  <span>Sentinel-2 Optical & InSAR Passes</span>
                </li>
                <li className="flex items-center gap-1.5">
                  <CheckCircle size={14} className="text-emerald-500" />
                  <span>Esri & MapLibre Vector Map Tiles</span>
                </li>
                <li className="flex items-center gap-1.5">
                  <CheckCircle size={14} className="text-emerald-500" />
                  <span>Real-time Rainfall & Slope Contours</span>
                </li>
              </ul>
            </div>

            <div className="bg-slate-50 border border-slate-200 p-4 rounded-2xl">
              <div className="flex items-center gap-2 text-emerald-700 font-extrabold text-xs mb-2">
                <Award size={16} />
                <span>COMMUNITY & RESPONSE</span>
              </div>
              <ul className="text-xs text-slate-700 space-y-1.5 font-medium">
                <li className="flex items-center gap-1.5">
                  <CheckCircle size={14} className="text-emerald-500" />
                  <span>Automated SMS & Siren Broadcasts</span>
                </li>
                <li className="flex items-center gap-1.5">
                  <CheckCircle size={14} className="text-emerald-500" />
                  <span>Evacuation Routing System</span>
                </li>
                <li className="flex items-center gap-1.5">
                  <CheckCircle size={14} className="text-emerald-500" />
                  <span>Field Geotag Incident Reporter</span>
                </li>
              </ul>
            </div>
          </div>

          {/* PROJECT LOGO & TEAM CREDITS */}
          <div className="bg-slate-900 text-white rounded-2xl p-5 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="h-12 w-12 rounded-xl bg-white p-1.5 flex items-center justify-center">
                <img src="/logo.svg" alt="AN.E GUARDIANS Emblem" className="h-full w-full object-contain" />
              </div>
              <div>
                <h4 className="text-base font-extrabold text-white">AN.E GUARDIANS Team</h4>
                <p className="text-xs text-slate-400">Smart India Hackathon (SIH) Innovation — 2026</p>
              </div>
            </div>
            <div className="text-right">
              <span className="text-xs font-bold text-cyan-400 bg-cyan-950 border border-cyan-800 px-3 py-1 rounded-lg">
                Verified System Operational
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
