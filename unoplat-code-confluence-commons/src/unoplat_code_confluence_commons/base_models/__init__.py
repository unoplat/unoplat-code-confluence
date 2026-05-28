"""Common Pydantic and SQLModel base models for unoplat-code-confluence projects."""

# Data model position models
from unoplat_code_confluence_commons.base_models.data_model_position import (
    DataModelPosition,
)

# Engine Pydantic models
from unoplat_code_confluence_commons.base_models.engine_models import (
    AnnotationLikeInfo,
    CallExpressionInfo,
    Concept,
    ConstructQueryConfig,
    Detection,
    DetectionResult,
    FeatureSpec,
    FeatureUsagePayload,
    FrameworkFeaturePayload,
    InheritanceInfo,
    LocatorStrategy,
    TargetLevel,
    ValidationStatus,
)

# Framework SQLModel models
from unoplat_code_confluence_commons.base_models.framework_models import (
    FeatureAbsolutePath,
    Framework,
    FrameworkFeature,
)
# SQL Base class
from unoplat_code_confluence_commons.base_models.sql_base import (
    SQLBase,
)

from unoplat_code_confluence_commons.configuration_models import (
    CodebaseConfig,
    RepositorySettings,
)

# Credentials model
from unoplat_code_confluence_commons.credentials import (
    Credentials,
)

# Flags model
from unoplat_code_confluence_commons.flags import (
    Flag,
)
from unoplat_code_confluence_commons.programming_language_metadata import (
    PackageManagerProvenance,
    PackageManagerType,
    ProgrammingLanguage,
    ProgrammingLanguageMetadata,
    WorkspaceOrchestratorType,
)

# Repository and Programming Language models
from unoplat_code_confluence_commons.repo_models import (
    CodebaseConfig as CodebaseConfigSQLModel,
    CodebaseWorkflowRun,
    Repository,
    RepositoryWorkflowOperation,
    RepositoryWorkflowRun,
)

__all__ = [
    # Data model position models
    "DataModelPosition",
    # Engine Pydantic models
    "TargetLevel",
    "LocatorStrategy",
    "Concept",
    "ConstructQueryConfig",
    "FeatureSpec",
    "FrameworkFeaturePayload",
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
    "RepositoryWorkflowRun",
    "RepositoryWorkflowOperation",
    "CodebaseWorkflowRun",
    "ProgrammingLanguageMetadata",
    "ProgrammingLanguage",
    "PackageManagerType",
    "PackageManagerProvenance",
    "WorkspaceOrchestratorType",
    # Credentials model
    "Credentials",
    # Flags model
    "Flag",
    # SQL Base class
    "SQLBase",
]
