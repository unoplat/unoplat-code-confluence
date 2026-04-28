"""Pydantic models for AI model configuration API."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Literal, Optional, Union, cast

from pydantic import BaseModel, ConfigDict, Field, model_validator

ThinkingLevelIn = Union[bool, Literal["minimal", "low", "medium", "high", "xhigh"]]
"""Unified thinking/reasoning level accepted by pydantic-ai ``ModelSettings``.

Pydantic-ai translates this per provider. On Bedrock it auto-routes to the
Anthropic (``thinking.budget_tokens``), OpenAI (``reasoning_effort``), or
Qwen (``reasoning_config``) request shape based on the model ID prefix, and
silently ignores the value on non-reasoning models via
``profile.supports_thinking``.
"""


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
    thinking: Optional[ThinkingLevelIn] = None


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

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    @classmethod
    def _fold_unknown_top_level_fields_into_extra_config(cls, data: object) -> object:
        """Preserve provider-specific top-level fields by moving them to extra_config."""
        if not isinstance(data, dict):
            return data

        payload = cast(dict[str, object], data)
        normalized_payload: dict[str, object] = dict(payload)
        raw_extra_config = normalized_payload.get("extra_config")
        if isinstance(raw_extra_config, dict):
            typed_extra_config = cast(dict[object, object], raw_extra_config)
            extra_config = {
                str(key): value for key, value in typed_extra_config.items()
            }
        else:
            extra_config = {}

        known_top_level_keys = set(cls.model_fields.keys())
        extra_keys = [
            key for key in normalized_payload if key not in known_top_level_keys
        ]
        for key in extra_keys:
            extra_config[key] = normalized_payload.pop(key)

        normalized_payload["extra_config"] = extra_config
        return normalized_payload


class AiModelConfigOut(AiModelConfigBase):
    """Output model for AI configuration (no secrets)."""

    has_api_key: bool = False
    created_at: datetime
    updated_at: datetime
