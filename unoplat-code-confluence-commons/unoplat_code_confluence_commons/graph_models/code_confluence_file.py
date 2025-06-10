# new imports (top of the file, after existing neomodel import list)
from neomodel import AsyncStructuredNode, StringProperty, AsyncRelationshipTo, AsyncOne

from unoplat_code_confluence_commons.graph_models.base_models import  ContainsRelationship
from neomodel import JSONProperty, ArrayProperty, FulltextIndex

# ⬇️  insert just above class `CodeConfluencePackage`
class CodeConfluenceFile(AsyncStructuredNode):
    """
    Graph node representing a single source file.

    Relationships
    ─────────────
    package  (PART_OF_PACKAGE)  -> CodeConfluencePackage
    """
    file_path = StringProperty(required=True, unique_index=True)
    content   = StringProperty(fulltext_index=FulltextIndex(analyzer="english"))
    checksum  = StringProperty()
    structural_signature = JSONProperty()
    global_variables = ArrayProperty(StringProperty(), default=[])
    class_variables = JSONProperty()
    imports = ArrayProperty(
        StringProperty(),
        default=[],
        fulltext_index=FulltextIndex(analyzer="english")
    )
    poi_labels = ArrayProperty(
        StringProperty(),
        fulltext_index=FulltextIndex(analyzer="english")
    )
    package = AsyncRelationshipTo(
        '.code_confluence_package.CodeConfluencePackage',
        'PART_OF_PACKAGE',
        model=ContainsRelationship,
        cardinality=AsyncOne,
    )