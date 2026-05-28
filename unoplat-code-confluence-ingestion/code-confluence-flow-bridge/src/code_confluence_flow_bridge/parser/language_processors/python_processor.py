"""Python language processor."""

from __future__ import annotations

from code_confluence_flow_bridge.engine.programming_language.python.language_service import (
    create_python_language_service,
)
from code_confluence_flow_bridge.parser.language_processors.language_processor_context import (
    LanguageProcessorContext,
)
from code_confluence_flow_bridge.parser.language_processors.shared import (
    SharedTreeSitterLanguageProcessor,
)


class PythonLanguageProcessor(SharedTreeSitterLanguageProcessor):
    """Language processor for Python source files."""

    def __init__(self, context: LanguageProcessorContext) -> None:
        super().__init__(context)
        self.language_service = create_python_language_service()
