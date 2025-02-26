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


def test_multi_class_nodes(extractor: PythonExtractFunctionCalls) -> None:
    """
    Test function call linkage between multiple class nodes in the same file.
    
    This test focuses on scenario #4 from the Function Call Linkage specification:
    - Python file with multiple (1..n) class nodes
    - Processing each class node's functions to map calls to:
      1. Other methods in the same class node
      2. Methods in other classes in the same file
      3. External functions/classes from imports
    """
    # 1. Setup test data - Create multiple class nodes
    
    # 1.1 Create first class node - TestClass
    test_class_node: ChapiNode = ChapiNode(
        NodeName="TestClass",
        Type="CLASS",
        Functions=[
            ChapiFunction(Name="test_method"),
            ChapiFunction(Name="helper_method")
        ]
    )
    
    # 1.2 Create second class node - DataProcessor
    data_processor_node: ChapiNode = ChapiNode(
        NodeName="DataProcessor",
        Type="CLASS",
        Functions=[
            ChapiFunction(Name="process_data"),
            ChapiFunction(Name="validate_input")
        ]
    )
    
    # 1.3 Create third class node - Logger
    logger_node: ChapiNode = ChapiNode(
        NodeName="Logger",
        Type="CLASS",
        Functions=[
            ChapiFunction(Name="log"),
            ChapiFunction(Name="debug")
        ]
    )
    
    # 1.4 Create object instantiation map
    inst_map: Dict[str, str] = {
        "processor": "DataProcessor",     # Instance of another class in the same file
        "logger": "Logger",               # Instance of another class in the same file
        "external_obj": "ExternalClass",  # Instance of an imported class
        "self.helper": "HelperClass"      # Instance variable of an imported class
    }
    
    # 1.5 Create import map
    import_map: Dict[str, str] = {
        # Imported classes
        "ExternalClass": "external.module.ExternalClass",
        "HelperClass": "helpers.util.HelperClass",
        
        # Imported functions
        "format_data": "formatters.data_format"
    }
    
    # 1.6 Create class nodes map for testing cross-class calls
    class_nodes_map: Dict[str, ChapiNode] = {
        "TestClass": test_class_node,
        "DataProcessor": data_processor_node, 
        "Logger": logger_node
    }
    
    # 2. Create various function call scenarios
    
    # 2.1 Self-referencing method call (same class)
    call1: ChapiFunctionCall = ChapiFunctionCall(
        FunctionName="helper_method",
        NodeName="self"
    )
    
    # 2.2 Direct method call to another class (cross-class, same file)
    call2: ChapiFunctionCall = ChapiFunctionCall(
        FunctionName="process_data",
        NodeName="DataProcessor"
    )
    
    # 2.3 Method call on an instance of another class in the same file
    call3: ChapiFunctionCall = ChapiFunctionCall(
        FunctionName="validate_input",
        NodeName="processor"
    )
    
    # 2.4 Method call on an instance of an imported class
    call4: ChapiFunctionCall = ChapiFunctionCall(
        FunctionName="process",
        NodeName="external_obj"
    )
    
    # 2.5 Imported function call
    call5: ChapiFunctionCall = ChapiFunctionCall(
        FunctionName="format_data",
        NodeName=None
    )
    
    # 2.6 Method call on another instance (Logger class in the same file)
    call6: ChapiFunctionCall = ChapiFunctionCall(
        FunctionName="log",
        NodeName="logger"
    )
    
    # 2.7 Method call on an instance variable that is an imported class
    call7: ChapiFunctionCall = ChapiFunctionCall(
        FunctionName="assist",
        NodeName="self.helper"
    )
    
    # 3. Process each call in the TestClass context
    test_class_calls: List[ChapiFunctionCall] = []
    test_class_calls.append(extractor._process_function_call(call1, inst_map, import_map, test_class_node, class_nodes_map) or call1)  # Self-reference
    test_class_calls.append(extractor._process_function_call(call2, inst_map, import_map, test_class_node, class_nodes_map) or call2)  # Direct cross-class
    test_class_calls.append(extractor._process_function_call(call3, inst_map, import_map, test_class_node, class_nodes_map) or call3)  # Instance of another class
    test_class_calls.append(extractor._process_function_call(call4, inst_map, import_map, test_class_node, class_nodes_map) or call4)  # External class instance
    test_class_calls.append(extractor._process_function_call(call5, inst_map, import_map, test_class_node, class_nodes_map) or call5)  # Imported function
    test_class_calls.append(extractor._process_function_call(call6, inst_map, import_map, test_class_node, class_nodes_map) or call6)  # Logger instance
    test_class_calls.append(extractor._process_function_call(call7, inst_map, import_map, test_class_node, class_nodes_map) or call7)  # Instance variable
    
    # 4. Process the same calls in the DataProcessor context
    data_processor_calls: List[ChapiFunctionCall] = []
    # Create a new self-reference for DataProcessor's own methods
    dp_self_call: ChapiFunctionCall = ChapiFunctionCall(
        FunctionName="validate_input",
        NodeName="self"
    )
    data_processor_calls.append(extractor._process_function_call(dp_self_call, inst_map, import_map, data_processor_node, class_nodes_map) or dp_self_call)
    data_processor_calls.append(extractor._process_function_call(call2, inst_map, import_map, data_processor_node, class_nodes_map) or call2)  # Direct to self
    
    # 5. Verify results for TestClass calls
    
    # 5.1 Self-referencing method call
    assert test_class_calls[0].type == FunctionCallType.SAME_FILE.value
    assert test_class_calls[0].node_name is None  # Should clear node_name for self-references
    assert test_class_calls[0].function_name == "helper_method"
    
    # 5.2 Direct call to another class's method
    assert test_class_calls[1].type == FunctionCallType.SAME_FILE.value
    assert test_class_calls[1].node_name == "DataProcessor"  # Should keep class name
    assert test_class_calls[1].function_name == "process_data"
    
    # 5.3 Call to method on instance of another class
    assert test_class_calls[2].type == FunctionCallType.SAME_FILE.value
    assert test_class_calls[2].node_name == "DataProcessor"  # Should be updated to class name
    assert test_class_calls[2].function_name == "validate_input"
    
    # 5.4 Call to method on external class instance
    assert test_class_calls[3].type == FunctionCallType.INTERNAL_CODEBASE.value
    assert test_class_calls[3].node_name == "external.module.ExternalClass"
    assert test_class_calls[3].function_name == "process"
    
    # 5.5 Imported function call
    assert test_class_calls[4].type == FunctionCallType.INTERNAL_CODEBASE.value
    assert test_class_calls[4].node_name == "formatters.data_format"
    assert test_class_calls[4].function_name == "format_data"
    
    # 5.6 Call to method on Logger instance
    assert test_class_calls[5].type == FunctionCallType.SAME_FILE.value
    assert test_class_calls[5].node_name == "Logger"
    assert test_class_calls[5].function_name == "log"
    
    # 5.7 Call to method on instance variable with imported class
    assert test_class_calls[6].type == FunctionCallType.INTERNAL_CODEBASE.value
    assert test_class_calls[6].node_name == "helpers.util.HelperClass"
    assert test_class_calls[6].function_name == "assist"
    
    # 6. Verify results for DataProcessor calls
    
    # 6.1 Self-referencing method within DataProcessor
    assert data_processor_calls[0].type == FunctionCallType.SAME_FILE.value
    assert data_processor_calls[0].node_name is None
    assert data_processor_calls[0].function_name == "validate_input"
    
    # 6.2 Direct reference to own method (different context)
    assert data_processor_calls[1].type == FunctionCallType.SAME_FILE.value 
    assert data_processor_calls[1].node_name == "DataProcessor"  # Kept as DataProcessor since that's the node's name
    assert data_processor_calls[1].function_name == "process_data"

def test_extract_function_calls_with_multiple_classes(extractor: PythonExtractFunctionCalls) -> None:
    """
    Test the extract_function_calls method with a file containing multiple class nodes.
    
    This tests the end-to-end process for a file with multiple classes, ensuring that:
    1. Function calls between methods in the same class are correctly linked
    2. Function calls between different classes in the same file are correctly linked
    3. Function calls to external entities are correctly linked
    """
    # 1. Create test data
    
    # 1.1 Create sample Python code with multiple classes
    entire_code: str = """
class DataProcessor:
    def __init__(self, config):
        self.config = config
        self.logger = Logger()
        self.validator = InputValidator()
    
    def process_data(self, data):
        # Call to another method in the same class
        if self.validate_input(data):
            # Call to a method in another class in the same file
            formatter = OutputFormatter()
            formatted_data = formatter.format(data)
            
            # Call to a static method in another class in the same file
            if ConfigManager.is_debug_mode():
                self.logger.log("Processing data")
            
            # Call to external function
            result = perform_calculation(formatted_data)
            return result
        return None
    
    def validate_input(self, data):
        # Call to method on instance variable
        return self.validator.is_valid(data)

class OutputFormatter:
    def format(self, data):
        # Call to static method in another class in the same file
        if ConfigManager.get_format_type() == "json":
            return self.format_json(data)
        return self.format_text(data)
    
    def format_json(self, data):
        # Call to imported function
        return json_encode(data)
    
    def format_text(self, data):
        # Call to external function
        return str(data)

class ConfigManager:
    @staticmethod
    def is_debug_mode():
        return True
    
    @staticmethod
    def get_format_type():
        return "json"
"""

    # 1.2 Create ChapiNodes for the classes
    data_processor_node: ChapiNode = ChapiNode(
        NodeName="DataProcessor",
        Type="CLASS",
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
        # Call to another method in the same class
        if self.validate_input(data):
            # Call to a method in another class in the same file
            formatter = OutputFormatter()
            formatted_data = formatter.format(data)
            
            # Call to a static method in another class in the same file
            if ConfigManager.is_debug_mode():
                self.logger.log("Processing data")
            
            # Call to external function
            result = perform_calculation(formatted_data)
            return result
        return None"""
            ),
            ChapiFunction(
                Name="validate_input",
                Content="""def validate_input(self, data):
        # Call to method on instance variable
        return self.validator.is_valid(data)"""
            )
        ]
    )
    
    output_formatter_node: ChapiNode = ChapiNode(
        NodeName="OutputFormatter",
        Type="CLASS",
        Functions=[
            ChapiFunction(
                Name="format",
                Content="""def format(self, data):
        # Call to static method in another class in the same file
        if ConfigManager.get_format_type() == "json":
            return self.format_json(data)
        return self.format_text(data)"""
            ),
            ChapiFunction(
                Name="format_json",
                Content="""def format_json(self, data):
        # Call to imported function
        return json_encode(data)"""
            ),
            ChapiFunction(
                Name="format_text",
                Content="""def format_text(self, data):
        # Call to external function
        return str(data)"""
            )
        ]
    )
    
    config_manager_node: ChapiNode = ChapiNode(
        NodeName="ConfigManager",
        Type="CLASS",
        Functions=[
            ChapiFunction(
                Name="is_debug_mode",
                Content="""@staticmethod
    def is_debug_mode():
        return True"""
            ),
            ChapiFunction(
                Name="get_format_type",
                Content="""@staticmethod
    def get_format_type():
        return "json\""""
            )
        ]
    )
    
    # 1.3 Create file_path_nodes dictionary
    file_path_nodes: Dict[str, List[ChapiNode]] = {
        "test_file.py": [data_processor_node, output_formatter_node, config_manager_node]
    }
    
    # 1.4 Create imports
    imports: List[UnoplatImport] = [
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
            Source="json.utils",
            UsageName=[
                ImportedName(original_name="json_encode", alias=None)
            ],
            ImportType=ImportType.INTERNAL
        ),
        UnoplatImport(
            Source="math.calculations",
            UsageName=[
                ImportedName(original_name="perform_calculation", alias=None)
            ],
            ImportType=ImportType.INTERNAL
        )
    ]
    
    # 2. Call extract_function_calls
    result_nodes = extractor.extract_function_calls(file_path_nodes, imports, entire_code)
    
    # 3. Get the processed nodes
    processed_nodes = result_nodes["test_file.py"]
    data_processor = next(node for node in processed_nodes if node.node_name == "DataProcessor")
    output_formatter = next(node for node in processed_nodes if node.node_name == "OutputFormatter")
    config_manager = next(node for node in processed_nodes if node.node_name == "ConfigManager")
    
    # 4. Verify that all functions have their function_calls populated
    assert data_processor.functions is not None
    for function in data_processor.functions:
        if function.name != "__init__":  # Skip __init__ as it only has instantiations
            assert function.function_calls is not None
            assert len(function.function_calls) > 0
    
    assert output_formatter.functions is not None
    for function in output_formatter.functions:
        assert function.function_calls is not None
    
    # 5. Verify specific function calls
    
    # 5.1 Check calls in DataProcessor.process_data
    process_data_fn = next(f for f in data_processor.functions if f.name == "process_data")
    
    # Check call to self.validate_input (same-class method)
    validate_call = next(call for call in process_data_fn.function_calls if call.function_name == "validate_input")
    assert validate_call.type == FunctionCallType.SAME_FILE.value
    assert validate_call.node_name is None
    
    # Check call to formatter.format (cross-class method in same file)
    format_call = next(call for call in process_data_fn.function_calls if call.function_name == "format")
    assert format_call.type == FunctionCallType.SAME_FILE.value
    assert format_call.node_name == "OutputFormatter"
    
    # Check call to ConfigManager.is_debug_mode (static method in another class in same file)
    debug_call = next(call for call in process_data_fn.function_calls if call.function_name == "is_debug_mode")
    assert debug_call.type == FunctionCallType.SAME_FILE.value
    assert debug_call.node_name == "ConfigManager"
    
    # Check call to self.logger.log (method on instance of imported class)
    log_call = next(call for call in process_data_fn.function_calls if call.function_name == "log")
    assert log_call.type == FunctionCallType.INTERNAL_CODEBASE.value
    assert log_call.node_name == "logging.utils.Logger"
    
    # Check call to perform_calculation (imported function)
    calc_call = next(call for call in process_data_fn.function_calls if call.function_name == "perform_calculation")
    assert calc_call.type == FunctionCallType.INTERNAL_CODEBASE.value
    assert calc_call.node_name == "math.calculations"
    
    # 5.2 Check calls in OutputFormatter.format
    format_fn = next(f for f in output_formatter.functions if f.name == "format")
    
    # Check call to ConfigManager.get_format_type (static method in another class in same file)
    format_type_call = next(call for call in format_fn.function_calls if call.function_name == "get_format_type")
    assert format_type_call.type == FunctionCallType.SAME_FILE.value
    assert format_type_call.node_name == "ConfigManager"
    
    # Check call to self.format_json (same-class method)
    format_json_call = next(call for call in format_fn.function_calls if call.function_name == "format_json")
    assert format_json_call.type == FunctionCallType.SAME_FILE.value
    assert format_json_call.node_name is None
    
    # Check call to self.format_text (same-class method)
    format_text_call = next(call for call in format_fn.function_calls if call.function_name == "format_text")
    assert format_text_call.type == FunctionCallType.SAME_FILE.value
    assert format_text_call.node_name is None
    
    # 5.3 Check calls in OutputFormatter.format_json
    format_json_fn = next(f for f in output_formatter.functions if f.name == "format_json")
    
    # Check call to json_encode (imported function)
    json_call = next(call for call in format_json_fn.function_calls if call.function_name == "json_encode")
    assert json_call.type == FunctionCallType.INTERNAL_CODEBASE.value
    assert json_call.node_name == "json.utils"