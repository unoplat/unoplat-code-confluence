# First Party
from unoplat_code_confluence.configuration.external_config import \
    ProgrammingLanguageMetadata
from unoplat_code_confluence.data_models.chapi_unoplat_codebase import \
    UnoplatCodebase
from unoplat_code_confluence.parser.codebase_parser_factory import \
    CodebaseParserFactory


class CodebaseParser():
    def parse_codebase(self, codebase_name: str, json_data: dict, local_workspace_path: str, programming_language_metadata: ProgrammingLanguageMetadata) -> UnoplatCodebase:
        """Concrete implementation of the parse_codebase method."""
        parser = CodebaseParserFactory.get_parser(programming_language_metadata.language.value)
        return parser.parse_codebase(codebase_name=codebase_name, json_data=json_data, local_workspace_path=local_workspace_path, programming_language_metadata=programming_language_metadata) 