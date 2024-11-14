from typing import List
import pytest
from unoplat_code_confluence.language_custom_parsing.import_segregation.python.python_import_segregation_strategy import PythonImportSegregationStrategy
from unoplat_code_confluence.data_models.chapi_unoplat_import import ChapiUnoplatImport
from unoplat_code_confluence.data_models.chapi_unoplat_node import ChapiUnoplatNode


@pytest.fixture
def strategy():
    return PythonImportSegregationStrategy(programming_language_version="3.12")


def test_consolidate_imports_simple_import(strategy):
    file_path: str = "/Users/jayghiya/Documents/unoplat/code_confluence_testing/unoplat-danswer/danswer/backend/danswer/connectors/confluence/onyx_confluence.py"
    with open(file_path, "r", encoding="utf-8") as file:
        code = file.read()
    result: List[ChapiUnoplatImport] = strategy.consolidate_imports(code)
    assert len(result) == 4



def test_process_metadata(strategy):
    file_path: str = "/Users/jayghiya/Documents/unoplat/code_confluence_testing/unoplat-danswer/danswer/backend/danswer/connectors/confluence/onyx_confluence.py"
    # Mock ChapiUnoplatNode for testing
    class_metadata = ChapiUnoplatNode()
    dependencies = set()
    programming_language_version = "3.9"
    
    result = strategy.process_metadata(
        local_workspace_path=file_path,
        class_metadata=class_metadata,
        dependencies=dependencies
    )
    
    # Assert result is a dictionary of dictionaries
    assert isinstance(result, dict)
    # Add more specific assertions based on expected output