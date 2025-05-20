from typing import AsyncGenerator, Generator, List

import pytest
from neomodel import config, adb, install_all_labels
from testcontainers.neo4j import Neo4jContainer

# Import graph model classes from the unoplat code confluence commons package
from unoplat_code_confluence_commons.graph_models import (
    CodeConfluenceGitRepository,  # Represents a Git repository
    CodeConfluenceCodebase,       # Represents a codebase within a repository
    CodeConfluencePackage,        # Represents a package within a codebase
    CodeConfluenceClass,          # Represents a class within a file
    CodeConfluenceInternalFunction,  # Represents a function within a class
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
    
    # Create and save a codebase node
    codebase: CodeConfluenceCodebase = await CodeConfluenceCodebase(
        qualified_name="org/repo/main",  # Unique identifier for the codebase
        name="main-codebase",  # Name of the codebase
        local_path="/test/repo/path"  # Local path where the codebase is stored
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
    # Connect codebase to package manager metadata (Codebase -> PackageManagerMetadata relationship)
    await codebase.package_manager_metadata.connect(metadata)
    
    # Verify repository to codebase relationship
    connected_codebases: List[CodeConfluenceCodebase] = await repo.codebases.all()
    assert len(connected_codebases) == 1
    assert connected_codebases[0].name == "main-codebase"
    
    # Verify codebase to package manager metadata relationship
    codebase_metadata = await connected_codebases[0].package_manager_metadata.all()
    assert len(codebase_metadata) == 1
    assert codebase_metadata[0].package_manager == "pip"


@pytest.mark.asyncio(scope="session")
async def test_complete_hierarchy() -> None:
    """Test creating a complete hierarchy from repo to function with the new package -> file -> node structure.
    
    This test verifies the complete hierarchy of the code confluence graph model:
    Repository -> Codebase -> Package -> File -> Class -> Function
    
    The test creates all necessary nodes, establishes relationships between them,
    and then verifies that the relationships can be traversed in both directions.
    It also tests the complete traversal path from repository to function.
    
    The hierarchy being tested represents the following structure:
    - A Git repository contains one or more codebases (branches)
    - A codebase contains one or more packages
    - A package contains one or more files
    - A file contains one or more nodes (classes, functions)
    - A class contains one or more functions
    
    Note: Some relationships are bidirectional (e.g., file <-> class)
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
        local_path="/test/repo/path"  # Local path where code is stored
    ).save()
    
    # Create package node (represents a module or package in the codebase)
    package: CodeConfluencePackage = await CodeConfluencePackage(
        qualified_name="org/repo/main/package",  # Unique identifier
        name="test_package"  # Package name
    ).save()
    
    # Create file node (represents a source code file)
    file: CodeConfluenceFile = await CodeConfluenceFile(
        file_path="/test/path.py",  # Path to the file
        content="# Test file content",  # File content
        checksum="abcdef123456"  # Checksum for file integrity/version tracking
    ).save()
    
    # Create class node (represents a class defined in the file)
    class_node: CodeConfluenceClass = await CodeConfluenceClass(
        qualified_name="org/repo/main/package/TestClass",  # Unique identifier
        name="TestClass",  # Class name
        file_path="/test/path.py",  # Path to file containing the class
        line_number=1  # Line number where class is defined
    ).save()
    
    # Create function node (represents a method within the class)
    function: CodeConfluenceInternalFunction = await CodeConfluenceInternalFunction(
        qualified_name="org/repo/main/package/TestClass/test_function",  # Unique identifier
        name="test_function",  # Function name
        file_path="/test/path.py",  # Path to file containing the function
        line_number=2,  # Line number where function is defined
        return_type="str",  # Return type of the function
        docstring="Test function"  # Function documentation
    ).save()
    
    # Connect nodes according to the hierarchy: repo -> codebase -> package -> file -> class -> function
    # Each connection represents a relationship in the graph database
    await repo.codebases.connect(codebase)  # Repository contains codebase
    await codebase.packages.connect(package)  # Codebase contains package
    await package.files.connect(file)  # Package contains file
    await file.nodes.connect(class_node)  # File contains class node
    await class_node.file.connect(file)  # Class belongs to file (bidirectional relationship)
    await class_node.functions.connect(function)  # Class contains function
    
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
    
    # Verify bidirectional relationship between file and class
    # 1. File -> Class (file contains class)
    file_classes = await found_file.nodes.all()
    assert len(file_classes) == 1, "Expected exactly one class connected to file"
    found_class: CodeConfluenceClass = file_classes[0]
    assert found_class.name == "TestClass", "Class name mismatch"
    
    # 2. Class -> File (class belongs to file)
    class_file = await found_class.file.all()
    assert len(class_file) == 1, "Expected exactly one file connected to class"
    assert class_file[0].file_path == "/test/path.py", "File path mismatch in bidirectional relationship"
    
    # Verify class -> function relationship
    class_functions: List[CodeConfluenceInternalFunction] = await found_class.functions.all()
    assert len(class_functions) == 1, "Expected exactly one function connected to class"
    found_function: CodeConfluenceInternalFunction = class_functions[0]
    assert found_function.name == "test_function", "Function name mismatch"
    
    # Test complete traversal from repo all the way to function
    # This verifies we can navigate the entire hierarchy: repo -> codebase -> package -> file -> class -> function
    # We need to await each step in the chain since these are async relationships
    codebases = await found_repo.codebases.all()
    codebase = codebases[0]
    packages = await codebase.packages.all()
    package = packages[0]
    files = await package.files.all()
    file = files[0]
    nodes = await file.nodes.all()
    node = nodes[0]  # This is the class node
    functions = await node.functions.all()
    function = functions[0]
    assert function.name == "test_function", "Function name mismatch after complete traversal"