import React from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { BenchmarkRun } from '../types';

interface BenchmarkBarChartProps {
  runs: BenchmarkRun[];
}

export const BenchmarkBarChart: React.FC<BenchmarkBarChartProps> = ({ runs }) => {
  const chartData = runs.map((r) => ({
    model: r.candidate_model,
    qualityRetention: r.quality_retention,
    costSavings: r.cost_savings_pct,
  }));

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
          <XAxis dataKey="model" tick={{ fontSize: 12, fill: '#475569' }} axisLine={false} tickLine={false} />
          <YAxis
            domain={[0, 100]}
            tick={{ fontSize: 11, fill: '#64748B' }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `${v}%`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0F172A',
              border: 'none',
              borderRadius: '8px',
              color: '#F8FAFC',
              fontSize: '12px',
            }}
            formatter={(val: number, name: string) => [`${Number(val).toFixed(1)}%`, name]}
          />
          <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
          <Bar
            dataKey="qualityRetention"
            name="Quality Retention (%)"
            fill="#4F46E5"
            radius={[6, 6, 0, 0]}
            maxBarSize={48}
          />
          <Bar
            dataKey="costSavings"
            name="Cost Savings vs gpt-4o (%)"
            fill="#10B981"
            radius={[6, 6, 0, 0]}
            maxBarSize={48}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
