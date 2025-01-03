# Third Party
import tree_sitter_python  # type: ignore
from tree_sitter import Language, Parser

# First Party
from src.code_confluence_flow_bridge.models.configuration.settings import ProgrammingLanguage


class CodeConfluenceTreeSitter:
    def __init__(self, language: ProgrammingLanguage):
        """Initialize parser based on programming language.
        
        Args:
            language: Programming language enum value
        """
        
        
        match language:
            case ProgrammingLanguage.PYTHON:
                PY_LANGUAGE = Language(tree_sitter_python.language()) #type: ignore
                self.parser = Parser()
                self.parser.language = PY_LANGUAGE #type: ignore
            case _:
                raise ValueError(f"Unsupported programming language: {language}")
                
    def get_parser(self) -> Parser:
        return self.parser