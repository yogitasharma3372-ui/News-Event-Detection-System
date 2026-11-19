import React, { useEffect, useState } from 'react';
import { Search, Filter, Calendar, Tag, ExternalLink, X, ChevronLeft, ChevronRight, Check } from 'lucide-react';
import { api } from '../api/client';
import { Article, ArticleListResponse } from '../types';
import { ArticleCard } from '../components/ArticleCard';

export const NewsExplorerPage: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [isLoading, setIsLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [sourceName, setSourceName] = useState('');
  const [category, setCategory] = useState('');
  const [assignedStatus, setAssignedStatus] = useState('');
  const [sourcesList, setSourcesList] = useState<string[]>([]);

  // Modals
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);
  const [reviewArticle, setReviewArticle] = useState<Article | null>(null);
  const [manualEventId, setManualEventId] = useState('');
  const [manualNotes, setManualNotes] = useState('');
  const [isSubmittingReview, setIsSubmittingReview] = useState(false);

  const fetchArticles = async () => {
    setIsLoading(true);
    try {
      const data: ArticleListResponse = await api.getArticles({
        search,
        source_name: sourceName,
        category,
        assigned_status: assignedStatus,
        page,
        page_size: 15
      });
      setArticles(data.items);
      setTotal(data.total);
      setPages(data.pages);
    } catch (err) {
      console.error('Failed to load articles:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Load sources list
    api.getSources().then((res) => {
      setSourcesList(res.sources.map((s) => s.name));
    }).catch(() => {});
  }, []);

  useEffect(() => {
    fetchArticles();
  }, [page, sourceName, category, assignedStatus]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchArticles();
  };

  const handleManualReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reviewArticle) return;
    setIsSubmittingReview(true);
    try {
      await api.reviewAssignment({
        article_id: reviewArticle.id,
        target_event_id: manualEventId.trim() ? manualEventId.trim() : null,
        notes: manualNotes
      });
      alert('Manual review recorded successfully! Saved in audit logs.');
      setReviewArticle(null);
      fetchArticles();
    } catch (err: any) {
      alert(`Review error: ${err.message}`);
    } finally {
      setIsSubmittingReview(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Search & Filter Header */}
      <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-5 space-y-4">
        <form onSubmit={handleSearchSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search headline, text keywords, or topics..."
              className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg transition shrink-0 cursor-pointer"
          >
            Search
          </button>
        </form>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div>
            <label className="block text-slate-400 mb-1 text-[11px]">Filter by News Source</label>
            <select
              value={sourceName}
              onChange={(e) => { setSourceName(e.target.value); setPage(1); }}
              className="w-full px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-slate-200 text-xs focus:outline-none focus:border-blue-500"
            >
              <option value="">All Sources</option>
              {sourcesList.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-slate-400 mb-1 text-[11px]">Category</label>
            <select
              value={category}
              onChange={(e) => { setCategory(e.target.value); setPage(1); }}
              className="w-full px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-slate-200 text-xs focus:outline-none focus:border-blue-500"
            >
              <option value="">All Categories</option>
              <option value="Natural Disasters">Natural Disasters</option>
              <option value="Science">Science</option>
              <option value="Economy">Economy</option>
              <option value="Environment">Environment</option>
              <option value="Politics">Politics</option>
              <option value="Culture">Culture</option>
            </select>
          </div>

          <div>
            <label className="block text-slate-400 mb-1 text-[11px]">Cluster Assignment Status</label>
            <select
              value={assignedStatus}
              onChange={(e) => { setAssignedStatus(e.target.value); setPage(1); }}
              className="w-full px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-slate-200 text-xs focus:outline-none focus:border-blue-500"
            >
              <option value="">All Articles</option>
              <option value="assigned">Assigned to Event Cluster</option>
              <option value="unassigned">Unassigned / Noise</option>
            </select>
          </div>
        </div>
      </div>

      {/* Article List Results */}
      <div className="space-y-4">
        <div className="flex items-center justify-between text-xs text-slate-400 px-1">
          <span>Found <strong className="text-slate-200">{total}</strong> articles</span>
          <span>Page {page} of {pages}</span>
        </div>

        {isLoading ? (
          <div className="py-16 flex flex-col items-center justify-center space-y-3">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-xs text-slate-400">Loading articles...</p>
          </div>
        ) : articles.length > 0 ? (
          <div className="grid grid-cols-1 gap-4">
            {articles.map((art) => (
              <ArticleCard
                key={art.id}
                article={art}
                onOpenDetails={(a) => setSelectedArticle(a)}
                onReview={(a) => setReviewArticle(a)}
              />
            ))}
          </div>
        ) : (
          <div className="py-16 text-center text-xs text-slate-500 bg-[#0f172a] rounded-xl border border-slate-800">
            No articles match the current filters.
          </div>
        )}

        {/* Pagination */}
        {pages > 1 && (
          <div className="flex items-center justify-center space-x-2 pt-4">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-2 rounded-lg bg-slate-800 text-slate-300 disabled:opacity-40 hover:bg-slate-700 transition"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="text-xs text-slate-400 px-3">
              Page {page} of {pages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(pages, p + 1))}
              disabled={page === pages}
              className="p-2 rounded-lg bg-slate-800 text-slate-300 disabled:opacity-40 hover:bg-slate-700 transition"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>

      {/* Modal: Article Detail Inspection */}
      {selectedArticle && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#0f172a] border border-slate-800 rounded-2xl max-w-2xl w-full p-6 space-y-4 max-h-[85vh] overflow-y-auto">
            <div className="flex items-start justify-between gap-4">
              <div className="space-y-1">
                <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 text-xs border border-blue-500/20 font-semibold">
                  {selectedArticle.source_name}
                </span>
                <h3 className="text-lg font-bold text-slate-100">{selectedArticle.headline}</h3>
              </div>
              <button
                onClick={() => setSelectedArticle(null)}
                className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex items-center gap-4 text-xs text-slate-400 border-y border-slate-800 py-2">
              <div>Published: {new Date(selectedArticle.published_at).toUTCString()}</div>
              <div>ID: <span className="font-mono text-slate-300">{selectedArticle.id}</span></div>
            </div>

            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Full Content</h4>
              <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-line">
                {selectedArticle.body}
              </p>
            </div>

            {selectedArticle.entities_json && (
              <div className="space-y-2 pt-2 border-t border-slate-800">
                <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Extracted Named Entities</h4>
                <div className="flex flex-wrap gap-1.5">
                  {JSON.parse(selectedArticle.entities_json).all?.map((e: string, i: number) => (
                    <span key={i} className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                      {e}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="flex items-center justify-between pt-4 border-t border-slate-800 text-xs">
              <span className="text-slate-500 font-mono text-[11px]">
                SHA-256: {selectedArticle.content_hash.slice(0, 16)}...
              </span>
              {selectedArticle.source_url && (
                <a
                  href={selectedArticle.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition flex items-center gap-1.5"
                >
                  <span>Open Original Source</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Modal: Manual Review Workflow */}
      {reviewArticle && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <form onSubmit={handleManualReviewSubmit} className="bg-[#0f172a] border border-slate-800 rounded-2xl max-w-lg w-full p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-slate-100">Manual Assignment Review</h3>
              <button
                type="button"
                onClick={() => setReviewArticle(null)}
                className="p-1.5 text-slate-400 hover:text-slate-200 rounded-lg transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg space-y-1">
              <p className="text-xs text-slate-400 font-medium">{reviewArticle.source_name}</p>
              <p className="text-xs font-semibold text-slate-200 line-clamp-2">{reviewArticle.headline}</p>
              <p className="text-[11px] text-slate-500">
                Currently: {reviewArticle.assigned_event_id ? `Assigned to ${reviewArticle.assigned_event_id}` : 'Unassigned Noise'}
              </p>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">
                  Target Event ID (Leave blank to make unassigned/noise)
                </label>
                <input
                  type="text"
                  value={manualEventId}
                  onChange={(e) => setManualEventId(e.target.value)}
                  placeholder="e.g. evt-9f82ab10"
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">
                  Reviewer Notes (Rationale for correction)
                </label>
                <textarea
                  value={manualNotes}
                  onChange={(e) => setManualNotes(e.target.value)}
                  rows={3}
                  placeholder="Explain why this article belongs or does not belong to the event..."
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500 resize-none"
                />
              </div>
            </div>

            <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setReviewArticle(null)}
                className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs rounded-lg transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmittingReview}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg transition disabled:opacity-50 flex items-center space-x-1"
              >
                <Check className="w-4 h-4" />
                <span>{isSubmittingReview ? 'Saving...' : 'Confirm Review'}</span>
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
