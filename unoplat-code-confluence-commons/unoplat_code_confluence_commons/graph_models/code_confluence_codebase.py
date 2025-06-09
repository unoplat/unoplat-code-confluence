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