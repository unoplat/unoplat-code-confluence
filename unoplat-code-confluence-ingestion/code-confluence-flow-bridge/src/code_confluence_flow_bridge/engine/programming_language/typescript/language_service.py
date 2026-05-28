"""TypeScript language-service factory."""

from __future__ import annotations

from code_confluence_flow_bridge.engine.programming_language.common.language_service import (
    LanguageServiceSpec,
)
from code_confluence_flow_bridge.engine.programming_language.typescript.typescript_source_context import (
    TypeScriptImportAliasStrategy,
)


def create_typescript_language_service() -> LanguageServiceSpec:
    """Factory Method for TypeScript parsing/detection collaborators."""
    return LanguageServiceSpec(
        language_name="typescript",
        alias_strategy=TypeScriptImportAliasStrategy(),
        supported_extensions=frozenset({".ts"}),
        ignored_file_names=frozenset({".d.ts"}),
    )
