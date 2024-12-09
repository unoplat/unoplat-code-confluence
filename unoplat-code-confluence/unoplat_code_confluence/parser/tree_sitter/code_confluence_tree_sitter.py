from unoplat_code_confluence.configuration.settings import ProgrammingLanguage
from tree_sitter import Language, Parser
import tree_sitter_python


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
    