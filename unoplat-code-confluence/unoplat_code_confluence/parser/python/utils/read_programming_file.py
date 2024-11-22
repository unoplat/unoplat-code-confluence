# Standard Library
from pathlib import Path


class ProgrammingFileReader:
    @staticmethod
    def read_file(file_path: str | Path) -> str:
        """
        Reads the content of a file and returns it as a string.
        
        Args:
            file_path (str | Path): Path to the file to be read
            
        Returns:
            str: Content of the file as a string
            
        Raises:
            FileNotFoundError: If the specified file does not exist
            IOError: If there are issues reading the file
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except IOError as e:
            raise IOError(f"Error reading file {file_path}: {str(e)}")
