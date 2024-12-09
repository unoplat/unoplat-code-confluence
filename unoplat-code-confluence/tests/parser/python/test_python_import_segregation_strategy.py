# Standard Library
import os
import tempfile
from pathlib import Path
from typing import List

import pytest

from unoplat_code_confluence.data_models.chapi.chapi_node import ChapiNode
from unoplat_code_confluence.data_models.chapi_forge.unoplat_import import UnoplatImport, ImportedName
from unoplat_code_confluence.data_models.chapi_forge.unoplat_import_type import ImportType
from unoplat_code_confluence.parser.python.python_import_segregation_strategy import PythonImportSegregationStrategy

@pytest.fixture
def strategy():
    return PythonImportSegregationStrategy()

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)

def create_test_file(temp_dir: Path, filename: str, content: str) -> str:
    """Create a test file with given content and return its path."""
    file_path = temp_dir / filename
    file_path.write_text(content)
    return str(file_path)

def test_empty_imports(strategy: PythonImportSegregationStrategy, temp_dir: Path):
    """Test segregation with empty file."""
    content = """
# Empty python file
    """
    file_path = create_test_file(temp_dir, "empty.py", content)
    
    node = ChapiNode(FilePath=file_path)
    result = strategy.process_imports(node)
    
    assert isinstance(result, dict)
    assert len(result) is 0
    
def test_internal_imports(strategy: PythonImportSegregationStrategy, temp_dir: Path):
    """Test segregation of internal imports."""
    content = """
# First Party
from myproject.utils import helper
from myproject.models import UserModel
    """
    file_path = create_test_file(temp_dir, "internal.py", content)
    
    node = ChapiNode(FilePath=file_path)
    result = strategy.process_imports(node)
    
    internal_imports = result[ImportType.INTERNAL]
    assert len(internal_imports) == 2
    
    # Check first import
    assert internal_imports[0].source == "myproject.utils"
    assert len(internal_imports[0].usage_names) == 1 #type: ignore
    assert internal_imports[0].usage_names[0].original_name == "helper" #type: ignore
    
    # Check second import
    assert internal_imports[1].source == "myproject.models"
    assert len(internal_imports[1].usage_names) == 1 #type: ignore
    assert internal_imports[1].usage_names[0].original_name == "UserModel" #type: ignore

def test_external_imports(strategy: PythonImportSegregationStrategy, temp_dir: Path):
    """Test segregation of external imports."""
    content = """
# Third Party
import pandas as pd
from requests import get, post
    """
    file_path = create_test_file(temp_dir, "external.py", content)
    
    node = ChapiNode(FilePath=file_path)
    result = strategy.process_imports(node)
    
    external_imports = result[ImportType.EXTERNAL]
    assert len(external_imports) == 2
    
    # Check pandas import
    assert external_imports[0].source == "pandas"
    assert len(external_imports[0].usage_names) == 1 #type: ignore
    assert external_imports[0].usage_names[0].original_name == "pandas" #type: ignore
    assert external_imports[0].usage_names[0].alias == "pd" #type: ignore
    
    # Check requests import
    assert external_imports[1].source == "requests" #type: ignore
    assert len(external_imports[1].usage_names) == 2 #type: ignore
    assert external_imports[1].usage_names[0].original_name == "get" #type: ignore
    assert external_imports[1].usage_names[1].original_name == "post" #type: ignore

def test_mixed_imports(strategy: PythonImportSegregationStrategy, temp_dir: Path):
    """Test segregation of mixed import types."""
    content = """
# Standard Library
import os
from datetime import datetime

# Third Party
import pandas as pd

# First Party
from myproject.utils import helper
    """
    file_path = create_test_file(temp_dir, "mixed.py", content)
    
    node = ChapiNode(FilePath=file_path)
    result = strategy.process_imports(node)
    
    # Check standard library imports
    standard_imports = result[ImportType.STANDARD]
    assert len(standard_imports) == 2
    assert standard_imports[0].source == "os"
    assert standard_imports[1].source == "datetime"
    
    # Check external imports
    external_imports = result[ImportType.EXTERNAL]
    assert len(external_imports) == 1
    assert external_imports[0].source == "pandas"
    assert external_imports[0].usage_names[0].alias == "pd" #type: ignore
    
    # Check internal imports
    internal_imports = result[ImportType.INTERNAL]
    assert len(internal_imports) == 1
    assert internal_imports[0].source == "myproject.utils"
    assert internal_imports[0].usage_names[0].original_name == "helper" #type: ignore