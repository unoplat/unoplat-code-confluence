from .base_models import BaseNode, ContainsRelationship
from neomodel import RelationshipFrom, RelationshipTo, StringProperty,ZeroOrMore,One,ArrayProperty,VectorIndex

class Class(BaseNode):
    """Represents a class in a package"""
    class_name = StringProperty(required=True)
    class_implementation_summary = StringProperty(default="")
    class_objective = StringProperty(default="")
    class_objective_embedding = ArrayProperty(
        default=[],
        vector_index=VectorIndex(dimensions=4096, similarity_function='cosine')
    )
    class_implementation_summary_embedding = ArrayProperty(
        default=[],
        vector_index=VectorIndex(dimensions=4096, similarity_function='cosine')
    )
    # Class relationships
    package = RelationshipFrom('Package', 'CONTAINS', model=ContainsRelationship, cardinality=One)
    methods = RelationshipTo('Method', 'CONTAINS', model=ContainsRelationship, cardinality=ZeroOrMore)
