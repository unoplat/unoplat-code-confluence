from neomodel import (
    StructuredNode, 
    StringProperty, 
    JSONProperty, 
    ArrayProperty,
    StructuredRel
)

class BaseNode(StructuredNode):
    """Base node with common properties"""
    qualified_name = StringProperty(unique_index=True, required=True)
    objective_embedding = ArrayProperty(default=[])
    implementation_embedding = ArrayProperty(default=[])

class ContainsRelationship(StructuredRel):
    """Relationship for representing containment between nodes"""
    pass
