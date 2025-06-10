****# Unoplat Code Confluence Commons Schema Documentation

This document provides a comprehensive overview of the graph data model schema used in the Unoplat Code Confluence Commons project. The schema is built using neomodel for Neo4j graph database integration.

## Table of Contents

- [Base Models](#base-models)
- [Node Models](#node-models)
- [Relationship Overview](#relationship-overview)

## Base Models

These models serve as the foundation for all other models in the schema.

### BaseNode

**Description**: Base node class that provides common properties for all nodes in the graph.

**Properties**:
- `qualified_name` (StringProperty, unique_index=True, required=True): Unique identifier for the node.

**Code**:
```python
from neomodel import (
    AsyncStructuredNode, 
    StringProperty,
    AsyncStructuredRel
)

class BaseNode(AsyncStructuredNode):
    """Base node with common properties"""
    qualified_name = StringProperty(unique_index=True, required=True)
```

### ContainsRelationship

**Description**: Relationship class for representing containment between nodes.

**Properties**: None (Pass-through relationship)

**Code**:
```python
class ContainsRelationship(AsyncStructuredRel):
    """Relationship for representing containment between nodes"""
    pass
```

## Node Models

### CodeConfluenceGitRepository

**Description**: Represents a Git repository in the system.

**Properties**:

- `repository_url` (StringProperty, required=True, unique_index=True): The URL used to clone or reference the repository.
- `repository_name` (StringProperty, required=True, unique_index=True): A human-friendly or organizational name for the repository.
- `repository_metadata` (JSONProperty): Arbitrary JSON metadata describing the repository.
- `readme` (StringProperty): Optional text content of the repository's main README.

**Relationships**:

- `codebases` (AsyncRelationshipTo → CodeConfluenceCodebase, 'CONTAINS_CODEBASE', cardinality=AsyncOneOrMore): Points to codebase nodes.

**Code**:
```python
from neomodel import (
    StringProperty,
    JSONProperty,
    AsyncRelationshipTo,
    AsyncOneOrMore
)
from .base_models import BaseNode, ContainsRelationship

class CodeConfluenceGitRepository(BaseNode):
    """
    Represents a Git repository in the system.

    Inherits from:
        BaseNode (which itself extends StructuredNode).
        - Includes common fields like 'qualified_name' (unique_index).

    Fields:
        repository_url (str): The URL used to clone or reference the repository.
        repository_name (str): A human-friendly or organizational name for the repository.
        repository_metadata (dict): Arbitrary JSON metadata describing the repository
                                    (e.g., stats, commits, custom config).
        github_organization (str): A specific GitHub (or other host) organization name.
        readme (str): Optional text content of the repository's main README.
    Relationships:
        codebases (RelationshipTo): Points to codebase nodes if needed.
                                    Uses ContainsRelationship to hold any
                                    extra relationship metadata.
    """
    repository_url = StringProperty(required=True,unique_index=True)
    repository_name = StringProperty(required=True, unique_index=True)
    repository_metadata = JSONProperty()
    readme = StringProperty()

    # Example relationship to a Codebase node class (not shown in this snippet)
    # The ContainsRelationship lets you store relationship metadata if desired
    codebases = AsyncRelationshipTo(
        '.code_confluence_codebase.CodeConfluenceCodebase',  # adjust import path to match your structure
        'CONTAINS_CODEBASE',
        model=ContainsRelationship,
        cardinality=AsyncOneOrMore
    )
```

### CodeConfluenceCodebase

**Description**: Represents a codebase within a Git repository.

**Properties**:

- `name` (StringProperty, required=True): The name of the codebase or root package.
- `readme` (StringProperty): Optional content of the codebase's README file.
- `root_packages` (ArrayProperty(StringProperty)): List of root package names in the codebase.
- `codebase_path` (StringProperty, required=True): File system path to the codebase.
- `programming_language` (StringProperty, choices=['python', 'java', 'go', 'typescript']): The primary programming language of the codebase.

**Relationships**:

- `packages` (AsyncRelationshipTo → CodeConfluencePackage, 'CONTAINS_PACKAGE', cardinality=AsyncZeroOrMore): Connects to package nodes.
- `package_manager_metadata` (AsyncRelationshipTo → CodeConfluencePackageManagerMetadata, 'HAS_PACKAGE_MANAGER_METADATA', cardinality=AsyncOne): Connects to package manager metadata node.
- `git_repository` (AsyncRelationshipTo → CodeConfluenceGitRepository, 'PART_OF_GIT_REPOSITORY', cardinality=AsyncOne): Connects to the parent git repository.

**Code**:

```python
from neomodel import (
    StringProperty,
    ArrayProperty,
    AsyncRelationshipTo,
    AsyncZeroOrMore,
    AsyncOne
)
from .base_models import BaseNode, ContainsRelationship

class CodeConfluenceCodebase(BaseNode):
    """
    Represents a codebase within a Git repository.

    Fields:
        name (str): The name of the codebase or root package.
        readme (str): Optional content of the codebase's README file.
        programming_language (str): The primary programming language of the codebase.
    
    Relationships:
        packages (RelationshipTo): Connects to package nodes.
        package_manager_metadata (RelationshipTo): Connects to package manager metadata node.
    """
    
    # Programming language choices
    PROGRAMMING_LANGUAGES = {
        'python': 'Python',
        'java': 'Java',
        'go': 'Go',
        'typescript': 'TypeScript',
    }
    
    name = StringProperty(required=True)
    readme = StringProperty()
    root_packages = ArrayProperty(StringProperty())
    codebase_path = StringProperty(required=True)
    programming_language = StringProperty(choices=PROGRAMMING_LANGUAGES)
    
    packages = AsyncRelationshipTo(
        '.code_confluence_package.CodeConfluencePackage',
        'CONTAINS_PACKAGE',
        model=ContainsRelationship,
        cardinality=AsyncZeroOrMore
    )
    
    package_manager_metadata = AsyncRelationshipTo(
        '.code_confluence_package_manager_metadata.CodeConfluencePackageManagerMetadata',
        'HAS_PACKAGE_MANAGER_METADATA',
        model=ContainsRelationship,
        cardinality=AsyncOne
    )
    
    git_repository = AsyncRelationshipTo(
        '.code_confluence_git_repository.CodeConfluenceGitRepository',
        'PART_OF_GIT_REPOSITORY',
        model=ContainsRelationship,
        cardinality=AsyncOne
    )
```

### CodeConfluencePackageManagerMetadata

**Description**: Represents package manager metadata for a codebase.

**Properties**:

- `dependencies` (JSONProperty, default={}): JSON object containing project dependencies.
- `package_manager` (StringProperty, required=True): Name of the package manager (e.g., pip, npm).
- `programming_language` (StringProperty, required=True): Programming language used in the codebase.
- `programming_language_version` (StringProperty): Version of the programming language.
- `project_version` (StringProperty): Version of the project.
- `description` (StringProperty): Description of the project.
- `license` (StringProperty): License of the project.
- `package_name` (StringProperty): Name of the package.
- `entry_points` (JSONProperty, default={}): Dictionary of script names to their entry points.
- `authors` (ArrayProperty(StringProperty)): List of project authors.

**Relationships**:

- `codebase` (AsyncRelationshipFrom ← CodeConfluenceCodebase, 'HAS_PACKAGE_MANAGER_METADATA', cardinality=AsyncOne): Connection back to the parent codebase.

**Code**:

```python
from neomodel import (
    StringProperty,
    JSONProperty,
    AsyncRelationshipFrom,
    ArrayProperty,
    AsyncOne
)
from .base_models import BaseNode, ContainsRelationship

class CodeConfluencePackageManagerMetadata(BaseNode):
    """
    Represents package manager metadata for a codebase.
    
    Fields:
        package_manager (str): Name of the package manager (e.g., pip, npm)
        programming_language (str): Programming language used in the codebase
        project_version (str): Version of the project
        programming_language_version (str): Version of the programming language
        description (str): Description of the project
        license (str): License of the project
        dependencies (dict): JSON object containing project dependencies
        entry_points (dict): Dictionary of script names to their entry points
        authors (list): List of project authors
        
    Relationships:
        codebase (RelationshipFrom): Connection back to the parent codebase
    """
    dependencies = JSONProperty(default={})
    package_manager = StringProperty(required=True)
    programming_language = StringProperty(required=True)
    programming_language_version = StringProperty()
    project_version = StringProperty()
    description = StringProperty()
    license = StringProperty()
    package_name = StringProperty()
    entry_points = JSONProperty(default={})
    authors = ArrayProperty(StringProperty())

    # Bidirectional relationship with CodeConfluenceCodebase
    codebase = AsyncRelationshipFrom(
        '.code_confluence_codebase.CodeConfluenceCodebase',
        'HAS_PACKAGE_MANAGER_METADATA',
        model=ContainsRelationship,
        cardinality=AsyncOne
    )
```

### CodeConfluencePackage

**Description**: Represents a package within a codebase.

**Properties**:

- `name` (StringProperty): The name of the package.

**Relationships**:

- `sub_packages` (AsyncRelationship ↔ CodeConfluencePackage, 'CONTAINS_PACKAGE', cardinality=AsyncZeroOrMore): Connects to sub-package nodes.
- `codebase` (AsyncRelationshipTo → CodeConfluenceCodebase, 'PART_OF_CODEBASE', cardinality=AsyncOne): Connects to the parent codebase.
- `files` (AsyncRelationshipTo → CodeConfluenceFile, 'CONTAINS_FILE', cardinality=AsyncZeroOrMore): Connects to files within the package.

**Code**:

```python
from neomodel import (
    StringProperty,
    AsyncRelationshipTo,
    AsyncZeroOrMore,
    AsyncRelationship,
    AsyncOne
)
from unoplat_code_confluence_commons.graph_models.base_models import BaseNode, ContainsRelationship

class CodeConfluencePackage(BaseNode):
    """
    Represents a package within a codebase.

    Fields:
        name (str): The name of the package.
        
    Relationships:
        sub_packages (RelationshipTo): Connects to sub-package nodes.
        codebase (RelationshipTo): Connects to the parent codebase.
        classes (RelationshipTo): Connects to the classes within the package.
    """
    name = StringProperty()
    
    
    sub_packages = AsyncRelationship(
        '.code_confluence_package.CodeConfluencePackage',
        'CONTAINS_PACKAGE',
        model=ContainsRelationship,
        cardinality=AsyncZeroOrMore
    )
    
    
    codebase = AsyncRelationshipTo(
        '.code_confluence_codebase.CodeConfluenceCodebase',
        'PART_OF_CODEBASE',
        model=ContainsRelationship,
        cardinality=AsyncOne
    )
    
    files = AsyncRelationshipTo(
        '.code_confluence_file.CodeConfluenceFile',
        'CONTAINS_FILE',
        model=ContainsRelationship,
        cardinality=AsyncZeroOrMore,
    )
```

### CodeConfluenceFile

**Description**: Graph node representing a single source file.

**Properties**:

- `file_path` (StringProperty, required=True, unique_index=True): Path to the file.
- `content` (StringProperty, fulltext_index=FulltextIndex(analyzer="english")): Content of the file with full-text search support.
- `checksum` (StringProperty): Checksum of the file content.
- `structural_signature` (JSONProperty): Structural signature of the file containing detailed structure information including class variables.
- `global_variables` (ArrayProperty(StringProperty), default=[]): List of global variables in the file.
- `imports` (ArrayProperty(StringProperty), default=[], fulltext_index=FulltextIndex(analyzer="english")): List of imports in the file with full-text search support.
- `poi_labels` (ArrayProperty(StringProperty), fulltext_index=FulltextIndex(analyzer="english")): Points of interest labels with full-text search support.

**Relationships**:

- `package` (AsyncRelationshipTo → CodeConfluencePackage, 'PART_OF_PACKAGE', cardinality=AsyncOne): Connection to the parent package.

**Code**:

```python
from neomodel import AsyncStructuredNode, StringProperty, AsyncRelationshipTo, AsyncOne
from neomodel import JSONProperty, ArrayProperty, FulltextIndex
from unoplat_code_confluence_commons.graph_models.base_models import ContainsRelationship

class CodeConfluenceFile(AsyncStructuredNode):
    """
    Graph node representing a single source file.

    Relationships
    ─────────────
    package  (PART_OF_PACKAGE)  -> CodeConfluencePackage
    """
    file_path = StringProperty(required=True, unique_index=True)
    content   = StringProperty(fulltext_index=FulltextIndex(analyzer="english"))
    checksum  = StringProperty()
    structural_signature = JSONProperty()
    global_variables = ArrayProperty(StringProperty(), default=[])
    imports = ArrayProperty(
        StringProperty(),
        default=[],
        fulltext_index=FulltextIndex(analyzer="english")
    )
    poi_labels = ArrayProperty(
        StringProperty(),
        fulltext_index=FulltextIndex(analyzer="english")
    )
    package = AsyncRelationshipTo(
        '.code_confluence_package.CodeConfluencePackage',
        'PART_OF_PACKAGE',
        model=ContainsRelationship,
        cardinality=AsyncOne,
    )
```

## Relationship Overview

This section provides a visual representation of how the models are connected:

```text
CodeConfluenceGitRepository
  ├── CONTAINS_CODEBASE → CodeConfluenceCodebase
      ├── HAS_PACKAGE_MANAGER_METADATA → CodeConfluencePackageManagerMetadata
      ├── PART_OF_GIT_REPOSITORY → CodeConfluenceGitRepository
      └── CONTAINS_PACKAGE → CodeConfluencePackage
          ├── PART_OF_CODEBASE → CodeConfluenceCodebase
          ├── CONTAINS_PACKAGE → CodeConfluencePackage (self-reference for sub-packages)
          └── CONTAINS_FILE → CodeConfluenceFile
              └── PART_OF_PACKAGE → CodeConfluencePackage
```

This schema represents a comprehensive graph model for code analysis and representation, capturing the relationships between repositories, codebases, packages, and files.
