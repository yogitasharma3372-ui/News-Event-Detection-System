import React, { useEffect, useState } from 'react';
import { Radio, Play, RefreshCw, CheckCircle2, AlertTriangle, Clock, Globe } from 'lucide-react';
import { api } from '../api/client';
import { IngestionJob } from '../types';

export const LiveMonitorPage: React.FC = () => {
  const [jobs, setJobs] = useState<IngestionJob[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // Ingestion Form
  const [provider, setProvider] = useState<'rss' | 'newsapi'>('rss');
  const [query, setQuery] = useState('');
  const [feedUrl, setFeedUrl] = useState('');
  const [maxArticles, setMaxArticles] = useState(15);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fetchJobs = async () => {
    setIsLoading(true);
    try {
      const data = await api.getIngestionJobs();
      setJobs(data);
    } catch (err) {
      console.error('Failed to load ingestion jobs:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleTriggerIngestion = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      await api.triggerIngestion({
        provider,
        query: query.trim() || undefined,
        feed_url: feedUrl.trim() || undefined,
        max_articles: maxArticles
      });
      setQuery('');
      setFeedUrl('');
      await fetchJobs();
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to start ingestion job.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Ingestion Trigger Form */}
      <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-5 space-y-4">
        <div>
          <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
            <Radio className="w-5 h-5 text-blue-400" />
            <span>Live News Ingestion Engine</span>
          </h3>
          <p className="text-xs text-slate-400">
            Fetch live news stories from open RSS feeds or configured API providers with automatic deduplication and online incremental assignment.
          </p>
        </div>

        {errorMessage && (
          <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-xs text-red-400 flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Ingestion Notice</p>
              <p>{errorMessage}</p>
            </div>
          </div>
        )}

        <form onSubmit={handleTriggerIngestion} className="space-y-4 text-xs">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-slate-400 mb-1">Provider Interface</label>
              <select
                value={provider}
                onChange={(e) => setProvider(e.target.value as any)}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-200 text-xs focus:outline-none focus:border-blue-500"
              >
                <option value="rss">Open RSS Feeds (BBC, NPR, Phys.org)</option>
                <option value="newsapi">NewsAPI (Requires configured API Key)</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Topic or Keyword Filter (Optional)</label>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g. earthquake, climate, inflation"
                className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Max Ingestion Batch Size</label>
              <input
                type="number"
                min="5"
                max="50"
                value={maxArticles}
                onChange={(e) => setMaxArticles(parseInt(e.target.value) || 15)}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-100 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          {provider === 'rss' && (
            <div>
              <label className="block text-slate-400 mb-1">Custom RSS / Atom URL (Leave blank to use default verified feeds)</label>
              <input
                type="url"
                value={feedUrl}
                onChange={(e) => setFeedUrl(e.target.value)}
                placeholder="https://example.com/rss.xml"
                className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500"
              />
            </div>
          )}

          <div className="flex justify-end pt-1">
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex items-center space-x-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg shadow-sm transition disabled:opacity-50 cursor-pointer"
            >
              <Play className="w-3.5 h-3.5" />
              <span>{isSubmitting ? 'Fetching & Ingesting...' : 'Start Ingestion'}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Ingestion Execution History Table */}
      <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Ingestion Job Logs</h3>
            <p className="text-xs text-slate-500">Audit trail of synchronization requests and deduplication outcomes</p>
          </div>
          <button
            onClick={fetchJobs}
            className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition"
            title="Refresh logs"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

        {isLoading ? (
          <div className="py-12 flex justify-center">
            <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : jobs.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900/60 text-slate-500 border-b border-slate-800 uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-2.5 px-3">Job ID</th>
                  <th className="py-2.5 px-3">Provider</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Fetched</th>
                  <th className="py-2.5 px-3">Inserted</th>
                  <th className="py-2.5 px-3">Duplicates</th>
                  <th className="py-2.5 px-3">Started At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-slate-800/30 transition">
                    <td className="py-3 px-3 text-slate-400">{job.id}</td>
                    <td className="py-3 px-3 text-slate-200 uppercase font-sans font-medium">{job.provider}</td>
                    <td className="py-3 px-3 font-sans">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-medium border ${
                        job.status === 'completed'
                          ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                          : job.status === 'failed'
                          ? 'bg-red-500/10 border-red-500/20 text-red-400'
                          : 'bg-blue-500/10 border-blue-500/20 text-blue-400'
                      }`}>
                        {job.status}
                      </span>
                    </td>
                    <td className="py-3 px-3">{job.articles_fetched}</td>
                    <td className="py-3 px-3 text-emerald-400 font-semibold">{job.articles_inserted}</td>
                    <td className="py-3 px-3 text-slate-500">{job.duplicates_skipped}</td>
                    <td className="py-3 px-3 text-slate-400 font-sans text-[11px]">
                      {new Date(job.start_time).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-12 text-center text-xs text-slate-500">
            No ingestion jobs executed yet.
          </div>
        )}
      </div>
    </div>
  );
};
