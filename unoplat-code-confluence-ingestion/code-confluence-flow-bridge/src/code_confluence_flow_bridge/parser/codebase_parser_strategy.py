# Standard Library
from abc import ABC, abstractmethod

from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_codebase import UnoplatCodebase

# First Party
from src.code_confluence_flow_bridge.models.configuration.settings import ProgrammingLanguageMetadata


class CodebaseParserStrategy(ABC):
    @abstractmethod
    def parse_codebase(self, codebase_name: str, json_data: dict, local_workspace_path: str, programming_language_metadata: ProgrammingLanguageMetadata) -> UnoplatCodebase:
        """Parse codebase based on language specific implementation"""
        pass
