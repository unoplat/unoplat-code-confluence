# Standard Library
from pathlib import Path
from typing import Dict, List

# Third Party
import pytest

# First Party
from src.code_confluence_flow_bridge.models.chapi.chapi_node import ChapiNode
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_import import ImportedName, UnoplatImport
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_import_type import ImportType
from src.code_confluence_flow_bridge.models.configuration.settings import ProgrammingLanguage
from src.code_confluence_flow_bridge.parser.python.python_import_segregation_strategy import PythonImportSegregationStrategy
from src.code_confluence_flow_bridge.parser.tree_sitter.code_confluence_tree_sitter import CodeConfluenceTreeSitter


class TestPythonImportSegregationStrategy:
    """Test suite for Python import segregation using Tree-sitter."""

    @pytest.fixture
    def source_directory(self) -> str:
        """Get the source directory prefix for internal imports."""
        return "src.code_confluence_flow_bridge"

    @pytest.fixture
    def test_file_path(self) -> Path:
        """Get path to test file with basic imports."""
        return Path(__file__).parent.parent.parent / "test_data" / "python_files" / "sample_imports.py"

    @pytest.fixture
    def complex_file_path(self) -> Path:
        """Get path to test file with complex import scenarios."""
        return Path(__file__).parent.parent.parent / "test_data" / "python_files" / "internal_imports_scenarios.py"

    @pytest.fixture
    def workflow_file_path(self) -> Path:
        """Get path to test file with workflow imports."""
        return Path(__file__).parent.parent.parent / "test_data" / "python_files" / "workflow_imports.py"

    @pytest.fixture
    def tree_sitter(self) -> CodeConfluenceTreeSitter:
        """Create CodeConfluenceTreeSitter instance."""
        return CodeConfluenceTreeSitter(language=ProgrammingLanguage.PYTHON)

    @pytest.fixture
    def strategy(self, tree_sitter: CodeConfluenceTreeSitter) -> PythonImportSegregationStrategy:
        """Create PythonImportSegregationStrategy instance."""
        return PythonImportSegregationStrategy(tree_sitter)

    @pytest.fixture
    def basic_node(self, test_file_path: Path) -> ChapiNode:
        """Create ChapiNode instance for basic import testing."""
        return ChapiNode(
            NodeName="TestClass",
            Type="CLASS",
            FilePath=str(test_file_path),
            Package="src.code_confluence_flow_bridge"
        )

    @pytest.fixture
    def complex_node(self, complex_file_path: Path) -> ChapiNode:
        """Create ChapiNode instance for complex import testing."""
        return ChapiNode(
            NodeName="ComplexProcessor",
            Type="CLASS",
            FilePath=str(complex_file_path),
            Package="src.code_confluence_flow_bridge"
        )

    @pytest.fixture
    def workflow_node(self, workflow_file_path: Path) -> ChapiNode:
        """Create ChapiNode instance for workflow imports testing."""
        return ChapiNode(
            NodeName="WorkflowImports",
            Type="MODULE",
            FilePath=str(workflow_file_path),
            Package="src.code_confluence_flow_bridge"
        )

    def test_basic_internal_imports(
        self, 
        strategy: PythonImportSegregationStrategy, 
        basic_node: ChapiNode,
        source_directory: str
    ) -> None:
        """Test detection of basic internal imports at module level."""
        imports = strategy.process_imports(source_directory, basic_node)
        internal_imports = imports[ImportType.INTERNAL]
        
        # Verify total count of internal imports
        assert len(internal_imports) == 3, "Should find 3 internal imports"
        
        # Check specific imports and their usage names
        chapi_import = next(
            imp for imp in internal_imports 
            if imp.source == "src.code_confluence_flow_bridge.models.chapi.chapi_node"
        )
        assert len(chapi_import.usage_names) == 1
        assert chapi_import.usage_names[0].original_name == "ChapiNode"
        assert chapi_import.usage_names[0].alias is None
        
        # Check import with multiple names and aliases
        unoplat_import = next(
            imp for imp in internal_imports 
            if imp.source == "src.code_confluence_flow_bridge.models.chapi_forge.unoplat_import"
        )
        assert len(unoplat_import.usage_names) == 2
        
        # Verify each imported name and its alias
        imported_names = {
            name.original_name: name.alias 
            for name in unoplat_import.usage_names
        }
        assert imported_names == {
            "ImportedName": None,
            "UnoplatImport": None
        }

    def test_method_level_internal_imports(
        self, 
        strategy: PythonImportSegregationStrategy, 
        complex_node: ChapiNode,
        source_directory: str
    ) -> None:
        """Test detection of internal imports within class methods."""
        imports = strategy.process_imports(source_directory, complex_node)
        internal_imports = imports[ImportType.INTERNAL]
        
        # Check constructor import
        init_import = next(
            imp for imp in internal_imports
            if imp.source == "src.code_confluence_flow_bridge.models.chapi.chapi_node"
        )
        assert len(init_import.usage_names) == 1
        assert init_import.usage_names[0].original_name == "ChapiNode"
        assert init_import.usage_names[0].alias is None
        
        # Check process_data method imports with aliases
        unoplat_import = next(
            imp for imp in internal_imports
            if imp.source == "src.code_confluence_flow_bridge.models.chapi_forge.unoplat_import"
        )
        assert len(unoplat_import.usage_names) == 2
        
        # Verify each imported name and its alias
        imported_names = {
            (name.original_name, name.alias)
            for name in unoplat_import.usage_names
        }
        assert imported_names == {
            ("ImportedName", "Name"),
            ("UnoplatImport", "Import")
        }
        
        # Check code import without aliases
        code_import = next(
            imp for imp in internal_imports
            if imp.source == "src.code_confluence_flow_bridge.models.code"
        )
        assert len(code_import.usage_names) == 2
        assert {name.original_name for name in code_import.usage_names} == {"Function", "Class"}
        assert all(name.alias is None for name in code_import.usage_names)

    def test_conditional_and_function_internal_imports(
        self, 
        strategy: PythonImportSegregationStrategy, 
        complex_node: ChapiNode,
        source_directory: str
    ) -> None:
        """Test detection of internal imports in conditional blocks and functions."""
        imports = strategy.process_imports(source_directory, complex_node)
        internal_imports = imports[ImportType.INTERNAL]
        
        # Verify conditional import
        assert any(
            imp.source == "src.code_confluence_flow_bridge.analyzer.code_analyzer"
            and imp.usage_names[0].original_name == "CodeAnalyzer"
            for imp in internal_imports
        ), "Should find conditional import"
        
        # Verify function-level import
        assert any(
            imp.source == "src.code_confluence_flow_bridge.utils.helpers"
            and imp.usage_names[0].original_name == "format_output"
            for imp in internal_imports
        ), "Should find function-level import"

    def test_try_except_and_multiline_internal_imports(
        self, 
        strategy: PythonImportSegregationStrategy, 
        complex_node: ChapiNode,
        source_directory: str
    ) -> None:
        """Test detection of internal imports in try-except blocks and multi-line imports."""
        imports = strategy.process_imports(source_directory, complex_node)
        internal_imports = imports[ImportType.INTERNAL]
        
        # Check try-except block import
        feature_import = next(
            imp for imp in internal_imports
            if imp.source == "src.code_confluence_flow_bridge.experimental.feature"
        )
        assert len(feature_import.usage_names) == 1
        assert feature_import.usage_names[0].original_name == "ExperimentalFeature"
        assert feature_import.usage_names[0].alias is None
        
        # Check multi-item import with mix of aliased and non-aliased imports
        base_import = next(
            imp for imp in internal_imports
            if imp.source == "src.code_confluence_flow_bridge.models.base"
        )
        assert len(base_import.usage_names) == 3
        
        # Verify each imported name and its alias status
        imported_names = {
            (name.original_name, name.alias)
            for name in base_import.usage_names
        }
        assert imported_names == {
            ("BaseModel", None),
            ("BaseSchema", None),
            ("BaseConfig", "Config")
        }

    def test_workflow_internal_imports(
        self, 
        strategy: PythonImportSegregationStrategy, 
        workflow_node: ChapiNode,
        source_directory: str
    ) -> None:
        """Test detection of internal imports within workflow context manager."""
        imports = strategy.process_imports(source_directory, workflow_node)
        
        
        # Check internal imports
        internal_imports = imports[ImportType.INTERNAL]
        assert len(internal_imports) == 5, "Should find 5 internal imports"
        
        # Verify each internal import
        expected_imports = {
            "src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata": {
                ("UnoplatPackageManagerMetadata", None)
            },
            "src.code_confluence_flow_bridge.models.configuration.settings": {
                ("PackageManagerType", None),
                ("ProgrammingLanguage", None),
                ("ProgrammingLanguageMetadata", None)
            },
            "src.code_confluence_flow_bridge.processor.codebase_processing.codebase_processing_activity": {
                ("CodebaseProcessingActivity", None)
            },
            "src.code_confluence_flow_bridge.processor.package_metadata_activity.package_manager_metadata_activity": {
                ("PackageMetadataActivity", None)
            },
            "src.code_confluence_flow_bridge.processor.package_metadata_activity.package_manager_metadata_ingestion": {
                ("PackageManagerMetadataIngestion", None)
            }
        }
        
        # Check each import's source and imported names
        for imp in internal_imports:
            assert imp.source in expected_imports, f"Unexpected import source: {imp.source}"
            
            actual_names = {
                (name.original_name, name.alias) 
                for name in imp.usage_names
            }
            assert actual_names == expected_imports[imp.source], (
                f"Mismatched imported names for {imp.source}\n"
                f"Expected: {expected_imports[imp.source]}\n"
                f"Got: {actual_names}"
            )

    