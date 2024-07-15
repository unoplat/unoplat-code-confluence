from abc import ABC, abstractmethod
from typing import List
from unoplat_code_confluence.data_models.chapi_unoplat_node import Node

class IParseJson(ABC):
    @abstractmethod
    def parse_json_to_nodes(self, json_data: dict, local_workspace_path: str, programming_language: str) -> List[Node]:
        """Parses JSON data into a list of Node objects."""
        pass
