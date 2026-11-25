import React from 'react';
import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { CostTimePoint } from '../types';

interface SpendTrendChartProps {
  data: CostTimePoint[];
}

export const SpendTrendChart: React.FC<SpendTrendChartProps> = ({ data }) => {
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="baselineGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#94A3B8" stopOpacity={0.25} />
              <stop offset="95%" stopColor="#94A3B8" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="actualGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#4F46E5" stopOpacity={0.35} />
              <stop offset="95%" stopColor="#4F46E5" stopOpacity={0.02} />
            </linearGradient>
            <linearGradient id="savingsGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: '#64748B' }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#64748B' }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `$${Number(v).toFixed(4)}`}
            width={68}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0F172A',
              border: 'none',
              borderRadius: '8px',
              color: '#F8FAFC',
              fontSize: '12px',
            }}
            formatter={(value: number, name: string) => [`$${Number(value).toFixed(5)}`, name]}
          />
          <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
          <Area
            type="monotone"
            dataKey="baseline_cost"
            name="Baseline Cost (gpt-4o)"
            stroke="#94A3B8"
            strokeDasharray="4 4"
            strokeWidth={1.75}
            fill="url(#baselineGrad)"
          />
          <Area
            type="monotone"
            dataKey="actual_cost"
            name="Actual Spend"
            stroke="#4F46E5"
            strokeWidth={2}
            fill="url(#actualGrad)"
          />
          <Area
            type="monotone"
            dataKey="savings"
            name="Net Savings"
            stroke="#10B981"
            strokeWidth={2}
            fill="url(#savingsGrad)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
