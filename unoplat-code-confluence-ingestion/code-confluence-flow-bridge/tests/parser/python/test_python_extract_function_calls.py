from typing import Dict, List, Optional

import pytest

from src.code_confluence_flow_bridge.models.chapi.chapi_function import ChapiFunction
from src.code_confluence_flow_bridge.models.chapi.chapi_functioncall import ChapiFunctionCall
from src.code_confluence_flow_bridge.models.chapi.chapi_node import ChapiNode
from src.code_confluence_flow_bridge.models.chapi.chapi_position import Position
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_import import ImportedName, UnoplatImport
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_import_type import ImportType
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_function_call_type import FunctionCallType
from src.code_confluence_flow_bridge.models.configuration.settings import ProgrammingLanguage
from src.code_confluence_flow_bridge.parser.python.python_extract_function_calls import PythonExtractFunctionCalls
from src.code_confluence_flow_bridge.parser.tree_sitter.code_confluence_tree_sitter import CodeConfluenceTreeSitter

@pytest.fixture
def extractor() -> PythonExtractFunctionCalls:
    """Create PythonExtractFunctionCalls with real tree-sitter parser."""
    tree_sitter = CodeConfluenceTreeSitter(language=ProgrammingLanguage.PYTHON)
    return PythonExtractFunctionCalls(code_confluence_tree_sitter=tree_sitter)

def test_extract_instantiations_ts(extractor: PythonExtractFunctionCalls) -> None:
    """Test extraction of class instantiations from Python code with multiple scenarios."""
    # Test file with various instantiation patterns
    file_source: str = """
# Simple instantiation
calculator = Calculator()

# Instantiation with arguments
parser = ArgumentParser(description="Test parser")

# Type-annotated instantiation (global scope)
config: Configuration = Configuration()

# Multiple instantiations
validator = DataValidator()
formatter = OutputFormatter()

def process_data():
    # Instantiation inside function
    processor = DataProcessor()
    
    # Type-annotated instantiation inside function
    logger: Logger = Logger()
    
    def nested_function():
        # Type-annotated instantiation in nested function
        cache: Cache = Cache()
        
        # Tuple unpacking inside nested function
        client, server = Client(), Server()
        
        return cache.get()
    
    return processor.run()

class TestClass:
    def __init__(self):
        # Instantiation in method
        self.helper = HelperClass()
        
        # Type-annotated attribute
        self.config: Config = Config()
        
    def test_method(self):
        # Another instantiation
        tester = TestRunner()
        
        # Tuple unpacking in method
        reader, writer = FileReader(), FileWriter()
        
        def inner_method():
            # Type-annotated in nested method function
            validator: Validator = Validator()
            
            # Tuple unpacking in nested method function
            model, view = Model(), View()
            return model.process()
        
        return tester.execute()

# Should not match these:
not_a_class = function_call()
also_not_class = my_var.method()
"""

    result: Dict[str, str] = extractor.extract_instantiations_ts(file_source)
    
    # Expected instantiations
    expected: Dict[str, str] = {
        "calculator": "Calculator",
        "parser": "ArgumentParser",
        "config": "Configuration",
        "validator": "DataValidator",
        "formatter": "OutputFormatter",
        "processor": "DataProcessor",
        "logger": "Logger",
        "cache": "Cache",
        "client": "Client",
        "server": "Server",
        "self.helper": "HelperClass",
        "self.config": "Config",
        "tester": "TestRunner",
        "reader": "FileReader",
        "writer": "FileWriter",
        "validator": "Validator",
        "model": "Model",
        "view": "View"
    }
    
    assert result == expected, f"Expected {expected}, got {result}"

def test_extract_instantiations_ts_with_complex_structures(extractor: PythonExtractFunctionCalls) -> None:
    """Test extraction of instantiations from complex Python code structures with nested elements."""
    file_source: str = """
# Procedural code with nested functions
def outer_function():
    # Instantiation in outer function
    logger = Logger()
    
    def inner_function():
        # Instantiation in inner function
        validator = Validator()
        return validator.validate()
    
    # Class instantiation in tuple unpacking within a function
    connection, session = DatabaseConnection(), SessionManager()
    
    return inner_function()

# Classes with nested methods and functions
class ComplexProcessor:
    def __init__(self):
        # Standard instantiation in constructor
        self.parser = ConfigParser()
        
    def process(self, data):
        # Attribute assignment in method
        self.helper = ProcessHelper()
        
        def local_processor():
            # Instantiation in a function inside a method
            transformer = DataTransformer()
            return transformer.transform(data)
        
        # Multiple instantiations in tuple unpacking in a method
        input_handler, output_handler = InputHandler(), OutputHandler()
        
        return local_processor()

# Procedural code after class definition
strategy = ProcessingStrategy()

# Should not match these
result = calculate_sum(10, 20)
data = process_list([1, 2, 3])
a, b = get_values(), fetch_data()  # Should not match as function names don't start with uppercase
"""

    result: Dict[str, str] = extractor.extract_instantiations_ts(file_source)
    
    # Expected instantiations
    expected: Dict[str, str] = {
        "logger": "Logger",
        "validator": "Validator",
        "connection": "DatabaseConnection",
        "session": "SessionManager",
        "self.parser": "ConfigParser",
        "self.helper": "ProcessHelper",
        "transformer": "DataTransformer",
        "input_handler": "InputHandler", 
        "output_handler": "OutputHandler",
        "strategy": "ProcessingStrategy"
    }
    
    assert result == expected, f"Expected {expected}, got {result}"

def test_extract_instantiations_ts_with_complex_assignments(extractor: PythonExtractFunctionCalls) -> None:
    """Test extraction of instantiations with more complex assignment patterns."""
    file_source: str = """
# Multiple assignments
b = MyClass()

e : MyDerivedClass = MyDerivedClass()

# Tuple unpacking (should match)
x, y = Point(), Vector()

# Attribute assignment (should match)
obj.attr = Helper()
"""

    result: Dict[str, str] = extractor.extract_instantiations_ts(file_source)
    
    # Should only match simple assignments
    expected: Dict[str, str] = {
        "b": "MyClass",
        "e": "MyDerivedClass",
        "x": "Point",
        "y": "Vector",
        "obj.attr": "Helper"
    }
    
    assert result == expected, f"Expected {expected}, got {result}"

def test_build_import_map(extractor: PythonExtractFunctionCalls) -> None:
    """Test building the import map from UnoplatImport objects."""
    # Create test imports with different scenarios
    imports = [
        # Scenario 1: Internal import with class (PascalCase) and function (snake_case)
        UnoplatImport(
            Source="package.module1",
            UsageName=[
                ImportedName(original_name="ClassA", alias=None),  # Class without alias
                ImportedName(original_name="ClassB", alias="AliasedClass"),  # Class with alias
                ImportedName(original_name="function_a", alias=None),  # Function without alias
                ImportedName(original_name="function_b", alias="aliased_func")  # Function with alias
            ],
            ImportType=ImportType.INTERNAL
        ),
        
        # Scenario 2: Another internal import with multiple classes and functions
        UnoplatImport(
            Source="package.module2",
            UsageName=[
                ImportedName(original_name="HelperClass", alias=None),
                ImportedName(original_name="DataProcessor", alias="Processor"),
                ImportedName(original_name="helper_function", alias=None)
            ],
            ImportType=ImportType.INTERNAL
        ),
        
        # Scenario 3: External import (should be ignored)
        UnoplatImport(
            Source="external.package",
            UsageName=[
                ImportedName(original_name="ExternalClass", alias=None)
            ],
            ImportType=ImportType.EXTERNAL
        ),
        
        # Scenario 4: Import with no usage_names (should be ignored)
        UnoplatImport(
            Source="package.empty",
            UsageName=None,
            ImportType=ImportType.INTERNAL
        )
    ]
    
    # Call the method being tested
    import_map = extractor._build_import_map(imports)
    
    # Expected results based on the rules:
    # - For PascalCase names: qualified_name = source.original_name
    # - For non-PascalCase names: qualified_name = source
    expected_map = {
        # From package.module1
        "ClassA": "package.module1.ClassA",  # Class without alias
        "AliasedClass": "package.module1.ClassB",  # Class with alias
        "function_a": "package.module1",  # Function without alias
        "aliased_func": "package.module1",  # Function with alias
        
        # From package.module2
        "HelperClass": "package.module2.HelperClass",  # Class without alias
        "Processor": "package.module2.DataProcessor",  # Class with alias
        "helper_function": "package.module2"  # Function without alias
    }
    
    # Verify the results
    assert import_map == expected_map, f"Expected {expected_map}, got {import_map}"

def test_extract_function_calls_from_content(extractor: PythonExtractFunctionCalls) -> None:
    """Test extraction of function calls from Python code with different call patterns."""
    # Sample Python code with various function call patterns
    code_content: str = '''
def sample_function():
    # Simple function calls
    print("Hello, world!")
    calculate_sum(1, 2, 3)
    
    # Method calls on objects
    calculator = Calculator()  # This is an instantiation, not a function call
    result = calculator.add(5, 10)
    data.process(input_data)
    
    # Nested attribute calls
    config.database.connect()
    app.models.User.get_by_id(123)
    
    # Mixed patterns in a complex expression
    return process_data(calculator.multiply(data.value, 2))
'''

    # Call the method being tested
    function_calls: List[ChapiFunctionCall] = extractor._extract_function_calls_from_content(code_content)
    
    # Expected function calls (in order of appearance in the code)
    expected_calls: List[Dict[str, Optional[str]]] = [
        # Simple function calls
        {"function_name": "print", "node_name": None},
        {"function_name": "calculate_sum", "node_name": None},
        
        # Method calls on objects
        # Note: Calculator() is intentionally not listed as it's an object instantiation
        {"function_name": "add", "node_name": "calculator"},
        {"function_name": "process", "node_name": "data"},
        
        # Nested attribute calls
        {"function_name": "connect", "node_name": "config.database"},
        {"function_name": "get_by_id", "node_name": "app.models.User"},
        
        # Mixed patterns
        {"function_name": "process_data", "node_name": None},
        {"function_name": "multiply", "node_name": "calculator"},
    ]
    
    # Verify the number of extracted calls matches expected
    assert len(function_calls) == len(expected_calls), \
        f"Expected {len(expected_calls)} function calls, got {len(function_calls)}"
    
    # Verify each extracted call
    for i, (actual, expected) in enumerate(zip(function_calls, expected_calls)):
        # Test function name
        expected_function_name: str = expected["function_name"]  # type: ignore
        expected_node_name: Optional[str] = expected["node_name"]  # type: ignore
        
        assert actual.function_name == expected_function_name, \
            f"Call #{i+1}: Expected function_name='{expected_function_name}', got '{actual.function_name}'"
        
        # Test node name
        if expected_node_name is None:
            assert actual.node_name is None, \
                f"Call #{i+1}: Expected node_name=None, got '{actual.node_name}'"
        else:
            assert actual.node_name == expected_node_name, \
                f"Call #{i+1}: Expected node_name='{expected_node_name}', got '{actual.node_name}'"
        
        # Verify position is populated with correct field names
        assert actual.position is not None, f"Call #{i+1}: Position should not be None"
        
        # Access position fields with null checks
        if actual.position and actual.position.start_line is not None:
            assert actual.position.start_line > 0, f"Call #{i+1}: start_line should be positive"
        
        if actual.position and actual.position.start_line_position is not None:
            assert actual.position.start_line_position > 0, f"Call #{i+1}: start_line_position should be positive"
        
        if actual.position and actual.position.stop_line is not None:
            assert actual.position.stop_line > 0, f"Call #{i+1}: stop_line should be positive"
        
        if actual.position and actual.position.stop_line_position is not None:
            assert actual.position.stop_line_position > 0, f"Call #{i+1}: stop_line_position should be positive"

def test_extract_function_calls_no_duplicates(extractor: PythonExtractFunctionCalls) -> None:
    """Test that nested attribute method calls are not duplicated in the extracted calls."""
    code_content: str = '''
def sample_function():
    # Test nested attribute method calls
    config.database.connect()
    app.models.User.get_by_id(123)
    
    # Test method calls on subscripted objects
    data_list[0].process()
    
    # More complex nested chains
    client.config.database.settings.update({"timeout": 30})
'''

    # Call the method being tested
    function_calls: List[ChapiFunctionCall] = extractor._extract_function_calls_from_content(code_content)
    
    # Extract just the function names and node names for easier comparison
    extracted_calls = [(call.function_name, call.node_name) for call in function_calls]
    
    # Each call should appear exactly once
    expected_calls = [
        ("connect", "config.database"),
        ("get_by_id", "app.models.User"),
        ("process", "data_list[0]"),
        ("update", "client.config.database.settings")
    ]
    
    # Check that we have the right number of calls (no duplicates)
    assert len(function_calls) == len(expected_calls), \
        f"Expected {len(expected_calls)} function calls, got {len(function_calls)}"
    
    # Check that each expected call is in the results exactly once
    for expected in expected_calls:
        assert extracted_calls.count(expected) == 1, \
            f"Expected call {expected} to appear exactly once, but found {extracted_calls.count(expected)} occurrences"

def test_extract_nested_function_calls(extractor: PythonExtractFunctionCalls) -> None:
    """Test extraction of nested function calls (functions called within other function calls)."""
    code_content: str = '''
def sample_function():
    # Function calls inside other function calls
    print(str(123))
    result = process_data(calculate_sum(1, 2, 3))
    
    # Method calls inside function calls
    display(calculator.add(5, 10))
    save_result(data.process(input_data))
    
    # Deeply nested calls
    result = outer_function(middle_function(inner_function(x)))
    
    # Mixed nested calls with attribute access
    config.update(user.get_preferences(user.profile.get_id()))
    
    # Function call with multiple nested calls
    combined = combine(
        transform(data.values), 
        normalize(data.get_stats()),
        filter_items(items, lambda x: validate(x))
    )
'''

    # Call the method being tested
    function_calls: List[ChapiFunctionCall] = extractor._extract_function_calls_from_content(code_content)
    
    # Extract just the function names and node names for easier comparison
    extracted_calls = [(call.function_name, call.node_name) for call in function_calls]
    
    # Expected function calls in no particular order
    expected_calls = [
        # Outer and inner simple function calls
        ("print", None),
        ("str", None),
        ("process_data", None),
        ("calculate_sum", None),
        
        # Method calls inside function calls
        ("display", None),
        ("add", "calculator"),
        ("save_result", None),
        ("process", "data"),
        
        # Deeply nested calls
        ("outer_function", None),
        ("middle_function", None),
        ("inner_function", None),
        
        # Mixed nested calls
        ("update", "config"),
        ("get_preferences", "user"),
        ("get_id", "user.profile"),
        
        # Function call with multiple nested calls
        ("combine", None),
        ("transform", None),
        ("normalize", None),
        ("get_stats", "data"),
        ("filter_items", None),
        ("validate", None),
    ]
    
    # Check we have the right number of calls
    assert len(function_calls) == len(expected_calls), \
        f"Expected {len(expected_calls)} function calls, got {len(function_calls)}"
    
    # Check that each expected call is present in the results
    for expected in expected_calls:
        assert expected in extracted_calls, \
            f"Expected call {expected} was not found in extracted calls"

def test_extract_static_class_method_calls(extractor: PythonExtractFunctionCalls) -> None:
    """Test extraction of static class method calls (Class.method() pattern)."""
    code_content: str = '''
def sample_function():
    # Direct static method calls
    User.get_by_id(123)
    Math.sqrt(16)
    Config.get_setting("database")
    
    # Static methods with nested classes
    database.models.User.find_all()
    app.utils.FileHandler.read_file("config.json")
    
    # Static method calls with chaining
    result = Logger.get_instance().log("message")
    items = Repository.get_instance().find_by_criteria({"type": "active"})
    
    # Static method calls with parameters that are themselves static calls
    processed_data = DataProcessor.process(
        Config.get_database_settings(),
        Validator.validate(InputData.parse("raw_data"))
    )
    
    # Mixed static and instance calls
    user = User.find_by_email("test@example.com")
    profile = user.get_profile()  # This is an instance method call, not a static call
    
    # Using imported classes with static methods
    result = MathUtil.calculate(Values.PI, 5)
    timestamp = DateUtils.now().format("YYYY-MM-DD")
'''

    # Call the method being tested
    function_calls: List[ChapiFunctionCall] = extractor._extract_function_calls_from_content(code_content)
    
    # Extract just the function names and node names for easier comparison
    extracted_calls = [(call.function_name, call.node_name) for call in function_calls]
    
    # Expected static class method calls (class name as node_name)
    expected_static_calls = [
        # Direct static method calls
        ("get_by_id", "User"),
        ("sqrt", "Math"),
        ("get_setting", "Config"),
        
        # Nested class static methods
        ("find_all", "database.models.User"),
        ("read_file", "app.utils.FileHandler"),
        
        # Static method calls with chaining
        ("get_instance", "Logger"),
        ("log", None),  # This will be None since it's on the return value of get_instance()
        ("get_instance", "Repository"),
        ("find_by_criteria", None),  # Similar to above
        
        # Nested static calls
        ("process", "DataProcessor"),
        ("get_database_settings", "Config"),
        ("validate", "Validator"),
        ("parse", "InputData"),
        
        # Mixed static and instance calls
        ("find_by_email", "User"),
        ("get_profile", "user"),  # Instance method
        
        # Imported class static methods
        ("calculate", "MathUtil"),
        ("now", "DateUtils"),
        ("format", None)  # Method on return value of DateUtils.now()
    ]
    
    # Verify all expected static calls are present
    for expected in expected_static_calls:
        assert expected in extracted_calls, \
            f"Expected call {expected} was not found in extracted calls"
    
    # Check that static class methods are properly captured
    static_class_calls = [call for call in function_calls 
                          if call.node_name and call.node_name[0].isupper()]
    
    # Verify we captured the correct number of static class method calls
    # Count expected calls where node_name starts with uppercase (static class)
    expected_static_class_count = sum(1 for _, node_name in expected_static_calls 
                                      if node_name and node_name[0].isupper())
    
    assert len(static_class_calls) == expected_static_class_count, \
        f"Expected {expected_static_class_count} static class method calls, got {len(static_class_calls)}"

def test_process_function_call(extractor: PythonExtractFunctionCalls) -> None:
    """Test the _process_function_call method that links function calls to their targets."""
    # 1. Setup test data
    
    # 1.1 Create a ChapiNode with functions to test local procedure calls
    node: ChapiNode = ChapiNode(
        NodeName="test_module",
        Functions=[
            ChapiFunction(Name="local_function"),
            ChapiFunction(Name="another_local_function")
        ]
    )
    
    # 1.2 Create object instantiation map (maps variables to class names)
    inst_map: Dict[str, str] = {
        "calculator": "Calculator",
        "parser": "ArgumentParser",
        "db": "Database",
        "client": "ApiClient",
        "self.validator": "Validator"
    }
    
    # 1.3 Create import map (maps local names to qualified names)
    # Similar to test_build_import_map but simplified
    import_map: Dict[str, str] = {
        # Class imports (qualified name is "source.original_name")
        "Calculator": "math.utils.Calculator",
        "ArgumentParser": "argparse.ArgumentParser",
        "Database": "db.models.Database",
        "ApiClient": "api.client.ApiClient",
        "Validator": "utils.validation.Validator",
        
        # Function imports (qualified name is just "source")
        "parse_config": "config.utils",
        "format_output": "output.formatter",
        
        # Static class methods (qualified name includes class)
        "User": "models.auth.User",
        "Math": "math.utils.Math"
    }
    
    # 2. Create test cases - different types of function calls
    
    # 2.1 Method call on an object (with class in import_map)
    call1: ChapiFunctionCall = ChapiFunctionCall(
        FunctionName="add",
        NodeName="calculator"
    )
    
    # 2.2 Method call on an object (class not in import_map)
    call2: ChapiFunctionCall = ChapiFunctionCall(
        FunctionName="process",
        NodeName="processor"  # Not in inst_map
    )
    
    # 2.3 Local procedure call
    call3: ChapiFunctionCall = ChapiFunctionCall(
        FunctionName="local_function"  # Matches a function in the node
    )
    
    # 2.4 Imported function call
    call4: ChapiFunctionCall = ChapiFunctionCall(
        FunctionName="parse_config"  # In import_map as a function
    )
    
    # 2.5 Static class method call
    call5: ChapiFunctionCall = ChapiFunctionCall(
        FunctionName="get_by_id",
        NodeName="User"  # In import_map as a class
    )
    
    # 2.6 Method call on an attribute object
    call6: ChapiFunctionCall = ChapiFunctionCall(
        FunctionName="validate",
        NodeName="self.validator"  # In inst_map
    )
    
    # 3. Process each call
    processed_calls: List[ChapiFunctionCall] = []
    processed_calls.append(extractor._process_function_call(call1, inst_map, import_map, node) or call1)
    processed_calls.append(extractor._process_function_call(call2, inst_map, import_map, node) or call2)
    processed_calls.append(extractor._process_function_call(call3, inst_map, import_map, node) or call3)
    processed_calls.append(extractor._process_function_call(call4, inst_map, import_map, node) or call4)
    processed_calls.append(extractor._process_function_call(call5, inst_map, import_map, node) or call5)
    processed_calls.append(extractor._process_function_call(call6, inst_map, import_map, node) or call6)
    
    # 4. Verify the results
    
    # 4.1 Method call on an object with class in import_map
    assert processed_calls[0].node_name == "math.utils.Calculator"
    assert processed_calls[0].function_name == "add"
    assert processed_calls[0].type == FunctionCallType.INTERNAL_CODEBASE.value
    
    # 4.2 Method call on an object with class not in import_map
    assert processed_calls[1].node_name == "processor"  # Unchanged
    assert processed_calls[1].function_name == "process"
    assert processed_calls[1].type == FunctionCallType.UNKNOWN.value
    
    # 4.3 Local procedure call
    assert processed_calls[2].node_name is None
    assert processed_calls[2].function_name == "local_function"
    assert processed_calls[2].type == FunctionCallType.SAME_FILE.value
    
    # 4.4 Imported function call
    assert processed_calls[3].node_name == "config.utils"
    assert processed_calls[3].function_name == "parse_config"
    assert processed_calls[3].type == FunctionCallType.INTERNAL_CODEBASE.value
    
    # 4.5 Static class method call
    assert processed_calls[4].node_name == "models.auth.User"
    assert processed_calls[4].function_name == "get_by_id"
    assert processed_calls[4].type == FunctionCallType.INTERNAL_CODEBASE.value
    
    # 4.6 Method call on an attribute object
    assert processed_calls[5].node_name == "utils.validation.Validator"
    assert processed_calls[5].function_name == "validate"
    assert processed_calls[5].type == FunctionCallType.INTERNAL_CODEBASE.value

# def test_process_function_call_comprehensive(extractor: PythonExtractFunctionCalls) -> None:
#     """Test the _process_function_call method with the improved logic and all possible cases."""
#     # 1. Setup test data
    
#     # 1.1 Create a ChapiNode with functions to test local procedure calls
#     procedural_node: ChapiNode = ChapiNode(
#         NodeName="test_module",
#         Type="",  # Empty type for procedural node
#         Functions=[
#             ChapiFunction(Name="local_function"),
#             ChapiFunction(Name="another_local_function")
#         ]
#     )
    
#     # 1.2 Create a class node to test method calls
#     class_node: ChapiNode = ChapiNode(
#         NodeName="TestClass",
#         Type="CLASS",
#         Functions=[
#             ChapiFunction(Name="class_method"),
#             ChapiFunction(Name="another_class_method")
#         ]
#     )
    
#     # 1.3 Create object instantiation map (maps variables to class names)
#     inst_map: Dict[str, str] = {
#         "calculator": "Calculator",
#         "parser": "ArgumentParser",
#         "db": "Database",
#         "client": "ApiClient",
#         "self.validator": "Validator",
#         "logger": "Logger"
#     }
    
#     # 1.4 Create import map (maps local names to qualified names)
#     import_map: Dict[str, str] = {
#         # Class imports (qualified name is "source.original_name")
#         "Calculator": "math.utils.Calculator",
#         "ArgumentParser": "argparse.ArgumentParser",
#         "Database": "db.models.Database",
#         "ApiClient": "api.client.ApiClient",
#         "Validator": "utils.validation.Validator",
#         "Logger": "logging.Logger",
        
#         # Static classes (directly importable)
#         "User": "models.auth.User",
#         "Math": "math.utils.Math",
#         "Config": "config.settings.Config",
        
#         # Function imports (qualified name is just "source")
#         "parse_config": "config.utils",
#         "format_output": "output.formatter"
#     }
    
#     # 2. Create test cases for ALL POSSIBLE SCENARIOS
    
#     # 2.1 Same file procedure call in procedural node - direct call
#     call1: ChapiFunctionCall = ChapiFunctionCall(
#         FunctionName="local_function",  # Matches a function in the procedural node
#         NodeName=None  # Direct call has no node_name
#     )
    
#     # 2.2 Same file class method call - direct call without self (will be processed in class_node)
#     call2: ChapiFunctionCall = ChapiFunctionCall(
#         FunctionName="class_method",  # Matches a method in the class node
#         NodeName=None  # Direct call has no node_name
#     )
    
#     # 2.3 Self-referencing class method call (will be processed in class_node)
#     call3: ChapiFunctionCall = ChapiFunctionCall(
#         FunctionName="another_class_method",
#         NodeName="self"  # Self reference
#     )
    
#     # 2.4 Static class method call
#     call4: ChapiFunctionCall = ChapiFunctionCall(
#         FunctionName="get_by_id",
#         NodeName="User"  # In import_map as a class
#     )
    
#     # 2.5 Imported function call - without node_name
#     call5: ChapiFunctionCall = ChapiFunctionCall(
#         FunctionName="parse_config"  # In import_map as a function
#     )
    
#     # 2.6 Method call on an instance - need both inst_map and import_map
#     call6: ChapiFunctionCall = ChapiFunctionCall(
#         FunctionName="add",
#         NodeName="calculator"  # In inst_map, which points to a class in import_map
#     )
    
#     # 2.7 Method call on an instance - in inst_map but class not in import_map
#     call7: ChapiFunctionCall = ChapiFunctionCall(
#         FunctionName="read",
#         NodeName="unknown_obj"  # Not in inst_map
#     )
    
#     # 2.8 Function call not found anywhere - should be UNKNOWN
#     call8: ChapiFunctionCall = ChapiFunctionCall(
#         FunctionName="unknown_function"  # Not local, not imported
#     )
    
#     # 3. Process each call for procedural node
#     procedural_calls: List[ChapiFunctionCall] = []
#     procedural_calls.append(extractor._process_function_call(call1, inst_map, import_map, procedural_node) or call1)  # Should match as local
#     procedural_calls.append(extractor._process_function_call(call2, inst_map, import_map, procedural_node) or call2)  # Should not match as local
#     procedural_calls.append(extractor._process_function_call(call4, inst_map, import_map, procedural_node) or call4)  # Static class
#     procedural_calls.append(extractor._process_function_call(call5, inst_map, import_map, procedural_node) or call5)  # Imported function
#     procedural_calls.append(extractor._process_function_call(call6, inst_map, import_map, procedural_node) or call6)  # Instance method
#     procedural_calls.append(extractor._process_function_call(call7, inst_map, import_map, procedural_node) or call7)  # Unknown instance
#     procedural_calls.append(extractor._process_function_call(call8, inst_map, import_map, procedural_node) or call8)  # Unknown function
    
#     # 4. Process self-referencing calls for class node
#     class_calls: List[ChapiFunctionCall] = []
#     class_calls.append(extractor._process_function_call(call2, inst_map, import_map, class_node) or call2)  # Direct method call
#     class_calls.append(extractor._process_function_call(call3, inst_map, import_map, class_node) or call3)  # Self-referencing method
    
#     # 5. Verify the results for procedural node
    
#     # 5.1 Same file function call
#     assert procedural_calls[0].type == FunctionCallType.SAME_FILE.value
#     assert procedural_calls[0].node_name is None
#     assert procedural_calls[0].function_name == "local_function"
    
#     # 5.2 Class method called directly from procedural code - should be UNKNOWN
#     assert procedural_calls[1].type == FunctionCallType.UNKNOWN.value
#     assert procedural_calls[1].node_name is None
#     assert procedural_calls[1].function_name == "class_method"
    
#     # 5.3 Static class method
#     assert procedural_calls[2].type == FunctionCallType.INTERNAL_CODEBASE.value
#     assert procedural_calls[2].node_name == "models.auth.User"
#     assert procedural_calls[2].function_name == "get_by_id"
    
#     # 5.4 Imported function
#     assert procedural_calls[3].type == FunctionCallType.INTERNAL_CODEBASE.value
#     assert procedural_calls[3].function_name == "parse_config"
#     assert procedural_calls[3].node_name == "config.utils"
    
#     # 5.5 Instance method with known class
#     assert procedural_calls[4].type == FunctionCallType.INTERNAL_CODEBASE.value
#     assert procedural_calls[4].node_name == "math.utils.Calculator"
#     assert procedural_calls[4].function_name == "add"
    
#     # 5.6 Unknown instance - should be UNKNOWN
#     assert procedural_calls[5].type == FunctionCallType.UNKNOWN.value
#     assert procedural_calls[5].node_name == "unknown_obj"  # Unchanged
#     assert procedural_calls[5].function_name == "read"
    
#     # 5.7 Unknown function - should be UNKNOWN
#     assert procedural_calls[6].type == FunctionCallType.UNKNOWN.value
#     assert procedural_calls[6].node_name is None
#     assert procedural_calls[6].function_name == "unknown_function"
    
#     # 6. Verify results for class node
    
#     # 6.1 Direct class method call without self
#     assert class_calls[0].type == FunctionCallType.SAME_FILE.value
#     assert class_calls[0].node_name is None
#     assert class_calls[0].function_name == "class_method"
    
#     # 6.2 Self-referencing method call
#     assert class_calls[1].type == FunctionCallType.SAME_FILE.value
#     assert class_calls[1].node_name is None  # Should clear node_name for self-references
#     assert class_calls[1].function_name == "another_class_method"

def test_handle_procedural_code(extractor: PythonExtractFunctionCalls) -> None:
    """
    Test handle_procedural_code method that processes a purely procedural file with no classes.
    
    This tests both scenarios:
    1. Linking calls to other procedures in the same file
    2. Linking calls to procedures or classes in other parts of the codebase
    """
    # 1. Set up test data
    
    # 1.1 Create a sample Python code that contains only procedural functions
    entire_code: str = """
# Some utility functions in a purely procedural file

def calculate_sum(a, b, c):
    # Internal function call to another procedure in the same file
    result = validate_numbers(a, b, c)
    if result:
        return a + b + c
    return 0

def validate_numbers(a, b, c):
    # Call to imported function from another file
    log_validation("Validating numbers")
    
    # Call to imported class method
    validator = InputValidator()
    if not validator.is_valid(a, b, c):
        return False
    
    # Call to imported static class method
    if not MathUtils.are_positive(a, b, c):
        return False
    
    return True

def process_data(data):
    # Call to another procedure in same file
    sum_value = calculate_sum(data.x, data.y, data.z)
    
    # Call to database service (imported class)
    db = DatabaseService()
    db.save(data.id, sum_value)
    
    # Call to static config class (imported)
    if Config.is_debug_mode():
        # Call to a function from logger module (imported)
        debug_log("Processed data with sum: " + str(sum_value))
    
    return sum_value

def main():
    # Import instance variable with imported class
    processor = DataProcessor()
    result = processor.process({})
    
    # Call to another procedure in same file
    processed = process_data(result)
    
    # Call to imported function from another module
    format_output(processed)
    
    return processed
"""

    # 1.2 Create a ChapiNode representing this procedural code with multiple functions
    node: ChapiNode = ChapiNode(
        NodeName="sample_utils",  # File name typically becomes the node name for procedural code
        Type="",  # Empty type indicates procedural node
        Functions=[
            ChapiFunction(
                Name="calculate_sum",
                Content="""def calculate_sum(a, b, c):
    # Internal function call to another procedure in the same file
    result = validate_numbers(a, b, c)
    if result:
        return a + b + c
    return 0"""
            ),
            ChapiFunction(
                Name="validate_numbers",
                Content="""def validate_numbers(a, b, c):
    # Call to imported function from another file
    log_validation("Validating numbers")
    
    # Call to imported class method
    validator = InputValidator()
    if not validator.is_valid(a, b, c):
        return False
    
    # Call to imported static class method
    if not MathUtils.are_positive(a, b, c):
        return False
    
    return True"""
            ),
            ChapiFunction(
                Name="process_data",
                Content="""def process_data(data):
    # Call to another procedure in same file
    sum_value = calculate_sum(data.x, data.y, data.z)
    
    # Call to database service (imported class)
    db = DatabaseService()
    db.save(data.id, sum_value)
    
    # Call to static config class (imported)
    if Config.is_debug_mode():
        # Call to a function from logger module (imported)
        debug_log("Processed data with sum: " + str(sum_value))
    
    return sum_value"""
            ),
            ChapiFunction(
                Name="main",
                Content="""def main():
    # Import instance variable with imported class
    processor = DataProcessor()
    result = processor.process({})
    
    # Call to another procedure in same file
    processed = process_data(result)
    
    # Call to imported function from another module
    format_output(processed)
    
    return processed"""
            )
        ]
    )

    # 1.3 Create a list of UnoplatImport objects representing imported entities
    imports: List[UnoplatImport] = [
        # Class imports
        UnoplatImport(
            Source="validators.input",
            UsageName=[
                ImportedName(original_name="InputValidator", alias=None)
            ],
            ImportType=ImportType.INTERNAL
        ),
        UnoplatImport(
            Source="services.database",
            UsageName=[
                ImportedName(original_name="DatabaseService", alias=None)
            ],
            ImportType=ImportType.INTERNAL
        ),
        UnoplatImport(
            Source="utils.math",
            UsageName=[
                ImportedName(original_name="MathUtils", alias=None)
            ],
            ImportType=ImportType.INTERNAL
        ),
        UnoplatImport(
            Source="config.settings",
            UsageName=[
                ImportedName(original_name="Config", alias=None)
            ],
            ImportType=ImportType.INTERNAL
        ),
        UnoplatImport(
            Source="processors.data",
            UsageName=[
                ImportedName(original_name="DataProcessor", alias=None)
            ],
            ImportType=ImportType.INTERNAL
        ),
        
        # Function imports
        UnoplatImport(
            Source="logger.debug",
            UsageName=[
                ImportedName(original_name="debug_log", alias=None)
            ],
            ImportType=ImportType.INTERNAL
        ),
        UnoplatImport(
            Source="validators.log",
            UsageName=[
                ImportedName(original_name="log_validation", alias=None)
            ],
            ImportType=ImportType.INTERNAL
        ),
        UnoplatImport(
            Source="formatter.output",
            UsageName=[
                ImportedName(original_name="format_output", alias=None)
            ],
            ImportType=ImportType.INTERNAL
        )
    ]

    # 2. Call the method being tested
    extractor.handle_procedural_code(node, imports, entire_code)

    # 3. Verify results
    
    # 3.1 All functions should have their function_calls populated
    if node.functions:  # Add null check
        for function in node.functions:
            assert function.function_calls is not None
            assert len(function.function_calls) > 0, f"Function {function.name} should have function calls"

    # 3.2 Verify specific function calls in each function
    assert node.functions is not None, "Node should have functions"
    
    # Verify calculate_sum function calls
    calculate_sum_fn = next(f for f in node.functions if f.name == "calculate_sum")
    assert calculate_sum_fn.function_calls is not None, "calculate_sum should have function calls"
    validate_call = next(call for call in calculate_sum_fn.function_calls if call.function_name == "validate_numbers")
    assert validate_call.type == FunctionCallType.SAME_FILE.value
    assert validate_call.node_name is None  # Same file procedure calls don't have node_name
    
    # Verify validate_numbers function calls
    validate_fn = next(f for f in node.functions if f.name == "validate_numbers")
    assert validate_fn.function_calls is not None, "validate_numbers should have function calls"
    
    # Check the log_validation call (imported function)
    log_call = next(call for call in validate_fn.function_calls if call.function_name == "log_validation")
    assert log_call.type == FunctionCallType.INTERNAL_CODEBASE.value
    assert log_call.node_name == "validators.log"  # For imported functions, node_name is set to the qualified name
    
    # Check the validator.is_valid call (method on instance of imported class)
    validator_call = next(call for call in validate_fn.function_calls if call.function_name == "is_valid")
    assert validator_call.type == FunctionCallType.INTERNAL_CODEBASE.value
    assert validator_call.node_name == "validators.input.InputValidator"
    
    # Check the MathUtils.are_positive call (static class method)
    math_call = next(call for call in validate_fn.function_calls if call.function_name == "are_positive")
    assert math_call.type == FunctionCallType.INTERNAL_CODEBASE.value
    assert math_call.node_name == "utils.math.MathUtils"
    
    # Verify process_data function calls
    process_fn = next(f for f in node.functions if f.name == "process_data")
    assert process_fn.function_calls is not None, "process_data should have function calls"
    
    # Check the calculate_sum call (same file procedure)
    calc_call = next(call for call in process_fn.function_calls if call.function_name == "calculate_sum")
    assert calc_call.type == FunctionCallType.SAME_FILE.value
    
    # Check the db.save call (method on instance of imported class)
    db_call = next(call for call in process_fn.function_calls if call.function_name == "save")
    assert db_call.type == FunctionCallType.INTERNAL_CODEBASE.value
    assert db_call.node_name == "services.database.DatabaseService"
    
    # Check the Config.is_debug_mode call (static class method)
    config_call = next(call for call in process_fn.function_calls if call.function_name == "is_debug_mode")
    assert config_call.type == FunctionCallType.INTERNAL_CODEBASE.value
    assert config_call.node_name == "config.settings.Config"
    
    # Check the debug_log call (imported function)
    debug_call = next(call for call in process_fn.function_calls if call.function_name == "debug_log")
    assert debug_call.type == FunctionCallType.INTERNAL_CODEBASE.value
    assert debug_call.node_name == "logger.debug"  # For imported functions, node_name is set to qualified name
    
    # Verify main function calls
    main_fn = next(f for f in node.functions if f.name == "main")
    assert main_fn.function_calls is not None, "main should have function calls"
    
    # Check the processor.process call (method on instance of imported class)
    processor_call = next(call for call in main_fn.function_calls if call.function_name == "process")
    assert processor_call.type == FunctionCallType.INTERNAL_CODEBASE.value
    assert processor_call.node_name == "processors.data.DataProcessor"
    
    # Check the process_data call (same file procedure)
    process_call = next(call for call in main_fn.function_calls if call.function_name == "process_data")
    assert process_call.type == FunctionCallType.SAME_FILE.value
    
    # Check the format_output call (imported function)
    format_call = next(call for call in main_fn.function_calls if call.function_name == "format_output")
    assert format_call.type == FunctionCallType.INTERNAL_CODEBASE.value
    assert format_call.node_name == "formatter.output"  # For imported functions, node_name is set to qualified name

def test_handle_class_code(extractor: PythonExtractFunctionCalls) -> None:
    """
    Test handle_class_code method that processes functions/methods in a class node.
    
    This tests two scenarios:
    1. Linking method calls to other methods in the same class (both direct and self-referencing calls)
    2. Linking method calls to procedures or classes' functions in the codebase
    """
    # 1. Set up test data
    
    # 1.1 Create a sample Python code that contains a class with methods
    entire_code: str = """
# A class with multiple methods that call each other and external entities

class DataProcessor:
    def __init__(self, config):
        self.config = config
        self.logger = Logger()
        self.validator = InputValidator()
    
    def process_data(self, data):
        # Call to another method in the same class (direct call without self)
        if self.validate_input(data):
            # Call to a method on self
            result = self.calculate_result(data)
            
            # Call to external static class method
            if Config.is_debug_mode():
                # Call to method on instance variable
                self.logger.log("Processed data successfully")
            
            # Call to imported function
            format_output(result)
            
            return result
        return None
    
    def validate_input(self, data):
        # Call to method on instance variable
        if not self.validator.is_valid(data):
            # Call to external function
            log_validation("Invalid data detected")
            return False
        
        # Call to static class method
        if not MathUtils.validate_numbers(data.values):
            return False
        
        return True
    
    def calculate_result(self, data):
        # Call another method in same class using self
        if self.validate_input(data):
            # Call to external function
            result = perform_calculation(data.x, data.y)
            
            # Call to another method in same class (direct call)
            self.log_result(result)
            
            return result
        return 0
    
    def log_result(self, result):
        # Call to method on instance variable
        self.logger.log(f"Result: {result}")
        
        # Call to external static class method
        if DatabaseConfig.is_persistence_enabled():
            # Call to external class instance method
            db = DatabaseService()
            db.save_result(result)
"""

    # 1.2 Create a ChapiNode representing this class
    node: ChapiNode = ChapiNode(
        NodeName="DataProcessor",
        Type="CLASS",  # Type is CLASS for class nodes
        Functions=[
            ChapiFunction(
                Name="__init__",
                Content="""def __init__(self, config):
        self.config = config
        self.logger = Logger()
        self.validator = InputValidator()"""
            ),
            ChapiFunction(
                Name="process_data",
                Content="""def process_data(self, data):
        # Call to another method in the same class (direct call without self)
        if self.validate_input(data):
            # Call to a method on self
            result = self.calculate_result(data)
            
            # Call to external static class method
            if Config.is_debug_mode():
                # Call to method on instance variable
                self.logger.log("Processed data successfully")
            
            # Call to imported function
            format_output(result)
            
            return result
        return None"""
            ),
            ChapiFunction(
                Name="validate_input",
                Content="""def validate_input(self, data):
        # Call to method on instance variable
        if not self.validator.is_valid(data):
            # Call to external function
            log_validation("Invalid data detected")
            return False
        
        # Call to static class method
        if not MathUtils.validate_numbers(data.values):
            return False
        
        return True"""
            ),
            ChapiFunction(
                Name="calculate_result",
                Content="""def calculate_result(self, data):
        # Call another method in same class using self
        if self.validate_input(data):
            # Call to external function
            result = perform_calculation(data.x, data.y)
            
            # Call to another method in same class (direct call)
            self.log_result(result)
            
            return result
        return 0"""
            ),
            ChapiFunction(
                Name="log_result",
                Content="""def log_result(self, result):
        # Call to method on instance variable
        self.logger.log(f"Result: {result}")
        
        # Call to external static class method
        if DatabaseConfig.is_persistence_enabled():
            # Call to external class instance method
            db = DatabaseService()
            db.save_result(result)"""
            )
        ]
    )

    # 1.3 Create a list of UnoplatImport objects representing imported entities
    imports: List[UnoplatImport] = [
        # Class imports
        UnoplatImport(
            Source="logging.utils",
            UsageName=[
                ImportedName(original_name="Logger", alias=None)
            ],
            ImportType=ImportType.INTERNAL
        ),
        UnoplatImport(
            Source="validators.input",
            UsageName=[
                ImportedName(original_name="InputValidator", alias=None)
            ],
            ImportType=ImportType.INTERNAL
        ),
        UnoplatImport(
            Source="config.settings",
            UsageName=[
                ImportedName(original_name="Config", alias=None)
            ],
            ImportType=ImportType.INTERNAL
        ),
        UnoplatImport(
            Source="utils.math",
            UsageName=[
                ImportedName(original_name="MathUtils", alias=None)
            ],
            ImportType=ImportType.INTERNAL
        ),
        UnoplatImport(
            Source="services.database",
            UsageName=[
                ImportedName(original_name="DatabaseService", alias=None)
            ],
            ImportType=ImportType.INTERNAL
        ),
        UnoplatImport(
            Source="config.database",
            UsageName=[
                ImportedName(original_name="DatabaseConfig", alias=None)
            ],
            ImportType=ImportType.INTERNAL
        ),
        
        # Function imports
        UnoplatImport(
            Source="formatter.output",
            UsageName=[
                ImportedName(original_name="format_output", alias=None)
            ],
            ImportType=ImportType.INTERNAL
        ),
        UnoplatImport(
            Source="validators.log",
            UsageName=[
                ImportedName(original_name="log_validation", alias=None)
            ],
            ImportType=ImportType.INTERNAL
        ),
        UnoplatImport(
            Source="calculation.math",
            UsageName=[
                ImportedName(original_name="perform_calculation", alias=None)
            ],
            ImportType=ImportType.INTERNAL
        )
    ]

    # 2. Call the method being tested
    extractor.handle_class_code(node, imports, entire_code)

    # 3. Verify results
    
    # 3.1 All non-init methods should have their function_calls populated
    assert node.functions is not None, "Node should have functions"
    for function in node.functions:
        assert function.function_calls is not None
        # Skip __init__ method since it only contains object instantiations, not function calls
        if function.name != "__init__":
            assert len(function.function_calls) > 0, f"Method {function.name} should have function calls"

    # 3.2 Verify specific function calls in each method
    
    # Verify process_data method calls
    process_data_method = next(f for f in node.functions if f.name == "process_data")
    assert process_data_method.function_calls is not None, "process_data should have function calls"
    
    # Check self.validate_input call (self-referencing method call)
    validate_call = next(call for call in process_data_method.function_calls 
                          if call.function_name == "validate_input")
    assert validate_call.type == FunctionCallType.SAME_FILE.value
    assert validate_call.node_name is None  # node_name should be cleared for self references
    
    # Check self.calculate_result call (self-referencing method call)
    calculate_call = next(call for call in process_data_method.function_calls 
                           if call.function_name == "calculate_result")
    assert calculate_call.type == FunctionCallType.SAME_FILE.value
    assert calculate_call.node_name is None  # node_name should be cleared for self references
    
    # Check Config.is_debug_mode call (static class method)
    config_call = next(call for call in process_data_method.function_calls 
                        if call.function_name == "is_debug_mode")
    assert config_call.type == FunctionCallType.INTERNAL_CODEBASE.value
    assert config_call.node_name == "config.settings.Config"
    
    # Check self.logger.log call (method on instance variable)
    logger_call = next(call for call in process_data_method.function_calls 
                        if call.function_name == "log" and call.node_name == "logging.utils.Logger")
    assert logger_call.type == FunctionCallType.INTERNAL_CODEBASE.value
    
    # Check format_output call (imported function)
    format_call = next(call for call in process_data_method.function_calls 
                        if call.function_name == "format_output")
    assert format_call.type == FunctionCallType.INTERNAL_CODEBASE.value
    assert format_call.node_name == "formatter.output"
    
    # Verify validate_input method calls
    validate_method = next(f for f in node.functions if f.name == "validate_input")
    assert validate_method.function_calls is not None, "validate_input should have function calls"
    
    # Check self.validator.is_valid call (method on instance variable)
    validator_call = next(call for call in validate_method.function_calls 
                           if call.function_name == "is_valid")
    assert validator_call.type == FunctionCallType.INTERNAL_CODEBASE.value
    assert validator_call.node_name == "validators.input.InputValidator"
    
    # Check log_validation call (imported function)
    log_call = next(call for call in validate_method.function_calls 
                     if call.function_name == "log_validation")
    assert log_call.type == FunctionCallType.INTERNAL_CODEBASE.value
    assert log_call.node_name == "validators.log"
    
    # Check MathUtils.validate_numbers call (static class method)
    math_call = next(call for call in validate_method.function_calls 
                      if call.function_name == "validate_numbers")
    assert math_call.type == FunctionCallType.INTERNAL_CODEBASE.value
    assert math_call.node_name == "utils.math.MathUtils"
    
    # Verify calculate_result method calls
    calculate_method = next(f for f in node.functions if f.name == "calculate_result")
    assert calculate_method.function_calls is not None, "calculate_result should have function calls"
    
    # Check self.validate_input call (self-referencing method call)
    validate_call = next(call for call in calculate_method.function_calls 
                          if call.function_name == "validate_input")
    assert validate_call.type == FunctionCallType.SAME_FILE.value
    assert validate_call.node_name is None  # node_name should be cleared for self references
    
    # Check perform_calculation call (imported function)
    perform_call = next(call for call in calculate_method.function_calls 
                         if call.function_name == "perform_calculation")
    assert perform_call.type == FunctionCallType.INTERNAL_CODEBASE.value
    assert perform_call.node_name == "calculation.math"
    
    # Check self.log_result call (self-referencing method call)
    log_result_call = next(call for call in calculate_method.function_calls 
                            if call.function_name == "log_result")
    assert log_result_call.type == FunctionCallType.SAME_FILE.value
    assert log_result_call.node_name is None  # node_name should be cleared for self references
    
    # Verify log_result method calls
    log_result_method = next(f for f in node.functions if f.name == "log_result")
    assert log_result_method.function_calls is not None, "log_result should have function calls"
    
    # Check self.logger.log call (method on instance variable)
    logger_call = next(call for call in log_result_method.function_calls 
                        if call.function_name == "log")
    assert logger_call.type == FunctionCallType.INTERNAL_CODEBASE.value
    assert logger_call.node_name == "logging.utils.Logger"
    
    # Check DatabaseConfig.is_persistence_enabled call (static class method)
    db_config_call = next(call for call in log_result_method.function_calls 
                           if call.function_name == "is_persistence_enabled")
    assert db_config_call.type == FunctionCallType.INTERNAL_CODEBASE.value
    assert db_config_call.node_name == "config.database.DatabaseConfig"
    
    # Check db.save_result call (method on instance of imported class)
    db_call = next(call for call in log_result_method.function_calls 
                    if call.function_name == "save_result")
    assert db_call.type == FunctionCallType.INTERNAL_CODEBASE.value
    assert db_call.node_name == "services.database.DatabaseService"