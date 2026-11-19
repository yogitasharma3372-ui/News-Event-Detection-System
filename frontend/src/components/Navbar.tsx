import React from 'react';
import { Newspaper, RefreshCw, Layers } from 'lucide-react';

interface NavbarProps {
  onRefresh: () => void;
  isRefreshing: boolean;
  totalArticles: number;
  totalEvents: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  onRefresh,
  isRefreshing,
  totalArticles,
  totalEvents
}) => {
  return (
    <header className="h-16 bg-[#0f172a] border-b border-slate-800 px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center space-x-3">
        <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
          <Newspaper className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-base font-semibold text-slate-100 leading-tight">
            News Event Detection & Tracking System
          </h1>
          <p className="text-xs text-slate-400">Time-Aware Semantic News Intelligence</p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <div className="hidden sm:flex items-center space-x-3 text-xs bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5">
          <div className="flex items-center space-x-1.5 text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-slate-400">Articles:</span>
            <span className="font-semibold text-slate-200">{totalArticles}</span>
          </div>
          <span className="text-slate-700">|</span>
          <div className="flex items-center space-x-1.5 text-slate-300">
            <Layers className="w-3.5 h-3.5 text-blue-400" />
            <span className="text-slate-400">Events:</span>
            <span className="font-semibold text-slate-200">{totalEvents}</span>
          </div>
        </div>

        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg border border-slate-700 transition disabled:opacity-50 cursor-pointer"
          title="Refresh Data"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-blue-400' : ''}`} />
          <span>{isRefreshing ? 'Refreshing...' : 'Refresh'}</span>
        </button>
      </div>
    </header>
  );
};
