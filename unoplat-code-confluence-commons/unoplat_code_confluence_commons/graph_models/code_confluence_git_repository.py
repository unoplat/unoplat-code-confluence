from neomodel import (
    StringProperty,
    JSONProperty,
    RelationshipTo,
    OneOrMore,
    StructuredNode
)
from .base_models import BaseNode, ContainsRelationship

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
        github_organization (str): A specific GitHub (or other host) organization name.
        readme (str): Optional text content of the repository’s main README.
    Relationships:
        codebases (RelationshipTo): Points to codebase nodes if needed.
                                    Uses ContainsRelationship to hold any
                                    extra relationship metadata.
    """
    repository_url = StringProperty(required=True,unique_index=True)
    repository_name = StringProperty(required=True)
    repository_metadata = JSONProperty()
    readme = StringProperty()

    # Example relationship to a Codebase node class (not shown in this snippet)
    # The ContainsRelationship lets you store relationship metadata if desired
    codebases = RelationshipTo(
        '.code_confluence_codebase.CodeConfluenceCodebase',  # adjust import path to match your structure
        'CONTAINS_CODEBASE',
        model=ContainsRelationship,
        cardinality=OneOrMore
    )