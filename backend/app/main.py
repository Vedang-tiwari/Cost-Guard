from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from app.api.routes import (
    analytics,
    applications,
    auth,
    benchmarks,
    budgets,
    chat,
    evaluations,
    health,
    models,
    playground,
    policies,
)
from app.core.config import get_settings
from app.core.exceptions import CostGuardException
from app.core.logging import get_logger, setup_logging
from app.core.metrics import get_prometheus_metrics
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

settings = get_settings()
setup_logging(debug=settings.DEBUG)
logger = get_logger("costguard")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Cost Guard Gateway starting up...", extra={"environment": settings.ENVIRONMENT})
    yield
    logger.info("Cost Guard Gateway shutting down...")


app = FastAPI(
    title="Cost Guard API Gateway",
    description="Intelligent LLM Cost Optimization & Quality Preservation Gateway",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(CostGuardException)
async def costguard_exception_handler(request: Request, exc: CostGuardException) -> JSONResponse:
    logger.warning(f"CostGuardException: {exc.message}", extra={"status_code": exc.status_code, "details": exc.details})
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": exc.__class__.__name__,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


# Include Routers
app.include_router(health.router)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(applications.router, prefix=settings.API_V1_PREFIX)
app.include_router(models.router, prefix=settings.API_V1_PREFIX)
app.include_router(chat.router, prefix=settings.API_V1_PREFIX)
app.include_router(budgets.router, prefix=settings.API_V1_PREFIX)
app.include_router(evaluations.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
app.include_router(policies.router, prefix=settings.API_V1_PREFIX)
app.include_router(benchmarks.router, prefix=settings.API_V1_PREFIX)
app.include_router(playground.router, prefix=settings.API_V1_PREFIX)


@app.get("/metrics", tags=["Observability"])
async def prometheus_metrics() -> Response:
    """Prometheus exposition metrics endpoint for scraper integration."""
    body, content_type = get_prometheus_metrics()
    return Response(content=body, media_type=content_type)


@app.get("/")
async def root():
    return {
        "name": "Cost Guard Gateway",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
    }
