import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { AlertTriangle, Plus, ShieldCheck } from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';
import { useAuth } from '../hooks/useAuth';
import { api } from '../services/api';

export const BudgetsPage: React.FC = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [limitAmount, setLimitAmount] = useState('100');
  const [warningThresh, setWarningThresh] = useState('0.8');
  const [period, setPeriod] = useState<'daily' | 'weekly' | 'monthly'>('monthly');
  const [hardLimit, setHardLimit] = useState(true);
  const [showCreate, setShowCreate] = useState(false);

  const { data: budgets, isLoading } = useQuery({
    queryKey: ['budgets-list'],
    queryFn: () => api.getBudgets(),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      api.createBudget({
        organization_id: user?.organization_id || '',
        budget_type: 'organization',
        limit_amount: Number(limitAmount),
        warning_threshold: Number(warningThresh),
        hard_limit: hardLimit,
        period,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['budgets-list'] });
      setShowCreate(false);
    },
  });

  const toggleHardLimit = useMutation({
    mutationFn: (payload: { id: string; hard_limit: boolean }) =>
      api.updateBudget(payload.id, { hard_limit: payload.hard_limit }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['budgets-list'] });
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Budgets & Spend Guards</h1>
          <p className="mt-1 text-sm text-slate-500">
            Configure daily, weekly, and monthly spending caps with warning alerts and automatic hard limits.
          </p>
        </div>

        <button
          type="button"
          onClick={() => setShowCreate(!showCreate)}
          className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
        >
          <Plus className="h-4 w-4" />
          New Budget Policy
        </button>
      </div>

      {showCreate && (
        <div className="rounded-xl border border-indigo-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-sm font-semibold text-slate-900">Create Budget Cap</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Spend Limit ($ USD)</label>
              <input
                type="number"
                step="1"
                min="1"
                value={limitAmount}
                onChange={(e) => setLimitAmount(e.target.value)}
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm tabular-nums"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Warning Threshold (0–1)</label>
              <input
                type="number"
                step="0.05"
                min="0.1"
                max="0.99"
                value={warningThresh}
                onChange={(e) => setWarningThresh(e.target.value)}
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm tabular-nums"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Reset Period</label>
              <select
                value={period}
                onChange={(e) => setPeriod(e.target.value as 'daily' | 'weekly' | 'monthly')}
                className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
            <div className="flex flex-col justify-end">
              <label className="mb-2 flex items-center gap-2 text-xs font-medium text-slate-700">
                <input
                  type="checkbox"
                  checked={hardLimit}
                  onChange={(e) => setHardLimit(e.target.checked)}
                  className="h-4 w-4 accent-indigo-600"
                />
                Enforce Hard Block (HTTP 429)
              </label>
              <button
                type="button"
                onClick={() => createMutation.mutate()}
                disabled={createMutation.isPending}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-500"
              >
                {createMutation.isPending ? 'Creating...' : 'Save Budget'}
              </button>
            </div>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="h-48 animate-pulse rounded-xl bg-slate-200" />
      ) : !budgets || budgets.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white p-12 text-center">
          <p className="text-sm font-medium text-slate-700">No spending budgets configured yet.</p>
          <p className="mt-1 text-xs text-slate-500">Click "New Budget Policy" above to protect against unexpected AI bills.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
          {budgets.map((b) => {
            const pct = Math.min(100, b.spend_percentage);
            const warnPct = b.warning_threshold * 100;
            const barColor =
              b.status === 'exceeded'
                ? 'bg-red-600'
                : pct >= warnPct
                  ? 'bg-amber-500'
                  : 'bg-emerald-500';

            return (
              <div key={b.id} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold capitalize text-slate-900">
                        {b.period} {b.budget_type} Budget
                      </span>
                      <StatusBadge
                        variant={
                          b.status === 'exceeded' ? 'danger' : b.status === 'warning' ? 'warning' : 'success'
                        }
                      >
                        {b.status}
                      </StatusBadge>
                    </div>
                    <p className="mt-1 text-xs text-slate-500">
                      Alert threshold at <span className="font-semibold">{warnPct.toFixed(0)}%</span>
                    </p>
                  </div>
                  <div className="text-right tabular-nums">
                    <p className="text-lg font-bold text-slate-900">${b.limit_amount.toFixed(2)}</p>
                    <p className="text-[11px] text-slate-500">Remaining: ${b.remaining_amount.toFixed(4)}</p>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mt-5">
                  <div className="mb-1.5 flex justify-between text-xs tabular-nums">
                    <span className="font-medium text-slate-700">
                      Current Spend: <span className="font-mono">${b.current_spend.toFixed(4)}</span>
                    </span>
                    <span className="font-semibold text-slate-900">{b.spend_percentage.toFixed(1)}%</span>
                  </div>
                  <div className="relative h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
                    <div
                      className={`h-full rounded-full transition-all ${barColor}`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>

                <div className="mt-4 flex items-center justify-between border-t border-slate-100 pt-3 text-xs">
                  <span className="flex items-center gap-1.5 text-slate-600">
                    {b.hard_limit ? (
                      <>
                        <AlertTriangle className="h-3.5 w-3.5 text-amber-500" /> Hard Limit Enforced (Blocks Requests)
                      </>
                    ) : (
                      <>
                        <ShieldCheck className="h-3.5 w-3.5 text-slate-400" /> Soft Alert Mode Only
                      </>
                    )}
                  </span>
                  <button
                    type="button"
                    onClick={() => toggleHardLimit.mutate({ id: b.id, hard_limit: !b.hard_limit })}
                    className="font-medium text-indigo-600 hover:text-indigo-500"
                  >
                    Switch to {b.hard_limit ? 'Soft Alert' : 'Hard Limit'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
