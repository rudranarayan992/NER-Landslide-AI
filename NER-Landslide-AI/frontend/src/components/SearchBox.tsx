import React, { useState } from 'react';
import maplibregl from 'maplibre-gl';

interface SearchBoxProps {
  map: maplibregl.Map | null;
}

export function SearchBox({ map }: SearchBoxProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!query.trim() || !map) return;

    setIsSearching(true);
    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      setResults(data.results || []);
    } catch (error) {
      console.error('Search failed:', error);
      setResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleResultClick = (result: any) => {
    if (map && result.center) {
      map.flyTo({
        center: [result.center[1], result.center[0]],
        zoom: result.zoom || 12,
        duration: 1000,
      });
      setResults([]);
      setQuery('');
    }
  };

  return (
    <div className="relative flex-1 max-w-md">
      <form onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Search states, districts, villages..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </form>

      {results.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 max-h-64 overflow-y-auto">
          {results.map((result, idx) => (
            <button
              key={idx}
              onClick={() => handleResultClick(result)}
              className="w-full text-left px-3 py-2 hover:bg-blue-50 transition-colors border-b border-gray-100 last:border-b-0"
            >
              <p className="text-sm font-medium text-gray-900">{result.name}</p>
              <p className="text-xs text-gray-600">{result.type}</p>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
