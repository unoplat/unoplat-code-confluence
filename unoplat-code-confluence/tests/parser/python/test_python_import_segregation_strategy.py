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
from unoplat_code_confluence.parser.python.python_import_segregation_strategy import (
    PythonImportSegregationStrategy,
)


@pytest.fixture
def segregation_strategy() -> PythonImportSegregationStrategy:
    """Fixture for PythonImportSegregationStrategy."""
    return PythonImportSegregationStrategy()


@pytest.fixture
def test_node() -> ChapiUnoplatNode:
    """Fixture for test node."""
    return ChapiUnoplatNode(FilePath="test_file.py")


def create_import(
    source: str, 
    usage_names: Union[str, list[str]], 
    import_type: ImportType,
    alias: str | None = None
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
        ImportType=import_type
    )


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
    
    result = segregation_strategy.process_imports( test_node)
    
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
    
    result = segregation_strategy.process_imports(test_node)
    
    third_party_imports = result[ImportType.EXTERNAL]  # Changed from THIRD_PARTY to EXTERNAL
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


def test_internal_imports(
    segregation_strategy: PythonImportSegregationStrategy,
    test_node: ChapiUnoplatNode,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test internal (first party) imports with various patterns."""
    content = """
# First Party
import myproject.utils
import myproject.core.models as models
from myproject.services import UserService
from myproject.database.session import Session as DBSession, Engine
"""
    monkeypatch.setattr(segregation_strategy.file_reader, "read_file", lambda _: content)
    
    result = segregation_strategy.process_imports(test_node)
    
    internal_imports = result[ImportType.INTERNAL]
    assert len(internal_imports) == 4
    
    # Test 'import myproject.utils'
    assert internal_imports[0].source == "myproject.utils"
    assert internal_imports[0].usage_names[0].original_name == "myproject.utils"
    assert internal_imports[0].usage_names[0].alias is None
    
    # Test 'import myproject.core.models as models'
    assert internal_imports[1].source == "myproject.core.models"
    assert internal_imports[1].usage_names[0].original_name == "myproject.core.models"
    assert internal_imports[1].usage_names[0].alias == "models"
    
    # Test 'from myproject.services import UserService'
    assert internal_imports[2].source == "myproject.services"
    assert internal_imports[2].usage_names[0].original_name == "UserService"
    assert internal_imports[2].usage_names[0].alias is None
    
    # Test 'from myproject.database.session import Session as DBSession, Engine'
    assert internal_imports[3].source == "myproject.database.session"
    assert len(internal_imports[3].usage_names) == 2
    assert internal_imports[3].usage_names[0].original_name == "Session"
    assert internal_imports[3].usage_names[0].alias == "DBSession"
    assert internal_imports[3].usage_names[1].original_name == "Engine"
    assert internal_imports[3].usage_names[1].alias is None


def test_multiline_imports(
    segregation_strategy: PythonImportSegregationStrategy,
    test_node: ChapiUnoplatNode,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test both multiline and normal import statements."""
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
    
    result = segregation_strategy.process_imports(test_node)
    
    third_party_imports = result[ImportType.EXTERNAL]
    assert len(third_party_imports) == 1
    
    # Test multiline import 'from sqlalchemy import (...)'
    assert third_party_imports[0].source == "sqlalchemy"
    assert len(third_party_imports[0].usage_names) == 4
    assert third_party_imports[0].usage_names[0].original_name == "Column"
    assert third_party_imports[0].usage_names[0].alias is None
    assert third_party_imports[0].usage_names[1].original_name == "Integer"
    assert third_party_imports[0].usage_names[1].alias == "Int"
    assert third_party_imports[0].usage_names[2].original_name == "String"
    assert third_party_imports[0].usage_names[2].alias == "Str"
    assert third_party_imports[0].usage_names[3].original_name == "ForeignKey"
    assert third_party_imports[0].usage_names[3].alias is None


def test_single_line_multiple_imports(
    segregation_strategy: PythonImportSegregationStrategy,
    test_node: ChapiUnoplatNode,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test single line imports with multiple items and aliases."""
    content = """
# Standard Library
from datetime import datetime as dt, timedelta, timezone as tz
from os import path, getcwd as get_current_dir, mkdir
import sys

# Third Party
from sqlalchemy.orm import Session as DBSession, relationship, backref as back_ref
import pandas as pd, numpy as np
from sqlalchemy import (
    Column,
    Integer as Int,
    String as Str,
    ForeignKey
)
"""
    monkeypatch.setattr(segregation_strategy.file_reader, "read_file", lambda _: content)
    
    result = segregation_strategy.process_imports(test_node)
    
    # Test standard library imports
    standard_imports = result[ImportType.STANDARD]
    assert len(standard_imports) == 3
    
    # Test 'from datetime import datetime as dt, timedelta, timezone as tz'
    assert standard_imports[0].source == "datetime"
    assert len(standard_imports[0].usage_names) == 3
    assert standard_imports[0].usage_names[0].original_name == "datetime"
    assert standard_imports[0].usage_names[0].alias == "dt"
    assert standard_imports[0].usage_names[1].original_name == "timedelta"
    assert standard_imports[0].usage_names[1].alias is None
    assert standard_imports[0].usage_names[2].original_name == "timezone"
    assert standard_imports[0].usage_names[2].alias == "tz"
    
    # Test 'from os import path, getcwd as get_current_dir, mkdir'
    assert standard_imports[1].source == "os"
    assert len(standard_imports[1].usage_names) == 3
    assert standard_imports[1].usage_names[0].original_name == "path"
    assert standard_imports[1].usage_names[0].alias is None
    assert standard_imports[1].usage_names[1].original_name == "getcwd"
    assert standard_imports[1].usage_names[1].alias == "get_current_dir"
    assert standard_imports[1].usage_names[2].original_name == "mkdir"
    assert standard_imports[1].usage_names[2].alias is None
    
    # Test 'import sys'
    assert standard_imports[2].source == "sys"
    assert len(standard_imports[2].usage_names) == 1
    assert standard_imports[2].usage_names[0].original_name == "sys"
    assert standard_imports[2].usage_names[0].alias is None
    
    # Test third party imports
    external_imports = result[ImportType.EXTERNAL]
    assert len(external_imports) == 4
    
    # Test 'from sqlalchemy.orm import Session as DBSession, relationship, backref as back_ref'
    assert external_imports[0].source == "sqlalchemy.orm"
    assert len(external_imports[0].usage_names) == 3
    assert external_imports[0].usage_names[0].original_name == "Session"
    assert external_imports[0].usage_names[0].alias == "DBSession"
    assert external_imports[0].usage_names[1].original_name == "relationship"
    assert external_imports[0].usage_names[1].alias is None
    assert external_imports[0].usage_names[2].original_name == "backref"
    assert external_imports[0].usage_names[2].alias == "back_ref"
    
    # Test 'import pandas as pd'
    assert external_imports[1].source == "pandas"
    assert len(external_imports[1].usage_names) == 1
    assert external_imports[1].usage_names[0].original_name == "pandas"
    assert external_imports[1].usage_names[0].alias == "pd"
    
    # Test 'import numpy as np'
    assert external_imports[2].source == "numpy"
    assert len(external_imports[2].usage_names) == 1
    assert external_imports[2].usage_names[0].original_name == "numpy"
    assert external_imports[2].usage_names[0].alias == "np"
    
    # Test multiline sqlalchemy import
    assert external_imports[3].source == "sqlalchemy"
    assert len(external_imports[3].usage_names) == 4
    assert external_imports[3].usage_names[0].original_name == "Column"
    assert external_imports[3].usage_names[0].alias is None
    assert external_imports[3].usage_names[1].original_name == "Integer"
    assert external_imports[3].usage_names[1].alias == "Int"
    assert external_imports[3].usage_names[2].original_name == "String"
    assert external_imports[3].usage_names[2].alias == "Str"
    assert external_imports[3].usage_names[3].original_name == "ForeignKey"
    assert external_imports[3].usage_names[3].alias is None

def test_deep_nested_imports(
    segregation_strategy: PythonImportSegregationStrategy,
    test_node: ChapiUnoplatNode,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test imports with multiple dots in the path."""
    content = """
# First Party
from very.deep.nested.module import function_a
from another.deep.module import ClassA as MyClass
import really.deep.nested.thing as thing
from my.deep.module import (
    ClassB,
    function_b as fb,
    CONSTANT
)
"""
    monkeypatch.setattr(segregation_strategy.file_reader, "read_file", lambda _: content)
    
    result = segregation_strategy.process_imports(test_node)
    
    internal_imports = result[ImportType.INTERNAL]
    assert len(internal_imports) == 4
    
    # Test deeply nested from import
    assert internal_imports[0].source == "very.deep.nested.module"
    assert internal_imports[0].usage_names[0].original_name == "function_a"
    assert internal_imports[0].usage_names[0].alias is None
    
    # Test deep import with alias
    assert internal_imports[1].source == "another.deep.module"
    assert internal_imports[1].usage_names[0].original_name == "ClassA"
    assert internal_imports[1].usage_names[0].alias == "MyClass"
    
    # Test deep direct import with alias
    assert internal_imports[2].source == "really.deep.nested.thing"
    assert internal_imports[2].usage_names[0].original_name == "really.deep.nested.thing"
    assert internal_imports[2].usage_names[0].alias == "thing"
    
    # Test deep multiline import
    assert internal_imports[3].source == "my.deep.module"
    assert len(internal_imports[3].usage_names) == 3
    assert internal_imports[3].usage_names[0].original_name == "ClassB"
    assert internal_imports[3].usage_names[0].alias is None
    assert internal_imports[3].usage_names[1].original_name == "function_b"
    assert internal_imports[3].usage_names[1].alias == "fb"
    assert internal_imports[3].usage_names[2].original_name == "CONSTANT"
    assert internal_imports[3].usage_names[2].alias is None

def test_local_imports(
    segregation_strategy: PythonImportSegregationStrategy,
    test_node: ChapiUnoplatNode,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test local imports section."""
    content = """
# Local
from .utils import helper_function
from .models import BaseModel as Model
from .constants import (
    DEFAULT_TIMEOUT,
    MAX_RETRIES as MAX_TRIES,
    ERROR_MESSAGES
)
import .config as cfg
"""
    monkeypatch.setattr(segregation_strategy.file_reader, "read_file", lambda _: content)
    
    result = segregation_strategy.process_imports(test_node)
    
    local_imports = result[ImportType.LOCAL]
    assert len(local_imports) == 4
    
    # Test simple local import
    assert local_imports[0].source == ".utils"
    assert local_imports[0].usage_names[0].original_name == "helper_function"
    assert local_imports[0].usage_names[0].alias is None
    
    # Test local import with alias
    assert local_imports[1].source == ".models"
    assert local_imports[1].usage_names[0].original_name == "BaseModel"
    assert local_imports[1].usage_names[0].alias == "Model"
    
    # Test local multiline import
    assert local_imports[2].source == ".constants"
    assert len(local_imports[2].usage_names) == 3
    assert local_imports[2].usage_names[0].original_name == "DEFAULT_TIMEOUT"
    assert local_imports[2].usage_names[0].alias is None
    assert local_imports[2].usage_names[1].original_name == "MAX_RETRIES"
    assert local_imports[2].usage_names[1].alias == "MAX_TRIES"
    assert local_imports[2].usage_names[2].original_name == "ERROR_MESSAGES"
    assert local_imports[2].usage_names[2].alias is None
    
    # Test direct local import with alias
    assert local_imports[3].source == ".config"
    assert local_imports[3].usage_names[0].original_name == ".config"
    assert local_imports[3].usage_names[0].alias == "cfg"