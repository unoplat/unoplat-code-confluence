from neomodel import (
    StringProperty,
    ArrayProperty,
    JSONProperty,
    AsyncRelationshipTo,
    AsyncRelationshipFrom,
    AsyncRelationship,
    AsyncZeroOrMore,
    AsyncOne,
    AsyncOneOrMore
)

from .base_models import AnnotatedRelationship, BaseNode, ContainsRelationship

class CodeConfluenceClass(BaseNode):
    """
    Represents a class-like node, combining fields from:
      - ChapiNode
      - UnoplatChapiForgeNode
    """
    # From ChapiNode
    name = StringProperty()       # NodeName
    type_ = StringProperty()           # Type (renamed to avoid Python 'type' shadowing)
    file_path = StringProperty()       # FilePath
    module = StringProperty()          # Module
    multiple_extend = ArrayProperty(StringProperty(), default=[])  # MultipleExtend
    fields = JSONProperty()                # Fields (list of ClassGlobalFieldModel)
    extend = StringProperty()          # Extend
    position = JSONProperty()          # Position
    content = StringProperty()         # Content

    # From UnoplatChapiForgeNode
    comments_description = StringProperty()  # CommentsDescription
    segregated_imports = JSONProperty()      # SegregatedImports
    dependent_internal_classes = ArrayProperty(StringProperty(), default=[])  # DependentInternalClasses
    global_variables = JSONProperty(default=[])            # GlobalVariables

    # RELATIONSHIPS
    # "Functions" from either ChapiNode or UnoplatChapiForgeNode become a relationship
    functions = AsyncRelationshipTo(".code_confluence_internal_function.CodeConfluenceInternalFunction", "HAS_FUNCTION",model=ContainsRelationship,cardinality=AsyncZeroOrMore)
    
    # Classes can also have annotations
    annotations = AsyncRelationship(".code_confluence_annotation.CodeConfluenceAnnotation", "HAS_ANNOTATION",model=AnnotatedRelationship,cardinality=AsyncZeroOrMore)
    
    # relation to package
    package = AsyncRelationshipTo(".code_confluence_package.CodeConfluencePackage", "PART_OF_PACKAGE",model=ContainsRelationship,cardinality=AsyncOne)
    
    file = AsyncRelationshipTo(
        '.code_confluence_file.CodeConfluenceFile',
        'PART_OF_FILE',
        model=ContainsRelationship,
        cardinality=AsyncOne,
    )