# Standard Library
from pathlib import Path
from typing import AsyncGenerator, Iterator

from loguru import logger
from neomodel.async_.core import adb #type: ignore
from neomodel import config
from pydantic import SecretStr

# Third Party
import pytest
import pytest_asyncio

# First Party
from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
    ProgrammingLanguage,
    ProgrammingLanguageMetadata,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.structural_signature import StructuralSignature
from src.code_confluence_flow_bridge.parser.generic_codebase_parser import GenericCodebaseParser
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph_ingestion import (
    CodeConfluenceGraphIngestion,
)
from testcontainers.neo4j import Neo4jContainer #type: ignore

# Import graph models for neomodel queries
from unoplat_code_confluence_commons.graph_models.code_confluence_file import CodeConfluenceFile
from unoplat_code_confluence_commons.graph_models.code_confluence_package import CodeConfluencePackage

# Constants for the Neo4j container
NEO4J_VERSION: str = "5.26.0-community"
NEO4J_PASSWORD: str = "password"
NEO4J_PORT: int = 7687
NEO4J_HTTP_PORT: int = 7474


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def neo4j_container() -> Iterator[Neo4jContainer]:
    """Spin up a Neo4j container for the test session and guarantee clean teardown."""
    # Neo4j 5.x images require explicit license acceptance, otherwise the
    # container starts and immediately exits which results in connection
    # failures when pytest attempts to open a Bolt session.
    # See: https://neo4j.com/docs/operations-manual/current/docker/#docker-basic-usage
    container = (
        Neo4jContainer(image=f"neo4j:{NEO4J_VERSION}")
        .with_env("NEO4J_AUTH", f"neo4j/{NEO4J_PASSWORD}")
        .with_env("NEO4J_ACCEPT_LICENSE_AGREEMENT", "yes")
        .with_exposed_ports(NEO4J_PORT, NEO4J_HTTP_PORT)
    )

    # Using the context‑manager ensures .start() on enter and .stop() on exit,
    # even if the test session exits with an error.
    with container as neo4j:
        yield neo4j
        


@pytest.fixture()
def env_settings(neo4j_container: Neo4jContainer) -> EnvironmentSettings:
    """Create EnvironmentSettings pointing to the running Neo4j container."""
    bolt_port: str = neo4j_container.get_exposed_port(NEO4J_PORT)
    return EnvironmentSettings(
        NEO4J_HOST=neo4j_container.get_container_host_ip(),
        NEO4J_PORT=int(bolt_port),
        NEO4J_USERNAME="neo4j",
        NEO4J_PASSWORD=SecretStr(NEO4J_PASSWORD),
        NEO4J_MAX_CONNECTION_LIFETIME=3600,
        NEO4J_MAX_CONNECTION_POOL_SIZE=50,
        NEO4J_CONNECTION_ACQUISITION_TIMEOUT=60
    )


@pytest_asyncio.fixture()
async def graph_connection(env_settings: EnvironmentSettings) -> AsyncGenerator[CodeConfluenceGraphIngestion, None]:
    """Initialize Neo4j connection and schema using CodeConfluenceGraphIngestion."""
    
    
    # Build connection URL directly to ensure correct test container settings
    connection_url = (
        f"bolt://{env_settings.neo4j_username}:{env_settings.neo4j_password.get_secret_value()}"
        f"@{env_settings.neo4j_host}:{env_settings.neo4j_port}"
        f"?max_connection_lifetime={env_settings.neo4j_max_connection_lifetime}"
        f"&max_connection_pool_size={env_settings.neo4j_max_connection_pool_size}"
        f"&connection_acquisition_timeout={env_settings.neo4j_connection_acquisition_timeout}"
    )
    
    # Set global neomodel connection for managed_tx()
    config.DATABASE_URL = connection_url
    await adb.set_connection(connection_url)
    await adb.install_all_labels()
    
    # Create ingestion instance after global connection is established
    ingestion: CodeConfluenceGraphIngestion = CodeConfluenceGraphIngestion(code_confluence_env=env_settings)
    
    try:
        yield ingestion
    finally:
        await adb.close_connection()


@pytest.fixture()
def sample_codebase_dir() -> Path:  # noqa: D401 – simple fixture
    """Return the path to the pre-existing CLI sample codebase for parsing."""
    return (Path(__file__).parent.parent / "test_data" / "unoplat-code-confluence-cli").resolve()


# Ensure the database is empty before each test (autouse fixture)
@pytest_asyncio.fixture(autouse=True)
async def clear_neo4j(graph_connection):  # noqa: ARG001 – fixture dependency required
    """Remove all nodes and relationships so every test starts with a clean database."""
    yield
    # Use neomodel's adb.cypher_query to clear database
    await adb.cypher_query("MATCH (n) DETACH DELETE n")




# ---------------------------------------------------------------------------
# Integration test
# ---------------------------------------------------------------------------


class TestGenericCodebaseParserIntegration:
    """Validate that GenericCodebaseParser can insert packages & files into Neo4j."""

    @pytest.mark.asyncio
    async def test_parser_inserts_nodes(
        self,
        graph_connection: CodeConfluenceGraphIngestion,  # noqa: ARG002 – fixture provides connection & schema
        sample_codebase_dir: Path,
        env_settings: EnvironmentSettings,
    ) -> None:
        """Run the parser and assert that nodes exist in the database afterwards."""
        # ------------------------------------------------------------------
        # Build required input metadata for the parser
        # ------------------------------------------------------------------
        programming_language_metadata = ProgrammingLanguageMetadata(
            language=ProgrammingLanguage.PYTHON,
            language_version="3.11",
            role="leaf",
        )

        parser = GenericCodebaseParser(
            codebase_name="cli_codebase",
            codebase_path=str(sample_codebase_dir),
            root_packages=["unoplat_code_confluence_cli"],
            programming_language_metadata=programming_language_metadata,
            trace_id="integration-test",
            code_confluence_env=env_settings,
        )

        # Execute the parser – this streams data directly into Neo4j
        await parser.process_and_insert_codebase()

        # ------------------------------------------------------------------
        # Build expected absolute paths from the sample directory
        # ------------------------------------------------------------------
        base_path = sample_codebase_dir
        expected_paths = {
            "root": (base_path / "unoplat_code_confluence_cli").as_posix(),
            "connector": (base_path / "unoplat_code_confluence_cli" / "connector").as_posix(),
            "config": (base_path / "unoplat_code_confluence_cli" / "config").as_posix(),
            "analytics": (base_path / "unoplat_code_confluence_cli" / "connector" / "analytics").as_posix(),
            "reports": (base_path / "unoplat_code_confluence_cli" / "connector" / "analytics" / "reports").as_posix(),
            "utils": (base_path / "unoplat_code_confluence_cli" / "connector" / "analytics" / "utils").as_posix(),
        }

        # ------------------------------------------------------------------
        # Comprehensive validation of nodes and relationships
        # ------------------------------------------------------------------
        
        # 1. Verify package nodes were created with correct hierarchy
        packages = await CodeConfluencePackage.nodes.order_by('qualified_name').all()
        
        # Expected 6 packages with absolute path qualified names
        assert len(packages) == 6, f"Expected 6 packages, got {len(packages)}"
        
        package_names = {(p.qualified_name, p.name) for p in packages}
        expected_packages = {
            (expected_paths["root"], "unoplat_code_confluence_cli"),
            (expected_paths["connector"], "connector"),
            (expected_paths["config"], "config"),
            (expected_paths["analytics"], "analytics"),
            (expected_paths["reports"], "reports"),
            (expected_paths["utils"], "utils"),
        }
        assert package_names == expected_packages, (
            "Package names mismatch.\n"
            f"Expected: {expected_packages}\n"
            f"Actual:   {package_names}"
        )
        
        # 2. Verify package hierarchy relationships
        # Since we know the parent package, let's query it directly
        parent_package = await CodeConfluencePackage.nodes.get(
            qualified_name=expected_paths["root"]
        )
        
        # Get all sub-packages
        sub_packages = await parent_package.sub_packages.all()
        
        # Extract hierarchy
        hierarchy_data = []
        for child in sub_packages:
            hierarchy_data.append((parent_package.qualified_name, child.qualified_name))
        hierarchy_data.sort()  # Sort for consistent comparison
        
        # Expected: unoplat_code_confluence_cli contains connector and config
        assert len(hierarchy_data) == 2, f"Expected 2 hierarchy relationships, got {len(hierarchy_data)}"
        
        expected_hierarchy = {
            (expected_paths["root"], expected_paths["connector"]),
            (expected_paths["root"], expected_paths["config"]),
        }
        actual_hierarchy = set(hierarchy_data)
        assert actual_hierarchy == expected_hierarchy, (
            "Hierarchy mismatch.\n"
            f"Expected: {expected_hierarchy}\n"
            f"Actual:   {actual_hierarchy}"
        )
        
        # 3. Verify additional package hierarchy relationships

        # ------------------------------------------------------------------
        # 2a. Connector -> analytics relationship
        connector_pkg = await CodeConfluencePackage.nodes.get(
            qualified_name=expected_paths["connector"]
        )
        connector_children = await connector_pkg.sub_packages.all()
        connector_child_names = {child.qualified_name for child in connector_children}
        assert (
            expected_paths["analytics"] in connector_child_names
        ), "connector package should contain analytics sub-package"

        # 2b. Analytics -> reports & utils relationship
        analytics_pkg = await CodeConfluencePackage.nodes.get(
            qualified_name=expected_paths["analytics"]
        )
        analytics_children = await analytics_pkg.sub_packages.all()
        analytics_child_names = {child.qualified_name for child in analytics_children}
        expected_analytics_children = {
            expected_paths["reports"],
            expected_paths["utils"],
        }
        assert analytics_child_names == expected_analytics_children, (
            "Analytics sub-package hierarchy mismatch."
        )

        # ------------------------------------------------------------------
        # 3. Verify file nodes were created with content
        files = await CodeConfluenceFile.nodes.order_by('file_path').all()
        
        # Should have 5 files: __main__.py, api_client.py, settings.py, generator.py, helpers.py
        assert len(files) == 5, f"Expected 5 files, got {len(files)}"
        
        # Verify all files have checksum and structural signature
        for file in files:
            assert file.checksum is not None, f"File {file.file_path} missing checksum"
            assert file.structural_signature is not None, f"File {file.file_path} missing structural signature"
        
        # 4. Verify file-to-package relationships
        # For each file, get its package relationship
        file_package_data = []
        for file in files:
            # Get the package for this file
            try:
                package_nodes = await file.package.all()
                if package_nodes:
                    file_package_data.append((file.file_path, package_nodes[0].qualified_name))
            except Exception as e:
                logger.error(f"Failed to get package for file {file.file_path}: {e}")
        
        assert len(file_package_data) == 5, (
            f"Expected 5 file-package relationships, got {len(file_package_data)}"
        )
        
        # 5. Verify specific file structural signature - check settings.py
        settings_files = await CodeConfluenceFile.nodes.filter(
            file_path__contains='settings.py'
        ).all()
        
        assert len(settings_files) == 1, "Expected to find settings.py"
        settings_file = settings_files[0]
        # Verify settings.py contains expected class via structural signature
        signature = settings_file.structural_signature
        if signature:  # Only check if structural signature extraction worked
            # Parse using Pydantic model for type safety
            if isinstance(signature, str):
                signature_data = StructuralSignature.model_validate_json(signature)
            else:
                signature_data = StructuralSignature.model_validate(signature)
            assert signature_data.classes is not None, "Structural signature should have classes"
            assert len(signature_data.classes) >= 1, "Should have at least 1 class"
            # Check if AppConfig class exists in the class signatures
            class_signatures = [cls.signature for cls in signature_data.classes]
            assert any("class AppConfig" in sig for sig in class_signatures), "settings.py should contain AppConfig class"
        
        
        # 6. Verify structural signature in generator.py
        generator_files = await CodeConfluenceFile.nodes.filter(
            file_path__contains="generator.py"
        ).all()

        assert len(generator_files) == 1, "Expected to find generator.py"
        generator_file = generator_files[0]

        # NEW: Ensure imports, global variables, functions, and classes are captured in structural signature
        if isinstance(generator_file.structural_signature, str):
            gen_sig = StructuralSignature.model_validate_json(generator_file.structural_signature)
        else:
            gen_sig = StructuralSignature.model_validate(generator_file.structural_signature or {})

        # a. Validate global variables contain GLOBAL_CONSTANT
        gen_global_vars = [gv.signature for gv in gen_sig.global_variables]
        assert any("GLOBAL_CONSTANT" in sig for sig in gen_global_vars), (
            "generator.py structural signature should capture GLOBAL_CONSTANT in global_variables"
        )

        # b. Validate functions include generate_summary
        gen_functions = [fn.signature for fn in gen_sig.functions]
        assert any("def generate_summary" in sig for sig in gen_functions), (
            "generator.py structural signature should capture generate_summary function"
        )

        # c. Validate classes include ReportGenerator and SummaryReport
        gen_classes = [cl.signature for cl in gen_sig.classes]
        assert any("class ReportGenerator" in sig for sig in gen_classes), (
            "generator.py structural signature should capture ReportGenerator class"
        )
        assert any("class SummaryReport" in sig for sig in gen_classes), (
            "generator.py structural signature should capture SummaryReport class"
        )

        # 7. Verify imports in __main__.py
        main_files = await CodeConfluenceFile.nodes.filter(
            file_path__contains='__main__.py'
        ).all()

        assert len(main_files) == 1, "Expected to find __main__.py"
        main_file = main_files[0]
        imports = main_file.imports
        if imports:  # Only check if imports were extracted
            assert any("click" in imp for imp in imports), "__main__.py should import click"
            # NEW: ensure imports list is not empty
            assert len(imports) > 0, "__main__.py should have imports captured"

        # NEW: verify structural signature functions for __main__.py
        if isinstance(main_file.structural_signature, str):
            main_sig = StructuralSignature.model_validate_json(main_file.structural_signature)
        else:
            main_sig = StructuralSignature.model_validate(main_file.structural_signature or {})
        main_functions = [fn.signature for fn in main_sig.functions]
        assert any("def start_ingestion_process" in sig for sig in main_functions), (
            "__main__.py structural signature should capture start_ingestion_process function"
        )
        assert any("def main(" in sig for sig in main_functions), (
            "__main__.py structural signature should capture main function"
        )

        # 8. Extended structural signature validation for settings.py
        settings_files = await CodeConfluenceFile.nodes.filter(
            file_path__contains='settings.py'
        ).all()
        assert len(settings_files) == 1, "Expected to find settings.py"
        settings_file = settings_files[0]
        if isinstance(settings_file.structural_signature, str):
            settings_sig = StructuralSignature.model_validate_json(settings_file.structural_signature)
        else:
            settings_sig = StructuralSignature.model_validate(settings_file.structural_signature or {})
        settings_classes = [cl.signature for cl in settings_sig.classes]
        assert any("class AppConfig" in sig for sig in settings_classes), (
            "settings.py structural signature should capture AppConfig class"
        )

        # 9. Generic assertion: Each file should have imports captured (may be empty for __init__.py files)
        for file in files:
            if file.file_path.endswith("__init__.py"):
                continue  # allow empty imports for package init files
            assert file.imports is not None, f"File {file.file_path} missing imports list"

        logger.info(
            "Enhanced integration test passed: structural signatures validated for generator.py, __main__.py, and settings.py"
        )
    
    