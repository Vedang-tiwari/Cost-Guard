from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"] = Field(..., description="Role of the message author")
    content: str = Field(..., min_length=1, description="Content of the message")


class OptimizationConfig(BaseModel):
    enabled: bool = Field(default=False, description="Enable cost guard optimizations")
    semantic_cache: bool = Field(default=False, description="Enable semantic caching")
    prompt_optimization: bool = Field(default=False, description="Enable prompt optimization")
    intelligent_routing: bool = Field(default=False, description="Enable intelligent model routing")


class QualityConfig(BaseModel):
    minimum_score: float = Field(default=0.90, ge=0.0, le=1.0, description="Minimum acceptable quality score")


class ChatCompletionRequest(BaseModel):
    model: str = Field(default="gpt-4o", description="Target model name or 'auto' for intelligent routing")
    messages: list[ChatMessage] = Field(..., min_length=1, description="List of chat messages")
    optimization: OptimizationConfig | None = Field(default=None, description="Optimization controls")
    quality: QualityConfig | None = Field(default=None, description="Quality preservation constraints")
    max_tokens: int | None = Field(default=None, gt=0, description="Maximum tokens to generate")
    temperature: float | None = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    stream: bool = Field(default=False, description="Whether to stream the response (future phase)")
