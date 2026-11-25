import time

from app.analyzer.complexity import analyze_complexity
from app.analyzer.token_estimator import estimate_expected_output_tokens, estimate_messages_tokens
from app.api.dependencies import verify_application_api_key
from app.cache.cache_policy import CachePolicy
from app.cache.semantic_cache import get_semantic_cache
from app.cost.calculator import calculate_baseline_cost, calculate_cost, calculate_savings
from app.cost.pricing_registry import get_model_pricing
from app.database.models.application import Application
from app.database.session import get_db
from app.evaluation.evaluator import QualityEvaluator
from app.gateway.optimization_pipeline import get_optimization_pipeline
from app.optimization.prompt_optimizer import optimize_prompt
from app.router.model_router import RoutingInput, get_model_router
from app.schemas.playground import (
    PlaygroundCompareRequest,
    PlaygroundCompareResponse,
    PlaygroundSideResult,
)
from app.schemas.request import (
    ChatCompletionRequest,
    ChatMessage,
    OptimizationConfig,
    QualityConfig,
)
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/playground", tags=["API Playground"])


@router.post("/compare", response_model=PlaygroundCompareResponse)
async def compare_playground(
    payload: PlaygroundCompareRequest,
    app: Application = Depends(verify_application_api_key),
    db: AsyncSession = Depends(get_db),
) -> PlaygroundCompareResponse:
    """
    Executes or simulates a side-by-side comparison between fixed baseline model execution
    and Cost Guard intelligent optimization.
    """
    messages: list[ChatMessage] = []
    if payload.system_prompt and payload.system_prompt.strip():
        messages.append(ChatMessage(role="system", content=payload.system_prompt.strip()))
    messages.append(ChatMessage(role="user", content=payload.prompt))

    if payload.execution_mode == "live":
        pipeline = get_optimization_pipeline()

        # Fixed execution
        t0 = time.perf_counter()
        fixed_req = ChatCompletionRequest(
            model=payload.fixed_model,
            messages=messages,
            optimization=OptimizationConfig(
                enabled=False,
                semantic_cache=False,
                prompt_optimization=False,
                intelligent_routing=False,
            ),
            quality=QualityConfig(minimum_score=0.0, eval_enabled=False),
            max_tokens=payload.max_tokens,
        )
        fixed_resp = await pipeline.execute(fixed_req, app, db)
        fixed_lat = round((time.perf_counter() - t0) * 1000, 2)

        # Optimized execution
        t1 = time.perf_counter()
        opt_req = ChatCompletionRequest(
            model="auto" if payload.intelligent_routing else payload.fixed_model,
            messages=messages,
            optimization=OptimizationConfig(
                enabled=True,
                semantic_cache=payload.semantic_cache,
                prompt_optimization=payload.prompt_optimization,
                intelligent_routing=payload.intelligent_routing,
            ),
            quality=QualityConfig(minimum_score=payload.minimum_quality_score, eval_enabled=True),
            max_tokens=payload.max_tokens,
        )
        opt_resp = await pipeline.execute(opt_req, app, db)
        opt_lat = round((time.perf_counter() - t1) * 1000, 2)

        complexity = analyze_complexity(messages)
        prompt_opt = optimize_prompt(messages, enabled=payload.prompt_optimization)

        return PlaygroundCompareResponse(
            execution_mode="live",
            fixed=PlaygroundSideResult(
                model=fixed_resp.model,
                provider=fixed_resp.provider,
                response_text=fixed_resp.response.content,
                input_tokens=fixed_resp.usage.input_tokens,
                output_tokens=fixed_resp.usage.output_tokens,
                total_tokens=fixed_resp.usage.total_tokens,
                cost=fixed_resp.cost.estimated_cost,
                baseline_cost=fixed_resp.cost.baseline_cost,
                savings=fixed_resp.cost.savings,
                savings_percentage=fixed_resp.cost.savings_percentage,
                latency_ms=fixed_lat,
                cache_hit=fixed_resp.optimization.cache_hit,
                prompt_optimized=fixed_resp.optimization.prompt_optimized,
                tokens_saved_by_prompt=0,
                complexity_score=complexity.score,
                task_type=complexity.task_type,
                routing_strategy=fixed_resp.optimization.routing_strategy,
                routing_reason=f"Explicit fixed model '{payload.fixed_model}'",
                quality_score=fixed_resp.optimization.quality_score,
                fallback_used=fixed_resp.optimization.fallback_used,
            ),
            optimized=PlaygroundSideResult(
                model=opt_resp.model,
                provider=opt_resp.provider,
                response_text=opt_resp.response.content,
                input_tokens=opt_resp.usage.input_tokens,
                output_tokens=opt_resp.usage.output_tokens,
                total_tokens=opt_resp.usage.total_tokens,
                cost=opt_resp.cost.estimated_cost,
                baseline_cost=opt_resp.cost.baseline_cost,
                savings=opt_resp.cost.savings,
                savings_percentage=opt_resp.cost.savings_percentage,
                latency_ms=opt_lat,
                cache_hit=opt_resp.optimization.cache_hit,
                prompt_optimized=opt_resp.optimization.prompt_optimized,
                tokens_saved_by_prompt=prompt_opt.tokens_saved,
                optimized_prompt_preview=prompt_opt.optimized_messages[-1].content,
                complexity_score=opt_resp.optimization.complexity_score,
                task_type=complexity.task_type,
                routing_strategy=opt_resp.optimization.routing_strategy,
                routing_reason=f"Routed via {opt_resp.optimization.routing_strategy}",
                quality_score=opt_resp.optimization.quality_score,
                fallback_used=opt_resp.optimization.fallback_used,
            ),
        )

    # Simulation Mode: Executes full Cost Guard analyzer, semantic cache lookup,
    # prompt compression, routing decision, and pricing formulas transparently.
    complexity = analyze_complexity(messages)
    raw_in_tokens = estimate_messages_tokens(messages, payload.fixed_model)
    expected_out = min(payload.max_tokens, estimate_expected_output_tokens(complexity.task_type, payload.max_tokens))

    fixed_pricing = get_model_pricing(payload.fixed_model)
    fixed_cost = calculate_cost(
        raw_in_tokens,
        expected_out,
        fixed_pricing.input_price_per_million,
        fixed_pricing.output_price_per_million,
    )
    fixed_baseline = calculate_baseline_cost(raw_in_tokens, expected_out)
    fixed_sav, fixed_sav_pct = calculate_savings(fixed_cost, fixed_baseline)

    # Optimized evaluation
    cache = get_semantic_cache()
    cache_hit = False
    cached_text = None
    if payload.semantic_cache:
        c_res = await cache.lookup(
            application_id=app.id,
            organization_id=app.organization_id,
            messages=messages,
            policy=CachePolicy(enabled=True),
            db=db,
        )
        if c_res.hit and c_res.response_content:
            cache_hit = True
            cached_text = c_res.response_content

    opt_res = optimize_prompt(messages, enabled=payload.prompt_optimization)
    opt_in_tokens = opt_res.optimized_tokens

    router_svc = get_model_router()
    decision = router_svc.route(
        RoutingInput(
            task_type=complexity.task_type,
            complexity_score=complexity.score,
            estimated_input_tokens=opt_in_tokens,
            expected_output_tokens=expected_out,
            quality_requirement=payload.minimum_quality_score,
            requested_model="auto" if payload.intelligent_routing else payload.fixed_model,
            strategy=payload.routing_strategy,
        )
    )

    if cache_hit:
        opt_cost = 0.0
        opt_out_tokens = 0
        opt_lat = 12.4
        opt_text = cached_text or ""
        opt_strategy = "semantic_cache"
        opt_reason = "Served directly from semantic vector cache (zero LLM call)"
        opt_provider = "cache"
    else:
        opt_pricing = get_model_pricing(decision.selected_model)
        opt_out_tokens = expected_out
        opt_cost = calculate_cost(
            opt_in_tokens,
            opt_out_tokens,
            opt_pricing.input_price_per_million,
            opt_pricing.output_price_per_million,
        )
        opt_lat = 310.0 if opt_pricing.tier == "low" else 640.0
        opt_strategy = decision.routing_strategy
        opt_reason = decision.reason
        opt_provider = decision.provider
        opt_text = (
            f"[Simulation Mode — {decision.selected_model} via {decision.provider}]\n"
            f"Prompt analyzed as '{complexity.task_type}' (complexity {complexity.score}/100). "
            f"Saved {opt_res.tokens_saved} prompt tokens via compression and routed with strategy '{opt_strategy}'."
        )

    opt_sav, opt_sav_pct = calculate_savings(opt_cost, fixed_cost if fixed_cost > 0 else fixed_baseline)
    evaluator = QualityEvaluator()
    q_eval = await evaluator.evaluate(
        candidate=opt_text,
        task_type=complexity.task_type,
        threshold=payload.minimum_quality_score,
    )

    fixed_sim_text = (
        f"[Simulation Mode — {payload.fixed_model} baseline]\n"
        f"Direct fixed-model execution consuming {raw_in_tokens} raw input tokens "
        f"without intelligent down-tier routing, compression, or semantic caching."
    )

    return PlaygroundCompareResponse(
        execution_mode="simulate",
        fixed=PlaygroundSideResult(
            model=payload.fixed_model,
            provider=fixed_pricing.provider,
            response_text=fixed_sim_text,
            input_tokens=raw_in_tokens,
            output_tokens=expected_out,
            total_tokens=raw_in_tokens + expected_out,
            cost=fixed_cost,
            baseline_cost=fixed_baseline,
            savings=fixed_sav,
            savings_percentage=fixed_sav_pct,
            latency_ms=1120.0,
            cache_hit=False,
            prompt_optimized=False,
            tokens_saved_by_prompt=0,
            complexity_score=complexity.score,
            task_type=complexity.task_type,
            routing_strategy="explicit",
            routing_reason=f"Fixed baseline model '{payload.fixed_model}'",
            quality_score=0.98,
            fallback_used=False,
        ),
        optimized=PlaygroundSideResult(
            model=decision.selected_model,
            provider=opt_provider,
            response_text=opt_text,
            input_tokens=opt_in_tokens,
            output_tokens=opt_out_tokens,
            total_tokens=opt_in_tokens + opt_out_tokens,
            cost=opt_cost,
            baseline_cost=fixed_cost if fixed_cost > 0 else fixed_baseline,
            savings=opt_sav,
            savings_percentage=opt_sav_pct,
            latency_ms=opt_lat,
            cache_hit=cache_hit,
            prompt_optimized=opt_res.tokens_saved > 0 or len(opt_res.methods_applied) > 0,
            tokens_saved_by_prompt=opt_res.tokens_saved,
            optimized_prompt_preview=opt_res.optimized_messages[-1].content,
            complexity_score=complexity.score,
            task_type=complexity.task_type,
            routing_strategy=opt_strategy,
            routing_reason=opt_reason,
            quality_score=q_eval.score,
            fallback_used=decision.fallback_required,
        ),
    )
