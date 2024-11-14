from abc import ABC, abstractmethod
from unoplat_code_confluence.data_models.chapi_unoplat_codebase import UnoplatCodebase
from unoplat_code_confluence.configuration.external_config import ProgrammingLanguageMetadata

class CodebaseParserStrategy(ABC):
    @abstractmethod
    def parse_codebase(self, json_data: dict, local_workspace_path: str, programming_language_metadata: ProgrammingLanguageMetadata) -> UnoplatCodebase:
        """Parse codebase based on language specific implementation"""
        pass 