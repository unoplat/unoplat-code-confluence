"""Language service factory/spec abstractions for parser pipelines."""

from __future__ import annotations

from dataclasses import dataclass

from code_confluence_flow_bridge.engine.programming_language.common.source_context import (
    ImportAliasStrategy,
    LanguagePackImportExtractor,
    SourceContextBuilder,
)


@dataclass(frozen=True)
class LanguageServiceSpec:
    """Abstract-factory product bundle for one programming language."""

    language_name: str
    alias_strategy: ImportAliasStrategy
    supported_extensions: frozenset[str]
    ignored_file_names: frozenset[str]

    def create_import_extractor(self) -> LanguagePackImportExtractor:
        """Factory Method for language-pack-backed import extraction."""
        return LanguagePackImportExtractor(language_name=self.language_name)

    def create_source_context_builder(self) -> SourceContextBuilder:
        """Factory Method for the source-context Template Method builder."""
        return SourceContextBuilder(
            language_name=self.language_name,
            import_extractor=self.create_import_extractor(),
            alias_strategy=self.alias_strategy,
        )
