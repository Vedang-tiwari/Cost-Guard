import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Check, Cpu, Edit3, Server, X } from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';
import { api } from '../services/api';
import type { ModelRegistryInfo } from '../types';

export const ModelsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [editingModel, setEditingModel] = useState<ModelRegistryInfo | null>(null);
  const [inPrice, setInPrice] = useState('');
  const [outPrice, setOutPrice] = useState('');

  const { data: models } = useQuery({
    queryKey: ['models-registry'],
    queryFn: () => api.getModels(true),
  });

  const { data: providers } = useQuery({
    queryKey: ['providers-status'],
    queryFn: () => api.getProvidersStatus(),
  });

  const { data: analytics } = useQuery({
    queryKey: ['analytics-models-perf'],
    queryFn: () => api.getModelAnalytics(30),
  });

  const updateMutation = useMutation({
    mutationFn: (payload: {
      id: string;
      input_price_per_million?: number;
      output_price_per_million?: number;
      is_active?: boolean;
    }) => {
      const { id, ...body } = payload;
      return api.updateModel(id, body);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['models-registry'] });
      setEditingModel(null);
    },
  });

  const perfByModel = new Map((analytics?.models ?? []).map((m) => [m.model, m]));

  const startEdit = (m: ModelRegistryInfo) => {
    setEditingModel(m);
    setInPrice(String(m.input_price_per_million));
    setOutPrice(String(m.output_price_per_million));
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Models & Providers</h1>
        <p className="mt-1 text-sm text-slate-500">
          Inspect provider readiness, manage catalog pricing per 1M tokens, and track per-model latency and selection volume.
        </p>
      </div>

      {/* Provider Configuration Cards (Never exposing secrets) */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {(providers ?? []).map((p) => (
          <div key={p.provider} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Server className="h-4 w-4 text-slate-500" />
                <span className="font-semibold capitalize text-slate-900">{p.provider}</span>
              </div>
              <StatusBadge variant={p.configured ? 'success' : 'neutral'}>
                {p.configured ? 'Configured' : 'Env Key Unset'}
              </StatusBadge>
            </div>
            <p className="mt-3 text-xs text-slate-500">
              Registered models: <span className="font-semibold text-slate-800">{p.models_count}</span>
            </p>
            <p className="mt-1 text-[11px] text-slate-400">API credentials reside securely on server env only</p>
          </div>
        ))}
      </div>

      {/* Models Registry Table */}
      <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <div className="flex items-center gap-2">
            <Cpu className="h-4 w-4 text-indigo-600" />
            <h2 className="text-base font-semibold text-slate-900">Model Registry & Performance</h2>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-200 bg-slate-50 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
              <tr>
                <th className="px-6 py-3">Model</th>
                <th className="px-6 py-3">Provider</th>
                <th className="px-6 py-3 text-right">Input / 1M</th>
                <th className="px-6 py-3 text-right">Output / 1M</th>
                <th className="px-6 py-3 text-right">Context Window</th>
                <th className="px-6 py-3 text-right">Volume (Share)</th>
                <th className="px-6 py-3 text-right">Avg Latency</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {(models ?? []).map((m) => {
                const perf = perfByModel.get(m.model_name);
                const isEditing = editingModel?.id === m.id;
                return (
                  <tr key={m.id} className="hover:bg-slate-50">
                    <td className="px-6 py-3 font-mono font-semibold text-slate-900">{m.model_name}</td>
                    <td className="px-6 py-3 capitalize text-slate-600">{m.provider}</td>
                    <td className="px-6 py-3 text-right font-mono tabular-nums">
                      {isEditing ? (
                        <input
                          type="number"
                          step="0.001"
                          value={inPrice}
                          onChange={(e) => setInPrice(e.target.value)}
                          className="w-20 rounded border border-indigo-400 px-1.5 py-0.5 text-right"
                        />
                      ) : (
                        `$${m.input_price_per_million.toFixed(3)}`
                      )}
                    </td>
                    <td className="px-6 py-3 text-right font-mono tabular-nums">
                      {isEditing ? (
                        <input
                          type="number"
                          step="0.001"
                          value={outPrice}
                          onChange={(e) => setOutPrice(e.target.value)}
                          className="w-20 rounded border border-indigo-400 px-1.5 py-0.5 text-right"
                        />
                      ) : (
                        `$${m.output_price_per_million.toFixed(3)}`
                      )}
                    </td>
                    <td className="px-6 py-3 text-right tabular-nums text-slate-600">
                      {m.context_window.toLocaleString()}
                    </td>
                    <td className="px-6 py-3 text-right tabular-nums text-slate-700">
                      {perf ? `${perf.request_count} (${perf.share_pct}%)` : '0 (0%)'}
                    </td>
                    <td className="px-6 py-3 text-right tabular-nums text-slate-600">
                      {perf ? `${perf.avg_latency_ms} ms` : '—'}
                    </td>
                    <td className="px-6 py-3">
                      <button
                        type="button"
                        onClick={() => updateMutation.mutate({ id: m.model_name, is_active: !m.is_active })}
                        title="Toggle active state"
                      >
                        <StatusBadge variant={m.is_active ? 'success' : 'neutral'}>
                          {m.is_active ? 'Active' : 'Disabled'}
                        </StatusBadge>
                      </button>
                    </td>
                    <td className="px-6 py-3 text-right">
                      {isEditing ? (
                        <div className="inline-flex items-center gap-1">
                          <button
                            type="button"
                            onClick={() =>
                              updateMutation.mutate({
                                id: m.model_name,
                                input_price_per_million: Number(inPrice),
                                output_price_per_million: Number(outPrice),
                              })
                            }
                            className="rounded bg-emerald-600 p-1 text-white hover:bg-emerald-500"
                          >
                            <Check className="h-3.5 w-3.5" />
                          </button>
                          <button
                            type="button"
                            onClick={() => setEditingModel(null)}
                            className="rounded bg-slate-200 p-1 text-slate-700 hover:bg-slate-300"
                          >
                            <X className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      ) : (
                        <button
                          type="button"
                          onClick={() => startEdit(m)}
                          className="inline-flex items-center gap-1 rounded border border-slate-200 px-2 py-1 text-[11px] font-medium text-slate-600 hover:bg-slate-100"
                        >
                          <Edit3 className="h-3 w-3" /> Edit Price
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
