from app.api.dependencies import verify_application_api_key
from app.core.exceptions import CostGuardException
from app.core.logging import get_logger
from app.database.models.application import Application
from app.database.session import get_db
from app.gateway.optimization_pipeline import get_optimization_pipeline
from app.schemas.request import ChatCompletionRequest
from app.schemas.response import ChatCompletionResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat Completions"])


@router.post("/completions", response_model=ChatCompletionResponse, status_code=status.HTTP_200_OK)
async def create_chat_completion(
    request: ChatCompletionRequest,
    app: Application = Depends(verify_application_api_key),
    db: AsyncSession = Depends(get_db),
) -> ChatCompletionResponse:
    """
    Executes a chat completion through the Cost Guard Gateway with intelligent optimization:
    - Complexity analysis and automatic model selection
    - Semantic caching for duplicate and similar requests
    - Safe prompt compression and token optimization
    - Exact cost accounting and baseline savings telemetry
    """
    pipeline = get_optimization_pipeline()
    try:
        return await pipeline.execute(request=request, application=app, db=db)
    except CostGuardException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected gateway error: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal gateway error",
        )
