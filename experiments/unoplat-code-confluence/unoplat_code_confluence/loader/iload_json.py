# Standard Library
import json
from abc import ABC, abstractmethod


class ILoadJson(ABC):
    @abstractmethod
    def load_json_from_file(self, file_path: str) -> json:
        """Load JSON data from a file and return a JSON object."""
        pass