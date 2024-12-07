# Standard Library
from abc import ABC, abstractmethod

# First Party
from unoplat_code_confluence.configuration.settings import ProgrammingLanguageMetadata
from unoplat_code_confluence.data_models.chapi_forge.unoplat_package_manager_metadata import \
    UnoplatPackageManagerMetadata


class PackageManagerStrategy(ABC):
    @abstractmethod
    def process_metadata(self, local_workspace_path: str, metadata: ProgrammingLanguageMetadata) -> UnoplatPackageManagerMetadata:
        """Process package manager specific metadata"""
        pass



