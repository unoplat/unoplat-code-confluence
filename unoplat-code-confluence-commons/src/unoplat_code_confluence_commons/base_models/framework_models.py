"""SQLModel models for PostgreSQL framework metadata tables."""

from unoplat_code_confluence_commons.base_models.engine_models import (
    Concept,
    ConstructQueryConfig,
    LocatorStrategy,
    TargetLevel,
)
from unoplat_code_confluence_commons.base_models.sql_base import SQLBase

from typing import List, Optional

from sqlalchemy import (
    ForeignKeyConstraint,
    Index,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.elements import ColumnElement


def _compose_feature_key(capability_key: str, operation_key: str) -> str:
    """Build the dotted convenience key from structured identity parts."""
    return f"{capability_key}.{operation_key}"


# ──────────────────────────────────────────────
# 1️⃣  Parent table: language-library pair
# ──────────────────────────────────────────────
class Framework(SQLBase):
    """Language-library combo ("python-fastapi", etc.)."""

    __tablename__ = "framework"
    __table_args__ = {"extend_existing": True}

    language: Mapped[str] = mapped_column(
        primary_key=True, comment="Programming language"
    )
    library: Mapped[str] = mapped_column(
        primary_key=True, comment="Library / framework"
    )
    docs_url: Mapped[Optional[str]] = mapped_column(default=None, comment="Docs URL")
    description: Mapped[Optional[str]] = mapped_column(
        default=None, comment="Framework/library description"
    )

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
    """Per-feature metadata keyed by capability + operation."""

    __tablename__ = "framework_feature"
    __table_args__ = (
        ForeignKeyConstraint(  # FK → Framework
            ["language", "library"],
            ["framework.language", "framework.library"],
            ondelete="CASCADE",
        ),
        Index(
            "framework_feature_definition_gin_idx",
            "feature_definition",
            postgresql_using="gin",
            postgresql_ops={"feature_definition": "jsonb_path_ops"},
        ),
        Index(
            "framework_feature_startpoint_bool_idx",
            text("coalesce((feature_definition['startpoint'])::boolean, false)"),
        ),
        {"extend_existing": True},
    )

    # Composite PK = language + library + capability_key + operation_key
    language: Mapped[str] = mapped_column(primary_key=True)
    library: Mapped[str] = mapped_column(primary_key=True)
    capability_key: Mapped[str] = mapped_column(
        primary_key=True,
        comment="Capability family this feature belongs to",
    )
    operation_key: Mapped[str] = mapped_column(
        primary_key=True,
        comment="Operation identifier within the capability",
    )

    feature_definition: Mapped[dict[str, object]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
        comment="Source-of-truth JSONB payload for feature schema fields",
    )

    # Relationships
    framework: Mapped[Framework] = relationship(back_populates="features")
    absolute_paths: Mapped[List["FeatureAbsolutePath"]] = relationship(
        back_populates="feature",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @property
    def feature_key(self) -> str:
        """Return the dotted convenience key derived from structured identity."""
        return _compose_feature_key(self.capability_key, self.operation_key)

    @property
    def description(self) -> Optional[str]:
        """Return description from feature_definition."""
        value = self.feature_definition.get("description")
        if value is None:
            return None
        if isinstance(value, str):
            return value
        raise TypeError("feature_definition.description must be a string")

    @property
    def target_level(self) -> TargetLevel:
        """Return target level from feature_definition."""
        value = self.feature_definition["target_level"]
        if isinstance(value, TargetLevel):
            return value
        if isinstance(value, str):
            return TargetLevel(value)
        raise TypeError("feature_definition.target_level must be a string enum value")

    @property
    def concept(self) -> Concept:
        """Return concept from feature_definition."""
        value = self.feature_definition["concept"]
        if isinstance(value, Concept):
            return value
        if isinstance(value, str):
            return Concept(value)
        raise TypeError("feature_definition.concept must be a string enum value")

    @property
    def locator_strategy(self) -> LocatorStrategy:
        """Return locator strategy from feature_definition."""
        value = self.feature_definition["locator_strategy"]
        if isinstance(value, LocatorStrategy):
            return value
        if isinstance(value, str):
            return LocatorStrategy(value)
        raise TypeError(
            "feature_definition.locator_strategy must be a string enum value"
        )

    @property
    def construct_query(self) -> Optional[dict[str, object]]:
        """Return construct_query from feature_definition."""
        value = self.feature_definition.get("construct_query")
        if value is None:
            return None
        if isinstance(value, dict):
            return value
        raise TypeError("feature_definition.construct_query must be an object")

    @property
    def startpoint(self) -> bool:
        """Return startpoint from feature_definition."""
        value = self.feature_definition["startpoint"]
        if isinstance(value, bool):
            return value
        raise TypeError("feature_definition.startpoint must be a boolean")

    @property
    def base_confidence(self) -> float | None:
        """Return base confidence from feature_definition when present."""
        value = self.feature_definition.get("base_confidence")
        if value is None:
            return None
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        raise TypeError("feature_definition.base_confidence must be a number")

    @classmethod
    def concept_sql_expression(cls) -> ColumnElement[str]:
        """SQL expression for concept reads/grouping."""
        return cls.feature_definition["concept"].astext

    @classmethod
    def startpoint_sql_expression(cls) -> ColumnElement[bool]:
        """SQL expression for startpoint reads/filtering."""
        return func.coalesce(cls.feature_definition["startpoint"].as_boolean(), False)

    @property
    def construct_query_typed(self) -> Optional[ConstructQueryConfig]:
        """Get construct_query as typed configuration."""
        construct_query = self.construct_query
        if not construct_query:
            return None
        try:
            return ConstructQueryConfig.model_validate(construct_query)
        except Exception:
            return None

    @construct_query_typed.setter
    def construct_query_typed(self, value: Optional[ConstructQueryConfig]) -> None:
        """Set construct_query from typed configuration."""
        updated_feature_definition = dict(self.feature_definition)
        if value is None:
            updated_feature_definition.pop("construct_query", None)
        else:
            updated_feature_definition["construct_query"] = value.model_dump(
                exclude_none=True
            )
        self.feature_definition = updated_feature_definition


# ──────────────────────────────────────────────
# 3️⃣  Junction table: one row per absolute_path
# ──────────────────────────────────────────────
class FeatureAbsolutePath(SQLBase):
    """Maps each absolute import path to its feature."""

    __tablename__ = "feature_absolute_path"
    __table_args__ = (
        ForeignKeyConstraint(  # FK → FrameworkFeature
            ["language", "library", "capability_key", "operation_key"],
            [
                "framework_feature.language",
                "framework_feature.library",
                "framework_feature.capability_key",
                "framework_feature.operation_key",
            ],
            ondelete="CASCADE",
        ),
        # Fast lookup by path + covering columns for an index-only probe
        Index(
            "path_lookup_idx",
            "absolute_path",
            postgresql_include=(
                "language",
                "library",
                "capability_key",
                "operation_key",
            ),
        ),
        {"extend_existing": True},
    )

    # Composite PK = language + library + capability_key + operation_key + absolute_path
    language: Mapped[str] = mapped_column(primary_key=True)
    library: Mapped[str] = mapped_column(primary_key=True)
    capability_key: Mapped[str] = mapped_column(primary_key=True)
    operation_key: Mapped[str] = mapped_column(primary_key=True)
    absolute_path: Mapped[str] = mapped_column(primary_key=True, comment="Import path")

    @property
    def feature_key(self) -> str:
        """Return the dotted convenience key derived from structured identity."""
        return _compose_feature_key(self.capability_key, self.operation_key)

    # Relationship back to metadata
    feature: Mapped[FrameworkFeature] = relationship(back_populates="absolute_paths")
