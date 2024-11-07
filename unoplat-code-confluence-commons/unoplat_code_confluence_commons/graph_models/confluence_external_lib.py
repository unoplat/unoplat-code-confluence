from neomodel import StructuredNode, StringProperty,RelationshipTo,ZeroOrMore

class ConfluenceExternalLibrary(StructuredNode):
    """Represents a external library in a method"""
    library_name = StringProperty(unique_index=True, required=True)
    library_version = StringProperty()
    library_doc_url = StringProperty()
    description = StringProperty()
    contains = RelationshipTo('.confluence_external_method.ConfluenceExternalMethod', 'CONTAINS', cardinality=ZeroOrMore)
