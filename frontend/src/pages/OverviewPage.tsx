import React, { useEffect, useState } from 'react';
import {
  FileText,
  Layers,
  HelpCircle,
  Radio,
  Clock,
  Sparkles,
  ArrowRight,
  TrendingUp
} from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, PieChart, Pie, Cell } from 'recharts';
import { api } from '../api/client';
import { SystemMetadata, Event } from '../types';
import { MetricCard } from '../components/MetricCard';

interface OverviewPageProps {
  onNavigateTab: (tab: any) => void;
  onOpenEvent: (event: Event) => void;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#64748b'];

export const OverviewPage: React.FC<OverviewPageProps> = ({
  onNavigateTab,
  onOpenEvent
}) => {
  const [metadata, setMetadata] = useState<SystemMetadata | null>(null);
  const [recentEvents, setRecentEvents] = useState<Event[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isImportingFixture, setIsImportingFixture] = useState(false);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [meta, eventsData] = await Promise.all([
        api.getMetadata(),
        api.getEvents({ page_size: 5 })
      ]);
      setMetadata(meta);
      setRecentEvents(eventsData.items);
    } catch (err: any) {
      setError(err.message || 'Failed to load system metadata.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleImportFixture = async () => {
    setIsImportingFixture(true);
    try {
      await api.importFixture();
      await api.detectEvents({});
      await loadData();
    } catch (err: any) {
      alert(`Import error: ${err.message}`);
    } finally {
      setIsImportingFixture(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs text-slate-400">Loading intelligence dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm space-y-3">
        <p className="font-semibold">Unable to connect to backend service</p>
        <p className="text-xs">{error}</p>
        <button
          onClick={loadData}
          className="px-3 py-1.5 bg-red-600 hover:bg-red-500 text-white text-xs rounded-lg transition"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  const categoryChartData = Object.entries(metadata?.event_categories_distribution || {}).map(([name, value]) => ({
    name,
    count: value
  }));

  const isEmpty = (metadata?.total_articles || 0) === 0;

  return (
    <div className="space-y-6">
      {/* Top Banner if Database is Empty */}
      {isEmpty && (
        <div className="p-6 bg-blue-950/40 border border-blue-800/60 rounded-2xl flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="space-y-1">
            <h3 className="text-base font-semibold text-blue-200">
              Welcome to the News Event Detection Research System
            </h3>
            <p className="text-xs text-blue-300/80 max-w-xl">
              The database is currently initialized and clean. Load the verified research fixture dataset (14 articles, 4 ground-truth event clusters) or import your own CSV/JSON files to begin experimentation.
            </p>
          </div>
          <button
            onClick={handleImportFixture}
            disabled={isImportingFixture}
            className="flex items-center space-x-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow-md transition disabled:opacity-50 shrink-0 cursor-pointer"
          >
            <Sparkles className="w-4 h-4" />
            <span>{isImportingFixture ? 'Importing & Clustering...' : 'Load Benchmark Fixture'}</span>
          </button>
        </div>
      )}

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Articles"
          value={metadata?.total_articles ?? 0}
          subtitle={`${metadata?.assigned_articles ?? 0} assigned to events`}
          icon={FileText}
          color="blue"
        />
        <MetricCard
          title="Detected Events"
          value={metadata?.total_events ?? 0}
          subtitle="Formed event clusters"
          icon={Layers}
          color="emerald"
        />
        <MetricCard
          title="Unassigned / Noise"
          value={metadata?.unassigned_articles ?? 0}
          subtitle="Distinct singleton stories"
          icon={HelpCircle}
          color="amber"
        />
        <MetricCard
          title="Active Sources"
          value={metadata?.total_sources ?? 0}
          subtitle={metadata?.latest_ingestion_timestamp ? `Latest: ${new Date(metadata.latest_ingestion_timestamp).toLocaleDateString()}` : 'No recent sync'}
          icon={Radio}
          color="purple"
        />
      </div>

      {/* Middle Visuals: Distribution & Model Parameters */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-[#0f172a] border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-slate-100">Event Distribution by Category</h3>
              <p className="text-xs text-slate-500">Clusters categorized via extractive entity & keyword signals</p>
            </div>
            <span className="text-xs text-slate-400 font-mono">
              {metadata?.total_events} clusters
            </span>
          </div>

          {categoryChartData.length > 0 ? (
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categoryChartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <XAxis dataKey="name" stroke="#64748b" fontSize={11} angle={-15} textAnchor="end" />
                  <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                    labelStyle={{ color: '#f1f5f9', fontWeight: 'bold' }}
                  />
                  <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-xs text-slate-500">
              No categorized events available yet.
            </div>
          )}
        </div>

        {/* System & Model Intelligence Card */}
        <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-5 space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div>
              <h3 className="text-sm font-semibold text-slate-100">Research Model Parameters</h3>
              <p className="text-xs text-slate-500">Active hybrid similarity weighting</p>
            </div>

            <div className="space-y-2.5 pt-2 text-xs">
              <div>
                <div className="flex justify-between text-slate-400 mb-1">
                  <span>Semantic Weight (α)</span>
                  <span className="font-semibold text-blue-400 font-mono">
                    {metadata?.hybrid_weights.alpha_semantic.toFixed(2)}
                  </span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div
                    className="bg-blue-500 h-full rounded-full"
                    style={{ width: `${(metadata?.hybrid_weights.alpha_semantic || 0) * 100}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-400 mb-1">
                  <span>Temporal Decay (β)</span>
                  <span className="font-semibold text-emerald-400 font-mono">
                    {metadata?.hybrid_weights.beta_temporal.toFixed(2)}
                  </span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div
                    className="bg-emerald-500 h-full rounded-full"
                    style={{ width: `${(metadata?.hybrid_weights.beta_temporal || 0) * 100}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-400 mb-1">
                  <span>Entity Overlap (γ)</span>
                  <span className="font-semibold text-amber-400 font-mono">
                    {metadata?.hybrid_weights.gamma_entity.toFixed(2)}
                  </span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div
                    className="bg-amber-500 h-full rounded-full"
                    style={{ width: `${(metadata?.hybrid_weights.gamma_entity || 0) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800/80 space-y-2 text-xs text-slate-400">
            <div className="flex items-center justify-between">
              <span>Embedding Engine:</span>
              <span className="text-slate-200 font-mono text-[11px] truncate max-w-[150px]">
                all-MiniLM-L6-v2
              </span>
            </div>
            <button
              onClick={() => onNavigateTab('research-lab')}
              className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg transition flex items-center justify-center space-x-1 cursor-pointer"
            >
              <span>Explore Research Lab</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Latest Detected Events */}
      <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Latest Detected Events</h3>
            <p className="text-xs text-slate-500">Recent chronological event clusters detected by hybrid inference</p>
          </div>
          <button
            onClick={() => onNavigateTab('event-explorer')}
            className="text-xs text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1 cursor-pointer"
          >
            <span>View All Events</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {recentEvents.length > 0 ? (
          <div className="divide-y divide-slate-800/80">
            {recentEvents.map((evt) => (
              <div
                key={evt.id}
                onClick={() => onOpenEvent(evt)}
                className="py-3 flex items-center justify-between gap-4 hover:bg-slate-800/30 px-3 rounded-lg transition cursor-pointer"
              >
                <div className="space-y-1 min-w-0">
                  <div className="flex items-center gap-2 text-xs">
                    <span className="px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 text-[11px] font-semibold">
                      {evt.article_count} articles
                    </span>
                    <span className="text-slate-500 text-[11px]">{evt.category}</span>
                  </div>
                  <h4 className="text-sm font-medium text-slate-200 truncate">{evt.title}</h4>
                </div>
                <div className="text-right text-xs text-slate-500 shrink-0">
                  <div>{new Date(evt.last_observed_at).toLocaleDateString()}</div>
                  <span className="text-[10px] text-slate-600 font-mono">{evt.id}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="py-8 text-center text-xs text-slate-500">
            No events detected yet. Click "Load Benchmark Fixture" above to cluster sample articles.
          </div>
        )}
      </div>
    </div>
  );
};
