from .base_models import BaseNode, ContainsRelationship
from neomodel import RelationshipFrom, RelationshipTo, StringProperty,ZeroOrMore,One,ArrayProperty,VectorIndex,FloatProperty

class Package(BaseNode):
    """Represents a package in the codebase"""
    package_objective = StringProperty(required=True)
    package_implementation_summary = StringProperty(required=True,default="")
    
    package_objective_embedding = ArrayProperty(
        FloatProperty(),
        vector_index=VectorIndex(dimensions=4096, similarity_function='cosine')
    )
    package_implementation_summary_embedding = ArrayProperty(
        FloatProperty(),
        vector_index=VectorIndex(dimensions=4096, similarity_function='cosine')
    )
    
    codebase = RelationshipFrom('Codebase', 'CONTAINS', model=ContainsRelationship, cardinality=One)

    sub_packages = RelationshipTo('Package', 'CONTAINS', model=ContainsRelationship, cardinality=ZeroOrMore)

    classes = RelationshipTo('Class', 'CONTAINS', model=ContainsRelationship, cardinality=ZeroOrMore)
