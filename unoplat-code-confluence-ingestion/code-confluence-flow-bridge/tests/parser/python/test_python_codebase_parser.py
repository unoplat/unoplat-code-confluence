# Standard Library
import json
from pathlib import Path
from typing import Dict, List

# Third Party
import pytest

# First Party
from src.code_confluence_flow_bridge.models.chapi.chapi_node import ChapiNode
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_chapi_forge_node import UnoplatChapiForgeNode
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package import UnoplatPackage
from src.code_confluence_flow_bridge.models.configuration.settings import PackageManagerType, ProgrammingLanguageMetadata, ProgrammingLanguage
from src.code_confluence_flow_bridge.parser.python.python_codebase_parser import PythonCodebaseParser


class TestPythonCodebaseParser:
    @pytest.fixture
    def parser(self) -> PythonCodebaseParser:
        """Create PythonCodebaseParser instance."""
        return PythonCodebaseParser()

    @pytest.fixture
    def test_data_dir(self) -> Path:
        """Get path to test data directory."""
        return Path(__file__).parent.parent.parent / "test_data"

    @pytest.fixture
    def local_workspace_path_cc_cli(self, test_data_dir: Path) -> Path:
        """Get local workspace path."""
        return test_data_dir /"unoplat-code-confluence-cli"/"unoplat_code_confluence_cli"

    @pytest.fixture
    def source_directory_cc_cli(self, test_data_dir: Path) -> Path:
        """Get source directory path."""
        return test_data_dir/"unoplat-code-confluence-cli"

    @pytest.fixture
    def local_workspace_path_cci(self, test_data_dir: Path) -> Path:
        """Get local workspace path."""
        return test_data_dir /"unoplat-code-confluence-ingestion"/"code-confluence-flow-bridge"/"src"/"code_confluence_flow_bridge"

    @pytest.fixture
    def source_directory_cci(self, test_data_dir: Path) -> Path:
        """Get source directory path."""
        return test_data_dir/"unoplat-code-confluence-ingestion"/"code-confluence-flow-bridge"
     
    @pytest.fixture
    def programming_language_metadata(self) -> ProgrammingLanguageMetadata:
        """Create programming language metadata."""
        return ProgrammingLanguageMetadata(
            language=ProgrammingLanguage.PYTHON,
            package_manager=PackageManagerType.UV,
            language_version=">3.11"
        )
    
    @pytest.fixture
    def code_confluence_ingestion_data(self, local_workspace_path_cci: Path) -> List[Dict]:
        """Create code confluence ingestion data."""
        with open(local_workspace_path_cci/"code_confluence_ingestion.json", 'r') as f:
            json_data = json.load(f)
        return json_data
    

    @pytest.fixture
    def sample_json_data(self,source_directory_cc_cli: Path) -> List[Dict]:
        """Create sample JSON data representing Python nodes."""
        with open(source_directory_cc_cli/"0_codes.json", 'r') as f:
            json_data = json.load(f)
        return json_data    
    
    # def test_parse_codebase_ingestion(
    #     self,
    #     parser: PythonCodebaseParser,
    #     code_confluence_ingestion_data: List[Dict],
    #     local_workspace_path_cci: Path,
    #     source_directory_cci: Path,
    #     programming_language_metadata: ProgrammingLanguageMetadata
    # ) -> None:
    #     """Test basic codebase parsing functionality."""
    #     packages: List[UnoplatPackage] = parser.parse_codebase(
    #         codebase_name="test_codebase",
    #         json_data=code_confluence_ingestion_data,
    #         local_workspace_path=str(local_workspace_path_cci),
    #         source_directory=str(source_directory_cci),
    #         programming_language_metadata=programming_language_metadata
    #     )

    #     # Verify packages were created
    #     assert len(packages) > 0


    
    def test_parse_codebase_basic(
        self,
        parser: PythonCodebaseParser,
        sample_json_data: List[Dict],
        local_workspace_path_cc_cli: Path,
        source_directory_cc_cli: Path,
        programming_language_metadata: ProgrammingLanguageMetadata
    ) -> None:
        """Test basic codebase parsing functionality."""
        packages: List[UnoplatPackage] = parser.parse_codebase(
            codebase_name="test_codebase",
            json_data=sample_json_data,
            local_workspace_path=str(local_workspace_path_cc_cli),
            source_directory=str(source_directory_cc_cli),
            programming_language_metadata=programming_language_metadata
        )

        # Verify packages were created
        assert len(packages) > 0

        # # Check package structure
        # models_package = next(
        #     pkg for pkg in packages 
        #     if pkg.name == "src.code_confluence_flow_bridge.models"
        # )
        # assert models_package is not None

        # utils_package = next(
        #     pkg for pkg in packages 
        #     if pkg.name == "src.code_confluence_flow_bridge.utils"
        # )
        # assert utils_package is not None

        # # Check nodes in packages
        # class_nodes = models_package.nodes["/workspace/src/code_confluence_flow_bridge/models/my_class.py"]
        # assert len(class_nodes) == 1
        # assert class_nodes[0].node_name == "MyClass"
        # assert class_nodes[0].type == "CLASS"

        # function_nodes = utils_package.nodes["/workspace/src/code_confluence_flow_bridge/utils/helpers.py"]
        # assert len(function_nodes) == 1
        # assert function_nodes[0].node_name == "helper_function"
        # assert function_nodes[0].type == "FUNCTION"

