from .base_models import BaseNode, ContainsRelationship
from neomodel import RelationshipFrom, StringProperty,One

class Method(BaseNode):
    """Represents a method in a class"""
    function_name = StringProperty(required=True)
    function_summary = StringProperty(default="")
    # Method relationships
    class_ = RelationshipFrom('Class', 'CONTAINS', model=ContainsRelationship, cardinality=One)
