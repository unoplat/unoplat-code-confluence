"""Common Pydantic and SQLModel base models for unoplat-code-confluence projects."""

# Structural signature models
from .structural_signature import (
    VariableInfo,
    FunctionInfo, 
    ClassInfo,
    StructuralSignature,
)

# Engine Pydantic models
from .engine_models import (
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
from .framework_models import (
    Framework,
    FrameworkFeature,
    FeatureAbsolutePath,
)

# Repository and Programming Language models
from ..repo_models import (
    Repository,
    CodebaseConfig as CodebaseConfigSQLModel,
    RepositoryWorkflowRun,
    CodebaseWorkflowRun,
)
from ..programming_language_metadata import (
    ProgrammingLanguageMetadata,
    ProgrammingLanguage,
    PackageManagerType,
)
from ..configuration_models import (
    CodebaseConfig,
    RepositorySettings,
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
]