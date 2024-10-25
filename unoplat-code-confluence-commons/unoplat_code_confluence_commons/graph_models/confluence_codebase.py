from neomodel import (
    StringProperty,
    RelationshipTo,
    RelationshipFrom,
    ZeroOrMore,
    One,
    ArrayProperty,
    VectorIndex,
    FloatProperty
)
from .base_models import BaseNode, ContainsRelationship

class ConfluenceCodebase(BaseNode):
    """Represents a codebase in the system"""
    codebase_summary = StringProperty(default="")
    codebase_objective = StringProperty(default="")
    codebase_objective_embedding = ArrayProperty(FloatProperty())
    codebase_implementation_embedding = ArrayProperty(FloatProperty())
    # One codebase can contain multiple packages
    packages = RelationshipTo('.confluence_package.ConfluencePackage', 'CONTAINS', model=ContainsRelationship, cardinality=ZeroOrMore)



