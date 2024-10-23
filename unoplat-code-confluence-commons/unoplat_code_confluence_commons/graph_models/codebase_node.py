from neomodel import (
    StringProperty,
    RelationshipTo,
    RelationshipFrom,
    ZeroOrMore,
    One,
    ArrayProperty,
    VectorIndex
)
from .base_models import BaseNode, ContainsRelationship

class Codebase(BaseNode):
    """Represents a codebase in the system"""
    codebase_summary = StringProperty(default="")
    codebase_objective = StringProperty(default="")
    codebase_objective_embedding = ArrayProperty(
        default=[],
        vector_index=VectorIndex(dimensions=4096, similarity_function='cosine')
    )
    codebase_implementation_embedding = ArrayProperty(
        default=[],
        vector_index=VectorIndex(dimensions=4096, similarity_function='cosine')
    )
    # One codebase can contain multiple packages
    packages = RelationshipTo('Package', 'CONTAINS', model=ContainsRelationship, cardinality=ZeroOrMore)



