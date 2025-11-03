"""
Pydantic models for the custom grammar detection engine.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

# ──────────────────────────────────────────────
# 🔄 Enum definitions - must be defined before use
# ──────────────────────────────────────────────


class TargetLevel(str, Enum):
    """Granularity of the code element owning the feature."""

    FUNCTION = "function"
    CLASS = "class"


class LocatorStrategy(str, Enum):
    """Strategy for locating the feature in code."""

    VARIABLE_BOUND = "VariableBound"
    DIRECT = "Direct"


class Concept(str, Enum):
    """Language-agnostic semantic concept used in refactored engine (see design doc)."""

    ANNOTATION_LIKE = "AnnotationLike"
    CALL_EXPRESSION = "CallExpression"
    INHERITANCE = "Inheritance"


# ──────────────────────────────────────────────
# 🔄 Typed models for construct_query structure
# ──────────────────────────────────────────────


class ConstructQueryConfig(BaseModel):
    """Typed construct query configuration matching JSON schema structure."""

    method_regex: Optional[str] = Field(
        None, description="Regex for method names (AnnotationLike)"
    )
    annotation_name_regex: Optional[str] = Field(
        None, description="Regex for annotation names"
    )
    attribute_regex: Optional[str] = Field(
        None, description="Regex for attribute patterns"
    )
    callee_regex: Optional[str] = Field(
        None, description="Regex for call expression callees"
    )
    superclass_regex: Optional[str] = Field(
        None, description="Regex for superclass names (Inheritance)"
    )

    model_config = ConfigDict(extra="forbid")


class FeatureSpec(BaseModel):
    """Strongly-typed feature specification from schema."""

    feature_key: str = Field(..., description="Unique feature identifier")
    library: str = Field(
        ..., description="Library/framework name this feature belongs to"
    )
    absolute_paths: List[str] = Field(
        ..., min_length=1, description="Fully qualified import paths"
    )
    target_level: TargetLevel = Field(..., description="function or class")
    concept: Concept = Field(
        ...,
        description="Semantic concept (AnnotationLike, CallExpression, Inheritance, etc.)",
    )
    locator_strategy: LocatorStrategy = Field(
        ..., description="VariableBound or Direct"
    )
    construct_query: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Language-specific tweaks for ConceptQuery construction (new schema field)",
    )

    @property
    def construct_query_typed(self) -> Optional[ConstructQueryConfig]:
        """Get construct_query as typed configuration."""
        if not self.construct_query:
            return None
        try:
            return ConstructQueryConfig.model_validate(self.construct_query)
        except Exception:
            return None

    @construct_query_typed.setter
    def construct_query_typed(self, value: Optional[ConstructQueryConfig]) -> None:
        """Set construct_query from typed configuration."""
        if value is None:
            self.construct_query = None
        else:
            self.construct_query = value.model_dump(exclude_none=True)

    description: Optional[str] = Field(None, description="Human-readable description")
    startpoint: bool = Field(
        default=False,
        description="Indicates whether this feature represents a starting point or entry point in the application",
    )


class Detection(BaseModel):
    """Result of feature detection in source code."""

    feature_key: str = Field(..., description="Feature that was detected")
    library: str = Field(
        ..., description="Library/framework name this feature belongs to"
    )
    match_text: str = Field(..., description="The actual text that matched")
    start_line: int = Field(..., description="Starting line number (1-indexed)")
    end_line: int = Field(..., description="Ending line number (1-indexed)")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class DetectionResult(BaseModel):
    """Complete detection result returned by an engine run."""

    success: bool = Field(..., description="Whether detection completed successfully")
    detections: Dict[str, List[Detection]] = Field(
        default_factory=dict,
        description="Feature key to list of detections",
    )
    errors: List[str] = Field(
        default_factory=list,
        description="Critical errors that prevented detection",
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Non-critical issues encountered during detection",
    )
    unsupported_features: List[str] = Field(
        default_factory=list,
        description="Features that couldn't be processed by the engine",
    )


# ──────────────────────────────────────────────
# 🔄 Concept Info Models for Simplified Detector
# ──────────────────────────────────────────────


class AnnotationLikeInfo(Detection):
    """Information about annotation-like detections (decorators, method calls)."""

    variable_names: List[str] = Field(
        default_factory=list, description="Variable names bound to the annotation"
    )
    match_text: str = Field(..., description="The matched text content")
    bound_object: str = Field(
        ..., description="Object the decorator is bound to (e.g., 'app', 'self.app')"
    )
    annotation_name: str = Field(
        ..., description="Decorator method name (e.g., 'get', 'post')"
    )


class CallExpressionInfo(Detection):
    """Information about call expression detections."""

    match_text: str = Field(..., description="The matched call expression text")
    callee: str = Field(..., description="Function name being called")
    args_text: str = Field(..., description="Arguments text")


class InheritanceInfo(Detection):
    """Information about inheritance detections."""

    match_text: str = Field(..., description="The matched inheritance text")
    subclass: str = Field(..., description="Child class name")
    superclass: str = Field(..., description="Parent class name")