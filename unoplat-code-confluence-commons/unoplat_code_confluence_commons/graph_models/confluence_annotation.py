from neomodel import StructuredNode, StringProperty, RelationshipFrom, ZeroOrMore, JSONProperty

class ConfluenceAnnotation(StructuredNode):
    name = StringProperty(required=True)
    key_values = JSONProperty()
    position = JSONProperty()
    # Relationships
    annotated_classes = RelationshipFrom('.confluence_class.ConfluenceClass', 'HAS_ANNOTATION', cardinality=ZeroOrMore)
    annotated_methods = RelationshipFrom('.confluence_method.ConfluenceMethod', 'HAS_ANNOTATION', cardinality=ZeroOrMore)