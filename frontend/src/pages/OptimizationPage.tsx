import React, { useEffect, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { CheckCircle2, Save, ShieldAlert, Sliders, TrendingDown } from 'lucide-react';
import { StatCard } from '../components/StatCard';
import { api } from '../services/api';
import type { OptimizationPolicy } from '../types';

export const OptimizationPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [form, setForm] = useState<Partial<OptimizationPolicy>>({});
  const [savedMsg, setSavedMsg] = useState('');

  const { data: policy, isLoading } = useQuery({
    queryKey: ['optimization-policy'],
    queryFn: () => api.getPolicy(),
  });

  const { data: savings } = useQuery({
    queryKey: ['analytics-savings-opt'],
    queryFn: () => api.getSavings(30),
  });

  const { data: overview } = useQuery({
    queryKey: ['analytics-overview-opt'],
    queryFn: () => api.getOverview(30),
  });

  useEffect(() => {
    if (policy) {
      setForm(policy);
    }
  }, [policy]);

  const saveMutation = useMutation({
    mutationFn: () =>
      api.updatePolicy({
        intelligent_routing: form.intelligent_routing,
        routing_strategy: form.routing_strategy,
        semantic_cache: form.semantic_cache,
        cache_similarity_threshold: form.cache_similarity_threshold,
        prompt_optimization: form.prompt_optimization,
        quality_gate_enabled: form.quality_gate_enabled,
        minimum_quality_score: form.minimum_quality_score,
        fallback_to_premium: form.fallback_to_premium,
        max_output_tokens: form.max_output_tokens,
      }),
    onSuccess: (updated) => {
      queryClient.setQueryData(['optimization-policy'], updated);
      setSavedMsg('Optimization policy updated successfully.');
      setTimeout(() => setSavedMsg(''), 3000);
    },
  });

  if (isLoading) {
    return <div className="h-64 animate-pulse rounded-xl bg-slate-200" />;
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Optimization Policy & Attribution</h1>
          <p className="mt-1 text-sm text-slate-500">
            Configure gateway routing strategies, semantic cache thresholds, quality gates, and fallback safety rules.
          </p>
        </div>

        <button
          type="button"
          onClick={() => saveMutation.mutate()}
          disabled={saveMutation.isPending}
          className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50"
        >
          <Save className="h-4 w-4" />
          {saveMutation.isPending ? 'Saving...' : 'Save Policy'}
        </button>
      </div>

      {savedMsg && (
        <div className="flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-2.5 text-xs font-medium text-emerald-800">
          <CheckCircle2 className="h-4 w-4 text-emerald-600" />
          {savedMsg}
        </div>
      )}

      {/* Savings Lever Attribution */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Intelligent Routing Savings"
          value={`$${(savings?.sources?.routing_savings ?? 0).toFixed(4)}`}
          subtitle="Routed to cost-effective tiers"
          icon={Sliders}
          accent="indigo"
        />
        <StatCard
          title="Semantic Cache Savings"
          value={`$${(savings?.sources?.cache_savings ?? 0).toFixed(4)}`}
          subtitle={`Hit rate: ${(overview?.cache_hit_rate ?? 0).toFixed(1)}%`}
          icon={TrendingDown}
          accent="emerald"
        />
        <StatCard
          title="Prompt Compression Savings"
          value={`$${(savings?.sources?.compression_savings ?? 0).toFixed(4)}`}
          subtitle="Input token stripping"
          icon={TrendingDown}
        />
        <StatCard
          title="Quality Fallback Rate"
          value={`${(overview?.fallback_rate ?? 0).toFixed(1)}%`}
          subtitle={`Avg quality: ${(overview?.avg_quality_score ?? 0).toFixed(1)}%`}
          icon={ShieldAlert}
          accent="amber"
        />
      </div>

      {/* Interactive Configuration Cards */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="space-y-5 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-base font-semibold text-slate-900">Routing & Caching Engines</h2>

          <label className="flex items-center justify-between rounded-lg border border-slate-100 bg-slate-50 p-4">
            <div>
              <p className="text-sm font-medium text-slate-900">Intelligent Model Routing</p>
              <p className="text-xs text-slate-500">Automatically route low/medium complexity prompts to cheaper capable tiers</p>
            </div>
            <input
              type="checkbox"
              checked={Boolean(form.intelligent_routing)}
              onChange={(e) => setForm({ ...form, intelligent_routing: e.target.checked })}
              className="h-4 w-4 accent-indigo-600"
            />
          </label>

          <div>
            <label className="mb-1.5 block text-xs font-medium text-slate-700">Default Routing Strategy</label>
            <select
              value={form.routing_strategy ?? 'complexity_based'}
              onChange={(e) => setForm({ ...form, routing_strategy: e.target.value })}
              className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900"
            >
              <option value="complexity_based">Complexity-Based (0–100 Scorer)</option>
              <option value="rule_based">Rule-Based Task Classification</option>
              <option value="explicit">Explicit Baseline Passthrough</option>
            </select>
          </div>

          <label className="flex items-center justify-between rounded-lg border border-slate-100 bg-slate-50 p-4">
            <div>
              <p className="text-sm font-medium text-slate-900">Semantic Vector Caching</p>
              <p className="text-xs text-slate-500">Serve compatible repeated queries directly with zero provider latency</p>
            </div>
            <input
              type="checkbox"
              checked={Boolean(form.semantic_cache)}
              onChange={(e) => setForm({ ...form, semantic_cache: e.target.checked })}
              className="h-4 w-4 accent-indigo-600"
            />
          </label>

          <div>
            <div className="mb-1.5 flex items-center justify-between text-xs">
              <span className="font-medium text-slate-700">Semantic Similarity Threshold</span>
              <span className="font-mono font-semibold text-indigo-600 tabular-nums">
                {(form.cache_similarity_threshold ?? 0.88).toFixed(2)}
              </span>
            </div>
            <input
              type="range"
              min={0.65}
              max={0.98}
              step={0.01}
              value={form.cache_similarity_threshold ?? 0.88}
              onChange={(e) => setForm({ ...form, cache_similarity_threshold: Number(e.target.value) })}
              className="w-full accent-indigo-600"
            />
          </div>
        </div>

        <div className="space-y-5 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-base font-semibold text-slate-900">Quality Preservation & Token Guards</h2>

          <label className="flex items-center justify-between rounded-lg border border-slate-100 bg-slate-50 p-4">
            <div>
              <p className="text-sm font-medium text-slate-900">Prompt Optimization</p>
              <p className="text-xs text-slate-500">Strip polite filler phrases & excess whitespace without changing instructions</p>
            </div>
            <input
              type="checkbox"
              checked={Boolean(form.prompt_optimization)}
              onChange={(e) => setForm({ ...form, prompt_optimization: e.target.checked })}
              className="h-4 w-4 accent-indigo-600"
            />
          </label>

          <label className="flex items-center justify-between rounded-lg border border-slate-100 bg-slate-50 p-4">
            <div>
              <p className="text-sm font-medium text-slate-900">Automated Quality Gate & Cascade Fallback</p>
              <p className="text-xs text-slate-500">Evaluate outputs and automatically retry with a premium model if score drops below minimum</p>
            </div>
            <input
              type="checkbox"
              checked={Boolean(form.quality_gate_enabled)}
              onChange={(e) => setForm({ ...form, quality_gate_enabled: e.target.checked })}
              className="h-4 w-4 accent-indigo-600"
            />
          </label>

          <div>
            <div className="mb-1.5 flex items-center justify-between text-xs">
              <span className="font-medium text-slate-700">Minimum Quality Score Threshold</span>
              <span className="font-mono font-semibold text-emerald-600 tabular-nums">
                {((form.minimum_quality_score ?? 0.85) * 100).toFixed(0)}%
              </span>
            </div>
            <input
              type="range"
              min={0.5}
              max={0.98}
              step={0.01}
              value={form.minimum_quality_score ?? 0.85}
              onChange={(e) => setForm({ ...form, minimum_quality_score: Number(e.target.value) })}
              className="w-full accent-emerald-600"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1.5 block text-xs font-medium text-slate-700">Fallback Policy</label>
              <select
                value={form.fallback_to_premium ? 'premium' : 'none'}
                onChange={(e) => setForm({ ...form, fallback_to_premium: e.target.value === 'premium' })}
                className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs text-slate-900"
              >
                <option value="premium">Escalate to Premium Model</option>
                <option value="none">Return Candidate Only</option>
              </select>
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-slate-700">Max Completion Tokens</label>
              <input
                type="number"
                min={64}
                max={32768}
                value={form.max_output_tokens ?? 1024}
                onChange={(e) => setForm({ ...form, max_output_tokens: Number(e.target.value) })}
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-xs font-mono tabular-nums text-slate-900"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
