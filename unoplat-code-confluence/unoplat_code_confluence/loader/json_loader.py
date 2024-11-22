# Standard Library
import json
from typing import Any

# Third Party
from loguru import logger

# First Party
from unoplat_code_confluence.loader.iload_json import ILoadJson


class JsonLoader(ILoadJson):
    @logger.catch
    def load_json_from_file(self, file_path: str) -> Any:
        """
        Load JSON data from a file and return the JSON object.

        This method uses Loguru for enhanced logging and exception handling. It attempts to open and read
        a JSON file specified by the file_path argument. If successful, it logs the success and returns the data.
        If an exception occurs, it logs the error and re-raises the exception.

        Args:
            file_path (str): The path to the JSON file to be loaded.

        Returns:
            json: The JSON object loaded from the file.

        Raises:
            Exception: Propagates any exceptions that occur during file opening or JSON loading.
        """
        try:
            with open(file_path, 'r') as file:
                data: Any = json.load(file)
            logger.info(f"JSON data successfully loaded from {file_path}")
            return data
        except Exception as e:
            logger.error(f"Failed to load JSON data from {file_path}: {e}")
            raise

