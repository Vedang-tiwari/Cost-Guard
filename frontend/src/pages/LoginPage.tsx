import React, { useState } from 'react';
import { KeyRound, ShieldCheck } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export const LoginPage: React.FC = () => {
  const { loginWithCredentials, loginWithApiKey } = useAuth();
  const navigate = useNavigate();

  const [tab, setTab] = useState<'credentials' | 'apikey'>('credentials');
  const [email, setEmail] = useState('demo@costguard.ai');
  const [password, setPassword] = useState('CostGuard2026!');
  const [apiKey, setApiKey] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      if (tab === 'credentials') {
        await loginWithCredentials(email, password);
      } else {
        await loginWithApiKey(apiKey);
      }
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4">
      <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-8 shadow-2xl">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Cost Guard Gateway</h1>
            <p className="text-xs text-slate-400">Intelligent LLM FinOps & Quality Console</p>
          </div>
        </div>

        <div className="mb-6 grid grid-cols-2 rounded-lg bg-slate-950 p-1">
          <button
            type="button"
            onClick={() => setTab('credentials')}
            className={`rounded-md py-1.5 text-xs font-medium transition-colors ${
              tab === 'credentials' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            Email & Password
          </button>
          <button
            type="button"
            onClick={() => setTab('apikey')}
            className={`flex items-center justify-center gap-1.5 rounded-md py-1.5 text-xs font-medium transition-colors ${
              tab === 'apikey' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            <KeyRound className="h-3.5 w-3.5" />
            API Key
          </button>
        </div>

        {error && (
          <div className="mb-4 rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-xs text-red-300">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {tab === 'credentials' ? (
            <>
              <div>
                <label className="mb-1.5 block text-xs font-medium text-slate-300">Work Email</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-indigo-500 focus:outline-none"
                  placeholder="developer@company.com"
                />
              </div>
              <div>
                <label className="mb-1.5 block text-xs font-medium text-slate-300">Password</label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-indigo-500 focus:outline-none"
                />
              </div>
              <p className="text-[11px] text-slate-500">
                Seeded demo credentials pre-filled (<code className="text-slate-300">scripts/seed_models.py</code>), or register a new workspace below.
              </p>
            </>
          ) : (
            <div>
              <label className="mb-1.5 block text-xs font-medium text-slate-300">Application API Key</label>
              <input
                type="password"
                required
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 font-mono text-sm text-white placeholder-slate-500 focus:border-indigo-500 focus:outline-none"
                placeholder="cg_live_... or cg_test_1234567890abcdef"
              />
            </div>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-lg bg-indigo-600 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-indigo-500 disabled:opacity-50"
          >
            {submitting ? 'Authenticating...' : 'Access Dashboard'}
          </button>
        </form>

        <p className="mt-6 text-center text-xs text-slate-400">
          New organization?{' '}
          <Link to="/register" className="font-medium text-indigo-400 hover:text-indigo-300">
            Create an account & API key
          </Link>
        </p>
      </div>
    </div>
  );
};
