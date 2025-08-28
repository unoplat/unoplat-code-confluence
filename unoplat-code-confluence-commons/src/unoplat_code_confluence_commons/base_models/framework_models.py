"""SQLModel models for PostgreSQL framework metadata tables."""

from typing import Any, Dict, List, Optional

from sqlalchemy import Column, Enum as SQLAlchemyEnum, ForeignKeyConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from .engine_models import Concept, ConstructQueryConfig, LocatorStrategy, TargetLevel


# ──────────────────────────────────────────────
# 1️⃣  Parent table: language-library pair
# ──────────────────────────────────────────────
class Framework(SQLModel, table=True):
    """Language-library combo ("python-fastapi", etc.)."""
    __tablename__ = "framework"
    __table_args__ = {"extend_existing": True}

    language: str = Field(primary_key=True, description="Programming language")
    library: str = Field(primary_key=True, description="Library / framework")
    docs_url: Optional[str] = Field(default=None, description="Docs URL")
    description: Optional[str] = Field(default=None, description="Framework/library description")

    # Relationships
    features: List["FrameworkFeature"] = Relationship(
        back_populates="framework",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )


# ──────────────────────────────────────────────
# 2️⃣  Feature metadata  (no absolute_path here)
# ──────────────────────────────────────────────
class FrameworkFeature(SQLModel, table=True):
    """Per-feature metadata (one row per feature_key)."""
    __tablename__ = "framework_feature"
    __table_args__ = (
        ForeignKeyConstraint(                             # FK → Framework
            ["language", "library"],
            ["framework.language", "framework.library"],
            ondelete="CASCADE",
        ),
        {"extend_existing": True}
    )

    # Composite PK = language + library + feature_key
    language: str = Field(primary_key=True)
    library: str = Field(primary_key=True)
    feature_key: str = Field(primary_key=True, description="Feature identifier")

    # Core fields with explicit PostgreSQL enum types
    target_level: TargetLevel = Field(
        sa_column=Column(
            SQLAlchemyEnum(TargetLevel, name="targetlevel", native_enum=True),
            nullable=False
        ),
        description="Granularity: function or class"
    )
    concept: Concept = Field(
        sa_column=Column(
            SQLAlchemyEnum(Concept, name="concept", native_enum=True),
            nullable=False
        ),
        description="Semantic concept (AnnotationLike, CallExpression, Inheritance)"
    )
    locator_strategy: LocatorStrategy = Field(
        sa_column=Column(
            SQLAlchemyEnum(LocatorStrategy, name="locatorstrategy", native_enum=True),
            nullable=False
        ),
        description="VariableBound or Direct"
    )
    construct_query: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
        description="Language-specific query tweaks for adapter construction",
    )
    description: Optional[str] = Field(default=None)
    startpoint: bool = Field(
        default=False,
        description="Indicates whether this feature represents a starting point or entry point in the application"
    )

    # Relationships
    framework: Framework = Relationship(back_populates="features")
    absolute_paths: List["FeatureAbsolutePath"] = Relationship(
        back_populates="feature",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
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


# ──────────────────────────────────────────────
# 3️⃣  Junction table: one row per absolute_path
# ──────────────────────────────────────────────
class FeatureAbsolutePath(SQLModel, table=True):
    """Maps each absolute import path to its feature."""
    __tablename__ = "feature_absolute_path"
    __table_args__ = (
        ForeignKeyConstraint(                             # FK → FrameworkFeature
            ["language", "library", "feature_key"],
            ["framework_feature.language",
             "framework_feature.library",
             "framework_feature.feature_key"],
            ondelete="CASCADE",
        ),
        # Fast lookup by path + covering columns for an index-only probe
        Index(
            "path_lookup_idx",
            "absolute_path",
            postgresql_include=("language", "library", "feature_key"),
        ),
        {"extend_existing": True}
    )

    # Composite PK = language + library + feature_key + absolute_path
    language: str = Field(primary_key=True)
    library: str = Field(primary_key=True)
    feature_key: str = Field(primary_key=True)
    absolute_path: str = Field(primary_key=True, description="Import path")

    # Relationship back to metadata
    feature: FrameworkFeature = Relationship(back_populates="absolute_paths")