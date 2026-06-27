from __future__ import annotations

from pydantic import BaseModel


class ModelConfigResponse(BaseModel):
    """Subset of Query Engine's model config response used by the CLI."""

    provider_key: str
    model_name: str
    has_api_key: bool = False
