from .base_models import BaseNode, ContainsRelationship
from neomodel import RelationshipFrom, RelationshipTo, StringProperty,ZeroOrMore,One,ArrayProperty,VectorIndex,FloatProperty

class ConfluencePackage(BaseNode):
    """Represents a package in the codebase"""
    package_objective = StringProperty(required=True)
    package_implementation_summary = StringProperty(required=True)
    
    package_objective_embedding = ArrayProperty(FloatProperty())
    package_implementation_summary_embedding = ArrayProperty(FloatProperty())
    confluence_codebase = RelationshipFrom('ConfluenceCodebase', 'CONTAINS', model=ContainsRelationship, cardinality=One)
    sub_packages = RelationshipTo('ConfluencePackage', 'CONTAINS', model=ContainsRelationship, cardinality=ZeroOrMore)
    classes = RelationshipTo('ConfluenceClass', 'CONTAINS', model=ContainsRelationship, cardinality=ZeroOrMore)
