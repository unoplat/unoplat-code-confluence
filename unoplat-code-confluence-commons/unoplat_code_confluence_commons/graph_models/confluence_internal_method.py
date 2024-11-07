from unoplat_code_confluence_commons.graph_models.base_models import BaseNode, ContainsRelationship, CallsRelationship, AnnotatedRelationship
from neomodel import RelationshipTo, StringProperty,One,ArrayProperty,FloatProperty,ZeroOrMore,IntegerProperty,JSONProperty,Relationship

class ConfluenceInternalMethod(BaseNode):
    """Represents a method in a class"""
        
    function_name = StringProperty(required=True)
    return_type = StringProperty()
    implementation_summary = StringProperty(default="")
    objective = StringProperty(default="")
    function_objective_embedding = ArrayProperty(FloatProperty())
    function_implementation_summary_embedding = ArrayProperty(FloatProperty())
    content = StringProperty()
    body_hash = IntegerProperty()
    local_variables = JSONProperty()
    description = StringProperty()
    # # Method relationships
    confluence_class = RelationshipTo('.confluence_class.ConfluenceClass', 'BELONGS_TO', model=ContainsRelationship, cardinality=One)
    annotations = Relationship('.confluence_annotation.ConfluenceAnnotation', 'HAS_ANNOTATION', model=AnnotatedRelationship, cardinality=ZeroOrMore)
    calls_methods = RelationshipTo('.confluence_internal_method.ConfluenceInternalMethod', 'CALLS', model=CallsRelationship, cardinality=ZeroOrMore)
    calls_external_methods = RelationshipTo('.confluence_external_method.ConfluenceExternalMethod', 'CALLS', model=CallsRelationship, cardinality=ZeroOrMore)