from unoplat_code_confluence.parser.codebase_parser_strategy import CodebaseParserStrategy
from unoplat_code_confluence.parser.python.python_codebase_parser import PythonCodebaseParser
from unoplat_code_confluence.configuration.external_config import ProgrammingLanguage

class UnsupportedLanguageError(Exception):
    pass

class CodebaseParserFactory:
    @staticmethod
    def get_parser(programming_language: str) -> CodebaseParserStrategy:
        if programming_language.lower() == ProgrammingLanguage.PYTHON.value:
            return PythonCodebaseParser()
        raise UnsupportedLanguageError(f"No parser implementation for language: {programming_language}") 