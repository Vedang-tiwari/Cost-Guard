import React from 'react';
import type { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string;
  subtitle?: string;
  icon: LucideIcon;
  accent?: 'default' | 'emerald' | 'indigo' | 'amber';
  badge?: string;
}

const accentStyles: Record<NonNullable<StatCardProps['accent']>, string> = {
  default: 'bg-slate-100 text-slate-700',
  emerald: 'bg-emerald-50 text-emerald-700',
  indigo: 'bg-indigo-50 text-indigo-700',
  amber: 'bg-amber-50 text-amber-700',
};

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  accent = 'default',
  badge,
}) => {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">{title}</p>
          <p className="mt-2 text-2xl font-bold tracking-tight text-slate-900 tabular-nums">{value}</p>
        </div>
        <div className={`rounded-lg p-2.5 ${accentStyles[accent]}`}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
      {(subtitle || badge) && (
        <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
          <span>{subtitle}</span>
          {badge && (
            <span className="rounded-full bg-emerald-50 px-2 py-0.5 font-semibold text-emerald-700 tabular-nums">
              {badge}
            </span>
          )}
        </div>
      )}
    </div>
  );
};
