from unoplat_code_confluence_commons.graph_models.base_models import (
    BaseNode,
    ContainsRelationship,
)

from neomodel import AsyncOneOrMore, AsyncRelationshipTo, JSONProperty, StringProperty


class CodeConfluenceGitRepository(BaseNode):
    """
    Represents a Git repository in the system.

    Inherits from:
        BaseNode (which itself extends StructuredNode).
        - Includes common fields like 'qualified_name' (unique_index).

    Fields:
        repository_url (str): The URL used to clone or reference the repository.
        repository_name (str): A human-friendly or organizational name for the repository.
        repository_metadata (dict): Arbitrary JSON metadata describing the repository
                                    (e.g., stats, commits, custom config).
        readme (str): Optional text content of the repository’s main README.
    Relationships:
        codebases (RelationshipTo): Points to codebase nodes if needed.
                                    Uses ContainsRelationship to hold any
                                    extra relationship metadata.
    """
    repository_url = StringProperty(required=True,unique_index=True)
    repository_name = StringProperty(required=True)  # Not unique - multiple orgs can have same repo name
    repository_metadata = JSONProperty()
    readme = StringProperty()

    # Example relationship to a Codebase node class (not shown in this snippet)
    # The ContainsRelationship lets you store relationship metadata if desired
    codebases = AsyncRelationshipTo(
        '.code_confluence_codebase.CodeConfluenceCodebase',  # adjust import path to match your structure
        'CONTAINS_CODEBASE',
        model=ContainsRelationship,
        cardinality=AsyncOneOrMore
    )
