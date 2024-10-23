from .base_models import BaseNode, ContainsRelationship
from neomodel import RelationshipFrom, RelationshipTo, StringProperty,ZeroOrMore,One

class Class(BaseNode):
    """Represents a class in a package"""
    node_name = StringProperty(required=True)
    node_summary = StringProperty(default="")
    node_objective = StringProperty(default="")
    # Class relationships
    package = RelationshipFrom('Package', 'CONTAINS', model=ContainsRelationship, cardinality=One)
    methods = RelationshipTo('Method', 'CONTAINS', model=ContainsRelationship, cardinality=ZeroOrMore)
