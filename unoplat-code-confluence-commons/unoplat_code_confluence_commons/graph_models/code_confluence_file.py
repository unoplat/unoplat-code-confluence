# new imports (top of the file, after existing neomodel import list)
from neomodel import StringProperty, AsyncRelationshipTo, AsyncRelationship, AsyncOne, AsyncZeroOrMore

from unoplat_code_confluence_commons.graph_models.base_models import BaseNode, ContainsRelationship

# ⬇️  insert just above class `CodeConfluencePackage`
class CodeConfluenceFile(BaseNode):
    """
    Graph node representing a single source file.

    Relationships
    ─────────────
    package  (PART_OF_PACKAGE)  -> CodeConfluencePackage
    nodes    (CONTAINS_NODE)    -> CodeConfluenceClass / CodeConfluenceInternalFunction
    """
    file_path = StringProperty(required=True, unique_index=True)
    content   = StringProperty()
    checksum  = StringProperty()

    package = AsyncRelationshipTo(
        '.code_confluence_package.CodeConfluencePackage',
        'PART_OF_PACKAGE',
        model=ContainsRelationship,
        cardinality=AsyncOne,
    )

    nodes = AsyncRelationship(
        '.code_confluence_class.CodeConfluenceClass',
        'CONTAINS_NODE',
        model=ContainsRelationship,
        cardinality=AsyncZeroOrMore,
    )