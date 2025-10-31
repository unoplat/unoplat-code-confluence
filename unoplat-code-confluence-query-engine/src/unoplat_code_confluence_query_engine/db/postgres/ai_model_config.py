"""AI model provider configuration SQLModel."""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import JSON
from unoplat_code_confluence_commons.base_models.sql_base import SQLBase


class AiModelConfig(SQLBase):
    """AI model provider configuration. Single active configuration only."""

    __tablename__ = "ai_model_config"

    # Single record approach - always id=1 for the active config
    id: Mapped[int] = mapped_column(default=1, primary_key=True)
    provider_key: Mapped[str] = mapped_column(comment="Provider identifier")
    model_name: Mapped[str] = mapped_column(comment="Model name/identifier")
    provider_kind: Mapped[str] = mapped_column(comment="native | openai_compat")
    base_url: Mapped[Optional[str]] = mapped_column(
        default=None, comment="Custom endpoint URL"
    )
    profile_key: Mapped[Optional[str]] = mapped_column(
        default=None, comment="Pydantic AI profile"
    )
    extra_config: Mapped[Dict[str, Any]] = mapped_column(
        JSON, default=dict, comment="Provider-specific configuration"
    )
    temperature: Mapped[Optional[float]] = mapped_column(default=None)
    top_p: Mapped[Optional[float]] = mapped_column(default=None)
    max_tokens: Mapped[Optional[int]] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now())