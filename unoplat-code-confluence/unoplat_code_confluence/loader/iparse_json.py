from abc import ABC, abstractmethod
from typing import List
from data_models.chapi_unoplat_node import Node

class IParseJson(ABC):
    @abstractmethod
    def parse_json_to_nodes(self, json_data: dict) -> List[Node]:
        """Parses JSON data into a list of Node objects."""
        pass
