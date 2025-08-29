"""Common Pydantic and SQLModel base models for unoplat-code-confluence projects."""

# Structural signature models
# Engine Pydantic models
from unoplat_code_confluence_commons.base_models.engine_models import (
    AnnotationLikeInfo,
    CallExpressionInfo,
    Concept,
    ConstructQueryConfig,
    Detection,
    DetectionResult,
    FeatureSpec,
    InheritanceInfo,
    LocatorStrategy,
    TargetLevel,
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
from unoplat_code_confluence_commons.base_models.structural_signature import (
    ClassInfo,
    FunctionInfo,
    StructuralSignature,
    VariableInfo,
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
    PackageManagerType,
    ProgrammingLanguage,
    ProgrammingLanguageMetadata,
)

# Repository and Programming Language models
from unoplat_code_confluence_commons.repo_models import (
    CodebaseConfig as CodebaseConfigSQLModel,
    CodebaseWorkflowRun,
    Repository,
    RepositoryWorkflowRun,
)

__all__ = [
    # Structural signature models
    "VariableInfo",
    "FunctionInfo",
    "ClassInfo", 
    "StructuralSignature",
    # Engine Pydantic models
    "TargetLevel",
    "LocatorStrategy",
    "Concept", 
    "ConstructQueryConfig",
    "FeatureSpec",
    "Detection",
    "DetectionResult",
    "AnnotationLikeInfo",
    "CallExpressionInfo", 
    "InheritanceInfo",
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
    "CodebaseWorkflowRun",
    "ProgrammingLanguageMetadata",
    "ProgrammingLanguage", 
    "PackageManagerType",
    # Credentials model
    "Credentials",
    # Flags model
    "Flag",
    # SQL Base class
    "SQLBase",
]