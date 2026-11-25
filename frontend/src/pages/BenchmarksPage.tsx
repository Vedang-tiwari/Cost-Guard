import React from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { FlaskConical, Play } from 'lucide-react';
import { BenchmarkBarChart } from '../charts/BenchmarkBarChart';
import { StatusBadge } from '../components/StatusBadge';
import { api } from '../services/api';

export const BenchmarksPage: React.FC = () => {
  const queryClient = useQueryClient();

  const { data: runs, isLoading } = useQuery({
    queryKey: ['benchmark-results'],
    queryFn: () => api.getBenchmarkResults(),
  });

  const runMutation = useMutation({
    mutationFn: () =>
      api.runBenchmarks(['gpt-4o-mini', 'gemini-1.5-flash', 'claude-3-5-haiku-20241022'], 'gpt-4o'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['benchmark-results'] });
    },
  });

  // Deduplicate latest run per candidate_model for chart display
  const latestByModel = Array.from(
    new Map((runs ?? []).map((r) => [r.candidate_model, r])).values()
  );

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Benchmark Comparisons</h1>
          <p className="mt-1 text-sm text-slate-500">
            Reproducible 14-prompt multi-category benchmark comparing cost savings and quality retention against baseline <code className="font-mono text-slate-700">gpt-4o</code>.
          </p>
        </div>

        <button
          type="button"
          onClick={() => runMutation.mutate()}
          disabled={runMutation.isPending}
          className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50"
        >
          <Play className="h-4 w-4" />
          {runMutation.isPending ? 'Running Suite...' : 'Re-run Benchmark Suite'}
        </button>
      </div>

      {/* Chart */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center gap-2">
          <FlaskConical className="h-4 w-4 text-indigo-600" />
          <h2 className="text-base font-semibold text-slate-900">Quality Retention vs Cost Savings (%)</h2>
        </div>
        {isLoading ? (
          <div className="h-72 animate-pulse rounded bg-slate-100" />
        ) : (
          <BenchmarkBarChart runs={latestByModel} />
        )}
      </div>

      {/* Detailed Category Matrix Cards */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {latestByModel.map((run) => (
          <div key={run.id} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-start justify-between border-b border-slate-100 pb-4">
              <div>
                <p className="font-mono text-sm font-bold text-slate-900">{run.candidate_model}</p>
                <p className="text-xs text-slate-500">vs baseline {run.reference_model}</p>
              </div>
              <StatusBadge variant="success">{run.cost_savings_pct.toFixed(1)}% Saved</StatusBadge>
            </div>

            <div className="my-4 grid grid-cols-2 gap-3 rounded-lg bg-slate-50 p-3 text-xs">
              <div>
                <p className="text-slate-500">Quality Retention</p>
                <p className="mt-0.5 text-base font-bold text-indigo-600 tabular-nums">
                  {run.quality_retention.toFixed(1)}%
                </p>
              </div>
              <div>
                <p className="text-slate-500">Suite Cost ({run.total_cases} cases)</p>
                <p className="mt-0.5 font-mono text-sm font-semibold text-slate-900 tabular-nums">
                  ${run.total_candidate_cost.toFixed(6)}
                </p>
              </div>
            </div>

            <div className="space-y-2">
              <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Category Quality Breakdown</p>
              {Object.entries(run.category_breakdown || {}).map(([cat, metrics]) => (
                <div key={cat} className="flex items-center justify-between text-xs">
                  <span className="capitalize text-slate-600">
                    {cat.replace('_', ' ')} ({metrics.count})
                  </span>
                  <span className="font-mono font-semibold text-slate-900 tabular-nums">
                    {(metrics.candidate_quality * 100).toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
