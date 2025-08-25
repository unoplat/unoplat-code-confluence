"""Common Pydantic and SQLModel base models for unoplat-code-confluence projects."""

# Structural signature models
from unoplat_code_confluence_commons.base_models.structural_signature import (
    VariableInfo,
    FunctionInfo, 
    ClassInfo,
    StructuralSignature,
)

# Engine Pydantic models
from unoplat_code_confluence_commons.base_models.engine_models import (
    TargetLevel,
    LocatorStrategy, 
    Concept,
    ConstructQueryConfig,
    FeatureSpec,
    Detection,
    DetectionResult,
    AnnotationLikeInfo,
    CallExpressionInfo,
    InheritanceInfo,
)

# Framework SQLModel models
from unoplat_code_confluence_commons.base_models.framework_models import (
    Framework,
    FrameworkFeature,
    FeatureAbsolutePath,
)

# Repository and Programming Language models
from unoplat_code_confluence_commons.repo_models import (
    Repository,
    CodebaseConfig as CodebaseConfigSQLModel,
    RepositoryWorkflowRun,
    CodebaseWorkflowRun,
)
from unoplat_code_confluence_commons.programming_language_metadata import (
    ProgrammingLanguageMetadata,
    ProgrammingLanguage,
    PackageManagerType,
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
]