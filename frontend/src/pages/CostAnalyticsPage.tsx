import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { SpendTrendChart } from '../charts/SpendTrendChart';
import { StatCard } from '../components/StatCard';
import { api } from '../services/api';
import { Coins, DollarSign, TrendingDown } from 'lucide-react';

export const CostAnalyticsPage: React.FC = () => {
  const [period, setPeriod] = useState<'daily' | 'weekly' | 'monthly'>('daily');
  const days = period === 'daily' ? 14 : period === 'weekly' ? 60 : 180;

  const { data: costs, isLoading } = useQuery({
    queryKey: ['analytics-costs', period, days],
    queryFn: () => api.getCosts(days, period),
  });

  const tokenData = [
    { name: 'Input Tokens Cost', cost: costs?.token_costs?.input_cost ?? 0 },
    { name: 'Output Tokens Cost', cost: costs?.token_costs?.output_cost ?? 0 },
  ];

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Cost Analytics</h1>
          <p className="mt-1 text-sm text-slate-500">
            Granular expenditure across time periods, providers, models, applications, and token direction.
          </p>
        </div>

        <div className="inline-flex rounded-lg border border-slate-200 bg-white p-1 shadow-sm">
          {(['daily', 'weekly', 'monthly'] as const).map((p) => (
            <button
              key={p}
              type="button"
              onClick={() => setPeriod(p)}
              className={`rounded-md px-3 py-1.5 text-xs font-medium capitalize transition-colors ${
                period === p ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
        <StatCard
          title="Actual Expenditure"
          value={`$${(costs?.total_spend ?? 0).toFixed(4)}`}
          subtitle={`Selected ${period} window`}
          icon={DollarSign}
          accent="indigo"
        />
        <StatCard
          title="Reference Baseline Spend"
          value={`$${(costs?.baseline_spend ?? 0).toFixed(4)}`}
          subtitle="Without Cost Guard optimizations"
          icon={Coins}
        />
        <StatCard
          title="Total Cost Avoided"
          value={`$${(costs?.total_savings ?? 0).toFixed(4)}`}
          subtitle="Direct savings retained"
          icon={TrendingDown}
          accent="emerald"
        />
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-base font-semibold text-slate-900 capitalize">
          {period} Spend vs Baseline Trend
        </h2>
        {isLoading ? (
          <div className="h-72 animate-pulse rounded bg-slate-100" />
        ) : (
          <SpendTrendChart data={costs?.breakdown ?? []} />
        )}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Cost by Provider */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="mb-4 text-sm font-semibold text-slate-900">Cost per Provider</h3>
          <div className="space-y-3">
            {(costs?.by_provider ?? []).length === 0 ? (
              <p className="text-xs text-slate-400">No provider spend recorded yet.</p>
            ) : (
              costs?.by_provider.map((item) => (
                <div key={item.name} className="flex items-center justify-between text-xs">
                  <span className="font-medium capitalize text-slate-700">{item.name}</span>
                  <span className="font-mono font-semibold text-slate-900 tabular-nums">
                    ${item.cost.toFixed(5)}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Cost by Application */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="mb-4 text-sm font-semibold text-slate-900">Cost per Application</h3>
          <div className="space-y-3">
            {(costs?.by_application ?? []).length === 0 ? (
              <p className="text-xs text-slate-400">No application spend recorded yet.</p>
            ) : (
              costs?.by_application.map((item) => (
                <div key={item.name} className="flex items-center justify-between text-xs">
                  <span className="truncate font-medium text-slate-700">{item.name}</span>
                  <span className="font-mono font-semibold text-slate-900 tabular-nums">
                    ${item.cost.toFixed(5)}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Input vs Output Token Cost */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="mb-4 text-sm font-semibold text-slate-900">Input vs Output Token Cost</h3>
          <div className="h-44 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={tokenData} layout="vertical" margin={{ left: 10, right: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" horizontal={false} />
                <XAxis type="number" tickFormatter={(v) => `$${Number(v).toFixed(3)}`} tick={{ fontSize: 10 }} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={115} />
                <Tooltip formatter={(v: number) => [`$${Number(v).toFixed(5)}`, 'Spend']} />
                <Bar dataKey="cost" fill="#4F46E5" radius={[0, 6, 6, 0]} barSize={24} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
