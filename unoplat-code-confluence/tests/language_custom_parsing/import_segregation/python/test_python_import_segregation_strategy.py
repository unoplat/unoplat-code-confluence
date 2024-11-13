from typing import List
import pytest
from unoplat_code_confluence.language_custom_parsing.import_segregation.python.python_import_segregation_strategy import PythonImportSegregationStrategy
from unoplat_code_confluence.data_models.chapi_unoplat_import import ChapiUnoplatImport


@pytest.fixture
def strategy():
    return PythonImportSegregationStrategy()


def test_parse_imports_simple_import(strategy):
    file_path: str = "/Users/jayghiya/Documents/unoplat/code_confluence_testing/unoplat-danswer/danswer/backend/danswer/connectors/confluence/onyx_confluence.py"
    with open(file_path, "r", encoding="utf-8") as file:
        code = file.read()
    result: List[ChapiUnoplatImport] = strategy.parse_imports(code)
    assert len(result) == 4
    