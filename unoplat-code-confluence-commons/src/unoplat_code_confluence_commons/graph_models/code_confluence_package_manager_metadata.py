from unoplat_code_confluence_commons.graph_models.base_models import (
    BaseNode,
    ContainsRelationship,
)

from neomodel import (
    ArrayProperty,
    AsyncOne,
    AsyncRelationshipFrom,
    JSONProperty,
    StringProperty,
)


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
    other_metadata = JSONProperty(default={})
    package_manager = StringProperty(required=True)
    programming_language = StringProperty(required=True)
    # programming_language_version = StringProperty()  # TODO: consolidated via other_metadata
    # project_version = StringProperty()  # TODO: consolidated via other_metadata
    # description = StringProperty()  # TODO: consolidated via other_metadata
    # license = StringProperty()  # TODO: consolidated via other_metadata
    # package_name = StringProperty()  # TODO: consolidated via other_metadata
    # entry_points = JSONProperty(default={})  # TODO: fold into other_metadata once ingestion path is updated
    # authors = ArrayProperty(StringProperty())  # TODO: move to other_metadata post-refactor

    # Bidirectional relationship with CodeConfluenceCodebase
    codebase = AsyncRelationshipFrom(
        '.code_confluence_codebase.CodeConfluenceCodebase',
        'HAS_PACKAGE_MANAGER_METADATA',
        model=ContainsRelationship,
        cardinality=AsyncOne
    )
