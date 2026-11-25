import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Activity, Coins, Database, DollarSign, ShieldCheck, TrendingDown } from 'lucide-react';
import { ModelDistributionChart } from '../charts/ModelDistributionChart';
import { SpendTrendChart } from '../charts/SpendTrendChart';
import { StatCard } from '../components/StatCard';
import { StatusBadge } from '../components/StatusBadge';
import { api } from '../services/api';

export const OverviewPage: React.FC = () => {
  const { data: overview, isLoading } = useQuery({
    queryKey: ['analytics-overview'],
    queryFn: () => api.getOverview(30),
  });

  const { data: costs } = useQuery({
    queryKey: ['analytics-costs-14'],
    queryFn: () => api.getCosts(14, 'daily'),
  });

  const { data: models } = useQuery({
    queryKey: ['analytics-models'],
    queryFn: () => api.getModelAnalytics(30),
  });

  const { data: logs } = useQuery({
    queryKey: ['analytics-logs'],
    queryFn: () => api.getLogs(8),
  });

  if (isLoading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 w-56 rounded bg-slate-200" />
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-32 rounded-xl bg-slate-200" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Gateway Overview</h1>
        <p className="mt-1 text-sm text-slate-500">
          Real-time spend telemetry, baseline savings, cache performance, and quality preservation.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard
          title="Total AI Spend (30d)"
          value={`$${(overview?.total_spend ?? 0).toFixed(4)}`}
          subtitle={`Baseline: $${(overview?.baseline_cost ?? 0).toFixed(4)}`}
          icon={DollarSign}
          accent="indigo"
        />
        <StatCard
          title="Estimated Net Savings"
          value={`$${(overview?.total_savings ?? 0).toFixed(4)}`}
          subtitle="vs gpt-4o reference baseline"
          badge={`${(overview?.savings_percentage ?? 0).toFixed(1)}% saved`}
          icon={TrendingDown}
          accent="emerald"
        />
        <StatCard
          title="Total Requests"
          value={(overview?.total_requests ?? 0).toLocaleString()}
          subtitle={`Avg latency: ${(overview?.avg_latency_ms ?? 0).toFixed(0)} ms (P95: ${(overview?.p95_latency_ms ?? 0).toFixed(0)} ms)`}
          icon={Activity}
        />
        <StatCard
          title="Avg Cost / Request"
          value={`$${(overview?.avg_cost_per_request ?? 0).toFixed(5)}`}
          subtitle={`Fallback rate: ${(overview?.fallback_rate ?? 0).toFixed(1)}%`}
          icon={Coins}
          accent="amber"
        />
        <StatCard
          title="Semantic Cache Hit Rate"
          value={`${(overview?.cache_hit_rate ?? 0).toFixed(1)}%`}
          subtitle="100% provider cost avoided on hits"
          icon={Database}
          accent="indigo"
        />
        <StatCard
          title="Avg Quality Score"
          value={`${(overview?.avg_quality_score ?? 0).toFixed(1)}%`}
          subtitle="Verified via quality gate & rubrics"
          icon={ShieldCheck}
          accent="emerald"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm lg:col-span-7">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-base font-semibold text-slate-900">Daily Expenditure vs Baseline</h2>
              <p className="text-xs text-slate-500">14-day comparison of actual gateway spend vs baseline cost</p>
            </div>
          </div>
          <SpendTrendChart data={costs?.breakdown ?? []} />
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm lg:col-span-5">
          <div className="mb-4">
            <h2 className="text-base font-semibold text-slate-900">Model Distribution</h2>
            <p className="text-xs text-slate-500">Traffic share across automatically routed & cached models</p>
          </div>
          <ModelDistributionChart models={models?.models ?? []} />
        </div>
      </div>

      {/* Recent Telemetry Logs */}
      <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-200 px-6 py-4">
          <h2 className="text-base font-semibold text-slate-900">Recent Request Telemetry</h2>
          <p className="text-xs text-slate-500">Latest requests processed through the Cost Guard optimization pipeline</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-200 bg-slate-50 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
              <tr>
                <th className="px-6 py-3">Request ID</th>
                <th className="px-6 py-3">Model / Provider</th>
                <th className="px-6 py-3">Strategy</th>
                <th className="px-6 py-3 text-right">Tokens</th>
                <th className="px-6 py-3 text-right">Actual Cost</th>
                <th className="px-6 py-3 text-right">Saved</th>
                <th className="px-6 py-3 text-right">Latency</th>
                <th className="px-6 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {!logs || logs.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-8 text-center text-slate-400">
                    No gateway traffic logged yet. Open the API Playground to test live or simulated optimization.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.request_id} className="hover:bg-slate-50">
                    <td className="px-6 py-3 font-mono text-slate-700">{log.request_id}</td>
                    <td className="px-6 py-3">
                      <span className="font-mono font-medium text-slate-900">{log.model}</span>
                      <span className="ml-1.5 text-slate-400">({log.provider})</span>
                    </td>
                    <td className="px-6 py-3">
                      {log.cache_hit ? (
                        <StatusBadge variant="info">semantic_cache</StatusBadge>
                      ) : (
                        <StatusBadge variant="neutral">{log.routing_strategy}</StatusBadge>
                      )}
                    </td>
                    <td className="px-6 py-3 text-right tabular-nums text-slate-600">
                      {log.input_tokens + log.output_tokens}
                    </td>
                    <td className="px-6 py-3 text-right font-mono tabular-nums text-slate-900">
                      ${log.actual_cost.toFixed(5)}
                    </td>
                    <td className="px-6 py-3 text-right font-mono font-medium tabular-nums text-emerald-600">
                      +${log.savings.toFixed(5)}
                    </td>
                    <td className="px-6 py-3 text-right tabular-nums text-slate-500">
                      {log.latency_ms.toFixed(0)} ms
                    </td>
                    <td className="px-6 py-3">
                      <StatusBadge variant={log.status === 'success' ? 'success' : 'danger'}>
                        {log.status}
                      </StatusBadge>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
