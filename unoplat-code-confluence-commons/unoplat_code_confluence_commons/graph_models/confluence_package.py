from .base_models import BaseNode, ContainsRelationship
from neomodel import  StringProperty,ZeroOrMore,One,ArrayProperty,VectorIndex,FloatProperty,Relationship

class ConfluencePackage(BaseNode):
    """Represents a package in the codebase"""
    package_objective = StringProperty(required=True)
    package_implementation_summary = StringProperty(required=True)
    package_objective_embedding = ArrayProperty(FloatProperty())
    package_implementation_summary_embedding = ArrayProperty(FloatProperty())
    confluence_codebase = Relationship('.confluence_codebase.ConfluenceCodebase', 'CONTAINS', model=ContainsRelationship, cardinality=One)
    sub_packages = Relationship('.confluence_package.ConfluencePackage', 'CONTAINS', model=ContainsRelationship, cardinality=ZeroOrMore)
    classes = Relationship('.confluence_class.ConfluenceClass', 'CONTAINS', model=ContainsRelationship, cardinality=ZeroOrMore)
