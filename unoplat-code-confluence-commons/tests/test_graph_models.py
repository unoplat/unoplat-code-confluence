from typing import AsyncGenerator, Generator, List

import pytest
from neomodel import config, adb, install_all_labels
from testcontainers.neo4j import Neo4jContainer

# Import graph model classes from the unoplat code confluence commons package
from unoplat_code_confluence_commons.graph_models import (
    CodeConfluenceGitRepository,  # Represents a Git repository
    CodeConfluenceCodebase,       # Represents a codebase within a repository
    CodeConfluencePackage,        # Represents a package within a codebase
    CodeConfluencePackageManagerMetadata,  # Represents package manager metadata
    CodeConfluenceFile            # Represents a file within a package
)



@pytest.fixture(scope="session")
def neo4j_container() -> Generator[Neo4jContainer, None, None]:
    """Start Neo4j container and configure connection.
    
    This fixture creates a Neo4j container using testcontainers, configures the
    neomodel connection URL, and yields the container for tests to use.
    
    Returns:
        Generator[Neo4jContainer, None, None]: The Neo4j container instance
    """
    # Create and start a Neo4j container with version 5.24
    with Neo4jContainer("neo4j:5.24") as container:
        # Configure neomodel to connect to the container
        config.DATABASE_URL = (
            f"bolt://neo4j:password@{container.get_container_host_ip()}"
            f":{container.get_exposed_port(7687)}"
        )
        yield container


@pytest.fixture(autouse=True)
async def setup_database(neo4j_container: Neo4jContainer) -> AsyncGenerator[None, None]:
    """Setup database before each test and cleanup after.
    
    This fixture runs automatically before each test. It clears the database,
    installs all Neo4j labels, runs the test, and then cleans up the database again.
    
    Args:
        neo4j_container (Neo4jContainer): The Neo4j container fixture
        
    Yields:
        AsyncGenerator[None, None]: Control returns to the test after yielding
    """
    # Clean the database before test
    await adb.cypher_query("MATCH (n) DETACH DELETE n")
    # Install all model labels in the database
    install_all_labels()
    # Run the test
    yield
    # Clean up after the test
    await adb.cypher_query("MATCH (n) DETACH DELETE n")


@pytest.mark.asyncio(scope="session")
async def test_create_git_repository() -> None:
    """Test creating a git repository node.
    
    This test verifies that:
    1. A CodeConfluenceGitRepository node can be created and saved to the database
    2. The node properties are correctly stored
    3. The node can be retrieved from the database using a query
    """
    # Create and save a repository node with metadata
    repo = await CodeConfluenceGitRepository(
        qualified_name="github.com/org/repo",  # Unique identifier for the repository
        repository_url="https://github.com/org/repo",  # URL to the repository
        repository_name="test-repo",  # Name of the repository
        repository_metadata={"stars": 100}  # Additional metadata as a dictionary
    ).save()
    
    # Verify the properties were saved correctly
    assert repo.repository_name == "test-repo"
    assert repo.repository_metadata["stars"] == 100
    
    # Retrieve the repository from the database and verify it exists
    found_repo = await CodeConfluenceGitRepository.nodes.get_or_none(repository_name="test-repo")
    assert found_repo is not None
    assert found_repo.repository_name == "test-repo"

@pytest.mark.asyncio(scope="session")
async def test_git_repository_codebase_relationship() -> None:
    """Test creating a git repository with a codebase relationship.
    
    This test verifies that:
    1. A repository and codebase can be created and connected
    2. A codebase can be connected to package manager metadata
    3. Relationships can be traversed in both directions
    4. The relationship structure: Repository -> Codebase -> PackageManagerMetadata
    """
    # Create and save a repository node
    repo: CodeConfluenceGitRepository = await CodeConfluenceGitRepository(
        qualified_name="github.com/org/repo",
        repository_url="https://github.com/org/repo",
        repository_name="test-repo"
    ).save()
    
    # Create and save a codebase node with new fields
    codebase: CodeConfluenceCodebase = await CodeConfluenceCodebase(
        qualified_name="org/repo/main",  # Unique identifier for the codebase
        name="main-codebase",  # Name of the codebase
        codebase_path="/test/repo/path",  # File system path to the codebase
        programming_language="python",  # New field: primary programming language
        root_packages=["main", "tests"]  # New field: list of root packages
    ).save()
    
    # Create and save package manager metadata
    metadata: CodeConfluencePackageManagerMetadata = await CodeConfluencePackageManagerMetadata(
        qualified_name="org/repo/main/metadata",  # Unique identifier for the metadata
        package_manager="pip",  # Package manager used (e.g., pip, npm)
        programming_language="python",  # Programming language of the codebase
        package_name="test-package"  # Name of the package
    ).save()
    
    # Connect repository to codebase (Repository -> Codebase relationship)
    await repo.codebases.connect(codebase)
    # Connect codebase to git repository (bidirectional relationship)
    await codebase.git_repository.connect(repo)
    # Connect codebase to package manager metadata (Codebase -> PackageManagerMetadata relationship)
    await codebase.package_manager_metadata.connect(metadata)
    
    # Verify repository to codebase relationship
    connected_codebases: List[CodeConfluenceCodebase] = await repo.codebases.all()
    assert len(connected_codebases) == 1
    assert connected_codebases[0].name == "main-codebase"
    # Verify new fields
    assert connected_codebases[0].programming_language == "python"
    assert connected_codebases[0].root_packages == ["main", "tests"]
    
    # Verify codebase to package manager metadata relationship
    codebase_metadata = await connected_codebases[0].package_manager_metadata.all()
    assert len(codebase_metadata) == 1
    assert codebase_metadata[0].package_manager == "pip"


@pytest.mark.asyncio(scope="session")
async def test_repository_to_file_hierarchy() -> None:
    """Test creating a complete hierarchy from repository to file.
    
    This test verifies the simplified hierarchy of the code confluence graph model:
    Repository -> Codebase -> Package -> File
    
    The test creates all necessary nodes, establishes relationships between them,
    and then verifies that the relationships can be traversed correctly.
    
    The hierarchy being tested represents the following structure:
    - A Git repository contains one or more codebases (branches)
    - A codebase contains one or more packages
    - A package contains one or more files
    
    Note: Some relationships are bidirectional (e.g., codebase <-> repository)
    """
    # Create repository node
    repo: CodeConfluenceGitRepository = await CodeConfluenceGitRepository(
        qualified_name="github.com/org/repo2",  # Unique identifier
        repository_url="https://github.com/org/repo2",  # Repository URL
        repository_name="test-repo-2"  # Repository name
    ).save()
    
    # Create codebase node (represents a branch or version of the codebase)
    codebase: CodeConfluenceCodebase = await CodeConfluenceCodebase(
        qualified_name="org/repo/main",  # Unique identifier
        name="main-codebase",  # Codebase name (e.g., main branch)
        codebase_path="/test/repo/path"  # Updated property name from local_path to codebase_path
    ).save()
    
    # Create package node (represents a module or package in the codebase)
    package: CodeConfluencePackage = await CodeConfluencePackage(
        qualified_name="org/repo/main/package",  # Unique identifier
        name="test_package"  # Package name
    ).save()
    
    # Create file node (represents a source code file) with new fields
    file: CodeConfluenceFile = await CodeConfluenceFile(
        file_path="/test/path.py",  # Path to the file
        content="# Test file content\nimport os\nimport sys\n\nx = 10",  # File content
        checksum="abcdef123456",  # Checksum for file integrity/version tracking
        # New fields
        imports=["os", "sys"],  # List of imports
        global_variables=["x"],  # List of global variables
        structural_signature={  # Structural information about the file
            "functions": [],
            "classes": []
        },
        class_variables={}  # No class variables in this simple file
    ).save()
    
    # Connect nodes according to the hierarchy: repo -> codebase -> package -> file
    # Each connection represents a relationship in the graph database
    await repo.codebases.connect(codebase)  # Repository contains codebase
    await codebase.git_repository.connect(repo)  # Codebase belongs to repository (bidirectional)
    await codebase.packages.connect(package)  # Codebase contains package
    await package.files.connect(file)  # Package contains file
    await file.package.connect(package)  # File belongs to package (bidirectional)
    
    # VERIFICATION SECTION
    # Now verify that all nodes and relationships were created correctly
    
    # Verify repository exists
    found_repo = await CodeConfluenceGitRepository.nodes.get_or_none(repository_name="test-repo-2")
    assert found_repo is not None, "Repository node was not found"
    
    # Verify repository -> codebase relationship
    repo_codebases: List[CodeConfluenceCodebase] = await found_repo.codebases.all()
    assert len(repo_codebases) == 1, "Expected exactly one codebase connected to repository"
    found_codebase: CodeConfluenceCodebase = repo_codebases[0]
    assert found_codebase.name == "main-codebase", "Codebase name mismatch"
    
    # Verify codebase -> repository relationship (bidirectional)
    codebase_repos = await found_codebase.git_repository.all()
    assert len(codebase_repos) == 1, "Expected exactly one repository connected to codebase"
    assert codebase_repos[0].repository_name == "test-repo-2", "Repository name mismatch in bidirectional relationship"
    
    # Verify codebase -> package relationship
    codebase_packages: List[CodeConfluencePackage] = await found_codebase.packages.all()
    assert len(codebase_packages) == 1, "Expected exactly one package connected to codebase"
    found_package: CodeConfluencePackage = codebase_packages[0]
    assert found_package.name == "test_package", "Package name mismatch"
    
    # Verify package -> file relationship
    package_files: List[CodeConfluenceFile] = await found_package.files.all()
    assert len(package_files) == 1, "Expected exactly one file connected to package"
    found_file: CodeConfluenceFile = package_files[0]
    assert found_file.file_path == "/test/path.py", "File path mismatch"
    
    # Verify new fields in file
    assert found_file.imports == ["os", "sys"], "Imports mismatch"
    assert found_file.global_variables == ["x"], "Global variables mismatch"
    assert found_file.structural_signature == {"functions": [], "classes": []}, "Structural signature mismatch"
    assert found_file.class_variables == {}, "Class variables mismatch"
    
    # Verify bidirectional relationship between file and package
    file_packages = await found_file.package.all()
    assert len(file_packages) == 1, "Expected exactly one package connected to file"
    assert file_packages[0].name == "test_package", "Package name mismatch in file->package relationship"
    
    # Test complete traversal from repo to file
    # This verifies we can navigate the entire hierarchy: repo -> codebase -> package -> file
    # We need to await each step in the chain since these are async relationships
    codebases = await found_repo.codebases.all()
    codebase = codebases[0]
    packages = await codebase.packages.all()
    package = packages[0]
    files = await package.files.all()
    file = files[0]
    assert file.file_path == "/test/path.py", "File path mismatch after complete traversal"


@pytest.mark.asyncio(scope="session")
async def test_new_codebase_and_file_fields() -> None:
    """Test the new fields added to CodeConfluenceCodebase and CodeConfluenceFile models.
    
    This test specifically verifies:
    1. CodeConfluenceCodebase new fields: programming_language, root_packages
    2. CodeConfluenceFile new fields: structural_signature, global_variables, class_variables, imports
    """
    # Create a codebase with all new fields populated
    codebase = await CodeConfluenceCodebase(
        qualified_name="test/codebase",
        name="test-codebase",
        codebase_path="/test/path",
        programming_language="python",  # Test programming language field
        root_packages=["src", "tests", "docs"],  # Test root_packages array field
        readme="# Test Codebase\nThis is a test README"  # Test readme field
    ).save()
    
    # Verify codebase fields
    assert codebase.programming_language == "python"
    assert codebase.root_packages == ["src", "tests", "docs"]
    assert codebase.readme == "# Test Codebase\nThis is a test README"
    
    # Create a package for the file
    package = await CodeConfluencePackage(
        qualified_name="test/codebase/src",
        name="src"
    ).save()
    
    # Connect codebase to package
    await codebase.packages.connect(package)
    
    # Create a file with all new fields populated
    file = await CodeConfluenceFile(
        file_path="/test/src/main.py",
        content="""import os
import sys
from typing import List

class MyClass:
    class_var = 42
    
    def method(self):
        pass

def my_function(x: int) -> int:
    return x * 2

global_var = "test"
""",
        checksum="xyz789",
        # Test new fields
        imports=["os", "sys", "typing.List"],
        global_variables=["global_var"],
        class_variables={"MyClass": ["class_var"]},
        structural_signature={
            "functions": [
                {
                    "name": "my_function",
                    "signature": "def my_function(x: int) -> int",
                    "position": {"start_line": 11, "end_line": 12}
                }
            ],
            "classes": [
                {
                    "name": "MyClass",
                    "signature": "class MyClass:",
                    "position": {"start_line": 5, "end_line": 9},
                    "methods": [
                        {
                            "name": "method",
                            "signature": "def method(self):",
                            "position": {"start_line": 8, "end_line": 9}
                        }
                    ]
                }
            ]
        }
    ).save()
    
    # Connect package to file and file to package (bidirectional)
    await package.files.connect(file)
    await file.package.connect(package)
    
    # Verify file fields
    assert file.imports == ["os", "sys", "typing.List"]
    assert file.global_variables == ["global_var"]
    assert file.class_variables == {"MyClass": ["class_var"]}
    assert file.structural_signature["functions"][0]["name"] == "my_function"
    assert file.structural_signature["classes"][0]["name"] == "MyClass"
    assert len(file.structural_signature["classes"][0]["methods"]) == 1
    
    # Test retrieval from database
    retrieved_file = await CodeConfluenceFile.nodes.get_or_none(file_path="/test/src/main.py")
    assert retrieved_file is not None
    assert retrieved_file.imports == ["os", "sys", "typing.List"]
    assert retrieved_file.structural_signature["classes"][0]["name"] == "MyClass"