from typing import List, Optional, Any
import pytest
from unoplat_code_confluence.data_models.chapi.chapi_class_global_fieldmodel import ClassGlobalFieldModel
from unoplat_code_confluence.parser.tree_sitter.code_confluence_tree_sitter import CodeConfluenceTreeSitter
from unoplat_code_confluence.parser.python.node_variables.node_variables_parser import NodeVariablesParser
from unoplat_code_confluence.configuration.settings import ProgrammingLanguage
from unoplat_code_confluence.data_models.chapi.chapi_node import ChapiNode
from unoplat_code_confluence.data_models.chapi.chapi_annotation import ChapiAnnotation
from unoplat_code_confluence.data_models.chapi.chapi_function import ChapiFunction
from unoplat_code_confluence.data_models.chapi.chapi_parameter import ChapiParameter
from unoplat_code_confluence.data_models.chapi.chapi_function import ChapiFunction
from unoplat_code_confluence.data_models.chapi.chapi_annotation import ChapiAnnotation
import json
from datetime import datetime
from uuid import uuid4



@pytest.fixture
def parser() -> NodeVariablesParser:
    """Create parser instance with Python language."""
    tree_sitter = CodeConfluenceTreeSitter(ProgrammingLanguage.PYTHON)
    return NodeVariablesParser(tree_sitter)


def test_global_variables(parser: NodeVariablesParser):
    """Test parsing of global variables in a complex file structure."""
    file_content = """
    
    from typing import ClassVar, Dict, List
    from datetime import datetime
    from uuid import uuid4
    
    # Global variables at start
    global_var = 1
    GLOBAL_CONSTANT = "test"
    
    class FirstClass:
        class_var = "test"
        CLASS_CONSTANT = 42
        
    # Global variables between classes
    BETWEEN_CLASSES_VAR: int = 100
    CONFIG_DICT = {"env": "prod"}
    
    class SecondClass:
        internal_var = "internal"
        
        def method(self):
            pass
            
    # Global variables after classes
    FINAL_CONSTANT = "final"
    debug_mode: bool = False
    
    # Global with computation
    COMPUTED_VALUE = 10 * 20
    
    # Global tuple unpacking
    x, y = 1, 2
    
    class ThirdClass:
        pass
    
    # More globals after last class
    LAST_VAR = "last"
    """
    
    global_vars = parser.parse_global_variables(file_content)
    var_dict = {v.class_field_name: v for v in global_vars}
    
    # Expected variables with positions
    expected_globals = {
        "global_var": {
            "value": "1",
            "position": {
                "start_line": 8,
                "start_pos": 4,
                "end_line": 8,
                "end_pos": 14
            }
        },
        "GLOBAL_CONSTANT": {
            "value": '"test"',
            "position": {
                "start_line": 9,
                "start_pos": 4,
                "end_pos": 19,
                "end_line": 9
            }
        },
        "BETWEEN_CLASSES_VAR": {
            "value": "100",
            "type": "int",
            "position": {
                "start_line": 16,
                "start_pos": 4,
                "end_pos": 23,
                "end_line": 16
            }
        },
        "CONFIG_DICT": {
            "value": '{"env":"prod"}',
            "position": {
                "start_line": 17,
                "start_pos": 4,
                "end_pos": 14,
                "end_line": 17
            }
        },
        "FINAL_CONSTANT": {
            "value": '"final"',
            "position": {
                "start_line": 25,
                "start_pos": 4,
                "end_pos": 17,
                "end_line": 25
            }
        },
        "debug_mode": {
            "value": "False",
            "type": "bool",
            "position": {
                "start_line": 26,
                "start_pos": 4,
                "end_pos": 13,
                "end_line": 26
            }
        },
        "COMPUTED_VALUE": {
            "value": "10 * 20",
            "position": {
                "start_line": 28,
                "start_pos": 4,
                "end_pos": 17,
                "end_line": 28
            }
        },
        "x": {
            "value": "1",
            "position": {
                "start_line": 31,
                "start_pos": 4,
                "end_pos": 5,
                "end_line": 31
            }
        },
        "y": {
            "value": "2",
            "position": {
                "start_line": 31,
                "start_pos": 7,
                "end_pos": 8,
                "end_line": 31
            }
        },
        "LAST_VAR": {
            "value": '"last"',
            "position": {
                "start_line": 37,
                "start_pos": 4,
                "end_pos": 11,
                "end_line": 37
            }
        }
    }
    
    # Verify we captured all expected globals
    assert len(var_dict) == len(expected_globals)
    
    # Check each global variable
    for var_name, expected in expected_globals.items():
        assert var_name in var_dict, f"Missing variable: {var_name}"
        var = var_dict[var_name]
        
        # Check value
        assert var.class_field_value == expected["value"]
        
        # Just verify position exists
        assert var.position is not None, f"Missing position for {var_name}"
        assert var.position.start_line > 0, f"Invalid start line for {var_name}"
        assert var.position.start_line_position >= 0, f"Invalid start position for {var_name}"
        assert var.position.stop_line > 0, f"Invalid end line for {var_name}"
        assert var.position.stop_line_position > 0, f"Invalid end position for {var_name}"
        
        # Check type hints where applicable
        if "type" in expected:
            assert var.class_field_type == expected["type"], f"Wrong type for {var_name}"

def test_variables_with_all_types(parser: NodeVariablesParser):
    # Test class with all types of variables
    complex_class_content = """
    class DatabaseConnection:
        # Class Variables (ClassVar)
        VERSION: ClassVar[str] = "1.0.0"
        SUPPORTED_MODES: ClassVar[List[str]] = ["debug", "prod"]
        
        # Instance Variables at class level
        host: str = "localhost"
        port: int = 5432
        _connection: Optional[Any] = None
        
        def __init__(self, username: str, password: str):
            # Local variables that should not be captured
            connection_attempts = 0
            retry_delay: int = 5
            
            # Instance Variables in __init__
            self.username = username
            self.password = password
            self._is_connected: bool = False
            self.last_query: Optional[str] = None
            
        # Instance variables between methods
        timeout: float = 30.0
        retry_count: int = 3
            
        @classmethod
        def get_connection_stats(cls) -> Dict[str, Any]:
            # Local variables that should not be captured
            current_time = datetime.now()
            stats_dict = {}
            connection_count: int = 0
            
            # Class Variables in classmethod
            cls._total_connections = 0
            cls.last_connection_time = datetime.now()
            return {
                "total": cls._total_connections,
                "last_time": cls.last_connection_time
            }
            
        # More ClassVar variables between methods
        MAX_POOL_SIZE: ClassVar[int] = 10
        DEFAULT_TIMEOUT: ClassVar[float] = 5.0
            
        def connect(self):
            # Local variables that should not be captured
            max_retries = 3
            timeout_seconds: float = 10.0
            connection_params = {"timeout": timeout_seconds}
            
            # Instance variables in method
            self.connect_time = datetime.now()
            self._connection_id = str(uuid4())
            
        # Instance variables after methods
        status: str = "initialized"
        last_error: Optional[str] = None
        
        # Final ClassVar at end of class
        METADATA: ClassVar[Dict[str, str]] = {
            "type": "database",
            "version": VERSION
        }
    """

    functions = [
        ChapiFunction(
            Name="__init__",
            Parameters=[
                ChapiParameter(TypeValue="self"),
                ChapiParameter(TypeValue="username"),
                ChapiParameter(TypeValue="password")
            ],
            Content="""
                def __init__(self, username: str, password: str):
                    # Local variables that should not be captured
                    connection_attempts = 0
                    retry_delay: int = 5
                    
                    # Instance Variables in __init__
                    self.username = username
                    self.password = password
                    self._is_connected: bool = False
                    self.last_query: Optional[str] = None
            """
        ),
        ChapiFunction(
            Name="get_connection_stats",
            Parameters=[ChapiParameter(TypeValue="cls")],
            Annotations=[ChapiAnnotation(Name="classmethod")],
            Content="""
                @classmethod
                def get_connection_stats(cls) -> Dict[str, Any]:
                    # Local variables that should not be captured
                    current_time = datetime.now()
                    stats_dict = {}
                    connection_count: int = 0
                    
                    # Class Variables in classmethod
                    cls._total_connections = 0
                    cls.last_connection_time = datetime.now()
                    return {
                        "total": cls._total_connections,
                        "last_time": cls.last_connection_time
                    }
            """
        ),
        ChapiFunction(
            Name="connect",
            Parameters=[ChapiParameter(TypeValue="self")],
            Content="""
                def connect(self):
                    # Local variables that should not be captured
                    max_retries = 3
                    timeout_seconds: float = 10.0
                    connection_params = {"timeout": timeout_seconds}
                    
                    # Instance variables in method
                    self.connect_time = datetime.now()
                    self._connection_id = str(uuid4())
            """
        )
    ]

    class_vars = parser.parse_class_variables(complex_class_content, functions)
    class_var_dict = {v.class_field_name: v for v in class_vars}

    # Expected variables grouped by type
    expected_class_vars = {
        # ClassVar variables
        "VERSION": {
            "value": '"1.0.0"',
            "type": "ClassVar[str]"
        },
        "SUPPORTED_MODES": {
            "value": '["debug", "prod"]',
            "type": "ClassVar[List[str]]"
        },
        
        # Instance variables at class level
        "host": {
            "value": '"localhost"',
            "type": "str"
        },
        "port": {
            "value": "5432",
            "type": "int"
        },
        "_connection": {
            "value": "None",
            "type": "Optional[Any]"
        },
        
        # Instance variables from __init__
        "username": {
            "value": "username",  # Parameter value
            "type": None
        },
        "password": {
            "value": "password",  # Parameter value
            "type": None
        },
        "_is_connected": {
            "value": "False",
            "type": "bool"
        },
        "last_query": {
            "value": "None",
            "type": "Optional[str]"
        },
        
        # Instance variables between methods
        "timeout": {
            "value": "30.0",
            "type": "float"
        },
        "retry_count": {
            "value": "3",
            "type": "int"
        },
        
        # Runtime class variables from classmethod
        "_total_connections": {
            "value": "0",
            "type": None
        },
        "last_connection_time": {
            "value": "datetime.now()",
            "type": None
        },
        
        # Additional ClassVar variables between methods
        "MAX_POOL_SIZE": {
            "value": "10",
            "type": "ClassVar[int]"
        },
        "DEFAULT_TIMEOUT": {
            "value": "5.0",
            "type": "ClassVar[float]"
        },
        
        # Instance variables from connect method
        "connect_time": {
            "value": "datetime.now()",
            "type": None
        },
        "_connection_id": {
            "value": "str(uuid4())",
            "type": None
        },
        
        # Instance variables after methods
        "status": {
            "value": '"initialized"',
            "type": "str"
        },
        "last_error": {
            "value": "None",
            "type": "Optional[str]"
        },
        
        # Final ClassVar at end
        "METADATA": {
            "value": '{\n            "type": "database",\n            "version": VERSION\n        }',
            "type": "ClassVar[Dict[str, str]]"
        }
    }

    # Verify we captured all variables
    assert len(class_var_dict) == len(expected_class_vars)

    # Helper function to normalize JSON strings
    def normalize_dict_str(value: str) -> str:
        """Normalize dictionary string representation."""
        if not value:
            return value
        
        # Remove whitespace and newlines
        value = ''.join(value.split())
        
        # If it's a dictionary (starts with { and ends with })
        if value.startswith('{') and value.endswith('}'):
            # Remove the outer braces
            content = value[1:-1]
            # Split by comma and normalize each key-value pair
            pairs = [pair.strip() for pair in content.split(',')]
            # Sort the pairs for consistent ordering
            pairs.sort()
            # Rebuild the dictionary string
            return '{' + ','.join(pairs) + '}'
        
        return value

    # Check each variable
    for var_name, expected in expected_class_vars.items():
        assert var_name in class_var_dict, f"Missing variable: {var_name}"
        var = class_var_dict[var_name]
        
        # Compare values using dictionary string normalization
        actual_value = normalize_dict_str(var.class_field_value) if var.class_field_value else None
        expected_value = normalize_dict_str(expected["value"]) if expected["value"] else None
        assert actual_value == expected_value, f"Wrong value for {var_name}. Expected {expected_value}, got {actual_value}"
        
        # Check type hints
        assert var.class_field_type == expected["type"], f"Wrong type for {var_name}"
        
        # Verify position exists and is valid
        assert var.position is not None, f"Missing position for {var_name}"
        assert var.position.start_line > 0, f"Invalid start line for {var_name}"
        assert var.position.start_line_position >= 0, f"Invalid start position for {var_name}"
        assert var.position.stop_line > 0, f"Invalid end line for {var_name}"
        assert var.position.stop_line_position > 0, f"Invalid end position for {var_name}"
    
    # Add assertions to verify local variables are not captured
    local_variables = [
        "connection_attempts",
        "retry_delay",
        "current_time",
        "stats_dict",
        "connection_count",
        "max_retries",
        "timeout_seconds",
        "connection_params"
    ]

    # Verify none of the local variables were captured
    for local_var in local_variables:
        assert local_var not in class_var_dict, f"Local variable {local_var} should not be captured"

    # Verify only expected variables are present
    for var_name in class_var_dict:
        assert var_name in expected_class_vars, f"Unexpected variable {var_name} was captured"
    
   
def test_class_complexities(parser: NodeVariablesParser):
    code = """
    class ComplexClass:
        # Initial class-level variables
        VAR1: int = 10
        VAR2: str = "hello"

        def method_one(self):
            # Local vars that should not be captured
            x = 1
            y: float = 2.0

        # Another class-level var after a method
        VAR3: float = 3.14

        @classmethod
        def method_two(cls):
            # Runtime class variable inside classmethod
            cls.CLASS_RUNTIME = 99
            # local var not captured
            temp_local = "runtime_local"

        # Another class-level var after a classmethod
        VAR4 = "var4_value"

        @property
        def name(self):
            # local var in property method (not captured)
            prop_local = 42
            return self.VAR2

        # Another class-level var after a property
        VAR5 = ["list", "of", "strings"]

        # Instance variable at the class level (simulating dataclass style)
        instance_field: Optional[str] = None

        # Another method to complicate transitions
        def method_three(self):
            # local vars again not captured
            a, b = 1, 2
            self.instance_dynamic = "not captured as top-level"
    """

    functions = [
        ChapiFunction(
            Name="method_one",
            Parameters=[
                ChapiParameter(TypeValue="self")
            ],
            Content="""
                def method_one(self):
                    # Local vars that should not be captured
                    x = 1
                    y: float = 2.0
            """
        ),
        ChapiFunction(
            Name="method_two",
            Parameters=[
                ChapiParameter(TypeValue="cls")
            ],
            Annotations=[ChapiAnnotation(Name="classmethod")],
            Content="""
                @classmethod
                def method_two(cls):
                    # Runtime class variable inside classmethod
                    cls.CLASS_RUNTIME = 99
                    # local var not captured
                    temp_local = "runtime_local"
            """
        ),
        ChapiFunction(
            Name="name",
            Parameters=[
                ChapiParameter(TypeValue="self")
            ],
            Annotations=[ChapiAnnotation(Name="property")],
            Content="""
                @property
                def name(self):
                    # local var in property method (not captured)
                    prop_local = 42
                    return self.VAR2
            """
        ),
        ChapiFunction(
            Name="method_three",
            Parameters=[
                ChapiParameter(TypeValue="self")
            ],
            Content="""
                def method_three(self):
                    # local vars again not captured
                    a, b = 1, 2
                    self.instance_dynamic = "not captured as top-level"
            """
        )
    ]

    variables = parser.parse_class_variables(code, functions)
    var_dict = {v.class_field_name: v for v in variables}

    # Expected variables:
    # VAR1, VAR2, VAR3, VAR4, VAR5 are top-level class variables
    # CLASS_RUNTIME is a runtime class variable introduced in a classmethod
    # instance_field is a top-level instance field (like a dataclass field)
    expected_vars = {
        "VAR1": {
            "type": "int",
            "value": "10"
        },
        "VAR2": {
            "type": "str",
            "value": '"hello"'
        },
        "VAR3": {
            "type": "float",
            "value": "3.14"
        },
        "CLASS_RUNTIME": {
            # Runtime class var, no type hint at assignment
            "type": None,
            "value": "99"
        },
        "VAR4": {
            # No type hint
            "type": None,
            "value": '"var4_value"'
        },
        "VAR5": {
            "type": None,
            "value": '["list", "of", "strings"]'
        },
        "instance_field": {
            "type": "Optional[str]",
            "value": "None"
        },
        "instance_dynamic": {
            "type": None,
            "value": '"not captured as top-level"'
        }
    }

    # 1. Test for correct number of variables
    assert len(var_dict) == len(expected_vars), f"Expected {len(expected_vars)} variables, got {len(var_dict)}"

    # 2. Test each expected variable's properties
    for var_name, expected in expected_vars.items():
        assert var_name in var_dict, f"Missing variable: {var_name}"
        var = var_dict[var_name]
        assert var.class_field_type == expected["type"], f"Wrong type for {var_name}"
        assert var.class_field_value == expected["value"], f"Wrong value for {var_name}"

        # Verify position exists and is valid
        assert var.position is not None, f"Missing position for {var_name}"
        assert var.position.start_line > 0, f"Invalid start line for {var_name}"
        assert var.position.start_line_position >= 0, f"Invalid start position for {var_name}"
        assert var.position.stop_line > 0, f"Invalid end line for {var_name}"
        assert var.position.stop_line_position > 0, f"Invalid end position for {var_name}"

    # 3. Test that no local variables were captured
    local_vars = [
        "x", "y",  # from method_one
        "temp_local",  # from method_two
        "prop_local",  # from name property
        "a", "b"  # from method_thre
    ]
    for local_var in local_vars:
        assert local_var not in var_dict, f"Local variable {local_var} should not be captured"

    # 4. Test that only expected variables are present
    for var_name in var_dict:
        assert var_name in expected_vars, f"Unexpected variable {var_name} was captured"