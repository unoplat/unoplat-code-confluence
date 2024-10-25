from .base_models import BaseNode, ContainsRelationship
from neomodel import RelationshipFrom, RelationshipTo, StringProperty,ZeroOrMore,One,ArrayProperty,VectorIndex,FloatProperty

class ConfluenceClass(BaseNode):
    """Represents a class in a package"""
    class_name = StringProperty(required=True)
    implementation_summary = StringProperty(default="")
    objective = StringProperty(default="")
    class_objective_embedding = ArrayProperty(FloatProperty())
    class_implementation_summary_embedding = ArrayProperty(FloatProperty())
    # Class relationships
    package = RelationshipTo('.confluence_package.ConfluencePackage', 'BELONGS_TO', model=ContainsRelationship, cardinality=One)
    methods = RelationshipTo('.confluence_method.ConfluenceMethod', 'CONTAINS', model=ContainsRelationship, cardinality=ZeroOrMore)
