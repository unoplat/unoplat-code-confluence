from neomodel import (
    AsyncStructuredNode, 
    StringProperty, 
    JSONProperty,
    AsyncStructuredRel
)

class BaseNode(AsyncStructuredNode):
    """Base node with common properties"""
    qualified_name = StringProperty(unique_index=True, required=True)
    
class ContainsRelationship(AsyncStructuredNode):
    """Relationship for representing containment between nodes"""
    pass

class AnnotatedRelationship(AsyncStructuredRel):
    """Relationship for representing annotation on nodes and methods"""
    position = JSONProperty()
    key_values = JSONProperty()      # KeyValues (list[ChapiAnnotationKeyVal])
