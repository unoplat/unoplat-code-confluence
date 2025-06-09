from neomodel import (
    AsyncStructuredNode, 
    StringProperty,
    AsyncStructuredRel
)

class BaseNode(AsyncStructuredNode):
    """Base node with common properties"""
    qualified_name = StringProperty(unique_index=True, required=True)
    
class ContainsRelationship(AsyncStructuredRel):
    """Relationship for representing containment between nodes"""
    pass
