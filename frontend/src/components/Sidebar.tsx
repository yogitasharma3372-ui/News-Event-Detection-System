import React from 'react';
import {
  LayoutDashboard,
  Search,
  Layers,
  Radio,
  FlaskConical,
  BarChart3,
  FolderInput,
  Settings,
  ChevronRight
} from 'lucide-react';

export type NavTab = 
  | 'overview' 
  | 'news-explorer' 
  | 'event-explorer' 
  | 'live-monitor' 
  | 'research-lab' 
  | 'evaluation' 
  | 'dataset-mgmt' 
  | 'settings';

interface SidebarProps {
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
}

const NAV_ITEMS: { id: NavTab; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'news-explorer', label: 'News Explorer', icon: Search },
  { id: 'event-explorer', label: 'Event Explorer', icon: Layers },
  { id: 'live-monitor', label: 'Live Monitor', icon: Radio },
  { id: 'research-lab', label: 'Research Lab', icon: FlaskConical },
  { id: 'evaluation', label: 'Evaluation & Ablation', icon: BarChart3 },
  { id: 'dataset-mgmt', label: 'Dataset Import', icon: FolderInput },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange }) => {
  return (
    <aside className="w-64 bg-[#090d16] border-r border-slate-800 flex flex-col justify-between shrink-0">
      <div className="p-4 space-y-1">
        <div className="px-3 py-2 text-[10px] font-bold tracking-wider text-slate-500 uppercase">
          Navigation
        </div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition cursor-pointer ${
                isActive
                  ? 'bg-blue-600 text-white shadow-sm shadow-blue-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center space-x-2.5">
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {isActive && <ChevronRight className="w-3.5 h-3.5 text-white" />}
            </button>
          );
        })}
      </div>

      <div className="p-4 border-t border-slate-800 text-xs text-slate-500 space-y-1">
        <div className="font-medium text-slate-400">NLP Research System</div>
        <div>Model: all-MiniLM-L6-v2</div>
        <div>Hybrid: Semantic + Time + NER</div>
      </div>
    </aside>
  );
};
