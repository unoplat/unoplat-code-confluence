from .base_models import BaseNode, ContainsRelationship
from neomodel import RelationshipFrom, RelationshipTo, StringProperty,ZeroOrMore,One

class Package(BaseNode):
    """Represents a package in the codebase"""
    package_objective = StringProperty(required=True)
    package_summary = StringProperty(required=True)
    # Package relationships
    codebase = RelationshipFrom('Codebase', 'CONTAINS', model=ContainsRelationship, cardinality=One)
    sub_packages = RelationshipTo('Package', 'CONTAINS', model=ContainsRelationship, cardinality=ZeroOrMore)
    parent_package = RelationshipFrom('Package', 'CONTAINS', model=ContainsRelationship, cardinality=ZeroOrMore)
    classes = RelationshipTo('Class', 'CONTAINS', model=ContainsRelationship, cardinality=ZeroOrMore)
