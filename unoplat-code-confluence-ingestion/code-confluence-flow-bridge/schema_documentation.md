# Unoplat Code Confluence Commons Schema Documentation

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
    JSONProperty,
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

### AnnotatedRelationship

**Description**: Relationship class for representing annotations on nodes and methods.

**Properties**:

- `position` (JSONProperty): Position information for the annotation.
- `key_values` (JSONProperty): Key-value pairs for the annotation (list of ChapiAnnotationKeyVal).

**Code**:
```python
class AnnotatedRelationship(AsyncStructuredRel):
    """Relationship for representing annotation on nodes and methods"""
    position = JSONProperty()
    key_values = JSONProperty()      # KeyValues (list[ChapiAnnotationKeyVal])
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
- `root_packages` (ArrayProperty(StringProperty)): List of root package paths within the codebase.
- `codebase_path` (StringProperty, required=True): Codebase root directory path.

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
        root_packages (ArrayProperty): List of root package paths within the codebase.
        codebase_path (str): Codebase root directory path.
    
    Relationships:
        packages (RelationshipTo): Connects to package nodes.
        package_manager_metadata (RelationshipTo): Connects to package manager metadata node.
    """
    name = StringProperty(required=True)
    readme = StringProperty()
    root_packages = ArrayProperty(StringProperty())
    codebase_path = StringProperty(required=True)
    
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
- `content` (StringProperty): Content of the file.
- `checksum` (StringProperty): Checksum of the file content.

**Relationships**:

- `package` (AsyncRelationshipTo → CodeConfluencePackage, 'PART_OF_PACKAGE', cardinality=AsyncOne): Connection to the parent package.
- `nodes` (AsyncRelationship ↔ CodeConfluenceClass, 'CONTAINS_NODE', cardinality=AsyncZeroOrMore): Connects to class nodes within the file.

**Code**:
```python
from neomodel import AsyncStructuredNode, StringProperty, AsyncRelationshipTo, AsyncRelationship, AsyncOne, AsyncZeroOrMore

from unoplat_code_confluence_commons.graph_models.base_models import BaseNode, ContainsRelationship

class CodeConfluenceFile(AsyncStructuredNode):
    """
    Graph node representing a single source file.

    Relationships
    ─────────────
    package  (PART_OF_PACKAGE)  -> CodeConfluencePackage
    nodes    (CONTAINS_NODE)    -> CodeConfluenceClass / CodeConfluenceInternalFunction
    """
    file_path = StringProperty(required=True, unique_index=True)
    content   = StringProperty()
    checksum  = StringProperty()

    package = AsyncRelationshipTo(
        '.code_confluence_package.CodeConfluencePackage',
        'PART_OF_PACKAGE',
        model=ContainsRelationship,
        cardinality=AsyncOne,
    )

    nodes = AsyncRelationship(
        '.code_confluence_class.CodeConfluenceClass',
        'CONTAINS_NODE',
        model=ContainsRelationship,
        cardinality=AsyncZeroOrMore,
    )
```

### CodeConfluenceClass

**Description**: Represents a class-like node, combining fields from ChapiNode and UnoplatChapiForgeNode.

**Properties**:

- `name` (StringProperty): The name of the class (NodeName).
- `type_` (StringProperty): Type of the node.
- `file_path` (StringProperty): Path to the file containing the class.
- `module` (StringProperty): Module containing the class.
- `multiple_extend` (ArrayProperty(StringProperty), default=[]): List of extended classes.
- `fields` (JSONProperty): Fields of the class (list of ClassGlobalFieldModel).
- `extend` (StringProperty): Class being extended.
- `position` (JSONProperty): Position information for the class.
- `content` (StringProperty): Content of the class.
- `comments_description` (StringProperty): Description from comments.
- `segregated_imports` (JSONProperty): Segregated imports information.
- `dependent_internal_classes` (ArrayProperty(StringProperty), default=[]): List of dependent internal classes.
- `global_variables` (JSONProperty, default=[]): Global variables.

**Relationships**:

- `functions` (AsyncRelationshipTo → CodeConfluenceInternalFunction, 'HAS_FUNCTION', cardinality=AsyncZeroOrMore): Connects to function nodes.
- `annotations` (AsyncRelationship ↔ CodeConfluenceAnnotation, 'HAS_ANNOTATION', cardinality=AsyncZeroOrMore): Connects to annotation nodes.
- `package` (AsyncRelationshipTo → CodeConfluencePackage, 'PART_OF_PACKAGE', cardinality=AsyncOne): Connects to the parent package.
- `file` (AsyncRelationshipTo → CodeConfluenceFile, 'PART_OF_FILE', cardinality=AsyncOne): Connects to the parent file.

**Code**:
```python
from neomodel import (
    StringProperty,
    ArrayProperty,
    JSONProperty,
    AsyncRelationshipTo,
    AsyncRelationshipFrom,
    AsyncRelationship,
    AsyncZeroOrMore,
    AsyncOne,
    AsyncOneOrMore
)

from .base_models import AnnotatedRelationship, BaseNode, ContainsRelationship

class CodeConfluenceClass(BaseNode):
    """
    Represents a class-like node, combining fields from:
      - ChapiNode
      - UnoplatChapiForgeNode
    """
    # From ChapiNode
    name = StringProperty()       # NodeName
    type_ = StringProperty()           # Type (renamed to avoid Python 'type' shadowing)
    file_path = StringProperty()       # FilePath
    module = StringProperty()          # Module
    multiple_extend = ArrayProperty(StringProperty(), default=[])  # MultipleExtend
    fields = JSONProperty()                # Fields (list of ClassGlobalFieldModel)
    extend = StringProperty()          # Extend
    position = JSONProperty()          # Position
    content = StringProperty()         # Content

    # From UnoplatChapiForgeNode
    comments_description = StringProperty()  # CommentsDescription
    segregated_imports = JSONProperty()      # SegregatedImports
    dependent_internal_classes = ArrayProperty(StringProperty(), default=[])  # DependentInternalClasses
    global_variables = JSONProperty(default=[])            # GlobalVariables

    # RELATIONSHIPS
    # "Functions" from either ChapiNode or UnoplatChapiForgeNode become a relationship
    functions = AsyncRelationshipTo(".code_confluence_internal_function.CodeConfluenceInternalFunction", "HAS_FUNCTION",model=ContainsRelationship,cardinality=AsyncZeroOrMore)
    
    # Classes can also have annotations
    annotations = AsyncRelationship(".code_confluence_annotation.CodeConfluenceAnnotation", "HAS_ANNOTATION",model=AnnotatedRelationship,cardinality=AsyncZeroOrMore)
    
    # relation to package
    package = AsyncRelationshipTo(".code_confluence_package.CodeConfluencePackage", "PART_OF_PACKAGE",model=ContainsRelationship,cardinality=AsyncOne)
    
    file = AsyncRelationshipTo(
        '.code_confluence_file.CodeConfluenceFile',
        'PART_OF_FILE',
        model=ContainsRelationship,
        cardinality=AsyncOne,
    )
```

### CodeConfluenceInternalFunction

**Description**: Represents a function-like node, combining fields from ChapiFunction and UnoplatChapiForgeFunction.

**Properties**:

- `name` (StringProperty): Name of the function.
- `return_type` (StringProperty): Return type of the function.
- `function_calls` (JSONProperty, default=[]): Function calls made within the function.
- `parameters` (JSONProperty, default=[]): Parameters of the function.
- `position` (JSONProperty): Position information for the function.
- `body_hash` (IntegerProperty): Hash of the function body.
- `content` (StringProperty): Content of the function.
- `comments_description` (StringProperty): Description from comments.

**Relationships**:

- `annotations` (AsyncRelationship ↔ CodeConfluenceAnnotation, 'HAS_ANNOTATION', cardinality=AsyncZeroOrMore): Connects to annotation nodes.
- `confluence_class` (AsyncRelationshipTo → CodeConfluenceClass, 'PART_OF_CLASS', cardinality=AsyncOne): Connects to the parent class.

**Code**:
```python
from neomodel import (
    StringProperty,
    IntegerProperty,
    JSONProperty,
    AsyncRelationshipTo,
    AsyncRelationship,
    AsyncZeroOrMore,
    AsyncOne
)
from .base_models import AnnotatedRelationship, BaseNode,ContainsRelationship

class CodeConfluenceInternalFunction(BaseNode):
    """
    Represents a function-like node, combining fields from:
      - ChapiFunction
      - UnoplatChapiForgeFunction
    """
    # From ChapiFunction
    name = StringProperty()              # Name
    return_type = StringProperty()       # ReturnType
    # function_calls, parameters, local_variables can be stored as JSON
    function_calls = JSONProperty(default=[])          # FunctionCalls
    parameters = JSONProperty(default=[])              # Parameters
    position = JSONProperty()            # Position
    body_hash = IntegerProperty()        # BodyHash
    content = StringProperty()           # Content
    comments_description = StringProperty() # CommentsDescription

    # RELATIONSHIPS
    annotations = AsyncRelationship(".code_confluence_annotation.CodeConfluenceAnnotation", "HAS_ANNOTATION",model=AnnotatedRelationship,cardinality=AsyncZeroOrMore)
    
    confluence_class = AsyncRelationshipTo(".code_confluence_class.CodeConfluenceClass", "PART_OF_CLASS",model=ContainsRelationship,cardinality=AsyncOne)
```

### CodeConfluenceAnnotation

**Description**: Represents an annotation node based on ChapiAnnotation.

**Properties**:

- `name` (StringProperty, required=True, unique_index=True): Name of the annotation.

**Relationships**:

- `annotated_classes` (AsyncRelationship ↔ CodeConfluenceClass, 'HAS_ANNOTATION', cardinality=AsyncZeroOrMore): Connects to annotated class nodes.
- `annotated_functions` (AsyncRelationship ↔ CodeConfluenceInternalFunction, 'HAS_ANNOTATION', cardinality=AsyncZeroOrMore): Connects to annotated function nodes.

**Code**:
```python
from neomodel import (
    AsyncStructuredNode,
    StringProperty,
    AsyncRelationship,
    AsyncZeroOrMore
)

from unoplat_code_confluence_commons.graph_models.base_models import AnnotatedRelationship

class CodeConfluenceAnnotation(AsyncStructuredNode):
    """
    Represents an annotation node based on ChapiAnnotation.
    """
    name = StringProperty(required=True,unique_index=True)      # Name
    # key_values can be stored as JSON if you don't need them as separate nodes
    annotated_classes = AsyncRelationship('.code_confluence_class.CodeConfluenceClass', 'HAS_ANNOTATION', model=AnnotatedRelationship, cardinality=AsyncZeroOrMore)
    annotated_functions = AsyncRelationship('.code_confluence_internal_function.CodeConfluenceInternalFunction', 'HAS_ANNOTATION', model=AnnotatedRelationship, cardinality=AsyncZeroOrMore)
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
              ├── PART_OF_PACKAGE → CodeConfluencePackage
              └── CONTAINS_NODE → CodeConfluenceClass
                  ├── PART_OF_FILE → CodeConfluenceFile
                  ├── PART_OF_PACKAGE → CodeConfluencePackage
                  ├── HAS_FUNCTION → CodeConfluenceInternalFunction
                  │   ├── PART_OF_CLASS → CodeConfluenceClass
                  │   └── HAS_ANNOTATION ↔ CodeConfluenceAnnotation
                  └── HAS_ANNOTATION ↔ CodeConfluenceAnnotation
                      ├── HAS_ANNOTATION ↔ CodeConfluenceClass
                      └── HAS_ANNOTATION ↔ CodeConfluenceInternalFunction
```

This schema represents a comprehensive graph model for code analysis and representation, capturing the relationships between repositories, codebases, packages, files, classes, functions, and annotations.
