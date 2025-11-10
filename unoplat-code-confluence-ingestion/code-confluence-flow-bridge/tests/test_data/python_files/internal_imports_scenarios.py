# Standard Library
from typing import List, Optional


class ComplexProcessor:
    """A class that demonstrates internal imports in various locations."""

    def __init__(self):
        # Internal import in method
        from src.code_confluence_flow_bridge.models.chapi.chapi_node import ChapiNode

        self.node = ChapiNode(NodeName="test")

    def process_data(self) -> None:
        # Multiple internal imports in method body
        from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_import import (
            UnoplatImport as Import,
        )
        from src.code_confluence_flow_bridge.models.code import Function

        # Use the imported types
        self.imports: List[Import] = []
        self.functions: List[Function] = []

    def analyze_code(self) -> Optional[str]:
        # Conditional import
        if not hasattr(self, "_analyzer"):
            from src.code_confluence_flow_bridge.analyzer.code_analyzer import (
                CodeAnalyzer,
            )

            self._analyzer = CodeAnalyzer()
        return self._analyzer.analyze()


def standalone_function():
    # Import in a function
    from src.code_confluence_flow_bridge.utils.helpers import format_output

    return format_output("test")


# Import in a try-except block
try:
    from src.code_confluence_flow_bridge.experimental.feature import ExperimentalFeature

    FEATURE_ENABLED = True
except ImportError:
    FEATURE_ENABLED = False

# Import with multiple items on same line
