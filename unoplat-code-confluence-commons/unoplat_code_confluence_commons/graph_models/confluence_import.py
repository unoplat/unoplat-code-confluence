from neomodel import StructuredNode, StringProperty, ArrayProperty, Relationship, ZeroOrMore

class ConfluenceImport(StructuredNode):
    source = StringProperty(required=True)
    
    usage_names = ArrayProperty(StringProperty())
    
    imported_by = Relationship('.confluence_class.ConfluenceClass', 'IMPORTS', cardinality=ZeroOrMore)