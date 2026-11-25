import React from 'react';
import { BarChart3, Cpu, DollarSign, FlaskConical, Gauge, KeyRound, Play, ShieldCheck, Sliders, LogOut } from 'lucide-react';
import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const NAV_ITEMS = [
  { to: '/', label: 'Overview', icon: Gauge },
  { to: '/playground', label: 'API Playground', icon: Play },
  { to: '/costs', label: 'Cost Analytics', icon: DollarSign },
  { to: '/models', label: 'Models & Providers', icon: Cpu },
  { to: '/optimization', label: 'Optimization Policy', icon: Sliders },
  { to: '/budgets', label: 'Budgets & Alerts', icon: BarChart3 },
  { to: '/benchmarks', label: 'Benchmarks', icon: FlaskConical },
  { to: '/applications', label: 'Apps & API Keys', icon: KeyRound },
];

export const DashboardLayout: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 z-20 flex w-64 flex-col border-r border-slate-800 bg-slate-950 text-slate-300">
        <div className="flex h-16 items-center gap-2.5 border-b border-slate-800 px-5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white shadow-sm">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <span className="text-base font-bold tracking-tight text-white">Cost Guard</span>
            <span className="ml-2 rounded bg-indigo-500/20 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-indigo-300">
              Gateway
            </span>
          </div>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'text-slate-400 hover:bg-slate-900 hover:text-white'
                  }`
                }
              >
                <Icon className="h-4 w-4 shrink-0" />
                {item.label}
              </NavLink>
            );
          })}
        </nav>

        <div className="border-t border-slate-800 p-4">
          <div className="mb-3 rounded-lg bg-slate-900 px-3 py-2">
            <p className="truncate text-xs font-semibold text-white">{user?.organization_name || 'Workspace'}</p>
            <p className="truncate text-[11px] text-slate-400">{user?.email}</p>
          </div>
          <button
            type="button"
            onClick={logout}
            className="flex w-full items-center justify-center gap-2 rounded-lg border border-slate-800 px-3 py-1.5 text-xs font-medium text-slate-300 transition-colors hover:bg-slate-900 hover:text-white"
          >
            <LogOut className="h-3.5 w-3.5" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex flex-1 flex-col pl-64">
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-slate-200 bg-white/80 px-8 backdrop-blur-md">
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            <span>Gateway Online</span>
            <span className="text-slate-300">|</span>
            <span className="font-mono text-slate-600">POST /api/v1/chat/completions</span>
          </div>
          <div className="flex items-center gap-4">
            <a
              href="/metrics"
              target="_blank"
              rel="noreferrer"
              className="text-xs font-medium text-slate-500 hover:text-indigo-600"
            >
              Prometheus /metrics
            </a>
            <a
              href="/docs"
              target="_blank"
              rel="noreferrer"
              className="rounded-md border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 shadow-sm hover:bg-slate-50"
            >
              OpenAPI Docs
            </a>
          </div>
        </header>

        <main className="mx-auto w-full max-w-7xl flex-1 p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
