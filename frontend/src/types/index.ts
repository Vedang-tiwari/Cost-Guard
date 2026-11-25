export interface UserProfile {
  id: string;
  email: string;
  full_name: string | null;
  organization_id: string | null;
  organization_name: string | null;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserProfile;
  default_api_key?: string | null;
}

export interface OverviewStats {
  total_requests: number;
  total_spend: number;
  baseline_cost: number;
  total_savings: number;
  savings_percentage: number;
  avg_cost_per_request: number;
  cache_hit_rate: number;
  avg_quality_score: number;
  avg_latency_ms: number;
  p95_latency_ms: number;
  fallback_rate: number;
}

export interface CostTimePoint {
  date: string;
  actual_cost: number;
  baseline_cost: number;
  savings: number;
  requests_count: number;
}

export interface NameCostItem {
  name: string;
  cost: number;
}

export interface CostAnalytics {
  total_spend: number;
  baseline_spend: number;
  total_savings: number;
  breakdown: CostTimePoint[];
  by_provider: NameCostItem[];
  by_model: NameCostItem[];
  by_application: NameCostItem[];
  token_costs: {
    input_cost?: number;
    output_cost?: number;
  };
}

export interface ModelStat {
  model: string;
  provider: string;
  request_count: number;
  share_pct: number;
  input_tokens: number;
  output_tokens: number;
  total_cost: number;
  avg_latency_ms: number;
  avg_quality_score: number | null;
}

export interface ModelAnalytics {
  total_models_used: number;
  models: ModelStat[];
}

export interface SavingsAnalytics {
  total_savings: number;
  savings_percentage: number;
  sources: {
    cache_savings: number;
    routing_savings: number;
    compression_savings: number;
  };
  monthly_projected_savings: number;
}

export interface RequestLogItem {
  request_id: string;
  model: string;
  provider: string;
  input_tokens: number;
  output_tokens: number;
  estimated_cost: number;
  actual_cost: number;
  savings: number;
  latency_ms: number;
  cache_hit: boolean;
  complexity_score: number;
  routing_strategy: string;
  quality_score: number | null;
  fallback_used: boolean;
  status: string;
  created_at: string;
}

export interface ModelRegistryInfo {
  id: string;
  provider: string;
  model_name: string;
  input_price_per_million: number;
  output_price_per_million: number;
  capabilities: Record<string, boolean>;
  context_window: number;
  is_active: boolean;
  pricing_version: string;
}

export interface ProviderStatusInfo {
  provider: string;
  configured: boolean;
  models_count: number;
  status: string;
}

export interface Budget {
  id: string;
  organization_id: string;
  application_id: string | null;
  budget_type: string;
  limit_amount: number;
  warning_threshold: number;
  hard_limit: boolean;
  period: string;
  current_spend: number;
  remaining_amount: number;
  spend_percentage: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface OptimizationPolicy {
  id: string;
  organization_id: string;
  intelligent_routing: boolean;
  routing_strategy: string;
  semantic_cache: boolean;
  cache_similarity_threshold: number;
  prompt_optimization: boolean;
  quality_gate_enabled: boolean;
  minimum_quality_score: number;
  fallback_to_premium: boolean;
  max_output_tokens: number;
  updated_at: string;
}

export interface BenchmarkRun {
  id: string;
  reference_model: string;
  candidate_model: string;
  total_cases: number;
  overall_quality_score: number;
  quality_retention: number;
  total_reference_cost: number;
  total_candidate_cost: number;
  cost_savings_pct: number;
  category_breakdown: Record<string, { candidate_quality: number; count: number }>;
  created_at: string;
}

export interface ApplicationItem {
  id: string;
  organization_id: string;
  name: string;
  key_prefix: string | null;
  status: string;
  created_at: string;
  api_key?: string;
}

export interface PlaygroundSideResult {
  model: string;
  provider: string;
  response_text: string;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  cost: number;
  baseline_cost: number;
  savings: number;
  savings_percentage: number;
  latency_ms: number;
  cache_hit: boolean;
  prompt_optimized: boolean;
  tokens_saved_by_prompt: number;
  optimized_prompt_preview?: string | null;
  complexity_score: number;
  task_type: string;
  routing_strategy: string;
  routing_reason: string;
  quality_score: number | null;
  fallback_used: boolean;
}

export interface PlaygroundCompareResponse {
  execution_mode: 'live' | 'simulate';
  fixed: PlaygroundSideResult;
  optimized: PlaygroundSideResult;
}
