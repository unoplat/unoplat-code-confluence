from neomodel import (
    StringProperty,
    RelationshipTo,
    RelationshipFrom,
    ZeroOrMore,
    One
)
from .base_models import BaseNode, ContainsRelationship

class Codebase(BaseNode):
    """Represents a codebase in the system"""
    codebase_summary = StringProperty(default="")
    codebase_objective = StringProperty(default="")
    # One codebase can contain multiple packages
    packages = RelationshipTo('Package', 'CONTAINS', model=ContainsRelationship, cardinality=ZeroOrMore)


