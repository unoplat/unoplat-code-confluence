from .base_models import BaseNode, ContainsRelationship, CallsRelationship
from neomodel import RelationshipTo, StringProperty,One,ArrayProperty,FloatProperty,ZeroOrMore,IntegerProperty,JSONProperty

class ConfluenceMethod(BaseNode):
    """Represents a method in a class"""
        
    function_name = StringProperty(required=True)
    return_type = StringProperty()
    implementation_summary = StringProperty(default="")
    objective = StringProperty(default="")
    function_objective_embedding = ArrayProperty(FloatProperty())
    function_implementation_summary_embedding = ArrayProperty(FloatProperty())
    content = StringProperty()
    body_hash = IntegerProperty()
    position = JSONProperty()
    local_variables = JSONProperty()
    
    # Method relationships
    confluence_class = RelationshipTo('.confluence_class.ConfluenceClass', 'BELONGS_TO', model=ContainsRelationship, cardinality=One)
    annotations = RelationshipTo('.confluence_annotation.ConfluenceAnnotation', 'HAS_ANNOTATION', cardinality=ZeroOrMore)
    calls_methods = RelationshipTo('.confluence_method.ConfluenceMethod', 'CALLS', model=CallsRelationship, cardinality=ZeroOrMore)