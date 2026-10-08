import React, { useMemo, useState } from 'react';
import maplibregl from 'maplibre-gl';

interface SearchBoxProps {
  map: maplibregl.Map | null;
}

const SAMPLE_SEARCH_RESULTS = [
  { name: 'Itanagar', type: 'district', center: [93.6167, 27.1], zoom: 11 },
  { name: 'Gangtok', type: 'district', center: [88.6065, 27.3314], zoom: 11 },
  { name: 'Guwahati', type: 'city', center: [91.7362, 26.1445], zoom: 11 },
  { name: 'Kohima', type: 'district', center: [94.1086, 25.6741], zoom: 11 },
  { name: 'Aizawl', type: 'district', center: [92.7362, 23.736], zoom: 11 },
  { name: 'Shillong', type: 'city', center: [91.8831, 25.5788], zoom: 12 },
  { name: 'Agartala', type: 'district', center: [91.2794, 23.8315], zoom: 11 },
  { name: 'Imphal', type: 'district', center: [93.9378, 24.817], zoom: 11 },
  { name: 'NH-39', type: 'road', center: [93.7, 25.9], zoom: 13 },
  { name: 'NH-37', type: 'road', center: [92.6, 26.1], zoom: 13 },
  { name: 'West Khasi Hills', type: 'district', center: [91.3, 25.4], zoom: 10 },
  { name: 'Mizoram', type: 'state', center: [92.8, 23.3], zoom: 8 },
  { name: '26.1445, 91.7362', type: 'coordinates', center: [91.7362, 26.1445], zoom: 12 },
];

export function SearchBox({ map }: SearchBoxProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const queryMatches = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return [];

    return SAMPLE_SEARCH_RESULTS.filter((item) =>
      item.name.toLowerCase().includes(q) ||
      item.type.toLowerCase().includes(q)
    ).slice(0, 8);
  }, [query]);

  const handleSearch = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed || !map) return;

    setIsSearching(true);
    try {
      const exact = SAMPLE_SEARCH_RESULTS.find(
        (item) => item.name.toLowerCase() === trimmed.toLowerCase()
      );

      const localMatches = queryMatches.length > 0 ? queryMatches : [];
      setResults(exact ? [exact, ...localMatches.filter((entry) => entry.name !== exact.name)] : localMatches);

      const coordinateMatch = trimmed.match(/^(-?\d+(?:\.\d+)?),\s*(-?\d+(?:\.\d+)?)$/);
      if (coordinateMatch) {
        const lon = Number(coordinateMatch[2]);
        const lat = Number(coordinateMatch[1]);
        map.flyTo({ center: [lon, lat], zoom: 12, duration: 1000 });
        setResults([]);
        setQuery('');
      } else if (exact) {
        map.flyTo({ center: [exact.center[0], exact.center[1]], zoom: exact.zoom || 12, duration: 1000 });
        setResults([]);
        setQuery('');
      }
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
        center: [result.center[0], result.center[1]],
        zoom: result.zoom || 12,
        duration: 1000,
      });
      setResults([]);
      setQuery('');
    }
  };

  return (
    <div className="relative w-[270px]">
      <form onSubmit={handleSearch} className="w-full">
        <input
          type="text"
          placeholder="Search places, roads, villages or coordinates"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setResults(queryMatches);
          }}
          className="w-full rounded-lg border border-slate-700 bg-slate-900/85 px-3 py-2 text-[10px] font-medium uppercase tracking-[0.12em] text-slate-100 placeholder:text-slate-400 focus:border-cyan-400 focus:outline-none shadow-lg"
        />
      </form>

      {isSearching && (
        <div className="absolute top-full left-0 right-0 mt-2 rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-[10px] uppercase tracking-[0.12em] text-slate-300 z-30">
          Searching...
        </div>
      )}

      {results.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-2 rounded-lg border border-slate-700 bg-slate-900/95 shadow-2xl z-30 max-h-64 overflow-y-auto">
          {results.map((result, idx) => (
            <button
              key={`${result.name}-${idx}`}
              type="button"
              onClick={() => handleResultClick(result)}
              className="w-full text-left px-3 py-2.5 hover:bg-slate-800 border-b border-slate-700 last:border-b-0"
            >
              <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-slate-100">{result.name}</p>
              <p className="mt-1 text-[9px] uppercase tracking-[0.16em] text-slate-400">{result.type}</p>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
