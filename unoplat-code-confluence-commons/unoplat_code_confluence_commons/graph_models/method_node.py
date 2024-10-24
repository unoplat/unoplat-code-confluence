from .base_models import BaseNode, ContainsRelationship
from neomodel import RelationshipFrom, StringProperty,One,ArrayProperty,VectorIndex,FloatProperty

class Method(BaseNode):
    """Represents a method in a class"""
    function_name = StringProperty(required=True)
    function_implementation_summary = StringProperty(default="")
    function_objective = StringProperty(default="")
    function_objective_embedding = ArrayProperty(
        FloatProperty(),
        vector_index=VectorIndex(dimensions=4096, similarity_function='cosine')
    )
    function_summary_embedding = ArrayProperty(
        FloatProperty(),
        vector_index=VectorIndex(dimensions=4096, similarity_function='cosine')
    )
    # Method relationships
    class_ = RelationshipFrom('Class', 'CONTAINS', model=ContainsRelationship, cardinality=One)
