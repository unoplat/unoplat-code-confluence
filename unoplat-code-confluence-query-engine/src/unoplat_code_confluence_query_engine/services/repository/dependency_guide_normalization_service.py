"""Normalize dependency-guide targets using explicit UI family registry rules."""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import re

from loguru import logger

from unoplat_code_confluence_query_engine.models.runtime.dependency_guide_target import (
    DependencyGuideTarget,
    UIDependencyFamilyRegistry,
    UIDependencyFamilyRule,
)

_MATCH_TYPE_PRIORITY: dict[str, int] = {
    "exact": 0,
    "prefix": 1,
    "regex": 2,
}
_SUPPORTED_FAMILY_KIND = "ui_component_library"
_REGISTRY_FILE_NAME = "ui_component_dependency_families.json"


def _registry_file_path() -> Path:
    """Resolve the absolute path to the UI component dependency families JSON registry."""
    package_root = Path(__file__).resolve().parents[2]
    return package_root / "config" / _REGISTRY_FILE_NAME


@lru_cache(maxsize=1)
def _load_ui_dependency_family_registry() -> UIDependencyFamilyRegistry:
    """Load and validate the UI dependency family registry from disk (cached after first call)."""
    registry_path = _registry_file_path()
    with registry_path.open("r", encoding="utf-8") as registry_file:
        raw_registry = json.load(registry_file)
    registry = UIDependencyFamilyRegistry.model_validate(raw_registry)
    logger.info(
        "Loaded UI dependency family registry from {} with {} families",
        registry_path,
        len(registry.families),
    )
    return registry


def _normalize_value(value: str) -> str:
    """Strip whitespace and lowercase a string for case-insensitive comparison."""
    return value.strip().lower()


def _is_rule_applicable(
    rule: UIDependencyFamilyRule,
    programming_language: str,
    package_manager: str,
) -> bool:
    """Check if a family rule applies for the given language and package manager."""
    if not rule.enabled:
        return False
    if rule.kind != _SUPPORTED_FAMILY_KIND:
        return False
    normalized_language = _normalize_value(programming_language)
    normalized_package_manager = _normalize_value(package_manager)
    if rule.languages and normalized_language not in {
        _normalize_value(value) for value in rule.languages
    }:
        return False
    if rule.package_managers and normalized_package_manager not in {
        _normalize_value(value) for value in rule.package_managers
    }:
        return False
    return True


def _matches_rule(rule: UIDependencyFamilyRule, dependency_name: str) -> bool:
    """Test whether a dependency name satisfies the rule's match criterion (exact, prefix, or regex)."""
    match_type = rule.match.type
    match_value = rule.match.value
    if match_type == "exact":
        return dependency_name == match_value
    if match_type == "prefix":
        return dependency_name.startswith(match_value)
    if match_type == "regex":
        return re.search(match_value, dependency_name) is not None
    raise ValueError(f"Unsupported UI dependency family match type: {match_type}")


def _get_rule_priority(rule: UIDependencyFamilyRule) -> int:
    """Return sort priority for a rule: exact (0) > prefix (1) > regex (2)."""
    try:
        return _MATCH_TYPE_PRIORITY[rule.match.type]
    except KeyError as error:
        raise ValueError(
            f"Unsupported UI dependency family match type: {rule.match.type}"
        ) from error


def _get_applicable_rules(
    programming_language: str,
    package_manager: str,
) -> list[UIDependencyFamilyRule]:
    """Filter registry rules by language/package-manager and return sorted by match-type priority."""
    registry = _load_ui_dependency_family_registry()
    applicable_rules = [
        rule
        for rule in registry.families
        if _is_rule_applicable(rule, programming_language, package_manager)
    ]
    return sorted(applicable_rules, key=_get_rule_priority)


def _find_matching_rule(
    dependency_name: str,
    rules: list[UIDependencyFamilyRule],
) -> UIDependencyFamilyRule | None:
    """Return the first rule that matches the dependency name, or None."""
    for rule in rules:
        if _matches_rule(rule, dependency_name):
            return rule
    return None


def _build_grouped_target(
    rule: UIDependencyFamilyRule,
    source_packages: list[str],
) -> DependencyGuideTarget:
    """Create a grouped DependencyGuideTarget from a family rule and its matched packages."""
    return DependencyGuideTarget(
        name=rule.display_name,
        source_packages=sorted(source_packages, key=str.lower),
    )


def _build_single_dependency_target(dependency_name: str) -> DependencyGuideTarget:
    """Create a pass-through DependencyGuideTarget for a dependency that matched no family rule."""
    return DependencyGuideTarget(
        name=dependency_name, source_packages=[dependency_name]
    )


def normalize_dependency_guide_targets(
    dependency_names: list[str],
    programming_language: str,
    package_manager: str,
) -> list[DependencyGuideTarget]:
    """Normalize raw dependency names into canonical documentation targets.

    Only dependencies that match explicit UI component family rules from the
    external JSON registry are collapsed. All other dependencies remain one
    package per target.
    """
    applicable_rules = _get_applicable_rules(programming_language, package_manager)
    grouped_packages_by_rule_id: dict[str, list[str]] = {}
    grouped_rule_by_id: dict[str, UIDependencyFamilyRule] = {}
    passthrough_targets: list[DependencyGuideTarget] = []
    unique_dependency_names = sorted(set(dependency_names), key=str.lower)

    for dependency_name in unique_dependency_names:
        matching_rule = _find_matching_rule(dependency_name, applicable_rules)
        if matching_rule is None:
            passthrough_targets.append(_build_single_dependency_target(dependency_name))
            continue
        grouped_rule_by_id[matching_rule.id] = matching_rule
        grouped_packages = grouped_packages_by_rule_id.setdefault(matching_rule.id, [])
        grouped_packages.append(dependency_name)

    grouped_targets = [
        _build_grouped_target(
            rule=grouped_rule_by_id[rule_id],
            source_packages=source_packages,
        )
        for rule_id, source_packages in grouped_packages_by_rule_id.items()
    ]
    normalized_targets = sorted(
        [*passthrough_targets, *grouped_targets],
        key=lambda target: target.name.lower(),
    )
    logger.info(
        "Normalized {} raw dependencies into {} dependency-guide targets for language={} package_manager={}",
        len(unique_dependency_names),
        len(normalized_targets),
        programming_language,
        package_manager,
    )
    return normalized_targets
