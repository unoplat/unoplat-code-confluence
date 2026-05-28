"""Python language-service factory."""

from __future__ import annotations

from code_confluence_flow_bridge.engine.programming_language.common.language_service import (
    LanguageServiceSpec,
)
from code_confluence_flow_bridge.engine.programming_language.python.python_source_context import (
    PythonImportAliasStrategy,
)


def create_python_language_service() -> LanguageServiceSpec:
    """Factory Method for Python parsing/detection collaborators."""
    return LanguageServiceSpec(
        language_name="python",
        alias_strategy=PythonImportAliasStrategy(),
        supported_extensions=frozenset({".py"}),
        ignored_file_names=frozenset({"__init__.py"}),
    )
