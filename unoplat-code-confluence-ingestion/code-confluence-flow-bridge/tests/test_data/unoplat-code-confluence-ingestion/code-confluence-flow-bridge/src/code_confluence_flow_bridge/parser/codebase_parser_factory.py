# First Party
from src.code_confluence_flow_bridge.models.configuration.settings import (
    ProgrammingLanguage,
)
from src.code_confluence_flow_bridge.parser.codebase_parser_strategy import (
    CodebaseParserStrategy,
)
from src.code_confluence_flow_bridge.parser.python.python_codebase_parser import (
    PythonCodebaseParser,
)


class UnsupportedLanguageError(Exception):
    pass


class CodebaseParserFactory:
    @staticmethod
    def get_parser(programming_language: str) -> CodebaseParserStrategy:
        if programming_language.lower() == ProgrammingLanguage.PYTHON.value:
            return PythonCodebaseParser()
        raise UnsupportedLanguageError(f"No parser implementation for language: {programming_language}")
