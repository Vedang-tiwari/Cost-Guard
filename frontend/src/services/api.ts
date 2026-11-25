import type {
  ApplicationItem,
  AuthResponse,
  BenchmarkRun,
  Budget,
  CostAnalytics,
  ModelAnalytics,
  ModelRegistryInfo,
  OptimizationPolicy,
  OverviewStats,
  PlaygroundCompareResponse,
  ProviderStatusInfo,
  RequestLogItem,
  SavingsAnalytics,
  UserProfile,
} from '../types';

const TOKEN_STORAGE_KEY = 'costguard_auth_token';
const AUTH_MODE_KEY = 'costguard_auth_mode'; // 'jwt' | 'apikey'

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

export function getStoredAuth(): { token: string | null; mode: 'jwt' | 'apikey' } {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);
  const mode = (localStorage.getItem(AUTH_MODE_KEY) as 'jwt' | 'apikey') || 'jwt';
  return { token, mode };
}

export function setStoredAuth(token: string, mode: 'jwt' | 'apikey'): void {
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
  localStorage.setItem(AUTH_MODE_KEY, mode);
}

export function clearStoredAuth(): void {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  localStorage.removeItem(AUTH_MODE_KEY);
}

async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const { token, mode } = getStoredAuth();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> | undefined),
  };

  if (token) {
    if (mode === 'apikey') {
      headers['X-API-Key'] = token;
    } else {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const errBody = await res.json();
      message = errBody?.error?.message || errBody?.detail || message;
    } catch {
      // ignore non-json
    }
    throw new Error(message);
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return res.json() as Promise<T>;
}

export const api = {
  // Auth
  login: (email: string, password: string) =>
    apiRequest<AuthResponse>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  register: (payload: {
    email: string;
    password: string;
    full_name: string;
    organization_name: string;
  }) =>
    apiRequest<AuthResponse>('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  me: () => apiRequest<UserProfile>('/api/v1/auth/me'),

  // Gateway Readiness
  ready: () =>
    apiRequest<{ status: string; database: string; providers: Record<string, boolean> }>('/ready'),

  // Analytics
  getOverview: (days = 30) => apiRequest<OverviewStats>(`/api/v1/analytics/overview?days=${days}`),
  getCosts: (days = 14, period: 'daily' | 'weekly' | 'monthly' = 'daily') =>
    apiRequest<CostAnalytics>(`/api/v1/analytics/costs?days=${days}&period=${period}`),
  getModelAnalytics: (days = 30) => apiRequest<ModelAnalytics>(`/api/v1/analytics/models?days=${days}`),
  getSavings: (days = 30) => apiRequest<SavingsAnalytics>(`/api/v1/analytics/savings?days=${days}`),
  getLogs: (limit = 30) => apiRequest<RequestLogItem[]>(`/api/v1/analytics/logs?limit=${limit}`),

  // Models & Providers
  getModels: (includeInactive = true) =>
    apiRequest<ModelRegistryInfo[]>(`/api/v1/models?include_inactive=${includeInactive}`),
  getProvidersStatus: () => apiRequest<ProviderStatusInfo[]>('/api/v1/models/providers/status'),
  updateModel: (
    modelId: string,
    payload: Partial<Pick<ModelRegistryInfo, 'input_price_per_million' | 'output_price_per_million' | 'is_active' | 'pricing_version'>>
  ) =>
    apiRequest<ModelRegistryInfo>(`/api/v1/models/${encodeURIComponent(modelId)}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),

  // Optimization Policy
  getPolicy: () => apiRequest<OptimizationPolicy>('/api/v1/policies'),
  updatePolicy: (payload: Partial<OptimizationPolicy>) =>
    apiRequest<OptimizationPolicy>('/api/v1/policies', {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),

  // Budgets
  getBudgets: () => apiRequest<Budget[]>('/api/v1/budgets'),
  createBudget: (payload: {
    organization_id: string;
    application_id?: string | null;
    budget_type: string;
    limit_amount: number;
    warning_threshold: number;
    hard_limit: boolean;
    period: string;
  }) =>
    apiRequest<Budget>('/api/v1/budgets', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  updateBudget: (
    budgetId: string,
    payload: Partial<Pick<Budget, 'limit_amount' | 'warning_threshold' | 'hard_limit' | 'period' | 'status'>>
  ) =>
    apiRequest<Budget>(`/api/v1/budgets/${budgetId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),

  // Benchmarks
  getBenchmarkResults: () => apiRequest<BenchmarkRun[]>('/api/v1/benchmarks/results'),
  runBenchmarks: (candidateModels: string[], referenceModel = 'gpt-4o') =>
    apiRequest<BenchmarkRun[]>('/api/v1/benchmarks/run', {
      method: 'POST',
      body: JSON.stringify({ candidate_models: candidateModels, reference_model: referenceModel }),
    }),

  // Applications
  getApplications: () => apiRequest<ApplicationItem[]>('/api/v1/applications'),
  createApplication: (name: string) =>
    apiRequest<ApplicationItem>('/api/v1/applications', {
      method: 'POST',
      body: JSON.stringify({ name }),
    }),
  revokeApplication: (id: string) =>
    apiRequest<void>(`/api/v1/applications/${id}`, {
      method: 'DELETE',
    }),

  // Playground
  comparePlayground: (payload: {
    prompt: string;
    system_prompt?: string;
    fixed_model: string;
    semantic_cache: boolean;
    prompt_optimization: boolean;
    intelligent_routing: boolean;
    routing_strategy: string;
    minimum_quality_score: number;
    max_tokens: number;
    execution_mode: 'live' | 'simulate';
  }) =>
    apiRequest<PlaygroundCompareResponse>('/api/v1/playground/compare', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
};
