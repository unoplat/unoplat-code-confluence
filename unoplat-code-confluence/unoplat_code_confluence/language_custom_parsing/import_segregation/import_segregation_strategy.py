
from abc import ABC, abstractmethod
from typing import Dict
from unoplat_code_confluence.data_models.unoplat_import import UnoplatImport
from unoplat_code_confluence.data_models.chapi_unoplat_node import ChapiUnoplatNode
from unoplat_code_confluence.data_models.unoplat_project_dependency import UnoplatProjectDependency


class ImportSegregationStrategy(ABC):
    
    def __init__(self, programming_language_version: str | None = None):
        self.programming_language_version = programming_language_version
    
    @abstractmethod
    def process_metadata(self, local_workspace_path: str, class_metadata: ChapiUnoplatNode, dependencies: set[str], programming_language_version: str | None = None) -> Dict[str,Dict[str,UnoplatImport]]:  
        """Process package manager specific metadata"""
        pass
