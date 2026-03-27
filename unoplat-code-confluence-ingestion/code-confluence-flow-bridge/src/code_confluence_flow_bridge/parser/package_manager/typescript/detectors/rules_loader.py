from __future__ import annotations

from pathlib import Path

from aiofile import async_open
from pydantic import ValidationError
import yaml

from src.code_confluence_flow_bridge.models.detection.shared.rules import (
    LanguageRules,
    ManagerRule,
    Signature,
)
from src.code_confluence_flow_bridge.models.detection.typescript.rules import (
    RuleManagerConfig,
    RulesFileConfig,
    RuleSignatureConfig,
)


def _build_signature(signature_config: str | RuleSignatureConfig) -> Signature:
    if isinstance(signature_config, str):
        return Signature(file=signature_config)
    return Signature(
        file=signature_config.file,
        glob=signature_config.glob,
        contains=signature_config.contains,
        contains_absence=signature_config.contains_absence,
    )


def _build_manager_rule(manager_config: RuleManagerConfig) -> ManagerRule:
    return ManagerRule(
        manager=manager_config.manager,
        weight=manager_config.weight,
        signatures=[
            _build_signature(signature_config)
            for signature_config in manager_config.signatures
        ],
        workspace_field=manager_config.workspace_field,
    )


async def load_typescript_language_rules(rules_path: str) -> LanguageRules:
    """Load and validate TypeScript package-manager rules from YAML."""
    rules_file = Path(rules_path)
    if not rules_file.exists():
        raise FileNotFoundError(f"Rules file not found: {rules_path}")

    async with async_open(rules_file, "r") as handle:
        content = await handle.read()

    loaded_rules = yaml.safe_load(content)
    if not isinstance(loaded_rules, dict):
        raise ValueError(f"Invalid rules file format: {rules_path}")

    try:
        rules_config = RulesFileConfig.model_validate(loaded_rules)
    except ValidationError as error:
        raise ValueError(f"Invalid rules file schema: {rules_path}\n{error}") from error

    return LanguageRules(
        ignores=rules_config.typescript.ignores,
        managers=[
            _build_manager_rule(manager_config)
            for manager_config in rules_config.typescript.managers
        ],
    )
