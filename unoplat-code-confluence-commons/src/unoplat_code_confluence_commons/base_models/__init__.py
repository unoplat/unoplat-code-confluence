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
]