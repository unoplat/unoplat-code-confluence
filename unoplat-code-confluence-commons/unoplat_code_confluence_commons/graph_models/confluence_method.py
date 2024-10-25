from .base_models import BaseNode, ContainsRelationship
from neomodel import RelationshipTo, StringProperty,One,ArrayProperty,FloatProperty

class ConfluenceMethod(BaseNode):
    """Represents a method in a class"""
    function_name = StringProperty(required=True)
    function_implementation_summary = StringProperty(default="")
    function_objective = StringProperty(default="")
    function_objective_embedding = ArrayProperty(FloatProperty())
    function_implementation_summary_embedding = ArrayProperty(FloatProperty())
    # Method relationships
    confluence_class = RelationshipTo('.confluence_class.ConfluenceClass', 'BELONGS_TO', model=ContainsRelationship, cardinality=One)
