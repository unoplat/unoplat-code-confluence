---
trigger: model_decision
description: Whenever information regarding neo4j schema is needed use this.
---

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

### ContainsRelationship

**Description**: Relationship class for representing containment between nodes.

**Properties**: None (Pass-through relationship)

### AnnotatedRelationship

**Description**: Relationship class for representing annotations on nodes and methods.

**Properties**:
- `position` (JSONProperty): Position information for the annotation.
- `key_values` (JSONProperty): Key-value pairs for the annotation (list of ChapiAnnotationKeyVal).

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

### CodeConfluenceCodebase

**Description**: Represents a codebase within a Git repository.

**Properties**:
- `name` (StringProperty, required=True): The name of the codebase or root package.
- `readme` (StringProperty): Optional content of the codebase's README file.
- `local_path` (StringProperty, required=True): Local file system path to the codebase.

**Relationships**:
- `packages` (AsyncRelationshipTo → CodeConfluencePackage, 'CONTAINS_PACKAGE', cardinality=AsyncZeroOrMore): Connects to package nodes.
- `package_manager_metadata` (AsyncRelationshipTo → CodeConfluencePackageManagerMetadata, 'HAS_PACKAGE_MANAGER_METADATA', cardinality=AsyncOne): Connects to package manager metadata node.
- `git_repository` (AsyncRelationshipTo → CodeConfluenceGitRepository, 'PART_OF_GIT_REPOSITORY', cardinality=AsyncOne): Connects to the parent git repository.

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

### CodeConfluencePackage

**Description**: Represents a package within a codebase.

**Properties**:
- `name` (StringProperty): The name of the package.

**Relationships**:
- `sub_packages` (AsyncRelationship ↔ CodeConfluencePackage, 'CONTAINS_PACKAGE', cardinality=AsyncZeroOrMore): Connects to sub-package nodes.
- `codebase` (AsyncRelationshipTo → CodeConfluenceCodebase, 'PART_OF_CODEBASE', cardinality=AsyncOne): Connects to the parent codebase.
- `files` (AsyncRelationshipTo → CodeConfluenceFile, 'CONTAINS_FILE', cardinality=AsyncZeroOrMore): Connects to files within the package.

### CodeConfluenceFile

**Description**: Graph node representing a single source file.

**Properties**:
- `file_path` (StringProperty, required=True, unique_index=True): Path to the file.
- `content` (StringProperty): Content of the file.
- `checksum` (StringProperty): Checksum of the file content.

**Relationships**:
- `package` (AsyncRelationshipTo → CodeConfluencePackage, 'PART_OF_PACKAGE', cardinality=AsyncOne): Connection to the parent package.
- `nodes` (AsyncRelationship ↔ CodeConfluenceClass, 'CONTAINS_NODE', cardinality=AsyncZeroOrMore): Connects to class nodes within the file.

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
- `global_