# Standard Library
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package import (
    UnoplatPackage,
)

# First Party
from src.code_confluence_flow_bridge.models.configuration.settings import (
    ProgrammingLanguageMetadata,
)

from abc import ABC, abstractmethod
from typing import List


class CodebaseParserStrategy(ABC):
    @abstractmethod
    def parse_codebase(self, codebase_name: str, json_data: dict, local_workspace_path: str, source_directory: str, programming_language_metadata: ProgrammingLanguageMetadata) -> List[UnoplatPackage]:
        """Parse codebase based on language specific implementation"""
        pass