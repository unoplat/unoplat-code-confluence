# Standard Library
from abc import ABC, abstractmethod

# First Party
from unoplat_code_confluence.configuration.settings import ProgrammingLanguageMetadata
from unoplat_code_confluence.data_models.chapi_forge.unoplat_codebase import UnoplatCodebase


class CodebaseParserStrategy(ABC):
    @abstractmethod
    def parse_codebase(self, codebase_name: str, json_data: dict, local_workspace_path: str, programming_language_metadata: ProgrammingLanguageMetadata) -> UnoplatCodebase:
        """Parse codebase based on language specific implementation"""
        pass 