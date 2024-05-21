from typing import List

from pydantic import ValidationError
from loader.iparse_json import IParseJson
from data_models.chapi_unoplat_node import Node

from loguru import logger

class JsonParser(IParseJson):
    def parse_json_to_nodes(self, json_data: dict) -> List[Node]:
        """Concrete implementation of the parse_json_to_nodes method."""
        nodes = []
        for item in json_data:
            try:
                node = Node(**item)
                nodes.append(node)
            except ValidationError as e:
                logger.error(f"Error validating node: {e}")
        return nodes
