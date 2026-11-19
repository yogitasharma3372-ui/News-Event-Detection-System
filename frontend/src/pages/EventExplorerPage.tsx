import React, { useEffect, useState } from 'react';
import { Layers, RefreshCw, SlidersHorizontal, ChevronRight, Search, Play } from 'lucide-react';
import { api } from '../api/client';
import { Event } from '../types';
import { EventCard } from '../components/EventCard';

interface EventExplorerPageProps {
  onOpenEvent: (event: Event) => void;
}

export const EventExplorerPage: React.FC<EventExplorerPageProps> = ({ onOpenEvent }) => {
  const [events, setEvents] = useState<Event[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [isLoading, setIsLoading] = useState(true);

  // Filters & Search
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  
  // Reprocess / Clustering Controls
  const [showConfig, setShowConfig] = useState(false);
  const [alpha, setAlpha] = useState(0.55);
  const [beta, setBeta] = useState(0.25);
  const [gamma, setGamma] = useState(0.20);
  const [threshold, setThreshold] = useState(0.60);
  const [decayHours, setDecayHours] = useState(72.0);
  const [isClustering, setIsClustering] = useState(false);

  const fetchEvents = async () => {
    setIsLoading(true);
    try {
      const data = await api.getEvents({
        search,
        category,
        page,
        page_size: 12
      });
      setEvents(data.items);
      setTotal(data.total);
      setPages(data.pages);
    } catch (err) {
      console.error('Failed to load events:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [page, category]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchEvents();
  };

  const handleRunDetection = async () => {
    setIsClustering(true);
    try {
      const res = await api.detectEvents({
        alpha,
        beta,
        gamma,
        similarity_threshold: threshold,
        decay_hours: decayHours
      });
      alert(`Event detection complete! Formed ${res.events_created} event clusters from ${res.clustered_articles} articles.`);
      setPage(1);
      fetchEvents();
    } catch (err: any) {
      alert(`Detection error: ${err.message}`);
    } finally {
      setIsClustering(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Filter and Reprocessing Bar */}
      <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
          <form onSubmit={handleSearchSubmit} className="relative flex-1 w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search event title..."
              className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </form>

          <div className="flex items-center space-x-2 w-full sm:w-auto">
            <select
              value={category}
              onChange={(e) => { setCategory(e.target.value); setPage(1); }}
              className="px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-blue-500"
            >
              <option value="">All Categories</option>
              <option value="Natural Disasters">Natural Disasters</option>
              <option value="Science">Science</option>
              <option value="Economy">Economy</option>
              <option value="Environment">Environment</option>
              <option value="Politics">Politics</option>
              <option value="Culture">Culture</option>
            </select>

            <button
              onClick={() => setShowConfig(!showConfig)}
              className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs font-medium border transition cursor-pointer ${
                showConfig
                  ? 'bg-blue-600 text-white border-blue-500'
                  : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
              }`}
            >
              <SlidersHorizontal className="w-3.5 h-3.5" />
              <span>Model Parameters</span>
            </button>
          </div>
        </div>

        {/* Reprocessing Controls Drawer */}
        {showConfig && (
          <div className="p-4 bg-slate-900/90 border border-slate-800 rounded-lg space-y-4 text-xs">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-semibold text-slate-200">Event Clustering Parameters</h4>
                <p className="text-[11px] text-slate-400">
                  Tune hybrid weights and similarity thresholds. Reprocessing updates all event clusters while protecting manual human corrections.
                </p>
              </div>
              <button
                onClick={handleRunDetection}
                disabled={isClustering}
                className="flex items-center space-x-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg shadow-sm transition disabled:opacity-50 cursor-pointer"
              >
                <Play className="w-3.5 h-3.5" />
                <span>{isClustering ? 'Clustering...' : 'Reprocess All Events'}</span>
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
              <div>
                <label className="flex justify-between text-slate-300 mb-1">
                  <span>Semantic Weight (α)</span>
                  <span className="font-mono text-blue-400">{alpha.toFixed(2)}</span>
                </label>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.05"
                  value={alpha}
                  onChange={(e) => setAlpha(parseFloat(e.target.value))}
                  className="w-full accent-blue-500"
                />
              </div>

              <div>
                <label className="flex justify-between text-slate-300 mb-1">
                  <span>Temporal Decay (β)</span>
                  <span className="font-mono text-emerald-400">{beta.toFixed(2)}</span>
                </label>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.05"
                  value={beta}
                  onChange={(e) => setBeta(parseFloat(e.target.value))}
                  className="w-full accent-emerald-500"
                />
              </div>

              <div>
                <label className="flex justify-between text-slate-300 mb-1">
                  <span>Entity Overlap (γ)</span>
                  <span className="font-mono text-amber-400">{gamma.toFixed(2)}</span>
                </label>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.05"
                  value={gamma}
                  onChange={(e) => setGamma(parseFloat(e.target.value))}
                  className="w-full accent-amber-500"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
              <div>
                <label className="flex justify-between text-slate-300 mb-1">
                  <span>Similarity Threshold</span>
                  <span className="font-mono text-slate-200">{threshold.toFixed(2)}</span>
                </label>
                <input
                  type="range"
                  min="0.30"
                  max="0.90"
                  step="0.02"
                  value={threshold}
                  onChange={(e) => setThreshold(parseFloat(e.target.value))}
                  className="w-full accent-slate-400"
                />
              </div>

              <div>
                <label className="flex justify-between text-slate-300 mb-1">
                  <span>Temporal Half-Decay Window (hours)</span>
                  <span className="font-mono text-slate-200">{decayHours}h</span>
                </label>
                <input
                  type="range"
                  min="12"
                  max="168"
                  step="12"
                  value={decayHours}
                  onChange={(e) => setDecayHours(parseFloat(e.target.value))}
                  className="w-full accent-slate-400"
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Events Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between text-xs text-slate-400 px-1">
          <span>Total Detected Events: <strong className="text-slate-200">{total}</strong></span>
          <span>Page {page} of {pages}</span>
        </div>

        {isLoading ? (
          <div className="py-16 flex flex-col items-center justify-center space-y-3">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-xs text-slate-400">Loading events...</p>
          </div>
        ) : events.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {events.map((evt) => (
              <EventCard
                key={evt.id}
                event={evt}
                onClick={onOpenEvent}
              />
            ))}
          </div>
        ) : (
          <div className="py-16 text-center text-xs text-slate-500 bg-[#0f172a] rounded-xl border border-slate-800 space-y-3">
            <p>No event clusters found in database.</p>
            <button
              onClick={handleRunDetection}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition font-medium"
            >
              Run Event Detection on Existing Articles
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
