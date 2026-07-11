"""
Unoplat Code Confluence Commons package.
Contains models and utilities for code analysis and representation.
"""

from unoplat_code_confluence_commons.base_models import (
    AnnotationLikeInfo,
    CallExpressionInfo,
    CallExpressionMatchPolicy,
    CodebaseConfig,
    CodebaseConfigSQLModel,
    Concept,
    ConstructQueryConfig,
    # Credentials model
    Credentials,
    Detection,
    DetectionResult,
    FeatureAbsolutePath,
    FeatureSpec,
    FeatureUsagePayload,
    # Flags model
    Flag,
    # Framework SQLModel models
    Framework,
    FrameworkFeature,
    InheritanceInfo,
    LocatorStrategy,
    PackageManagerProvenance,
    PackageManagerType,
    ProgrammingLanguage,
    ProgrammingLanguageMetadata,
    # Repository and Programming Language models
    Repository,
    RepositorySettings,
    # Engine Pydantic models
    TargetLevel,
    ValidationStatus,
    WorkspaceOrchestratorType,
)
from unoplat_code_confluence_commons.credential_enums import (
    CredentialNamespace,
    ProviderKey,
    SecretKind,
)
from unoplat_code_confluence_commons.pr_metadata_model import (
    PrMetadata,
)
from unoplat_code_confluence_commons.relational_models import (
    UnoplatCodeConfluenceCodebase,
    UnoplatCodeConfluenceCodebaseFramework,
    UnoplatCodeConfluenceFile,
    UnoplatCodeConfluenceFileFrameworkFeature,
    UnoplatCodeConfluenceGitRepository,
    UnoplatCodeConfluencePackageManagerMetadata,
)
from unoplat_code_confluence_commons.repo_models import (
    RepositoryAgentMdSnapshot,
)
from unoplat_code_confluence_commons.security import (
    decrypt_token,
    encrypt_token,
)
from unoplat_code_confluence_commons.workflow_envelopes import (
    CodebaseWorkflowDbActivityEnvelope,
    ParentWorkflowDbActivityEnvelope,
)
from unoplat_code_confluence_commons.workflow_models import (
    ErrorReport,
    JobStatus,
)

__all__ = [
    # Engine Pydantic models
    "TargetLevel",
    "LocatorStrategy",
    "Concept",
    "CallExpressionMatchPolicy",
    "ConstructQueryConfig",
    "FeatureSpec",
    "FeatureUsagePayload",
    "Detection",
    "DetectionResult",
    "AnnotationLikeInfo",
    "CallExpressionInfo",
    "InheritanceInfo",
    "ValidationStatus",
    # Framework SQLModel models
    "Framework",
    "FrameworkFeature",
    "FeatureAbsolutePath",
    # Repository and Programming Language models
    "Repository",
    "CodebaseConfigSQLModel",
    "CodebaseConfig",
    "RepositorySettings",
    "ProgrammingLanguageMetadata",
    "ProgrammingLanguage",
    "PackageManagerType",
    "PackageManagerProvenance",
    "WorkspaceOrchestratorType",
    "RepositoryAgentMdSnapshot",
    "PrMetadata",
    # Credentials and related enums
    "Credentials",
    "CredentialNamespace",
    "ProviderKey",
    "SecretKind",
    # Flags model
    "Flag",
    # Relational models (PostgreSQL)
    "UnoplatCodeConfluenceGitRepository",
    "UnoplatCodeConfluenceCodebase",
    "UnoplatCodeConfluencePackageManagerMetadata",
    "UnoplatCodeConfluenceFile",
    "UnoplatCodeConfluenceCodebaseFramework",
    "UnoplatCodeConfluenceFileFrameworkFeature",
    # Security utilities
    "encrypt_token",
    "decrypt_token",
    # Workflow models
    "JobStatus",
    "ErrorReport",
    # Workflow envelope models
    "ParentWorkflowDbActivityEnvelope",
    "CodebaseWorkflowDbActivityEnvelope",
]
