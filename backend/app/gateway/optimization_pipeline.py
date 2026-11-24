import time
import uuid

from app.analyzer.complexity import analyze_complexity
from app.analyzer.token_estimator import (
    estimate_expected_output_tokens,
    estimate_messages_tokens,
)
from app.budgets.budget_manager import budget_manager
from app.cache.cache_policy import CachePolicy, is_request_cacheable
from app.cache.semantic_cache import get_semantic_cache
from app.core.exceptions import CostGuardException
from app.core.logging import get_logger
from app.core.metrics import record_request_metrics
from app.cost.calculator import (
    calculate_baseline_cost,
    calculate_cost,
    calculate_savings,
)
from app.cost.pricing_registry import get_model_pricing, pricing_registry
from app.database.models.application import Application
from app.database.models.request_log import RequestLog
from app.evaluation.evaluator import QualityEvaluator
from app.optimization.prompt_optimizer import optimize_prompt
from app.providers.factory import get_provider_factory
from app.router.fallback import get_fallback_model
from app.router.model_router import RoutingInput, get_model_router
from app.schemas.request import ChatCompletionRequest
from app.schemas.response import (
    AssistantMessage,
    ChatCompletionResponse,
    CostInfo,
    OptimizationInfo,
    UsageInfo,
)
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)


class OptimizationPipeline:
    """
    Orchestrates the Cost Guard intelligent request lifecycle:
    Analysis -> Token Estimation -> Budget Verification -> Semantic Cache ->
    Prompt Optimization -> Model Routing -> Provider Execution -> Quality Gate &
    Fallback -> Cost Calculation & Observability.
    """

    def __init__(self):
        self.router = get_model_router()
        self.cache = get_semantic_cache()
        self.provider_factory = get_provider_factory()
        self.evaluator = QualityEvaluator()

    async def execute(
        self,
        request: ChatCompletionRequest,
        application: Application,
        db: AsyncSession,
    ) -> ChatCompletionResponse:
        request_id = f"req_{uuid.uuid4().hex[:12]}"
        start_time = time.perf_counter()

        opt_config = request.optimization

        # -------------------------------------------------------------
        # Step 1: Request Analysis & Complexity Scoring
        # -------------------------------------------------------------
        complexity_analysis = analyze_complexity(request.messages)
        complexity_score = complexity_analysis.score
        task_type = complexity_analysis.task_type

        # -------------------------------------------------------------
        # Step 2: Token Estimation
        # -------------------------------------------------------------
        estimated_input_tokens = estimate_messages_tokens(request.messages, request.model)
        expected_output_tokens = estimate_expected_output_tokens(task_type, request.max_tokens)

        # Baseline cost (what it would cost on standard reference gpt-4o)
        baseline_cost = calculate_baseline_cost(estimated_input_tokens, expected_output_tokens)

        # -------------------------------------------------------------
        # Step 3: Semantic Cache Check
        # -------------------------------------------------------------
        cache_policy = CachePolicy(
            enabled=opt_config.semantic_cache if opt_config else True
        )
        is_cacheable, _ = is_request_cacheable(request, cache_policy)

        if is_cacheable:
            cache_result = await self.cache.lookup(
                application_id=application.id,
                organization_id=application.organization_id,
                messages=request.messages,
                policy=cache_policy,
                db=db,
            )
            if cache_result.hit and cache_result.response_content:
                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                savings = baseline_cost
                savings_pct = 100.0

                # Log cache hit
                log_entry = RequestLog(
                    request_id=request_id,
                    application_id=application.id,
                    organization_id=application.organization_id,
                    provider="cache",
                    model=cache_result.model or request.model,
                    input_tokens=estimated_input_tokens,
                    output_tokens=0,
                    estimated_cost=0.0,
                    actual_cost=0.0,
                    latency_ms=latency_ms,
                    cache_hit=True,
                    complexity_score=complexity_score,
                    routing_strategy="cache_hit",
                    status="success",
                )
                db.add(log_entry)
                await db.commit()

                # Record Prometheus metrics for cache hit
                record_request_metrics(
                    provider="cache",
                    model=cache_result.model or request.model,
                    status_code="200",
                    cache_hit=True,
                    latency_ms=latency_ms,
                    actual_cost=0.0,
                    baseline_cost=baseline_cost,
                    input_tokens=estimated_input_tokens,
                    output_tokens=0,
                )

                return ChatCompletionResponse(
                    request_id=request_id,
                    model=cache_result.model or request.model,
                    provider="cache",
                    response=AssistantMessage(content=cache_result.response_content),
                    usage=UsageInfo(
                        input_tokens=estimated_input_tokens,
                        output_tokens=0,
                        total_tokens=estimated_input_tokens,
                    ),
                    cost=CostInfo(
                        estimated_cost=0.0,
                        baseline_cost=baseline_cost,
                        savings=savings,
                        savings_percentage=savings_pct,
                    ),
                    optimization=OptimizationInfo(
                        cache_hit=True,
                        routing_strategy="semantic_cache",
                        complexity_score=complexity_score,
                        prompt_optimized=False,
                        fallback_used=False,
                    ),
                )

        # -------------------------------------------------------------
        # Step 4: Prompt Optimization
        # -------------------------------------------------------------
        prompt_opt_enabled = opt_config.prompt_optimization if opt_config else True
        opt_result = optimize_prompt(request.messages, enabled=prompt_opt_enabled)
        working_messages = opt_result.optimized_messages
        is_prompt_optimized = len(opt_result.methods_applied) > 0 or opt_result.tokens_saved > 0
        current_input_tokens = opt_result.optimized_tokens

        # -------------------------------------------------------------
        # Step 5: Model Routing
        # -------------------------------------------------------------
        routing_enabled = opt_config.intelligent_routing if opt_config else (request.model == "auto")
        routing_input = RoutingInput(
            task_type=task_type,
            complexity_score=complexity_score,
            estimated_input_tokens=current_input_tokens,
            expected_output_tokens=expected_output_tokens,
            quality_requirement=request.quality.minimum_score if request.quality else 0.90,
            requested_model=request.model if not routing_enabled else "auto",
            strategy="complexity_based",
        )
        routing_decision = self.router.route(routing_input)
        selected_model = routing_decision.selected_model
        selected_provider = routing_decision.provider

        # -------------------------------------------------------------
        # Step 5b: Budget Check
        # -------------------------------------------------------------
        await budget_manager.check_budget(
            session=db,
            organization_id=application.organization_id,
            application_id=application.id,
            estimated_cost=routing_decision.estimated_cost,
        )

        # -------------------------------------------------------------
        # Step 6: Provider Execution
        # -------------------------------------------------------------
        execution_request = ChatCompletionRequest(
            model=selected_model,
            messages=working_messages,
            max_tokens=request.max_tokens or expected_output_tokens,
            temperature=request.temperature,
            stream=False,
        )

        provider = self.provider_factory.get_provider(selected_provider)
        try:
            provider_response = await provider.generate(execution_request)
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            request_status = "success"
            error_message = None
        except CostGuardException as e:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            request_status = "error"
            error_message = e.message

            log_entry = RequestLog(
                request_id=request_id,
                application_id=application.id,
                organization_id=application.organization_id,
                provider=selected_provider,
                model=selected_model,
                input_tokens=current_input_tokens,
                output_tokens=0,
                estimated_cost=0.0,
                actual_cost=0.0,
                latency_ms=latency_ms,
                cache_hit=False,
                complexity_score=complexity_score,
                routing_strategy=routing_decision.routing_strategy,
                status=request_status,
                error_message=error_message,
            )
            db.add(log_entry)
            await db.commit()
            raise e

        # -------------------------------------------------------------
        # Step 6b: Quality Gate & Threshold-Based Cascade Fallback
        # -------------------------------------------------------------
        quality_score: float | None = None
        fallback_used = False
        fallback_from: str | None = None

        if request.quality and (request.quality.eval_enabled or request.quality.minimum_score > 0):
            eval_res = await self.evaluator.evaluate(
                candidate=provider_response.content,
                task_type=task_type,
                threshold=request.quality.minimum_score,
            )
            quality_score = eval_res.score

            if request.quality.eval_enabled and not eval_res.passed:
                fallback_target = get_fallback_model(selected_model)
                if fallback_target != selected_model:
                    logger.info(
                        f"Quality gate failed (score={quality_score:.2f} < {request.quality.minimum_score}). "
                        f"Triggering fallback from {selected_model} to {fallback_target}."
                    )
                    fallback_entry = pricing_registry.get(fallback_target)
                    fb_provider_name = fallback_entry.provider if fallback_entry else "openai"
                    fb_provider = self.provider_factory.get_provider(fb_provider_name)

                    try:
                        fb_execution_request = ChatCompletionRequest(
                            model=fallback_target,
                            messages=working_messages,
                            max_tokens=request.max_tokens or expected_output_tokens,
                            temperature=request.temperature,
                            stream=False,
                        )
                        fb_response = await fb_provider.generate(fb_execution_request)
                        fallback_from = selected_model
                        selected_model = fallback_target
                        selected_provider = fb_provider_name
                        provider_response = fb_response
                        fallback_used = True

                        # Re-evaluate with fallback response
                        re_eval = await self.evaluator.evaluate(
                            candidate=provider_response.content,
                            task_type=task_type,
                            threshold=request.quality.minimum_score,
                        )
                        quality_score = re_eval.score
                    except Exception as fb_err:
                        logger.warning(f"Fallback invocation to {fallback_target} failed: {fb_err}")

        # -------------------------------------------------------------
        # Step 7: Accurate Cost Calculation & Spend Tracking
        # -------------------------------------------------------------
        in_tokens = provider_response.usage.input_tokens or current_input_tokens
        out_tokens = provider_response.usage.output_tokens or 0
        total_tokens = in_tokens + out_tokens

        pricing = get_model_pricing(selected_model)
        actual_cost = calculate_cost(
            input_tokens=in_tokens,
            output_tokens=out_tokens,
            input_price_per_million=pricing.input_price_per_million,
            output_price_per_million=pricing.output_price_per_million,
        )

        actual_baseline = calculate_baseline_cost(in_tokens, out_tokens)
        savings, savings_pct = calculate_savings(actual_cost, actual_baseline)

        # Record actual spend on budget
        await budget_manager.record_spend(
            session=db,
            organization_id=application.organization_id,
            application_id=application.id,
            actual_cost=actual_cost,
        )

        # -------------------------------------------------------------
        # Step 8: Store in Semantic Cache if Cacheable
        # -------------------------------------------------------------
        if is_cacheable and request_status == "success":
            await self.cache.store(
                application_id=application.id,
                organization_id=application.organization_id,
                messages=request.messages,
                response_content=provider_response.content,
                model=selected_model,
                policy=cache_policy,
                db=db,
                tokens_saved=total_tokens,
            )

        # -------------------------------------------------------------
        # Step 9: Observability, Metrics & Persistence
        # -------------------------------------------------------------
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        log_entry = RequestLog(
            request_id=request_id,
            application_id=application.id,
            organization_id=application.organization_id,
            provider=selected_provider,
            model=selected_model,
            input_tokens=in_tokens,
            output_tokens=out_tokens,
            estimated_cost=routing_decision.estimated_cost,
            actual_cost=actual_cost,
            latency_ms=latency_ms,
            cache_hit=False,
            complexity_score=complexity_score,
            routing_strategy=routing_decision.routing_strategy,
            quality_score=quality_score,
            fallback_used=fallback_used,
            status="success",
        )
        db.add(log_entry)
        await db.commit()

        # Prometheus metrics recording
        record_request_metrics(
            provider=selected_provider,
            model=selected_model,
            status_code="200",
            cache_hit=False,
            latency_ms=latency_ms,
            actual_cost=actual_cost,
            baseline_cost=actual_baseline,
            input_tokens=in_tokens,
            output_tokens=out_tokens,
            fallback_used=fallback_used,
            fallback_from=fallback_from,
        )

        return ChatCompletionResponse(
            request_id=request_id,
            model=selected_model,
            provider=selected_provider,
            response=AssistantMessage(content=provider_response.content),
            usage=UsageInfo(
                input_tokens=in_tokens,
                output_tokens=out_tokens,
                total_tokens=total_tokens,
            ),
            cost=CostInfo(
                estimated_cost=actual_cost,
                baseline_cost=actual_baseline,
                savings=savings,
                savings_percentage=savings_pct,
            ),
            optimization=OptimizationInfo(
                cache_hit=False,
                routing_strategy=routing_decision.routing_strategy,
                complexity_score=complexity_score,
                prompt_optimized=is_prompt_optimized,
                fallback_used=fallback_used,
                quality_score=quality_score,
            ),
        )


_pipeline_instance: OptimizationPipeline | None = None


def get_optimization_pipeline() -> OptimizationPipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = OptimizationPipeline()
    return _pipeline_instance
