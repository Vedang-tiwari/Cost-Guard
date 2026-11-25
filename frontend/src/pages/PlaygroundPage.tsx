import React, { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { ArrowRight, CheckCircle2, Cpu, Play, Sparkles, Zap } from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';
import { api } from '../services/api';
import type { PlaygroundCompareResponse } from '../types';

const PRESET_PROMPTS = [
  {
    label: 'Simple Classification',
    prompt:
      'Please kindly classify the following customer review into Positive, Neutral, or Negative sentiment: The onboarding flow was super clean and fast!',
  },
  {
    label: 'Structured JSON Extraction',
    prompt:
      'Extract the vendor name, invoice total, and due date from this snippet as valid JSON: ACME Cloud billed $1,450.00 due on December 15, 2026.',
  },
  {
    label: 'Complex Architecture Reasoning',
    prompt:
      'Analyze the trade-offs step-by-step between eventual consistency with CRDTs versus strong consistency with distributed Raft consensus for a multi-region AI billing ledger. Compare latency, failure recovery, and partition tolerance implications.',
  },
];

export const PlaygroundPage: React.FC = () => {
  const [prompt, setPrompt] = useState(PRESET_PROMPTS[0].prompt);
  const [systemPrompt, setSystemPrompt] = useState('');
  const [fixedModel, setFixedModel] = useState('gpt-4o');
  const [intelligentRouting, setIntelligentRouting] = useState(true);
  const [semanticCache, setSemanticCache] = useState(true);
  const [promptOpt, setPromptOpt] = useState(true);
  const [routingStrategy, setRoutingStrategy] = useState('complexity_based');
  const [minQuality, setMinQuality] = useState(0.85);
  const [maxTokens, setMaxTokens] = useState(512);
  const [executionMode, setExecutionMode] = useState<'simulate' | 'live'>('simulate');
  const [result, setResult] = useState<PlaygroundCompareResponse | null>(null);

  const { data: providersStatus } = useQuery({
    queryKey: ['providers-status'],
    queryFn: () => api.getProvidersStatus(),
  });

  const compareMutation = useMutation({
    mutationFn: () =>
      api.comparePlayground({
        prompt,
        system_prompt: systemPrompt || undefined,
        fixed_model: fixedModel,
        semantic_cache: semanticCache,
        prompt_optimization: promptOpt,
        intelligent_routing: intelligentRouting,
        routing_strategy: routingStrategy,
        minimum_quality_score: minQuality,
        max_tokens: maxTokens,
        execution_mode: executionMode,
      }),
    onSuccess: (data) => {
      setResult(data);
    },
  });

  const anyLiveProvider = providersStatus?.some((p) => p.configured) ?? false;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">API Playground</h1>
          <p className="mt-1 text-sm text-slate-500">
            Compare fixed-model execution side-by-side against Cost Guard intelligent routing, prompt compression, and semantic caching.
          </p>
        </div>

        <div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white p-1 shadow-sm">
          <button
            type="button"
            onClick={() => setExecutionMode('simulate')}
            className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
              executionMode === 'simulate'
                ? 'bg-indigo-600 text-white'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            Engine Simulation Mode
          </button>
          <button
            type="button"
            onClick={() => setExecutionMode('live')}
            className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
              executionMode === 'live'
                ? 'bg-emerald-600 text-white'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            Live Provider Execution {!anyLiveProvider ? '(No Keys Configured)' : ''}
          </button>
        </div>
      </div>

      {/* Presets & Input Controls */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <div className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm lg:col-span-8">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Prompt Input</span>
            <div className="flex flex-wrap gap-1.5">
              {PRESET_PROMPTS.map((preset) => (
                <button
                  key={preset.label}
                  type="button"
                  onClick={() => setPrompt(preset.prompt)}
                  className="rounded-md border border-slate-200 bg-slate-50 px-2.5 py-1 text-[11px] font-medium text-slate-700 hover:border-indigo-300 hover:bg-indigo-50 hover:text-indigo-700"
                >
                  {preset.label}
                </button>
              ))}
            </div>
          </div>

          <textarea
            rows={4}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter a user prompt to compare baseline vs optimized execution..."
            className="w-full rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm text-slate-900 focus:border-indigo-500 focus:bg-white focus:outline-none"
          />

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-600">Optional System Prompt</label>
            <input
              type="text"
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              placeholder="e.g., You are a strict JSON extraction engine."
              className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-900 focus:border-indigo-500 focus:bg-white focus:outline-none"
            />
          </div>

          <div className="flex items-center justify-between pt-2">
            <span className="text-xs text-slate-500">
              {executionMode === 'simulate'
                ? 'Simulation uses Cost Guard analyzer, router, prompt optimizer, cache & pricing catalog with synthesized completion text.'
                : 'Live mode executes both fixed and auto-routed calls against configured provider APIs.'}
            </span>
            <button
              type="button"
              disabled={!prompt.trim() || compareMutation.isPending}
              onClick={() => compareMutation.mutate()}
              className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-indigo-500 disabled:opacity-50"
            >
              <Play className="h-4 w-4" />
              {compareMutation.isPending ? 'Running Comparison...' : 'Run Comparison'}
            </button>
          </div>
          {compareMutation.error && (
            <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
              {compareMutation.error.message}
            </div>
          )}
        </div>

        {/* Optimization Configuration Panel */}
        <div className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm lg:col-span-4">
          <h2 className="text-sm font-semibold text-slate-900">Routing & Optimization Settings</h2>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-600">Baseline Fixed Model</label>
            <select
              value={fixedModel}
              onChange={(e) => setFixedModel(e.target.value)}
              className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-800 focus:border-indigo-500 focus:outline-none"
            >
              <option value="gpt-4o">gpt-4o (OpenAI Baseline)</option>
              <option value="claude-3-5-sonnet-20241022">claude-3-5-sonnet-20241022</option>
              <option value="gemini-1.5-pro">gemini-1.5-pro</option>
            </select>
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-600">Routing Strategy</label>
            <select
              value={routingStrategy}
              onChange={(e) => setRoutingStrategy(e.target.value)}
              className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-800 focus:border-indigo-500 focus:outline-none"
            >
              <option value="complexity_based">Complexity-Based Routing</option>
              <option value="rule_based">Rule-Based Task Routing</option>
            </select>
          </div>

          <div className="space-y-2.5 pt-1">
            <label className="flex cursor-pointer items-center justify-between text-xs">
              <span className="font-medium text-slate-700">Intelligent Auto Routing</span>
              <input
                type="checkbox"
                checked={intelligentRouting}
                onChange={(e) => setIntelligentRouting(e.target.checked)}
                className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
              />
            </label>
            <label className="flex cursor-pointer items-center justify-between text-xs">
              <span className="font-medium text-slate-700">Semantic Cache Lookup</span>
              <input
                type="checkbox"
                checked={semanticCache}
                onChange={(e) => setSemanticCache(e.target.checked)}
                className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
              />
            </label>
            <label className="flex cursor-pointer items-center justify-between text-xs">
              <span className="font-medium text-slate-700">Prompt Optimization</span>
              <input
                type="checkbox"
                checked={promptOpt}
                onChange={(e) => setPromptOpt(e.target.checked)}
                className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
              />
            </label>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-1">
            <div>
              <label className="mb-1 block text-[11px] font-medium text-slate-500">Min Quality ({minQuality})</label>
              <input
                type="range"
                min={0.5}
                max={0.99}
                step={0.01}
                value={minQuality}
                onChange={(e) => setMinQuality(Number(e.target.value))}
                className="w-full accent-indigo-600"
              />
            </div>
            <div>
              <label className="mb-1 block text-[11px] font-medium text-slate-500">Max Tokens</label>
              <input
                type="number"
                min={32}
                max={4096}
                value={maxTokens}
                onChange={(e) => setMaxTokens(Number(e.target.value))}
                className="w-full rounded border border-slate-200 px-2 py-1 text-xs tabular-nums"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Comparison Results */}
      {result && (
        <div className="space-y-4">
          {/* Routing Decision Summary Strip */}
          <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-indigo-200 bg-indigo-50/70 px-6 py-4">
            <div className="flex items-center gap-3">
              <Sparkles className="h-5 w-5 text-indigo-600" />
              <div className="text-xs">
                <p className="font-semibold text-indigo-950">
                  Task Classified: <span className="uppercase">{result.optimized.task_type}</span> • Complexity Score:{' '}
                  <span className="tabular-nums font-bold">{result.optimized.complexity_score}/100</span>
                </p>
                <p className="text-indigo-700">{result.optimized.routing_reason}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <p className="text-[11px] font-medium uppercase text-indigo-600">Net Cost Savings</p>
                <p className="text-lg font-bold text-emerald-600 tabular-nums">
                  {result.optimized.savings_percentage.toFixed(1)}% (${result.optimized.savings.toFixed(5)})
                </p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {/* Fixed Model Card */}
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <Cpu className="h-4 w-4 text-slate-500" />
                  <h3 className="text-sm font-semibold text-slate-900">Fixed Model Execution</h3>
                </div>
                <StatusBadge variant="neutral">{result.fixed.model}</StatusBadge>
              </div>

              <div className="mb-4 grid grid-cols-3 gap-3 rounded-lg bg-slate-50 p-3 text-xs">
                <div>
                  <p className="text-slate-500">Est. Cost</p>
                  <p className="mt-0.5 font-mono font-bold text-slate-900 tabular-nums">
                    ${result.fixed.cost.toFixed(5)}
                  </p>
                </div>
                <div>
                  <p className="text-slate-500">Tokens (In/Out)</p>
                  <p className="mt-0.5 font-mono font-semibold text-slate-800 tabular-nums">
                    {result.fixed.input_tokens} / {result.fixed.output_tokens}
                  </p>
                </div>
                <div>
                  <p className="text-slate-500">Latency</p>
                  <p className="mt-0.5 font-mono font-semibold text-slate-800 tabular-nums">
                    {result.fixed.latency_ms} ms
                  </p>
                </div>
              </div>

              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 text-xs leading-relaxed text-slate-700 whitespace-pre-wrap">
                {result.fixed.response_text}
              </div>
            </div>

            {/* Cost Guard Optimized Card */}
            <div className="rounded-xl border-2 border-indigo-500/30 bg-white p-6 shadow-sm">
              <div className="mb-4 flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4 text-indigo-600" />
                  <h3 className="text-sm font-semibold text-slate-900">Cost Guard Optimized</h3>
                </div>
                <div className="flex items-center gap-1.5">
                  <StatusBadge variant="info">{result.optimized.model}</StatusBadge>
                  {result.optimized.cache_hit && <StatusBadge variant="success">CACHE HIT</StatusBadge>}
                  {result.optimized.fallback_used && <StatusBadge variant="warning">FALLBACK</StatusBadge>}
                </div>
              </div>

              <div className="mb-4 grid grid-cols-4 gap-2 rounded-lg bg-emerald-50/70 p-3 text-xs">
                <div>
                  <p className="text-emerald-800">Actual Cost</p>
                  <p className="mt-0.5 font-mono font-bold text-emerald-700 tabular-nums">
                    ${result.optimized.cost.toFixed(5)}
                  </p>
                </div>
                <div>
                  <p className="text-emerald-800">Tokens</p>
                  <p className="mt-0.5 font-mono font-semibold text-slate-800 tabular-nums">
                    {result.optimized.input_tokens} / {result.optimized.output_tokens}
                  </p>
                </div>
                <div>
                  <p className="text-emerald-800">Quality</p>
                  <p className="mt-0.5 flex items-center gap-1 font-mono font-semibold text-slate-800 tabular-nums">
                    <CheckCircle2 className="h-3 w-3 text-emerald-600" />
                    {((result.optimized.quality_score ?? 0.95) * 100).toFixed(0)}%
                  </p>
                </div>
                <div>
                  <p className="text-emerald-800">Latency</p>
                  <p className="mt-0.5 font-mono font-semibold text-slate-800 tabular-nums">
                    {result.optimized.latency_ms} ms
                  </p>
                </div>
              </div>

              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 text-xs leading-relaxed text-slate-800 whitespace-pre-wrap">
                {result.optimized.response_text}
              </div>

              {result.optimized.prompt_optimized && result.optimized.optimized_prompt_preview && (
                <div className="mt-3 rounded-lg border border-indigo-100 bg-indigo-50/50 p-3 text-[11px]">
                  <div className="mb-1 flex items-center justify-between font-semibold text-indigo-900">
                    <span className="flex items-center gap-1">
                      <ArrowRight className="h-3 w-3" /> Compressed Prompt Preview
                    </span>
                    <span className="text-emerald-700 tabular-nums">
                      -{result.optimized.tokens_saved_by_prompt} tokens saved
                    </span>
                  </div>
                  <p className="font-mono text-indigo-800">{result.optimized.optimized_prompt_preview}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
