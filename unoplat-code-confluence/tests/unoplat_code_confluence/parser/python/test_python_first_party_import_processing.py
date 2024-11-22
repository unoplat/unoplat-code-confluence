# Standard Library
import os
from pathlib import Path
from typing import Dict, List, Union

# Third Party
import pytest

# First Party
from unoplat_code_confluence.data_models.chapi_unoplat_import import ChapiUnoplatImport
from unoplat_code_confluence.data_models.chapi_unoplat_node import ChapiUnoplatNode
from unoplat_code_confluence.data_models.unoplat_import import ImportedName, UnoplatImport
from unoplat_code_confluence.data_models.unoplat_import_type import ImportType
from unoplat_code_confluence.parser.python.python_first_party_import_processing import (
    PythonFirstPartyImportProcessing,
)
from unoplat_code_confluence.parser.python.python_import_segregation_strategy import (
    PythonImportSegregationStrategy,
)


@pytest.fixture
def processor() -> PythonFirstPartyImportProcessing:
    return PythonFirstPartyImportProcessing()


@pytest.fixture
def segregation_strategy() -> PythonImportSegregationStrategy:
    return PythonImportSegregationStrategy()


@pytest.fixture
def test_node() -> ChapiUnoplatNode:
    """Fixture for test node."""
    return ChapiUnoplatNode(FilePath="test_file.py")


def create_import(
    source: str,
    usage_names: Union[str, list[str]],
    import_type: ImportType,
    alias: str | None = None,
) -> UnoplatImport:
    """Helper to create UnoplatImport instances for testing.

    Args:
        source: The source module/package
        usage_names: Single name or list of names being imported
        import_type: Type of import (STANDARD, EXTERNAL, INTERNAL, LOCAL)
        alias: Optional alias for the import

    Returns:
        UnoplatImport: A configured import instance
    """
    # Convert single string to list if needed
    if isinstance(usage_names, str):
        imported_names = [ImportedName(original_name=usage_names, alias=alias)]
    else:
        imported_names = [ImportedName(original_name=name) for name in usage_names]

    return UnoplatImport(
        Source=source,
        UsageName=imported_names,
        ImportType=import_type,
    )


def test_absolute_first_party_imports(processor: PythonFirstPartyImportProcessing) -> None:
    """Test processing of absolute first party imports."""
    root_package = "myproject"
    file_path = "/workspace/myproject/module.py"
    imports = [
        create_import("myproject.utils", "utils_func", ImportType.INTERNAL),
        create_import("myproject.core.models", "Model", ImportType.INTERNAL),
        create_import(
            "myproject.services.user",
            ["create_user", "delete_user"],
            ImportType.INTERNAL,
        ),
    ]

    result = processor.process_first_party_imports(root_package, file_path, imports)

    assert len(result) == 3
    assert result[0].source == "myproject.utils"
    assert result[0].usage_names[0].original_name == "utils_func"
    assert result[1].source == "myproject.core.models"
    assert result[1].usage_names[0].original_name == "Model"
    assert result[2].source == "myproject.services.user"
    assert result[2].usage_names[0].original_name == "create_user"
    assert result[2].usage_names[1].original_name == "delete_user"


def test_first_party_imports_with_aliases(processor: PythonFirstPartyImportProcessing) -> None:
    """Test first party imports with aliases."""
    root_package = "myproject"
    file_path = "/workspace/myproject/module.py"
    imports = [
        create_import("myproject.database", "Session", ImportType.INTERNAL, "DBSession"),
        create_import("myproject.core.models", "UserModel", ImportType.INTERNAL, "User"),
        create_import(
            "myproject.utils.helpers",
            ["create_token", "validate_token"],
            ImportType.INTERNAL,
        ),
    ]

    result = processor.process_first_party_imports(root_package, file_path, imports)

    assert len(result) == 3
    assert result[0].source == "myproject.database"
    assert result[0].usage_names[0].original_name == "Session"
    assert result[0].usage_names[0].alias == "DBSession"
    assert result[1].source == "myproject.core.models"
    assert result[1].usage_names[0].original_name == "UserModel"
    assert result[1].usage_names[0].alias == "User"
    assert result[2].source == "myproject.utils.helpers"
    assert result[2].usage_names[0].original_name == "create_token"
    assert result[2].usage_names[1].original_name == "validate_token"


def test_standard_library_imports(
    segregation_strategy: PythonImportSegregationStrategy,
    test_node: ChapiUnoplatNode,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test standard library imports with various patterns."""
    content = """
# Standard Library
import os
import sys as system
from pathlib import Path
from datetime import datetime as dt, timedelta
"""
    monkeypatch.setattr(segregation_strategy.file_reader, "read_file", lambda _: content)

    result = segregation_strategy.process_imports("test_package", test_node)

    standard_imports = result[ImportType.STANDARD]
    assert len(standard_imports) == 4

    # Test 'import os'
    assert standard_imports[0].source == "os"
    assert standard_imports[0].usage_names[0].original_name == "os"
    assert standard_imports[0].usage_names[0].alias is None

    # Test 'import sys as system'
    assert standard_imports[1].source == "sys"
    assert standard_imports[1].usage_names[0].original_name == "sys"
    assert standard_imports[1].usage_names[0].alias == "system"

    # Test 'from pathlib import Path'
    assert standard_imports[2].source == "pathlib"
    assert standard_imports[2].usage_names[0].original_name == "Path"
    assert standard_imports[2].usage_names[0].alias is None

    # Test 'from datetime import datetime as dt, timedelta'
    assert standard_imports[3].source == "datetime"
    assert len(standard_imports[3].usage_names) == 2
    assert standard_imports[3].usage_names[0].original_name == "datetime"
    assert standard_imports[3].usage_names[0].alias == "dt"
    assert standard_imports[3].usage_names[1].original_name == "timedelta"
    assert standard_imports[3].usage_names[1].alias is None


def test_third_party_imports(
    segregation_strategy: PythonImportSegregationStrategy,
    test_node: ChapiUnoplatNode,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test third party imports with various patterns."""
    content = """
# Third Party
import pandas as pd
import numpy
from requests import get, post as http_post
from sqlalchemy.orm import Session as DBSession, relationship
"""
    monkeypatch.setattr(segregation_strategy.file_reader, "read_file", lambda _: content)

    result = segregation_strategy.process_imports("test_package", test_node)

    third_party_imports = result[ImportType.EXTERNAL]
    assert len(third_party_imports) == 4

    # Test 'import pandas as pd'
    assert third_party_imports[0].source == "pandas"
    assert third_party_imports[0].usage_names[0].original_name == "pandas"
    assert third_party_imports[0].usage_names[0].alias == "pd"

    # Test 'import numpy'
    assert third_party_imports[1].source == "numpy"
    assert third_party_imports[1].usage_names[0].original_name == "numpy"
    assert third_party_imports[1].usage_names[0].alias is None

    # Test 'from requests import get, post as http_post'
    assert third_party_imports[2].source == "requests"
    assert len(third_party_imports[2].usage_names) == 2
    assert third_party_imports[2].usage_names[0].original_name == "get"
    assert third_party_imports[2].usage_names[0].alias is None
    assert third_party_imports[2].usage_names[1].original_name == "post"
    assert third_party_imports[2].usage_names[1].alias == "http_post"

    # Test 'from sqlalchemy.orm import Session as DBSession, relationship'
    assert third_party_imports[3].source == "sqlalchemy.orm"
    assert len(third_party_imports[3].usage_names) == 2
    assert third_party_imports[3].usage_names[0].original_name == "Session"
    assert third_party_imports[3].usage_names[0].alias == "DBSession"
    assert third_party_imports[3].usage_names[1].original_name == "relationship"
    assert third_party_imports[3].usage_names[1].alias is None


def test_multiline_imports(
    segregation_strategy: PythonImportSegregationStrategy,
    test_node: ChapiUnoplatNode,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test multiline import statements."""
    content = """
# Third Party
from sqlalchemy import (
    Column,
    Integer as Int,
    String as Str,
    ForeignKey
)
"""
    monkeypatch.setattr(segregation_strategy.file_reader, "read_file", lambda _: content)

    result = segregation_strategy.process_imports("test_package", test_node)

    third_party_imports = result[ImportType.EXTERNAL]
    assert len(third_party_imports) == 1

    # Test multiline import
    assert third_party_imports[0].source == "sqlalchemy"
    assert len(third_party_imports[0].usage_names) == 4
    assert third_party_imports[0].usage_names[0].original_name == "Column"
    assert third_party_imports[0].usage_names[0].alias is None
    assert third_party_imports[0].usage_names[1].original_name == "Integer"
    assert third_party_imports[0].usage_names[1].alias == "Int"
    assert third_party_imports[0].usage_names[2].original_name == "String"
    assert third_party_imports[2].usage_names[2].alias == "Str"
    assert third_party_imports[0].usage_names[3].original_name == "ForeignKey"
    assert third_party_imports[0].usage_names[3].alias is None