import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Check, Copy, KeyRound, Plus, Trash2 } from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';
import { api } from '../services/api';

export const ApplicationsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [name, setName] = useState('');
  const [createdKey, setCreatedKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const { data: apps, isLoading } = useQuery({
    queryKey: ['applications-list'],
    queryFn: () => api.getApplications(),
  });

  const createMutation = useMutation({
    mutationFn: () => api.createApplication(name.trim()),
    onSuccess: (created) => {
      setName('');
      setCreatedKey(created.api_key || null);
      queryClient.invalidateQueries({ queryKey: ['applications-list'] });
    },
  });

  const revokeMutation = useMutation({
    mutationFn: (id: string) => api.revokeApplication(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications-list'] });
    },
  });

  const copyText = (val: string) => {
    navigator.clipboard.writeText(val);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Applications & API Keys</h1>
        <p className="mt-1 text-sm text-slate-500">
          Provision scoped application API keys to authenticate applications hitting the Cost Guard Gateway.
        </p>
      </div>

      {/* Create Form */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="mb-3 text-sm font-semibold text-slate-900">Create New Application Key</h2>
        <div className="flex flex-wrap gap-3">
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., Customer Support Agent Prod"
            className="min-w-[260px] flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
          />
          <button
            type="button"
            disabled={!name.trim() || createMutation.isPending}
            onClick={() => createMutation.mutate()}
            className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-50"
          >
            <Plus className="h-4 w-4" />
            Generate API Key
          </button>
        </div>

        {createdKey && (
          <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 p-4">
            <p className="text-xs font-semibold text-emerald-900">
              API Key Created — Copy now! Only SHA-256 hashes are persisted on the server.
            </p>
            <div className="mt-2 flex items-center justify-between rounded border border-emerald-200 bg-white px-3 py-2">
              <code className="font-mono text-xs text-slate-900">{createdKey}</code>
              <button
                type="button"
                onClick={() => copyText(createdKey)}
                className="inline-flex items-center gap-1 rounded bg-slate-100 px-2 py-1 text-xs font-medium text-slate-700 hover:bg-slate-200"
              >
                {copied ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
                {copied ? 'Copied' : 'Copy'}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Applications Table */}
      <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-200 px-6 py-4">
          <h2 className="flex items-center gap-2 text-base font-semibold text-slate-900">
            <KeyRound className="h-4 w-4 text-indigo-600" /> Registered Applications
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-200 bg-slate-50 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
              <tr>
                <th className="px-6 py-3">Application Name</th>
                <th className="px-6 py-3">Key Prefix</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Created</th>
                <th className="px-6 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-slate-400">
                    Loading applications...
                  </td>
                </tr>
              ) : (
                (apps ?? []).map((appItem) => (
                  <tr key={appItem.id} className="hover:bg-slate-50">
                    <td className="px-6 py-3 font-semibold text-slate-900">{appItem.name}</td>
                    <td className="px-6 py-3 font-mono text-slate-600">{appItem.key_prefix || 'cg_••••'}</td>
                    <td className="px-6 py-3">
                      <StatusBadge variant={appItem.status === 'active' ? 'success' : 'danger'}>
                        {appItem.status}
                      </StatusBadge>
                    </td>
                    <td className="px-6 py-3 text-slate-500">
                      {new Date(appItem.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-3 text-right">
                      {appItem.status === 'active' && (
                        <button
                          type="button"
                          onClick={() => revokeMutation.mutate(appItem.id)}
                          className="inline-flex items-center gap-1 rounded border border-red-200 px-2 py-1 text-[11px] font-medium text-red-600 hover:bg-red-50"
                        >
                          <Trash2 className="h-3 w-3" /> Revoke
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Integration Code Snippet */}
      <div className="rounded-xl border border-slate-800 bg-slate-950 p-6 text-slate-200">
        <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-indigo-400">Quick Integration (cURL)</p>
        <pre className="overflow-x-auto font-mono text-xs leading-relaxed text-slate-300">
{`curl -X POST http://localhost:8000/api/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: <YOUR_APPLICATION_API_KEY>" \\
  -d '{
    "model": "auto",
    "messages": [{"role": "user", "content": "Classify this review: Great product!"}],
    "optimization": {"enabled": true, "semantic_cache": true, "prompt_optimization": true, "intelligent_routing": true}
  }'`}
        </pre>
      </div>
    </div>
  );
};
