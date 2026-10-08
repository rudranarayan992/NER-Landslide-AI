import React, { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import {
  LayoutDashboard,
  MapPin,
  Bell,
  Activity,
  FileText,
  Camera,
  CloudRain,
  Building2,
  BarChart3,
  ShieldCheck,
  Settings,
  ChevronRight,
  Menu,
  RefreshCw,
  AlertTriangle,
  Mountain,
  User,
  Check,
  Home,
  Radio,
  Layers,
  Info,
  Send,
  X
} from 'lucide-react';
import { DisasterAIAssistant } from './DisasterAIAssistant';
import { AlertCenter } from './AlertCenter';
import { RouteSystem } from './RouteSystem';

interface ZoneData {
  id: string;
  name: string;
  level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  mlProb: number;
  fos: number;
  rainfall: string;
  soilMoisture: string;
  coordinates: [number, number];
}

const ZONES: ZoneData[] = [
  {
    id: 'gangtok-1',
    name: 'Gangtok Zone 1',
    level: 'CRITICAL',
    mlProb: 0.91,
    fos: 0.74,
    rainfall: '168 mm',
    soilMoisture: '78%',
    coordinates: [88.6138, 27.3389],
  },
  {
    id: 'tawang-ridge',
    name: 'Tawang Ridge',
    level: 'HIGH',
    mlProb: 0.82,
    fos: 0.89,
    rainfall: '142 mm',
    soilMoisture: '71%',
    coordinates: [91.8667, 27.5833],
  },
  {
    id: 'shillong-east',
    name: 'Shillong East',
    level: 'MEDIUM',
    mlProb: 0.54,
    fos: 1.12,
    rainfall: '95 mm',
    soilMoisture: '58%',
    coordinates: [91.8933, 25.5788],
  },
  {
    id: 'guwahati-hills',
    name: 'Guwahati Hills',
    level: 'LOW',
    mlProb: 0.21,
    fos: 1.65,
    rainfall: '45 mm',
    soilMoisture: '38%',
    coordinates: [91.7362, 26.1445],
  },
  {
    id: 'aizawl-3',
    name: 'Aizawl Zone 03',
    level: 'LOW',
    mlProb: 0.18,
    fos: 1.82,
    rainfall: '38 mm',
    soilMoisture: '34%',
    coordinates: [92.7176, 23.7271],
  },
  {
    id: 'lunglei-zone',
    name: 'Lunglei Zone',
    level: 'HIGH',
    mlProb: 0.78,
    fos: 0.85,
    rainfall: '135 mm',
    soilMoisture: '69%',
    coordinates: [92.7333, 22.8833],
  },
];

const SHELTERS = [
  { name: 'Shillong Relief Camp 1', coords: [91.88, 25.56] as [number, number] },
  { name: 'Gangtok Community Shelter', coords: [88.62, 27.34] as [number, number] },
  { name: 'Silchar Safe Haven', coords: [92.78, 24.83] as [number, number] },
  { name: 'Aizawl Sports Complex Shelter', coords: [92.72, 23.73] as [number, number] },
];

export function GISMap() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const [activeTab, setActiveTab] = useState<string>('live-risk-map');
  const [selectedZone, setSelectedZone] = useState<ZoneData>(ZONES[0]);
  const [evacuationMode, setEvacuationMode] = useState<boolean>(false);
  const [showDisasterAI, setShowDisasterAI] = useState<boolean>(false);
  const [showAlertsModal, setShowAlertsModal] = useState<boolean>(false);
  const [showRouteModal, setShowRouteModal] = useState<boolean>(false);
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(true);

  // Map layer toggle states matching reference app
  const [layerState, setLayerState] = useState({
    riskZones: true,
    rainfall: false,
    soilMoisture: false,
    roads: true,
    villages: true,
    infrastructure: true,
    sensors: true,
    fieldReports: true,
    shelters: true,
    landslideHistory: false,
  });

  const toggleLayer = (key: keyof typeof layerState) => {
    setLayerState((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  useEffect(() => {
    if (!mapContainer.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: JSON.stringify({
        version: 8,
        sources: {
          osm: {
            type: 'raster',
            tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
            tileSize: 256,
            attribution: '© OpenStreetMap contributors',
          },
        },
        layers: [{ id: 'osm-tiles', type: 'raster', source: 'osm' }],
      }),
      center: [91.88, 25.57],
      zoom: 6.8,
    });

    map.current.addControl(new maplibregl.NavigationControl(), 'top-left');

    return () => map.current?.remove();
  }, []);

  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'live-risk-map', label: 'Live Risk Map', icon: MapPin },
    { id: 'alerts', label: 'Alerts', icon: Bell, badge: '3' },
    { id: 'sensor-monitoring', label: 'Sensor Monitoring', icon: Activity },
    { id: 'reports', label: 'Reports', icon: FileText },
    { id: 'field-reports', label: 'Field Reports', icon: Camera },
    { id: 'weather', label: 'Weather', icon: CloudRain },
    { id: 'infrastructure', label: 'Infrastructure', icon: Building2 },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'admin-response', label: 'Admin / Response', icon: ShieldCheck },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  const getLevelBadgeClass = (level: string) => {
    switch (level) {
      case 'CRITICAL':
        return 'bg-red-100 text-red-700 border-red-200';
      case 'HIGH':
        return 'bg-orange-100 text-orange-700 border-orange-200';
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'LOW':
        return 'bg-emerald-100 text-emerald-700 border-emerald-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'CRITICAL':
        return '#dc2626';
      case 'HIGH':
        return '#ea580c';
      case 'MEDIUM':
        return '#d97706';
      case 'LOW':
        return '#16a34a';
      default:
        return '#64748b';
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-100 font-sans text-slate-800 antialiased">
      {/* LEFT SIDEBAR NAVIGATION */}
      <aside
        className={`${
          sidebarOpen ? 'w-60' : 'w-0 -ml-60'
        } transition-all duration-300 ease-in-out bg-slate-50 border-r border-slate-200 flex flex-col flex-shrink-0 z-30 select-none`}
      >
        {/* LOGO & BRANDING */}
        <div className="p-4 border-b border-slate-200/80 flex items-center gap-3">
          <div className="h-9 w-9 rounded-lg bg-red-600 flex items-center justify-center text-white shadow-md">
            <Mountain size={20} className="stroke-[2.5]" />
          </div>
          <div>
            <h1 className="text-base font-extrabold text-slate-900 tracking-tight leading-none">
              NER-Landslide
            </h1>
            <p className="text-[11px] font-medium text-slate-500 mt-1">
              Early Warning System
            </p>
          </div>
        </div>

        {/* NAVIGATION LINKS */}
        <nav className="flex-1 overflow-y-auto px-3 py-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => {
                  setActiveTab(item.id);
                  if (item.id === 'alerts') setShowAlertsModal(true);
                }}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 shadow-sm'
                    : 'text-slate-600 hover:bg-slate-200/60 hover:text-slate-900'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    size={16}
                    className={isActive ? 'text-blue-600' : 'text-slate-400'}
                  />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">
                    {item.badge}
                  </span>
                )}
                {isActive && !item.badge && (
                  <ChevronRight size={14} className="text-blue-600" />
                )}
              </button>
            );
          })}
        </nav>

        {/* SIDEBAR FOOTER */}
        <div className="p-3 border-t border-slate-200/80 bg-slate-100/50 text-[10px] text-slate-400 font-medium">
          <p className="font-bold text-slate-600">NER Landslide EWS</p>
          <p className="mt-0.5">Prototype v1.0 — 2026</p>
          <p className="mt-0.5">College Hackathon Project</p>
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
        {/* TOP HEADER BAR */}
        <header className="h-14 bg-white border-b border-slate-200 px-4 flex items-center justify-between flex-shrink-0 z-20 shadow-xs">
          <div className="flex items-center gap-4">
            <button
              type="button"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-md transition"
              title="Toggle sidebar"
            >
              <Menu size={18} />
            </button>

            <div className="flex items-center gap-3 text-xs font-semibold">
              <div className="flex items-center gap-1.5 text-slate-700 bg-slate-100 px-2.5 py-1 rounded-md">
                <MapPin size={14} className="text-blue-600" />
                <span>NER Regional Disaster Center — Shillong Command</span>
              </div>
              <span className="text-slate-300">|</span>
              <div className="flex items-center gap-1.5 text-emerald-600 font-medium">
                <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                <span>System Operational</span>
              </div>
              <span className="text-slate-300">|</span>
              <div className="flex items-center gap-1 text-slate-400 font-normal">
                <RefreshCw size={12} className="animate-spin" />
                <span>Updated 0s ago</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setShowAlertsModal(true)}
              className="relative p-2 text-slate-600 hover:bg-slate-100 rounded-full transition"
              title="View Alerts"
            >
              <Bell size={18} />
              <span className="absolute top-1 right-1 h-4 w-4 bg-red-500 text-white text-[9px] font-bold flex items-center justify-center rounded-full border border-white">
                3
              </span>
            </button>

            <button
              type="button"
              onClick={() => setShowDisasterAI(!showDisasterAI)}
              className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 text-white rounded-lg text-xs font-bold shadow-sm hover:bg-blue-700 transition"
            >
              <Radio size={14} />
              <span>Ask AI Assistant</span>
            </button>

            <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
              <div className="h-8 w-8 rounded-full bg-slate-800 text-white flex items-center justify-center font-bold text-xs">
                <User size={16} />
              </div>
              <span className="text-xs font-semibold text-slate-700 hidden sm:inline">
                District Control
              </span>
            </div>
          </div>
        </header>

        {/* 2-COLUMN MAP & PANELS WORKSPACE */}
        <div className="flex-1 flex min-h-0 relative">
          {/* CENTER: INTERACTIVE MAP VIEW */}
          <main className="flex-1 relative bg-slate-200 overflow-hidden">
            {/* TOP OVERLAY TAGS */}
            <div className="absolute top-3 left-3 z-10 flex items-center gap-2 pointer-events-auto">
              <div className="px-3 py-1 bg-amber-100/90 border border-amber-300 text-amber-800 text-xs font-bold rounded-md shadow-sm backdrop-blur-xs flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-amber-500" />
                <span>DEMO / SIMULATION DATA</span>
              </div>

              <button
                type="button"
                onClick={() => setEvacuationMode(!evacuationMode)}
                className={`px-3 py-1 text-xs font-bold rounded-md shadow-sm transition flex items-center gap-1.5 ${
                  evacuationMode
                    ? 'bg-red-600 text-white border border-red-700 animate-pulse'
                    : 'bg-red-500 text-white hover:bg-red-600'
                }`}
              >
                <AlertTriangle size={14} />
                <span>
                  {evacuationMode ? 'Evacuation Mode ACTIVE' : 'Evacuation Mode'}
                </span>
              </button>
            </div>

            {/* MAP CANVAS CONTAINER */}
            <div ref={mapContainer} className="w-full h-full" />

            {/* CUSTOM INTERACTIVE MAP MARKERS OVERLAY */}
            <div className="absolute inset-0 pointer-events-none z-10">
              {layerState.riskZones &&
                ZONES.map((zone) => (
                  <button
                    key={zone.id}
                    type="button"
                    onClick={() => setSelectedZone(zone)}
                    style={{
                      left: `${35 + (zone.coordinates[0] - 88) * 12}%`,
                      top: `${25 + (27.5 - zone.coordinates[1]) * 15}%`,
                    }}
                    className={`absolute pointer-events-auto transform -translate-x-1/2 -translate-y-1/2 flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-bold shadow-lg transition-transform hover:scale-110 border ${getLevelBadgeClass(
                      zone.level
                    )}`}
                  >
                    <span
                      className="h-2.5 w-2.5 rounded-full"
                      style={{ backgroundColor: getLevelColor(zone.level) }}
                    />
                    <span>{zone.name}</span>
                  </button>
                ))}

              {layerState.shelters &&
                SHELTERS.map((s, idx) => (
                  <div
                    key={s.name}
                    style={{
                      left: `${42 + idx * 10}%`,
                      top: `${32 + idx * 11}%`,
                    }}
                    className="absolute pointer-events-auto transform -translate-x-1/2 -translate-y-1/2 bg-slate-900 text-white px-2 py-0.5 rounded text-[11px] font-bold shadow-md flex items-center gap-1 border border-slate-700"
                  >
                    <Home size={12} className="text-amber-400" />
                    <span>Shelter</span>
                  </div>
                ))}
            </div>
          </main>

          {/* RIGHT SIDEBAR CONTROL & DETAIL PANELS */}
          <aside className="w-80 bg-white border-l border-slate-200 flex flex-col flex-shrink-0 overflow-y-auto p-4 space-y-4 shadow-xs z-20">
            {/* MAP LAYERS CARD */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 shadow-xs">
              <div className="flex items-center gap-1.5 text-xs font-bold text-slate-500 tracking-wider uppercase mb-3">
                <Layers size={14} className="text-slate-400" />
                <span>MAP LAYERS</span>
              </div>

              <div className="grid grid-cols-1 gap-2 text-xs font-medium text-slate-700">
                {[
                  { key: 'riskZones', label: 'Risk Zones' },
                  { key: 'rainfall', label: 'Rainfall' },
                  { key: 'soilMoisture', label: 'Soil Moisture' },
                  { key: 'roads', label: 'Roads' },
                  { key: 'villages', label: 'Villages' },
                  { key: 'infrastructure', label: 'Infrastructure' },
                  { key: 'sensors', label: 'Sensors' },
                  { key: 'fieldReports', label: 'Field Reports' },
                  { key: 'shelters', label: 'Shelters' },
                  { key: 'landslideHistory', label: 'Landslide History' },
                ].map((item) => {
                  const isChecked =
                    layerState[item.key as keyof typeof layerState];
                  return (
                    <label
                      key={item.key}
                      className="flex items-center gap-2.5 cursor-pointer hover:text-slate-900 select-none"
                    >
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() =>
                          toggleLayer(item.key as keyof typeof layerState)
                        }
                        className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span>{item.label}</span>
                    </label>
                  );
                })}
              </div>
            </div>

            {/* MAP LEGEND CARD */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 shadow-xs">
              <div className="flex items-center justify-between text-xs font-bold text-slate-500 tracking-wider uppercase mb-2.5">
                <span>MAP LEGEND</span>
                <span className="text-[10px] text-slate-400 font-medium">
                  RISK LEVEL
                </span>
              </div>

              <div className="space-y-1.5 text-xs font-bold">
                <div className="flex items-center gap-2 text-slate-700">
                  <span className="h-3 w-3 rounded bg-red-600" />
                  <span>CRITICAL</span>
                </div>
                <div className="flex items-center gap-2 text-slate-700">
                  <span className="h-3 w-3 rounded bg-orange-500" />
                  <span>HIGH</span>
                </div>
                <div className="flex items-center gap-2 text-slate-700">
                  <span className="h-3 w-3 rounded bg-yellow-500" />
                  <span>MEDIUM</span>
                </div>
                <div className="flex items-center gap-2 text-slate-700">
                  <span className="h-3 w-3 rounded bg-emerald-600" />
                  <span>LOW</span>
                </div>
              </div>
            </div>

            {/* SELECTED ZONE CARD */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 shadow-xs space-y-3">
              <div className="text-xs font-bold text-slate-500 tracking-wider uppercase">
                SELECTED ZONE
              </div>

              <div className="flex items-center justify-between">
                <h3 className="text-base font-extrabold text-slate-900">
                  {selectedZone.name}
                </h3>
                <span
                  className={`px-2.5 py-0.5 text-[11px] font-bold rounded-full border ${getLevelBadgeClass(
                    selectedZone.level
                  )}`}
                >
                  {selectedZone.level}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="bg-white p-2.5 rounded-lg border border-slate-200 shadow-2xs">
                  <p className="text-[10px] font-semibold text-slate-400">
                    ML Probability
                  </p>
                  <p className="text-base font-bold text-slate-900 mt-0.5">
                    {selectedZone.mlProb}
                  </p>
                </div>

                <div className="bg-white p-2.5 rounded-lg border border-slate-200 shadow-2xs">
                  <p className="text-[10px] font-semibold text-slate-400">
                    TRIGRS FoS
                  </p>
                  <p className="text-base font-bold text-red-600 mt-0.5">
                    {selectedZone.fos}
                  </p>
                </div>

                <div className="bg-white p-2.5 rounded-lg border border-slate-200 shadow-2xs">
                  <p className="text-[10px] font-semibold text-slate-400">
                    Rainfall
                  </p>
                  <p className="text-xs font-bold text-slate-800 mt-1">
                    {selectedZone.rainfall}
                  </p>
                </div>

                <div className="bg-white p-2.5 rounded-lg border border-slate-200 shadow-2xs">
                  <p className="text-[10px] font-semibold text-slate-400">
                    Soil Moisture
                  </p>
                  <p className="text-xs font-bold text-slate-800 mt-1">
                    {selectedZone.soilMoisture}
                  </p>
                </div>
              </div>
            </div>
          </aside>
        </div>
      </div>

      {/* MODAL DIALOGS */}
      {showDisasterAI && (
        <DisasterAIAssistant
          onClose={() => setShowDisasterAI(false)}
          selectedLocation={selectedZone.name}
        />
      )}
      {showAlertsModal && (
        <AlertCenter onClose={() => setShowAlertsModal(false)} />
      )}
      {showRouteModal && (
        <RouteSystem map={map.current} onClose={() => setShowRouteModal(false)} />
      )}
    </div>
  );
}
