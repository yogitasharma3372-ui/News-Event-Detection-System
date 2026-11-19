import React from 'react';
import { ExternalLink, Calendar, Tag, ShieldCheck, HelpCircle } from 'lucide-react';
import { Article } from '../types';

interface ArticleCardProps {
  article: Article;
  onOpenDetails?: (article: Article) => void;
  onReview?: (article: Article) => void;
}

export const ArticleCard: React.FC<ArticleCardProps> = ({
  article,
  onOpenDetails,
  onReview
}) => {
  const publishedDate = new Date(article.published_at).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'UTC',
    timeZoneName: 'short'
  });

  // Extract entities preview if present
  let entities: string[] = [];
  if (article.entities_json) {
    try {
      const parsed = JSON.parse(article.entities_json);
      entities = parsed.all || [];
    } catch {
      // ignore
    }
  }

  const isAssigned = !!article.assigned_event_id;

  return (
    <div className="bg-[#0f172a] border border-slate-800 hover:border-slate-700 transition rounded-xl p-5 space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center gap-2 flex-wrap text-xs">
            <span className="px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/20 text-blue-400 font-medium">
              {article.source_name}
            </span>
            {article.category && (
              <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                {article.category}
              </span>
            )}
            <span className={`px-2 py-0.5 rounded text-[11px] font-medium border flex items-center gap-1 ${
              isAssigned
                ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                : 'bg-amber-500/10 border-amber-500/20 text-amber-400'
            }`}>
              {isAssigned ? <ShieldCheck className="w-3 h-3" /> : <HelpCircle className="w-3 h-3" />}
              {isAssigned ? 'Assigned' : 'Unassigned / Noise'}
            </span>
          </div>

          <h3 className="text-base font-semibold text-slate-100 hover:text-blue-400 transition cursor-pointer"
              onClick={() => onOpenDetails && onOpenDetails(article)}>
            {article.headline}
          </h3>
        </div>

        {article.source_url && (
          <a
            href={article.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition shrink-0"
            title="Open original publication"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        )}
      </div>

      <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
        {article.body}
      </p>

      {entities.length > 0 && (
        <div className="flex items-center gap-1.5 flex-wrap pt-1">
          <Tag className="w-3 h-3 text-slate-500 shrink-0" />
          {entities.slice(0, 5).map((ent, i) => (
            <span key={i} className="text-[11px] px-1.5 py-0.5 rounded bg-slate-800/80 text-slate-400 border border-slate-700/50">
              {ent}
            </span>
          ))}
          {entities.length > 5 && (
            <span className="text-[10px] text-slate-500">+{entities.length - 5} more</span>
          )}
        </div>
      )}

      <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 text-xs text-slate-500">
        <div className="flex items-center gap-1">
          <Calendar className="w-3.5 h-3.5" />
          <span>{publishedDate}</span>
        </div>

        <div className="flex items-center gap-2">
          {onReview && (
            <button
              onClick={() => onReview(article)}
              className="text-xs text-blue-400 hover:text-blue-300 font-medium cursor-pointer"
            >
              Manual Review
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
