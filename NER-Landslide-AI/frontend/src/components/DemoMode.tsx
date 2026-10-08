import React, { useState, useEffect } from 'react';

interface SystemStatusData {
  verified: number;
  operational: number;
  partial: number;
  awaiting_data: number;
  blocked: number;
  total: number;
}

interface Component {
  name: string;
  type: string;
  status: string;
  message: string;
  blocking_reasons?: string[];
}

interface DemoModeProps {
  onClose?: () => void;
}

const DemoMode: React.FC<DemoModeProps> = ({ onClose }) => {
  const [systemStatus, setSystemStatus] = useState<SystemStatusData | null>(null);
  const [components, setComponents] = useState<Record<string, Component>>({});
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'verified' | 'awaiting' | 'blocked'>('overview');

  useEffect(() => {
    fetchSystemStatus();
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch('/api/system-status');
      const data = await response.json();
      setSystemStatus(data.summary);
      setComponents(data.components);
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'VERIFIED':
        return 'bg-green-100 text-green-900 border-green-300';
      case 'OPERATIONAL':
        return 'bg-blue-100 text-blue-900 border-blue-300';
      case 'PARTIAL':
        return 'bg-yellow-100 text-yellow-900 border-yellow-300';
      case 'AWAITING_DATA':
        return 'bg-orange-100 text-orange-900 border-orange-300';
      case 'BLOCKED':
        return 'bg-red-100 text-red-900 border-red-300';
      default:
        return 'bg-gray-100 text-gray-900 border-gray-300';
    }
  };

  const getStatusBadgeColor = (status: string): string => {
    switch (status) {
      case 'VERIFIED':
      case 'OPERATIONAL':
        return 'bg-green-500';
      case 'PARTIAL':
        return 'bg-yellow-500';
      case 'AWAITING_DATA':
        return 'bg-orange-500';
      case 'BLOCKED':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const filteredComponents = Object.entries(components).filter(([_, comp]) => {
    switch (activeTab) {
      case 'verified':
        return ['VERIFIED', 'OPERATIONAL'].includes(comp.status);
      case 'awaiting':
        return comp.status === 'AWAITING_DATA';
      case 'blocked':
        return comp.status === 'BLOCKED' || comp.status === 'PARTIAL';
      default:
        return true;
    }
  });

  if (loading) {
    return (
      <div className="w-full h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="w-full min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      {/* Header Banner */}
      <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded">
        <h1 className="text-2xl font-bold text-red-900 mb-2">
          ⚠️ DEMONSTRATION MODE - NOT OPERATIONAL
        </h1>
        <p className="text-red-700">
          This system is demonstrating complete architecture with scientifically honest status labels.
          Some components are intentionally marked BLOCKED or AWAITING DATA to reflect real system state.
        </p>
      </div>

      {/* Summary Statistics */}
      {systemStatus && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow border-t-4 border-green-500">
            <div className="text-2xl font-bold text-green-600">{systemStatus.verified}</div>
            <div className="text-sm text-gray-600">Verified</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow border-t-4 border-blue-500">
            <div className="text-2xl font-bold text-blue-600">{systemStatus.operational}</div>
            <div className="text-sm text-gray-600">Operational</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow border-t-4 border-yellow-500">
            <div className="text-2xl font-bold text-yellow-600">{systemStatus.partial}</div>
            <div className="text-sm text-gray-600">Partial</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow border-t-4 border-orange-500">
            <div className="text-2xl font-bold text-orange-600">{systemStatus.awaiting_data}</div>
            <div className="text-sm text-gray-600">Awaiting Data</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow border-t-4 border-red-500">
            <div className="text-2xl font-bold text-red-600">{systemStatus.blocked}</div>
            <div className="text-sm text-gray-600">Blocked</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="flex border-b">
          <button
            onClick={() => setActiveTab('overview')}
            className={`flex-1 px-4 py-3 font-semibold ${
              activeTab === 'overview'
                ? 'border-b-2 border-indigo-600 text-indigo-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Complete Overview
          </button>
          <button
            onClick={() => setActiveTab('verified')}
            className={`flex-1 px-4 py-3 font-semibold ${
              activeTab === 'verified'
                ? 'border-b-2 border-indigo-600 text-indigo-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            ✓ Verified ({systemStatus?.verified || 0})
          </button>
          <button
            onClick={() => setActiveTab('awaiting')}
            className={`flex-1 px-4 py-3 font-semibold ${
              activeTab === 'awaiting'
                ? 'border-b-2 border-indigo-600 text-indigo-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            ⏳ Awaiting ({systemStatus?.awaiting_data || 0})
          </button>
          <button
            onClick={() => setActiveTab('blocked')}
            className={`flex-1 px-4 py-3 font-semibold ${
              activeTab === 'blocked'
                ? 'border-b-2 border-indigo-600 text-indigo-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            ✕ Blocked ({systemStatus?.blocked || 0})
          </button>
        </div>

        {/* Components List */}
        <div className="p-6">
          {filteredComponents.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No components in this category</p>
          ) : (
            <div className="space-y-4">
              {filteredComponents.map(([key, component]) => (
                <div
                  key={key}
                  className={`p-4 rounded-lg border-2 ${getStatusColor(component.status)}`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 className="font-bold text-lg">{component.name}</h3>
                      <p className="text-sm opacity-75">{component.type}</p>
                    </div>
                    <span className={`${getStatusBadgeColor(component.status)} text-white px-3 py-1 rounded-full text-sm font-semibold`}>
                      {component.status}
                    </span>
                  </div>
                  
                  <p className="mb-3">{component.message}</p>
                  
                  {component.blocking_reasons && component.blocking_reasons.length > 0 && (
                    <details className="text-sm">
                      <summary className="cursor-pointer font-semibold mb-2 opacity-75 hover:opacity-100">
                        Blocking Reasons ({component.blocking_reasons.length})
                      </summary>
                      <ul className="ml-4 space-y-1 opacity-75">
                        {component.blocking_reasons.map((reason, idx) => (
                          <li key={idx} className="list-disc">{reason}</li>
                        ))}
                      </ul>
                    </details>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Legend */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">Status Legend</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border-l-4 border-green-500 pl-4">
            <h3 className="font-bold text-green-700">✓ VERIFIED</h3>
            <p className="text-sm text-gray-600">Real, validated data or component</p>
          </div>
          <div className="border-l-4 border-blue-500 pl-4">
            <h3 className="font-bold text-blue-700">✓ OPERATIONAL</h3>
            <p className="text-sm text-gray-600">Working end-to-end in the system</p>
          </div>
          <div className="border-l-4 border-yellow-500 pl-4">
            <h3 className="font-bold text-yellow-700">◐ PARTIAL</h3>
            <p className="text-sm text-gray-600">Partially implemented or working</p>
          </div>
          <div className="border-l-4 border-orange-500 pl-4">
            <h3 className="font-bold text-orange-700">⏳ AWAITING DATA</h3>
            <p className="text-sm text-gray-600">Implemented, waiting for verified data</p>
          </div>
          <div className="border-l-4 border-red-500 pl-4 md:col-span-2">
            <h3 className="font-bold text-red-700">✕ BLOCKED</h3>
            <p className="text-sm text-gray-600">Cannot proceed, documented scientific reason</p>
          </div>
        </div>
      </div>

      {/* Demonstration Path */}
      <div className="bg-white rounded-lg shadow p-6 mt-6">
        <h2 className="text-xl font-bold mb-4">Demonstration Path</h2>
        <ol className="space-y-2 text-sm">
          <li><span className="font-semibold">1.</span> Return to GIS Map to view 33,904 verified historical landslides</li>
          <li><span className="font-semibold">2.</span> Switch map layers (Street, Satellite, Topographic, Terrain)</li>
          <li><span className="font-semibold">3.</span> Click on a landslide to see detailed provenance and attributes</li>
          <li><span className="font-semibold">4.</span> Search for a state/district/village to navigate</li>
          <li><span className="font-semibold">5.</span> View road network and villages (verified infrastructure)</li>
          <li><span className="font-semibold">6.</span> Submit a field report to test report workflow</li>
          <li><span className="font-semibold">7.</span> Use LLM assistant to query historical data and data status</li>
          <li><span className="font-semibold">8.</span> Review this dashboard to understand complete architecture</li>
        </ol>
      </div>

      {/* Close Button */}
      {onClose && (
        <div className="mt-6 text-center">
          <button
            onClick={onClose}
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-6 rounded-lg"
          >
            Return to GIS Map
          </button>
        </div>
      )}
    </div>
  );
};

export default DemoMode;
