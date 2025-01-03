from neomodel import (
    StringProperty,
    RelationshipTo,
    RelationshipFrom,
    StructuredRel,
    ZeroOrMore,
    One
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
    """
    name = StringProperty(required=True)
    

    
    # Relationship to sub-packages within the package
    sub_packages = RelationshipTo(
        '.code_confluence_package.CodeConfluencePackage',
        'CONTAINS_PACKAGE',
        model=ContainsRelationship,
        cardinality=ZeroOrMore
    )
    
    # Relationship to the parent codebase
    codebase = RelationshipFrom(
        '.code_confluence_codebase.CodeConfluenceCodebase',
        'PART_OF_CODEBASE',
        model=ContainsRelationship,
        cardinality=One
    )
    
    classes = RelationshipTo(
        '.code_confluence_class.CodeConfluenceClass',
        'CONTAINS_CLASS',
        model=ContainsRelationship,
        cardinality=ZeroOrMore
    )