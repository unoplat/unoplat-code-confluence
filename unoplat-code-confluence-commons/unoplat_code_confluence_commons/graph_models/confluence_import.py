from neomodel import StructuredNode, StringProperty, ArrayProperty, RelationshipFrom, ZeroOrMore

class ConfluenceImport(StructuredNode):
    source = StringProperty(required=True)
    
    usage_names = ArrayProperty(StringProperty())
    
    imported_by = RelationshipFrom('.confluence_class.ConfluenceClass', 'IMPORTS', cardinality=ZeroOrMore)