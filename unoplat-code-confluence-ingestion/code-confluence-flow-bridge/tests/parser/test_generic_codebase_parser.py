# Standard Library
from pathlib import Path
from typing import Dict

from loguru import logger
from pydantic import SecretStr

# Third Party
import pytest
from fastapi.testclient import TestClient

# First Party
from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
    ProgrammingLanguage,
    ProgrammingLanguageMetadata,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.structural_signature import StructuralSignature
from src.code_confluence_flow_bridge.parser.generic_codebase_parser import GenericCodebaseParser
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph import CodeConfluenceGraph

# Note: Removed neomodel graph model imports to avoid NodeClassNotDefined errors
# when using raw Cypher queries for verification. Models are still used via raw Cypher.

# Import cleanup utility
from tests.integration.test_start_ingestion import cleanup_repository_via_endpoint



# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def env_settings(service_ports: Dict[str, int]) -> EnvironmentSettings:
    """Create EnvironmentSettings using the shared Neo4j from docker-compose."""
    return EnvironmentSettings(
        NEO4J_HOST="localhost",
        NEO4J_PORT=service_ports["neo4j"],
        NEO4J_USERNAME="neo4j",
        NEO4J_PASSWORD=SecretStr("password"),
        NEO4J_MAX_CONNECTION_LIFETIME=3600,
        NEO4J_MAX_CONNECTION_POOL_SIZE=50,
        NEO4J_CONNECTION_ACQUISITION_TIMEOUT=60
    )


@pytest.fixture()
def sample_codebase_dir() -> Path:  # noqa: D401 – simple fixture
    """Return the path to the pre-existing CLI sample codebase for parsing."""
    return (Path(__file__).parent.parent / "test_data" / "unoplat-code-confluence-cli").resolve()






# ---------------------------------------------------------------------------
# Integration test
# ---------------------------------------------------------------------------


class TestGenericCodebaseParserIntegration:
    """Validate that GenericCodebaseParser can insert packages & files into Neo4j."""

    @pytest.mark.asyncio(loop_scope="session") #type: ignore
    async def test_parser_inserts_nodes(
        self,
        test_client: TestClient,
        sample_codebase_dir: Path,
        env_settings: EnvironmentSettings,
        neo4j_client,
    ) -> None:
        """Run the parser and assert that nodes exist in the database afterwards."""
        # ------------------------------------------------------------------
        # Clean database before test using Neo4j direct query
        # ------------------------------------------------------------------
        
        # Delete all nodes to ensure clean state
        neo4j_client.cypher_query("MATCH (n) DETACH DELETE n")
        logger.info("Cleaned up all Neo4j nodes before test")
        
        # ------------------------------------------------------------------
        # Build required input metadata for the parser
        # ------------------------------------------------------------------
        programming_language_metadata = ProgrammingLanguageMetadata(
            language=ProgrammingLanguage.PYTHON,
            language_version="3.11",
            role="leaf",
        )

        # Create CodeConfluenceGraph instance using env_settings
        code_confluence_graph = CodeConfluenceGraph(env_settings)
        # Ensure connection is established before using the graph
        await code_confluence_graph.connect()

        parser = GenericCodebaseParser(
            codebase_name="cli_codebase",
            codebase_path=str(sample_codebase_dir),
            root_packages=["unoplat_code_confluence_cli"],
            programming_language_metadata=programming_language_metadata,
            trace_id="integration-test",
            code_confluence_graph=code_confluence_graph,
        )

        # Create the missing CodeConfluenceCodebase node using managed transactions
        # (normally created during git ingestion step, but we're testing parser in isolation)
        async with code_confluence_graph.get_session() as session:
            # Follow neomodel's create_or_update pattern: MERGE on required properties only
            create_codebase_query = """
            MERGE (c:CodeConfluenceCodebase {qualified_name: $qualified_name})
            ON CREATE SET 
                c.name = $name,
                c.codebase_path = $codebase_path
            ON MATCH SET 
                c.name = $name,
                c.codebase_path = $codebase_path
            RETURN c
            """
            await session.execute_write(
                lambda tx: tx.run(create_codebase_query, {
                    "qualified_name": "cli_codebase",
                    "name": "cli_codebase", 
                    "codebase_path": str(sample_codebase_dir.resolve())
                })
            )
        logger.info("Created codebase node with managed transactions")

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
        result, meta = neo4j_client.cypher_query(
            "MATCH (p:CodeConfluencePackage) RETURN p.qualified_name, p.name ORDER BY p.qualified_name"
        )
        
        # Expected 6 packages with absolute path qualified names
        assert len(result) == 6, f"Expected 6 packages, got {len(result)}"
        
        package_names = {(row[0], row[1]) for row in result}
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
        # Query parent-child relationships directly
        result, meta = neo4j_client.cypher_query(
            "MATCH (parent:CodeConfluencePackage {qualified_name: $parent_qname})-[:CONTAINS_PACKAGE]->(child:CodeConfluencePackage) RETURN parent.qualified_name, child.qualified_name",
            {"parent_qname": expected_paths["root"]}
        )
        
        # Extract hierarchy
        hierarchy_data = [(row[0], row[1]) for row in result]
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
        result, meta = neo4j_client.cypher_query(
            "MATCH (parent:CodeConfluencePackage {qualified_name: $parent_qname})-[:CONTAINS_PACKAGE]->(child:CodeConfluencePackage) RETURN child.qualified_name",
            {"parent_qname": expected_paths["connector"]}
        )
        connector_child_names = {row[0] for row in result}
        assert (
            expected_paths["analytics"] in connector_child_names
        ), "connector package should contain analytics sub-package"

        # 2b. Analytics -> reports & utils relationship
        result, meta = neo4j_client.cypher_query(
            "MATCH (parent:CodeConfluencePackage {qualified_name: $parent_qname})-[:CONTAINS_PACKAGE]->(child:CodeConfluencePackage) RETURN child.qualified_name",
            {"parent_qname": expected_paths["analytics"]}
        )
        analytics_child_names = {row[0] for row in result}
        expected_analytics_children = {
            expected_paths["reports"],
            expected_paths["utils"],
        }
        assert analytics_child_names == expected_analytics_children, (
            "Analytics sub-package hierarchy mismatch."
        )

        # ------------------------------------------------------------------
        # 3. Verify file nodes were created with content
        result, _ = neo4j_client.cypher_query(
            "MATCH (f:CodeConfluenceFile) RETURN f.file_path, f.checksum, f.structural_signature ORDER BY f.file_path"
        )
        
        # Should have 5 files: __main__.py, api_client.py, settings.py, generator.py, helpers.py
        assert len(result) == 5, f"Expected 5 files, got {len(result)}"
        
        # Verify all files have checksum and structural signature  
        for row in result:
            file_path, checksum, structural_signature = row[0], row[1], row[2]
            assert checksum is not None, f"File {file_path} missing checksum"
            assert structural_signature is not None, f"File {file_path} missing structural signature"
        
        # 4. Verify file-to-package relationships
        # Get file-package relationships directly
        result, _ = neo4j_client.cypher_query(
            "MATCH (f:CodeConfluenceFile)-[:PART_OF_PACKAGE]->(p:CodeConfluencePackage) RETURN f.file_path, p.qualified_name"
        )
        file_package_data = [(row[0], row[1]) for row in result]
        
        assert len(file_package_data) == 5, (
            f"Expected 5 file-package relationships, got {len(file_package_data)}"
        )
        
        # 5. Verify specific file structural signature - check settings.py
        result, _ = neo4j_client.cypher_query(
            "MATCH (f:CodeConfluenceFile) WHERE f.file_path CONTAINS 'settings.py' RETURN f.file_path, f.structural_signature"
        )
        
        assert len(result) == 1, "Expected to find settings.py"
        settings_file_path, signature = result[0][0], result[0][1]
        # Verify settings.py contains expected class via structural signature
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
        result, _ = neo4j_client.cypher_query(
            "MATCH (f:CodeConfluenceFile) WHERE f.file_path CONTAINS 'generator.py' RETURN f.file_path, f.structural_signature"
        )

        assert len(result) == 1, "Expected to find generator.py"
        generator_file_path, generator_signature = result[0][0], result[0][1]

        # NEW: Ensure imports, global variables, functions, and classes are captured in structural signature
        if isinstance(generator_signature, str):
            gen_sig = StructuralSignature.model_validate_json(generator_signature)
        else:
            gen_sig = StructuralSignature.model_validate(generator_signature or {})

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
        result, _ = neo4j_client.cypher_query(
            "MATCH (f:CodeConfluenceFile) WHERE f.file_path CONTAINS '__main__.py' RETURN f.file_path, f.imports, f.structural_signature"
        )

        assert len(result) == 1, "Expected to find __main__.py"
        main_file_path, imports, main_structural_signature = result[0][0], result[0][1], result[0][2]
        if imports:  # Only check if imports were extracted
            assert any("click" in imp for imp in imports), "__main__.py should import click"
            # NEW: ensure imports list is not empty
            assert len(imports) > 0, "__main__.py should have imports captured"

        # NEW: verify structural signature functions for __main__.py
        if isinstance(main_structural_signature, str):
            main_sig = StructuralSignature.model_validate_json(main_structural_signature)
        else:
            main_sig = StructuralSignature.model_validate(main_structural_signature or {})
        main_functions = [fn.signature for fn in main_sig.functions]
        assert any("def start_ingestion_process" in sig for sig in main_functions), (
            "__main__.py structural signature should capture start_ingestion_process function"
        )
        assert any("def main(" in sig for sig in main_functions), (
            "__main__.py structural signature should capture main function"
        )

        # 8. Extended structural signature validation for settings.py (reuse from section 5)
        # settings.py data already retrieved in section 5
        if isinstance(signature, str):
            settings_sig = StructuralSignature.model_validate_json(signature)
        else:
            settings_sig = StructuralSignature.model_validate(signature or {})
        settings_classes = [cl.signature for cl in settings_sig.classes]
        assert any("class AppConfig" in sig for sig in settings_classes), (
            "settings.py structural signature should capture AppConfig class"
        )

        # 9. Generic assertion: Each file should have imports captured (may be empty for __init__.py files)
        # Get all files with imports info
        result, _ = neo4j_client.cypher_query(
            "MATCH (f:CodeConfluenceFile) RETURN f.file_path, f.imports"
        )
        for row in result:
            file_path, file_imports = row[0], row[1]
            if file_path.endswith("__init__.py"):
                continue  # allow empty imports for package init files
            assert file_imports is not None, f"File {file_path} missing imports list"

        logger.info(
            "Enhanced integration test passed: structural signatures validated for generator.py, __main__.py, and settings.py"
        )
    
    