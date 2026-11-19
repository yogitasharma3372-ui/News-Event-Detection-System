import React from 'react';
import { Calendar, ExternalLink, Clock, Sparkles } from 'lucide-react';
import { TimelineItem } from '../types';

interface TimelineViewProps {
  timeline: TimelineItem[];
}

export const TimelineView: React.FC<TimelineViewProps> = ({ timeline }) => {
  if (timeline.length === 0) {
    return (
      <div className="p-8 text-center text-slate-500 bg-slate-900/50 rounded-xl border border-slate-800">
        No chronological timeline events available.
      </div>
    );
  }

  return (
    <div className="relative pl-6 space-y-8 before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-[2px] before:bg-slate-800">
      {timeline.map((item, index) => {
        const dateStr = new Date(item.published_at).toLocaleString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          timeZone: 'UTC',
          timeZoneName: 'short'
        });

        return (
          <div key={item.article_id} className="relative group">
            {/* Timeline node icon */}
            <div className={`absolute -left-[30px] top-1.5 w-5 h-5 rounded-full border-2 flex items-center justify-center transition ${
              item.is_first_observed
                ? 'bg-blue-600 border-blue-400 text-white shadow-md shadow-blue-500/30'
                : 'bg-slate-900 border-slate-700 text-slate-400 group-hover:border-blue-500'
            }`}>
              {item.is_first_observed ? (
                <Sparkles className="w-2.5 h-2.5" />
              ) : (
                <div className="w-1.5 h-1.5 rounded-full bg-slate-400 group-hover:bg-blue-400" />
              )}
            </div>

            {/* Timeline card */}
            <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-4 space-y-2 hover:border-slate-700 transition">
              <div className="flex items-center justify-between gap-2 flex-wrap">
                <div className="flex items-center gap-2 text-xs">
                  <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-medium">
                    {item.source_name}
                  </span>
                  {item.is_first_observed && (
                    <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 font-medium text-[11px]">
                      First Observed by System
                    </span>
                  )}
                  <span className="text-slate-400 text-[11px] flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {dateStr}
                  </span>
                </div>

                <div className="text-[11px] text-slate-500 font-mono">
                  Score: <span className="text-slate-300 font-semibold">{item.combined_score.toFixed(3)}</span>
                </div>
              </div>

              <div className="flex items-start justify-between gap-2">
                <h4 className="text-sm font-semibold text-slate-100 leading-snug">
                  {item.headline}
                </h4>
                {item.source_url && (
                  <a
                    href={item.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-1 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded transition shrink-0"
                    title="Read original publication"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
              </div>

              <p className="text-xs text-slate-400 leading-relaxed">
                {item.summary_excerpt}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
};
