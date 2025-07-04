# Standard Library
# First Party
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models import (
    UnoplatPackageManagerMetadata,
)
from src.code_confluence_flow_bridge.models.configuration.settings import (
    ProgrammingLanguageMetadata,
)

from abc import ABC, abstractmethod


class PackageManagerStrategy(ABC):
    @abstractmethod
    def process_metadata(self, local_workspace_path: str, metadata: ProgrammingLanguageMetadata) -> UnoplatPackageManagerMetadata:
        """
        Process package manager specific metadata

        Args:
            local_workspace_path: Path to the local workspace
            metadata: Programming language metadata from config

        Returns:
            UnoplatPackageManagerMetadata: Processed package manager metadata
        """
        pass
