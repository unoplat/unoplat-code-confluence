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


def compute_credential_hash(credential: str) -> str:
    """Compute deterministic SHA256 hash of credential for build ID.

    This creates a consistent hash from the plaintext credential that can be
    included in the build ID. We cannot use the encrypted credential directly
    because Fernet encryption includes a random IV, producing different
    ciphertext for the same plaintext.

    Args:
        credential: Plaintext credential value

    Returns:
        First 12 characters of SHA256 hash
    """
    return hashlib.sha256(credential.encode()).hexdigest()[:12]


def generate_build_id(
    config: AiModelConfig,
    credential_hash: str | None,
) -> str:
    """Generate deterministic Build ID from AI model configuration.

    The Build ID is derived from provider, model, configuration,
    and credential hash to ensure workers with different configurations
    or credentials get unique versions.

    Args:
        config: AI model configuration from database
        credential_hash: Hash of the credential (from compute_credential_hash),
            or None if no credential is stored

    Returns:
        Build ID in format: {deployment_name}.{hash}
    """
    # Build deterministic string from config fields that affect agent behavior
    config_str = f"{config.provider_key}:{config.model_name}:{config.provider_kind}"

    # Include extra_config if present (sorted for determinism)
    if config.extra_config:
        sorted_items = sorted(config.extra_config.items())
        config_str += f":{sorted_items}"

    # Include credential hash if provided
    if credential_hash:
        config_str += f":cred:{credential_hash}"

    # Generate SHA256 hash and take first 12 characters
    hash_digest = hashlib.sha256(config_str.encode()).hexdigest()[:12]

    return f"{DEPLOYMENT_NAME}.{hash_digest}"
