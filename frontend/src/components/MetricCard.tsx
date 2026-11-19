import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  color?: 'blue' | 'emerald' | 'amber' | 'purple' | 'slate';
}

const COLOR_MAP = {
  blue: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
  emerald: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  amber: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
  purple: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
  slate: 'text-slate-400 bg-slate-500/10 border-slate-500/20',
};

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  color = 'blue'
}) => {
  return (
    <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-5 flex items-start justify-between shadow-sm">
      <div className="space-y-1">
        <p className="text-xs font-medium text-slate-400">{title}</p>
        <p className="text-2xl font-bold text-slate-100">{value}</p>
        {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
      </div>
      <div className={`p-2.5 rounded-lg border ${COLOR_MAP[color]}`}>
        <Icon className="w-5 h-5" />
      </div>
    </div>
  );
};
