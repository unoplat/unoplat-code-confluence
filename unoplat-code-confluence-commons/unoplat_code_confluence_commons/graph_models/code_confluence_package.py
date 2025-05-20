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
    
    # classes = AsyncRelationshipTo(
    #     '.code_confluence_class.CodeConfluenceClass',
    #     'CONTAINS_CLASS',
    #     model=ContainsRelationship,
    #     cardinality=AsyncZeroOrMore
    # )
