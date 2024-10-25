from .base_models import BaseNode, ContainsRelationship
from neomodel import RelationshipFrom, RelationshipTo, StringProperty,ZeroOrMore,One,ArrayProperty,VectorIndex,FloatProperty

class ConfluenceClass(BaseNode):
    """Represents a class in a package"""
    class_name = StringProperty(required=True)
    class_implementation_summary = StringProperty(default="")
    class_objective = StringProperty(default="")
    class_objective_embedding = ArrayProperty(FloatProperty())
    class_implementation_summary_embedding = ArrayProperty(FloatProperty())
    # Class relationships
    package = RelationshipFrom('.confluence_package.ConfluencePackage', 'CONTAINS', model=ContainsRelationship, cardinality=One)
    methods = RelationshipTo('.confluence_method.ConfluenceMethod', 'CONTAINS', model=ContainsRelationship, cardinality=ZeroOrMore)
