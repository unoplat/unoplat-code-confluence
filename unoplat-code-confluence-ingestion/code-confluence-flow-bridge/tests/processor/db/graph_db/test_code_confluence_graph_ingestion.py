# # Standard Library
# import os
# from pathlib import Path
# from typing import AsyncGenerator

# # Third Party
# from pydantic_core import ValidationError
# import pytest
# from loguru import logger
# from neomodel import AsyncNodeSet, db as neomodel_db  # Import neomodel db for cypher queries
# from neomodel.async_.core import adb
# from testcontainers.neo4j import Neo4jContainer

# from unoplat_code_confluence_commons.graph_models.code_confluence_codebase import CodeConfluenceCodebase
# from unoplat_code_confluence_commons.graph_models.code_confluence_git_repository import CodeConfluenceGitRepository
# from pydantic import SecretStr
# from temporalio.exceptions import ApplicationError

# # First Party
# from src.code_confluence_flow_bridge.models.configuration.settings import EnvironmentSettings
# from src.code_confluence_flow_bridge.models.workflow.parent_child_clone_metadata import ParentChildCloneMetadata
# from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph_ingestion import CodeConfluenceGraphIngestion

# # Constants for Neo4j container
# NEO4J_VERSION = "5.26.0-community"  # Latest stable version
# NEO4J_PASSWORD = "password"
# NEO4J_PORT = 7687

# @pytest.fixture(scope="session")
# def neo4j_container():
#     """Create and start Neo4j test container"""
#     container = Neo4jContainer(
#         image=f"neo4j:{NEO4J_VERSION}"
#     )
    
#     # Configure Neo4j auth and other settings
#     container.with_env("NEO4J_AUTH", f"neo4j/{NEO4J_PASSWORD}")
    
#     # Expose the bolt port
#     container.with_exposed_ports(NEO4J_PORT)
    
#     # Start container
#     container.start()
    
#     yield container
    
#     container.stop()
    

# @pytest.fixture
# def env_settings(neo4j_container: Neo4jContainer) -> EnvironmentSettings:
#     """Create test environment settings from container"""
#     # Get the mapped port for bolt
#     neo4j_port = neo4j_container.get_exposed_port(NEO4J_PORT)
    
#     return EnvironmentSettings(
#         NEO4J_HOST=neo4j_container.get_container_host_ip(),
#         NEO4J_PORT=int(neo4j_port),  # Convert to int to fix type error
#         NEO4J_USERNAME="neo4j",
#         NEO4J_PASSWORD=SecretStr(NEO4J_PASSWORD),
#         NEO4J_MAX_CONNECTION_LIFETIME=3600,
#         NEO4J_MAX_CONNECTION_POOL_SIZE=50,
#         NEO4J_CONNECTION_ACQUISITION_TIMEOUT=60
#     )

# @pytest.fixture
# async def graph_ingestion(env_settings: EnvironmentSettings) -> AsyncGenerator[CodeConfluenceGraphIngestion, None]:
#     """Create and initialize graph ingestion instance"""
#     ingestion = CodeConfluenceGraphIngestion(code_confluence_env=env_settings)
#     await ingestion.initialize()
#     yield ingestion
#     await ingestion.close()

# @pytest.fixture
# def sample_git_repo() -> UnoplatGitRepository:
#     """Create sample git repository data"""
#     return UnoplatGitRepository(
#         repository_url="https://github.com/unoplat/unoplat-code-confluence",
#         repository_name="unoplat-code-confluence",
#         github_organization="unoplat",
#         repository_metadata={
#             "stars": 10,
#             "forks": 5,
#             "language": "Python"
#         },
#         readme="# Sample README",
#         codebases=[
#             UnoplatCodebase(
#                 name="unoplat_code_confluence",
#                 readme="# Sample Codebase README",
#                 local_path="/tmp/unoplat-code-confluence",
#                 source_directory="src",
#                 package_manager_metadata=UnoplatPackageManagerMetadata(
#                     programming_language="python",
#                     package_manager="poetry"
#                 )
#             )
#         ]
#     )

# class TestCodeConfluenceGraphIngestion:
#     """Test cases for CodeConfluenceGraphIngestion"""

#     @pytest.mark.asyncio
#     async def test_insert_git_repo(self, graph_ingestion: CodeConfluenceGraphIngestion, sample_git_repo: UnoplatGitRepository):
#         """Test inserting git repository data"""
#         # Insert repository
#         metadata = await graph_ingestion.insert_code_confluence_git_repo(sample_git_repo)
        
#         # Verify metadata
#         assert isinstance(metadata, ParentChildCloneMetadata)
#         assert metadata.repository_qualified_name == "unoplat_unoplat-code-confluence"
#         assert len(metadata.codebase_qualified_names) == 1
#         assert metadata.codebase_qualified_names[0] == "unoplat_unoplat-code-confluence_unoplat_code_confluence"

#         # Verify repository node
#         repo_nodes = await CodeConfluenceGitRepository.nodes.filter(
#             qualified_name=metadata.repository_qualified_name
#         ).all()
#         assert len(repo_nodes) == 1
#         repo_node: CodeConfluenceGitRepository = repo_nodes[0]
#         assert repo_node.repository_url == sample_git_repo.repository_url
#         assert repo_node.repository_name == sample_git_repo.repository_name
        

#         # Verify codebase node
#         codebase_nodes = await CodeConfluenceCodebase.nodes.filter(
#             qualified_name=metadata.codebase_qualified_names[0]
#         ).all()
#         assert len(codebase_nodes) == 1
#         codebase_node = codebase_nodes[0]
#         assert codebase_node.name == sample_git_repo.codebases[0].name

#         # Verify relationships
#         repo_codebases = await repo_node.codebases.all()
#         assert len(repo_codebases) == 1
#         assert repo_codebases[0].qualified_name == metadata.codebase_qualified_names[0]



#     @pytest.mark.asyncio
#     async def test_insert_package_manager_metadata(self, graph_ingestion: CodeConfluenceGraphIngestion):
#         """Test inserting package manager metadata"""
#         # First create a codebase node to link metadata to
#         codebase_qualified_name = "test_org_test-repo_test_codebase"
#         codebase_dict = {
#             "qualified_name": codebase_qualified_name,
#             "name": "test_codebase",
#             "readme": "# Test Codebase",
#             "local_path": "/tmp/test-codebase",
#         }
        
#         # Create codebase node using save method to avoid type error
#         created_codebase = CodeConfluenceCodebase(**codebase_dict)
#         await created_codebase.save()
#         assert created_codebase is not None
        
#         # Create sample package manager metadata
#         package_metadata = UnoplatPackageManagerMetadata(
#             dependencies={
#                 "requests": UnoplatProjectDependency(
#                     version=UnoplatVersion(minimum_version="2.0.0")
#                 )
#             },
#             package_name="test-package",
#             programming_language="python",
#             package_manager="poetry",
#             programming_language_version="3.9",
#             project_version="1.0.0",
#             description="Test package",
#             authors=["Test Author"],
#             entry_points={"cli": "test_package.cli:main"}
#         )
        
#         # Insert metadata
#         await graph_ingestion.insert_code_confluence_codebase_package_manager_metadata(
#             codebase_qualified_name=codebase_qualified_name,
#             package_manager_metadata=package_metadata
#         )
        
#         # Verify metadata node was created and linked
#         retrieved_codebase: CodeConfluenceCodebase = await CodeConfluenceCodebase.nodes.get(
#             qualified_name=codebase_qualified_name
#         )
        
#         metadata_nodes = await retrieved_codebase.package_manager_metadata.all()
#         assert len(metadata_nodes) == 1
#         metadata_node = metadata_nodes[0]
        
#         # Verify metadata fields
#         assert metadata_node.package_name == package_metadata.package_name
#         assert metadata_node.programming_language == package_metadata.programming_language
#         assert metadata_node.package_manager == package_metadata.package_manager
#         assert metadata_node.programming_language_version == package_metadata.programming_language_version
#         assert metadata_node.project_version == package_metadata.project_version
#         assert metadata_node.description == package_metadata.description
#         assert metadata_node.authors == package_metadata.authors
#         assert metadata_node.entry_points == package_metadata.entry_points
#         assert metadata_node.dependencies["requests"]["version"]["minimum_version"] == "2.0.0"

#     @pytest.mark.asyncio
#     async def test_insert_code_confluence_package(self, graph_ingestion: CodeConfluenceGraphIngestion):
#         """Test inserting package with files and nodes into the graph database."""
#         # First create a codebase node to link packages to
#         codebase_qualified_name = "test_org_test-repo_test_codebase_for_packages"
#         codebase_dict = {
#             "qualified_name": codebase_qualified_name,
#             "name": "test_codebase",
#             "readme": "# Test Codebase",
#             "local_path": "/tmp/test-codebase",
#         }
        
#         # Create codebase node using save method to avoid type error
#         created_codebase = CodeConfluenceCodebase(**codebase_dict)
#         await created_codebase.save()
#         assert created_codebase is not None
        
#         # Import required classes
#         from src.code_confluence_flow_bridge.models.chapi.chapi_position import Position
#         from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_file import UnoplatFile
#         from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package import UnoplatPackage
#         from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_chapi_forge_node import UnoplatChapiForgeNode
#         from unoplat_code_confluence_commons.graph_models.code_confluence_package import CodeConfluencePackage
#         from unoplat_code_confluence_commons.graph_models.code_confluence_file import CodeConfluenceFile
#         from unoplat_code_confluence_commons.graph_models.code_confluence_class import CodeConfluenceClass
        
#         # Create a sample node with proper parameters
#         sample_node = UnoplatChapiForgeNode(
#             NodeName="TestClass", #type:ignore
#             # Omitting Position to avoid lint errors
#         )
        
#         # Create a sample file with the node
#         sample_file = UnoplatFile(
#             file_path="/tmp/test-codebase/src/test_module/test_file.py",
#             nodes=[sample_node]
#         )
        
#         # Create a sample package with the file
#         sample_package = UnoplatPackage(
#             name="test_module",
#             files={
#                 "/tmp/test-codebase/src/test_module/test_file.py": sample_file
#             }
#         )
        
#         # Insert the package into the graph database
#         await graph_ingestion.insert_code_confluence_package(
#             codebase_qualified_name=codebase_qualified_name,
#             packages=[sample_package]
#         )
        
#         # Verify package node was created and linked to codebase
#         retrieved_codebase: CodeConfluenceCodebase = await CodeConfluenceCodebase.nodes.get(
#             qualified_name=codebase_qualified_name
#         )
        
#         # Get packages related to the codebase - using cypher query instead of direct relationship access
#         # This avoids the AsyncRelationshipTo.all() lint error
#         query = f"MATCH (c:CodeConfluenceCodebase {{qualified_name: $qualified_name}})-[:CONTAINS_PACKAGE]->(p:CodeConfluencePackage) RETURN p"
#         results, _ =  await adb.cypher_query(
#             query, {"qualified_name": codebase_qualified_name}, resolve_objects=True
#         )
#         package_nodes = [row[0] for row in results]
#         assert len(package_nodes) > 0
        
#         # Find our specific package
#         package_node = None
#         for pkg in package_nodes:
#             if pkg.name == sample_package.name:
#                 package_node = pkg
#                 break
        
#         assert package_node is not None
#         assert package_node.qualified_name == f"{codebase_qualified_name}.{sample_package.name}"
        
#         # Verify file node was created and linked to package
#         file_path = "/tmp/test-codebase/src/test_module/test_file.py"
#         file_nodes = await AsyncNodeSet(CodeConfluenceFile).filter(
#             file_path=file_path
#         ).all()
#         assert len(file_nodes) > 0
#         file_node = file_nodes[0]
        
#         # Get package related to file - using cypher query
#         query = f"MATCH (f:CodeConfluenceFile {{file_path: $file_path}})-[:PART_OF_PACKAGE]->(p:CodeConfluencePackage) RETURN p"
#         results, _ =  await adb.cypher_query(
#             query, {"file_path": file_path}, resolve_objects=True
#         )
#         file_packages = [row[0] for row in results]
#         assert len(file_packages) > 0
#         file_package = file_packages[0]
#         assert file_package.qualified_name == package_node.qualified_name
        
#         # Verify class node was created and linked to file
#         # Since we're using CodeConfluenceClass instead of a generic CodeConfluenceNode
#         # Filter class nodes by qualified_name instead of name
#         class_nodes = await AsyncNodeSet(CodeConfluenceClass).filter(
#             qualified_name__contains="TestClass"  # Using qualified_name for filtering
#         ).all()
#         assert len(class_nodes) > 0
#         class_node = class_nodes[0]
        
#         # Verify class node properties
#         assert "TestClass" in class_node.qualified_name  # Check qualified_name instead of name

#     @pytest.mark.asyncio
#     async def test_idempotent_git_repo_insertion(self, graph_ingestion: CodeConfluenceGraphIngestion, sample_git_repo: UnoplatGitRepository):
#         """Test that inserting the same git repository twice succeeds gracefully without errors"""
#         # Insert repository first time
#         metadata1 = await graph_ingestion.insert_code_confluence_git_repo(sample_git_repo)
        
#         # Verify first insertion
#         assert isinstance(metadata1, ParentChildCloneMetadata)
#         assert metadata1.repository_qualified_name == "unoplat_unoplat-code-confluence"
        
#         # Insert the same repository again - should succeed gracefully
#         metadata2 = await graph_ingestion.insert_code_confluence_git_repo(sample_git_repo)
        
#         # Verify second insertion returns same metadata
#         assert isinstance(metadata2, ParentChildCloneMetadata)
#         assert metadata2.repository_qualified_name == metadata1.repository_qualified_name
#         assert metadata2.codebase_qualified_names == metadata1.codebase_qualified_names
        
#         # Verify only one repository node exists
#         repo_nodes = await CodeConfluenceGitRepository.nodes.filter(
#             qualified_name=metadata1.repository_qualified_name
#         ).all()
#         assert len(repo_nodes) == 1
        
#         # Verify only one codebase node exists  
#         codebase_nodes = await CodeConfluenceCodebase.nodes.filter(
#             qualified_name=metadata1.codebase_qualified_names[0]
#         ).all()
#         assert len(codebase_nodes) == 1

#     @pytest.mark.asyncio
#     async def test_idempotent_package_metadata_insertion(self, graph_ingestion: CodeConfluenceGraphIngestion):
#         """Test that inserting the same package metadata twice succeeds gracefully"""
#         # First create a codebase node
#         codebase_qualified_name = "test_org_test-repo_test_codebase_idempotent"
#         codebase_dict = {
#             "qualified_name": codebase_qualified_name,
#             "name": "test_codebase",
#             "readme": "# Test Codebase",
#             "local_path": "/tmp/test-codebase",
#         }
        
#         # Create codebase node using save method to avoid type error
#         created_codebase = CodeConfluenceCodebase(**codebase_dict)
#         await created_codebase.save()
#         assert created_codebase is not None
        
#         # Create sample package manager metadata
#         package_metadata = UnoplatPackageManagerMetadata(
#             dependencies={
#                 "requests": UnoplatProjectDependency(
#                     version=UnoplatVersion(minimum_version="2.0.0")
#                 )
#             },
#             package_name="test-package-idempotent",
#             programming_language="python",
#             package_manager="poetry",
#             programming_language_version="3.9",
#             project_version="1.0.0",
#             description="Test package for idempotency",
#             authors=["Test Author"],
#             entry_points={"cli": "test_package.cli:main"}
#         )
        
#         # Insert metadata first time
#         await graph_ingestion.insert_code_confluence_codebase_package_manager_metadata(
#             codebase_qualified_name=codebase_qualified_name,
#             package_manager_metadata=package_metadata
#         )
        
#         # Insert the same metadata again - should succeed gracefully
#         await graph_ingestion.insert_code_confluence_codebase_package_manager_metadata(
#             codebase_qualified_name=codebase_qualified_name,
#             package_manager_metadata=package_metadata
#         )
        
#         # Verify only one metadata node exists
#         retrieved_codebase = await CodeConfluenceCodebase.nodes.get(
#             qualified_name=codebase_qualified_name
#         )
#         metadata_nodes = await retrieved_codebase.package_manager_metadata.all()
#         assert len(metadata_nodes) == 1
        
#         # Verify metadata fields are still correct
#         metadata_node = metadata_nodes[0]
#         assert metadata_node.package_name == package_metadata.package_name
#         assert metadata_node.programming_language == package_metadata.programming_language