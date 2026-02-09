"""Pydantic models for AI model configuration API."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ProviderKind(str, Enum):
    """Provider kind enumeration."""

    NATIVE = "native"
    OPENAI_COMPAT = "openai_compat"


class ModelParams(BaseModel):
    """Validated inference parameters stored in the JSONB model_params column."""

    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(None, gt=0)
    request_limit: Optional[int] = Field(None, gt=0, le=1000)


class AiModelConfigBase(BaseModel):
    """Base model with common AI configuration fields."""

    provider_key: str
    model_name: str
    # Optional top-level hint for providers that support a nested provider (e.g., HuggingFace)
    # This is persisted under `extra_config.provider_name` for storage/back-compat
    provider_name: Optional[str] = None
    provider_kind: Optional[ProviderKind] = None
    base_url: Optional[str] = None
    profile_key: Optional[str] = None
    extra_config: Dict[str, Any] = Field(default_factory=dict)
    model_params: Optional[ModelParams] = None


class AiModelConfigIn(AiModelConfigBase):
    """Input model for creating/updating AI configuration."""

    pass


class AiModelConfigOut(AiModelConfigBase):
    """Output model for AI configuration (no secrets)."""

    has_api_key: bool = False
    created_at: datetime
    updated_at: datetime
