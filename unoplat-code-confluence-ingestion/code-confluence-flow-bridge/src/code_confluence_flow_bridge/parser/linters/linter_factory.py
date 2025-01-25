# Standard Library
from typing import Dict, Tuple

# First Party
from src.code_confluence_flow_bridge.models.configuration.settings import ProgrammingLanguage
from src.code_confluence_flow_bridge.models.workflow.code_confluence_linter import LinterType
from src.code_confluence_flow_bridge.parser.linters.linter_strategy import LinterStrategy
from src.code_confluence_flow_bridge.parser.linters.python.ruff_strategy import RuffStrategy


class LinterStrategyFactory:
    # Map (language, linter) pairs to their strategy classes
    _strategies: Dict[Tuple[ProgrammingLanguage, LinterType], type[LinterStrategy]] = {(ProgrammingLanguage.PYTHON, LinterType.RUFF): RuffStrategy}

    @classmethod
    def get_strategy(cls, programming_language: ProgrammingLanguage, linter_type: LinterType) -> LinterStrategy:
        """
        Get appropriate linter strategy based on programming language and linter type

        Args:
            programming_language: Programming language enum
            linter_type: Type of linter to use

        Returns:
            LinterStrategy: Appropriate strategy instance

        Raises:
            UnsupportedLinterError: If combination is not supported
        """
        key = (programming_language, linter_type)

        if key not in cls._strategies:
            raise UnsupportedLinterError(f"Unsupported combination - Language: {programming_language}, " f"Linter: {linter_type}")

        return cls._strategies[key]()


class UnsupportedLinterError(Exception):
    pass
