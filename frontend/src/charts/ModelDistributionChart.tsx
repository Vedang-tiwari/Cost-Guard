import React from 'react';
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import type { ModelStat } from '../types';

const COLORS = ['#4F46E5', '#10B981', '#0EA5E9', '#F59E0B', '#EC4899', '#8B5CF6'];

interface ModelDistributionChartProps {
  models: ModelStat[];
}

export const ModelDistributionChart: React.FC<ModelDistributionChartProps> = ({ models }) => {
  if (!models.length) {
    return (
      <div className="flex h-64 items-center justify-center text-sm text-slate-400">
        No model traffic recorded yet. Send requests or run the Playground.
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center gap-4 lg:flex-row">
      <div className="h-56 w-full lg:w-1/2">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={models}
              dataKey="request_count"
              nameKey="model"
              cx="50%"
              cy="50%"
              innerRadius={52}
              outerRadius={82}
              paddingAngle={3}
            >
              {models.map((_, idx) => (
                <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: '#0F172A',
                border: 'none',
                borderRadius: '8px',
                color: '#F8FAFC',
                fontSize: '12px',
              }}
              formatter={(value: number, name: string) => [`${value} requests`, name]}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="w-full space-y-2.5 lg:w-1/2">
        {models.map((m, idx) => (
          <div key={m.model} className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 overflow-hidden">
              <span
                className="h-2.5 w-2.5 shrink-0 rounded-full"
                style={{ backgroundColor: COLORS[idx % COLORS.length] }}
              />
              <span className="truncate font-mono font-medium text-slate-700">{m.model}</span>
            </div>
            <div className="flex items-center gap-3 tabular-nums">
              <span className="text-slate-500">{m.request_count} reqs</span>
              <span className="w-12 text-right font-semibold text-slate-900">{m.share_pct}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
