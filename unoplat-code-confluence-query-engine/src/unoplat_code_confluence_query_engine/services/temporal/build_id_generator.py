"""Build ID generator for Temporal Worker Versioning.

This module generates deterministic Build IDs from AI model configuration
to enable safe worker deployments using Temporal's Worker Versioning feature.
"""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from unoplat_code_confluence_query_engine.db.postgres.ai_model_config import (
        AiModelConfig,
    )

# Deployment name used for Worker Versioning
DEPLOYMENT_NAME = "llm_agents"


def generate_build_id(config: AiModelConfig) -> str:
    """Generate deterministic Build ID from AI model configuration.

    The Build ID is derived from provider, model, and configuration
    to ensure workers with different model configurations get unique versions.

    Args:
        config: AI model configuration from database

    Returns:
        Build ID in format: {deployment_name}.{hash}
    """
    # Build deterministic string from config fields that affect agent behavior
    config_str = f"{config.provider_key}:{config.model_name}:{config.provider_kind}"

    # Include extra_config if present (sorted for determinism)
    if config.extra_config:
        sorted_items = sorted(config.extra_config.items())
        config_str += f":{sorted_items}"

    # Generate SHA256 hash and take first 12 characters
    hash_digest = hashlib.sha256(config_str.encode()).hexdigest()[:12]

    return f"{DEPLOYMENT_NAME}.{hash_digest}"
