import React from 'react';

interface Feature {
  type: 'Feature';
  id: string | number;
  properties: Record<string, any>;
  geometry: {
    type: string;
    coordinates: any[];
  };
}

interface SelectedFeatureData {
  type: string;
  data: Feature | null;
}

interface InfoPanelProps {
  selectedFeature: SelectedFeatureData | null;
}

export function InfoPanel({ selectedFeature }: InfoPanelProps) {
  const renderContent = () => {
    if (!selectedFeature || !selectedFeature.data) {
      return (
        <div className="p-6 text-center text-gray-500">
          <p className="text-sm">Click a map feature to inspect its information</p>
        </div>
      );
    }

    const feature = selectedFeature.data;
    const props = feature.properties || {};
    const coords = feature.geometry?.coordinates || [];

    const getTypeLabel = () => {
      switch (selectedFeature.type) {
        case 'landslide':
          return 'Historical Landslide Event';
        case 'state':
          return 'State Boundary';
        case 'village':
          return 'Village/Settlement';
        case 'road':
          return 'Road';
        default:
          return 'Feature';
      }
    };

    return (
      <div className="space-y-4">
        {/* Header */}
        <div className="bg-blue-50 p-4 border-b border-blue-200">
          <p className="text-xs text-blue-600 font-semibold uppercase tracking-wide">
            {getTypeLabel()}
          </p>
          <p className="text-lg font-bold text-gray-900 mt-1">
            {props.name || props.event_id || props.state || 'Unnamed Feature'}
          </p>
        </div>

        {/* Properties */}
        <div className="px-4 py-3 space-y-3">
          {/* Coordinates */}
          {coords.length >= 2 && (
            <div>
              <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                Coordinates
              </p>
              <p className="text-sm text-gray-900 font-mono">
                {coords[1]?.toFixed(6)}, {coords[0]?.toFixed(6)}
              </p>
            </div>
          )}

          {/* Event-specific properties */}
          {selectedFeature.type === 'landslide' && (
            <>
              {props.event_id && (
                <div>
                  <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    Event ID
                  </p>
                  <p className="text-sm text-gray-900">{props.event_id}</p>
                </div>
              )}
              {props.date && (
                <div>
                  <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    Date
                  </p>
                  <p className="text-sm text-gray-900">{props.date}</p>
                </div>
              )}
              {props.state && (
                <div>
                  <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    State
                  </p>
                  <p className="text-sm text-gray-900">{props.state}</p>
                </div>
              )}
              {props.district && (
                <div>
                  <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    District
                  </p>
                  <p className="text-sm text-gray-900">{props.district}</p>
                </div>
              )}
              {props.type_of_movement && (
                <div>
                  <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    Type of Movement
                  </p>
                  <p className="text-sm text-gray-900">{props.type_of_movement}</p>
                </div>
              )}
              {props.trigger && (
                <div>
                  <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    Trigger
                  </p>
                  <p className="text-sm text-gray-900">{props.trigger}</p>
                </div>
              )}
              {props.source && (
                <div>
                  <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    Data Source
                  </p>
                  <p className="text-sm text-gray-900">{props.source}</p>
                </div>
              )}
            </>
          )}

          {/* State properties */}
          {selectedFeature.type === 'state' && (
            <>
              {props.state_name && (
                <div>
                  <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    State Name
                  </p>
                  <p className="text-sm text-gray-900">{props.state_name}</p>
                </div>
              )}
              {props.population && (
                <div>
                  <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    Population
                  </p>
                  <p className="text-sm text-gray-900">{props.population.toLocaleString()}</p>
                </div>
              )}
            </>
          )}

          {/* Village properties */}
          {selectedFeature.type === 'village' && (
            <>
              {props.village_name && (
                <div>
                  <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    Village Name
                  </p>
                  <p className="text-sm text-gray-900">{props.village_name}</p>
                </div>
              )}
              {props.population && (
                <div>
                  <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    Population
                  </p>
                  <p className="text-sm text-gray-900">{props.population.toLocaleString()}</p>
                </div>
              )}
              {props.district && (
                <div>
                  <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    District
                  </p>
                  <p className="text-sm text-gray-900">{props.district}</p>
                </div>
              )}
            </>
          )}

          {/* Generic properties */}
          {Object.entries(props).map(([key, value]) => {
            // Skip already displayed properties
            if (['name', 'event_id', 'date', 'state', 'district', 'village_name', 
                  'type_of_movement', 'trigger', 'source', 'state_name', 'population'].includes(key)) {
              return null;
            }
            // Skip geometry properties
            if (key.startsWith('_') || key === 'properties') return null;

            return (
              <div key={key}>
                <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                  {key.replace(/_/g, ' ')}
                </p>
                <p className="text-sm text-gray-900">
                  {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                </p>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="px-4 py-3 border-t border-gray-200 bg-gray-50 text-xs text-gray-500">
          <p>Click another feature to inspect, or click the map to close</p>
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-white">
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <h2 className="text-lg font-bold text-gray-900">Feature Information</h2>
      </div>
      <div className="flex-1 overflow-y-auto">
        {renderContent()}
      </div>
    </div>
  );
}
