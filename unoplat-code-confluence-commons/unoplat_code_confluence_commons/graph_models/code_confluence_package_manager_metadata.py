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
