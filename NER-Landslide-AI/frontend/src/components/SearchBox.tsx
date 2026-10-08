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
    <div className="relative w-[230px]">
      <form onSubmit={handleSearch} className="w-full">
        <input
          type="text"
          placeholder="Search district, village, landslide..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full rounded-md border border-slate-700 bg-slate-900/80 px-2.5 py-1.5 text-[10px] uppercase tracking-[0.12em] text-slate-100 placeholder:text-slate-400 focus:border-cyan-400 focus:outline-none"
        />
      </form>

      {results.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 rounded-md border border-slate-700 bg-slate-900 shadow-xl z-20 max-h-64 overflow-y-auto">
          {results.map((result, idx) => (
            <button
              key={idx}
              onClick={() => handleResultClick(result)}
              className="w-full text-left px-2.5 py-2 hover:bg-slate-800 border-b border-slate-700 last:border-b-0"
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
