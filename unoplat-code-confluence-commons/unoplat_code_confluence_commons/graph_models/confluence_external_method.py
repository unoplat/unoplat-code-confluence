

from neomodel import StructuredNode, StringProperty, RelationshipTo, One, ZeroOrMore
from unoplat_code_confluence_commons.graph_models.base_models import CallsRelationship
from unoplat_code_confluence_commons.graph_models.confluence_method_type import MethodTypeChoices

class ConfluenceExternalMethod(StructuredNode):
    """Represents a external method in a method"""
    function_name = StringProperty(unique_index=True, required=True)
    return_type = StringProperty()
    method_type = StringProperty(choices=MethodTypeChoices.choices,default=MethodTypeChoices.EXTERNAL)
    called_by = RelationshipTo('.confluence_internal_method.ConfluenceInternalMethod', 'CALLED_BY', model=CallsRelationship, cardinality=ZeroOrMore)
    library = RelationshipTo('.confluence_external_lib.ConfluenceExternalLibrary', 'BELONGS_TO', cardinality=One)