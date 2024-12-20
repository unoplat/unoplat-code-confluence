# Standard Library
from abc import ABC, abstractmethod
from typing import List

# First Party
from unoplat_code_confluence.data_models.chapi_unoplat_node import \
    ChapiUnoplatNode


class IParseJson(ABC):
    @abstractmethod
    def parse_json_to_nodes(self, json_data: dict, local_workspace_path: str, programming_language: str) -> List[ChapiUnoplatNode]:
        """Parses JSON data into a list of Node objects."""
        pass

