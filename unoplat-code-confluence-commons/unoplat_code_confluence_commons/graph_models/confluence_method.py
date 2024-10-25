from .base_models import BaseNode, ContainsRelationship
from neomodel import Relationship, StringProperty,One,ArrayProperty,VectorIndex,FloatProperty

class ConfluenceMethod(BaseNode):
    """Represents a method in a class"""
    function_name = StringProperty(required=True)
    function_implementation_summary = StringProperty(default="")
    function_objective = StringProperty(default="")
    function_objective_embedding = ArrayProperty(FloatProperty())
    function_summary_embedding = ArrayProperty(FloatProperty())
    # Method relationships
    confluence_class = Relationship('.confluence_class.ConfluenceClass', 'CONTAINS', model=ContainsRelationship, cardinality=One)
