import React from 'react';
import { Layers, Calendar, ChevronRight, Tag } from 'lucide-react';
import { Event } from '../types';

interface EventCardProps {
  event: Event;
  onClick: (event: Event) => void;
}

export const EventCard: React.FC<EventCardProps> = ({ event, onClick }) => {
  const firstSeen = new Date(event.first_observed_at).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
  const lastSeen = new Date(event.last_observed_at).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });

  let entities: string[] = [];
  if (event.key_entities_json) {
    try {
      const parsed = JSON.parse(event.key_entities_json);
      entities = parsed.all || [];
    } catch {
      // ignore
    }
  }

  return (
    <div
      onClick={() => onClick(event)}
      className="bg-[#0f172a] border border-slate-800 hover:border-blue-500/50 hover:shadow-md hover:shadow-blue-500/5 transition rounded-xl p-5 space-y-3 cursor-pointer group"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-xs">
            <span className="px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/20 text-blue-400 font-semibold flex items-center gap-1">
              <Layers className="w-3 h-3" />
              {event.article_count} {event.article_count === 1 ? 'Article' : 'Articles'}
            </span>
            <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300 font-medium">
              {event.category}
            </span>
            <span className="text-slate-500 text-[11px]">ID: {event.id}</span>
          </div>

          <h3 className="text-base font-semibold text-slate-100 group-hover:text-blue-400 transition leading-snug">
            {event.title}
          </h3>
        </div>

        <div className="p-1.5 text-slate-400 group-hover:text-blue-400 group-hover:translate-x-1 transition shrink-0">
          <ChevronRight className="w-5 h-5" />
        </div>
      </div>

      {event.description && (
        <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
          {event.description}
        </p>
      )}

      {entities.length > 0 && (
        <div className="flex items-center gap-1.5 flex-wrap pt-1">
          <Tag className="w-3 h-3 text-slate-500 shrink-0" />
          {entities.slice(0, 4).map((ent, i) => (
            <span key={i} className="text-[11px] px-1.5 py-0.5 rounded bg-slate-800/80 text-slate-400 border border-slate-700/50">
              {ent}
            </span>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 text-xs text-slate-500">
        <div className="flex items-center gap-1.5">
          <Calendar className="w-3.5 h-3.5" />
          <span>Timeline: {firstSeen} – {lastSeen}</span>
        </div>
        <span className="text-[11px] text-slate-500 font-mono">Method: {event.assignment_method}</span>
      </div>
    </div>
  );
};
