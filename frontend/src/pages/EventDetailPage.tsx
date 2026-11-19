import React, { useEffect, useState } from 'react';
import {
  ArrowLeft,
  Calendar,
  Layers,
  Tag,
  ExternalLink,
  Clock,
  Sparkles,
  ShieldCheck,
  FileText
} from 'lucide-react';
import { api } from '../api/client';
import { Event, EventDetail, TimelineItem, Article } from '../types';
import { TimelineView } from '../components/TimelineView';
import { ArticleCard } from '../components/ArticleCard';

interface EventDetailPageProps {
  eventId: string;
  onBack: () => void;
}

export const EventDetailPage: React.FC<EventDetailPageProps> = ({ eventId, onBack }) => {
  const [eventDetail, setEventDetail] = useState<EventDetail | null>(null);
  const [timeline, setTimeline] = useState<TimelineItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeView, setActiveView] = useState<'timeline' | 'articles'>('timeline');

  useEffect(() => {
    const loadDetail = async () => {
      setIsLoading(true);
      try {
        const [detailData, timelineData] = await Promise.all([
          api.getEvent(eventId),
          api.getEventTimeline(eventId)
        ]);
        setEventDetail(detailData);
        setTimeline(timelineData);
      } catch (err) {
        console.error('Failed to load event details:', err);
      } finally {
        setIsLoading(false);
      }
    };
    loadDetail();
  }, [eventId]);

  if (isLoading) {
    return (
      <div className="py-20 flex flex-col items-center justify-center space-y-3">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-xs text-slate-400">Loading event detail & timeline...</p>
      </div>
    );
  }

  if (!eventDetail) {
    return (
      <div className="p-8 text-center text-slate-400 space-y-4">
        <p>Event not found.</p>
        <button
          onClick={onBack}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs rounded-lg transition"
        >
          Return to Events
        </button>
      </div>
    );
  }

  const firstSeen = new Date(eventDetail.first_observed_at).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'UTC',
    timeZoneName: 'short'
  });

  const lastSeen = new Date(eventDetail.last_observed_at).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'UTC',
    timeZoneName: 'short'
  });

  let entities: { persons?: string[]; orgs?: string[]; locs?: string[]; all?: string[] } = {};
  if (eventDetail.key_entities_json) {
    try {
      entities = JSON.parse(eventDetail.key_entities_json);
    } catch {
      // ignore
    }
  }

  // Count unique sources
  const sourcesSet = new Set(eventDetail.articles.map((a) => a.source_name));

  return (
    <div className="space-y-6">
      {/* Back button and Header */}
      <button
        onClick={onBack}
        className="flex items-center space-x-1.5 text-xs text-slate-400 hover:text-slate-200 transition cursor-pointer"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Event Explorer</span>
      </button>

      {/* Hero Event Header */}
      <div className="bg-[#0f172a] border border-slate-800 rounded-2xl p-6 space-y-4 shadow-sm">
        <div className="flex items-center gap-2 flex-wrap text-xs">
          <span className="px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 font-semibold flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5" />
            {eventDetail.article_count} Associated Articles
          </span>
          <span className="px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 font-medium">
            {eventDetail.category}
          </span>
          <span className="text-slate-500 font-mono text-[11px]">ID: {eventDetail.id}</span>
        </div>

        <h2 className="text-xl sm:text-2xl font-bold text-slate-100 leading-snug">
          {eventDetail.title}
        </h2>

        {eventDetail.description && (
          <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl space-y-1">
            <div className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              <FileText className="w-3.5 h-3.5 text-blue-400" />
              <span>Extractive Event Synthesis</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              {eventDetail.description}
            </p>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2 border-t border-slate-800/80 text-xs">
          <div>
            <span className="text-slate-500 block">First Observed by System:</span>
            <span className="text-slate-200 font-medium">{firstSeen}</span>
          </div>
          <div>
            <span className="text-slate-500 block">Most Recent Update:</span>
            <span className="text-slate-200 font-medium">{lastSeen}</span>
          </div>
          <div>
            <span className="text-slate-500 block">Reporting Sources ({sourcesSet.size}):</span>
            <span className="text-slate-200 font-medium">{Array.from(sourcesSet).join(', ')}</span>
          </div>
        </div>

        {/* Entities Summary */}
        {entities.all && entities.all.length > 0 && (
          <div className="pt-2 border-t border-slate-800/80 flex items-center gap-2 flex-wrap text-xs">
            <Tag className="w-3.5 h-3.5 text-slate-500 shrink-0" />
            <span className="text-slate-500 text-[11px]">Key Entities:</span>
            {entities.all.map((ent, i) => (
              <span key={i} className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[11px] border border-slate-700/60">
                {ent}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Tabs: Timeline vs Articles View */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setActiveView('timeline')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition cursor-pointer ${
              activeView === 'timeline'
                ? 'bg-blue-600 text-white'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            Chronological Timeline ({timeline.length})
          </button>
          <button
            onClick={() => setActiveView('articles')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition cursor-pointer ${
              activeView === 'articles'
                ? 'bg-blue-600 text-white'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            All Articles ({eventDetail.articles.length})
          </button>
        </div>
      </div>

      {/* Active Tab View */}
      {activeView === 'timeline' ? (
        <TimelineView timeline={timeline} />
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {eventDetail.articles.map((art) => (
            <ArticleCard key={art.id} article={art} />
          ))}
        </div>
      )}
    </div>
  );
};
