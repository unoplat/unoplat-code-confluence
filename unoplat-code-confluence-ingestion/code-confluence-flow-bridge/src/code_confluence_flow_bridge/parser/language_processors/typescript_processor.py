"""TypeScript language processor."""

from __future__ import annotations

from code_confluence_flow_bridge.engine.programming_language.typescript.language_service import (
    create_typescript_language_service,
)
from code_confluence_flow_bridge.parser.language_processors.language_processor_context import (
    LanguageProcessorContext,
)
from code_confluence_flow_bridge.parser.language_processors.shared import (
    SharedTreeSitterLanguageProcessor,
)


class TypeScriptLanguageProcessor(SharedTreeSitterLanguageProcessor):
    """Language processor for `.ts` TypeScript source files.

    `.tsx` remains out of scope because tree-sitter-language-pack exposes it as a
    separate `tsx` grammar with separate query requirements.
    """

    def __init__(self, context: LanguageProcessorContext) -> None:
        super().__init__(context)
        self.language_service = create_typescript_language_service()
