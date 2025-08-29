"""SQLModel models for PostgreSQL framework metadata tables."""

from unoplat_code_confluence_commons.base_models.engine_models import (
    Concept,
    ConstructQueryConfig,
    LocatorStrategy,
    TargetLevel,
)
from unoplat_code_confluence_commons.base_models.sql_base import SQLBase

from typing import Any, Dict, List, Optional

from sqlalchemy import ForeignKeyConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship


# ──────────────────────────────────────────────
# 1️⃣  Parent table: language-library pair
# ──────────────────────────────────────────────
class Framework(SQLBase):
    """Language-library combo ("python-fastapi", etc.)."""
    __tablename__ = "framework"
    __table_args__ = {"extend_existing": True}

    language: Mapped[str] = mapped_column(primary_key=True, comment="Programming language")
    library: Mapped[str] = mapped_column(primary_key=True, comment="Library / framework")
    docs_url: Mapped[Optional[str]] = mapped_column(default=None, comment="Docs URL")
    description: Mapped[Optional[str]] = mapped_column(default=None, comment="Framework/library description")

    # Relationships
    features: Mapped[List["FrameworkFeature"]] = relationship(
        back_populates="framework",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ──────────────────────────────────────────────
# 2️⃣  Feature metadata  (no absolute_path here)
# ──────────────────────────────────────────────
class FrameworkFeature(SQLBase):
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
    language: Mapped[str] = mapped_column(primary_key=True)
    library: Mapped[str] = mapped_column(primary_key=True)
    feature_key: Mapped[str] = mapped_column(primary_key=True, comment="Feature identifier")

    # Core fields with explicit PostgreSQL enum types
    target_level: Mapped[TargetLevel] = mapped_column(
        nullable=False,
        comment="Granularity: function or class"
    )
    concept: Mapped[Concept] = mapped_column(
        nullable=False,
        comment="Semantic concept (AnnotationLike, CallExpression, Inheritance)"
    )
    locator_strategy: Mapped[LocatorStrategy] = mapped_column(
        nullable=False,
        comment="VariableBound or Direct"
    )
    construct_query: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
        comment="Language-specific query tweaks for adapter construction",
    )
    description: Mapped[Optional[str]] = mapped_column(default=None)
    startpoint: Mapped[bool] = mapped_column(
        default=False,
        comment="Indicates whether this feature represents a starting point or entry point in the application"
    )

    # Relationships
    framework: Mapped[Framework] = relationship(back_populates="features")
    absolute_paths: Mapped[List["FeatureAbsolutePath"]] = relationship(
        back_populates="feature",
        cascade="all, delete-orphan",
        passive_deletes=True,
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
class FeatureAbsolutePath(SQLBase):
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
    language: Mapped[str] = mapped_column(primary_key=True)
    library: Mapped[str] = mapped_column(primary_key=True)
    feature_key: Mapped[str] = mapped_column(primary_key=True)
    absolute_path: Mapped[str] = mapped_column(primary_key=True, comment="Import path")

    # Relationship back to metadata
    feature: Mapped[FrameworkFeature] = relationship(back_populates="absolute_paths")