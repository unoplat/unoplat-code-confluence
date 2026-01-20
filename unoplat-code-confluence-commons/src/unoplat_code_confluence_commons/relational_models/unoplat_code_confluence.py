"""PostgreSQL ORM models for Code Confluence relational storage."""

from __future__ import annotations

from unoplat_code_confluence_commons.base_models.sql_base import SQLBase



from typing import Any, Dict, List, Optional

from sqlalchemy import ForeignKeyConstraint, Index, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UnoplatCodeConfluenceGitRepository(SQLBase):
    """Git repository stored in PostgreSQL for Code Confluence."""

    __tablename__ = "code_confluence_git_repository"
    __table_args__ = (
        Index("uq_cc_git_repo_url", "repository_url", unique=True),
        {"extend_existing": True},
    )

    qualified_name: Mapped[str] = mapped_column(primary_key=True)
    repository_url: Mapped[str] = mapped_column(nullable=False)
    repository_name: Mapped[str] = mapped_column(nullable=False)
    repository_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, default=None
    )
    readme: Mapped[Optional[str]] = mapped_column(default=None)
    domain: Mapped[Optional[str]] = mapped_column(default=None)
    github_organization: Mapped[Optional[str]] = mapped_column(default=None)

    codebases: Mapped[List["UnoplatCodeConfluenceCodebase"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class UnoplatCodeConfluenceCodebase(SQLBase):
    """Codebase stored in PostgreSQL for Code Confluence."""

    __tablename__ = "code_confluence_codebase"
    __table_args__ = (
        ForeignKeyConstraint(
            ["repository_qualified_name"],
            ["code_confluence_git_repository.qualified_name"],
            ondelete="CASCADE",
        ),
        {"extend_existing": True},
    )

    qualified_name: Mapped[str] = mapped_column(primary_key=True)
    repository_qualified_name: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    readme: Mapped[Optional[str]] = mapped_column(default=None)
    root_packages: Mapped[Optional[List[str]]] = mapped_column(JSONB, default=None)
    codebase_path: Mapped[str] = mapped_column(nullable=False)
    codebase_folder: Mapped[Optional[str]] = mapped_column(default=None)
    programming_language: Mapped[Optional[str]] = mapped_column(default=None)

    repository: Mapped[UnoplatCodeConfluenceGitRepository] = relationship(
        back_populates="codebases"
    )
    package_manager_metadata: Mapped[
        Optional["UnoplatCodeConfluencePackageManagerMetadata"]
    ] = relationship(
        back_populates="codebase",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
    files: Mapped[List["UnoplatCodeConfluenceFile"]] = relationship(
        back_populates="codebase",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    frameworks: Mapped[List["UnoplatCodeConfluenceCodebaseFramework"]] = relationship(
        back_populates="codebase",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class UnoplatCodeConfluencePackageManagerMetadata(SQLBase):
    """Package manager metadata stored in PostgreSQL for Code Confluence."""

    __tablename__ = "code_confluence_package_manager_metadata"
    __table_args__ = (
        ForeignKeyConstraint(
            ["codebase_qualified_name"],
            ["code_confluence_codebase.qualified_name"],
            ondelete="CASCADE",
        ),
        Index(
            "uq_cc_pkg_metadata_codebase",
            "codebase_qualified_name",
            unique=True,
        ),
        {"extend_existing": True},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codebase_qualified_name: Mapped[str] = mapped_column(nullable=False)
    dependencies: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    other_metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    package_manager: Mapped[str] = mapped_column(nullable=False)
    programming_language: Mapped[str] = mapped_column(nullable=False)

    codebase: Mapped[UnoplatCodeConfluenceCodebase] = relationship(
        back_populates="package_manager_metadata"
    )


class UnoplatCodeConfluenceFile(SQLBase):
    """Source file stored in PostgreSQL for Code Confluence."""

    __tablename__ = "code_confluence_file"
    __table_args__ = (
        ForeignKeyConstraint(
            ["codebase_qualified_name"],
            ["code_confluence_codebase.qualified_name"],
            ondelete="CASCADE",
        ),
        {"extend_existing": True},
    )

    file_path: Mapped[str] = mapped_column(primary_key=True)
    codebase_qualified_name: Mapped[str] = mapped_column(nullable=False)
    checksum: Mapped[Optional[str]] = mapped_column(default=None)
    structural_signature: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, default=None
    )
    imports: Mapped[List[str]] = mapped_column(JSONB, default=list)
    has_data_model: Mapped[bool] = mapped_column(default=False)
    data_model_positions: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)

    codebase: Mapped[UnoplatCodeConfluenceCodebase] = relationship(
        back_populates="files"
    )
    framework_features: Mapped[List["UnoplatCodeConfluenceFileFrameworkFeature"]] = (
        relationship(
            back_populates="file",
            cascade="all, delete-orphan",
            passive_deletes=True,
        )
    )


class UnoplatCodeConfluenceCodebaseFramework(SQLBase):
    """Join table linking codebases to frameworks."""

    __tablename__ = "code_confluence_codebase_framework"
    __table_args__ = (
        ForeignKeyConstraint(
            ["codebase_qualified_name"],
            ["code_confluence_codebase.qualified_name"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["framework_language", "framework_library"],
            ["framework.language", "framework.library"],
            ondelete="CASCADE",
        ),
        {"extend_existing": True},
    )

    codebase_qualified_name: Mapped[str] = mapped_column(primary_key=True)
    framework_language: Mapped[str] = mapped_column(primary_key=True)
    framework_library: Mapped[str] = mapped_column(primary_key=True)

    codebase: Mapped[UnoplatCodeConfluenceCodebase] = relationship(
        back_populates="frameworks"
    )


class UnoplatCodeConfluenceFileFrameworkFeature(SQLBase):
    """Join table linking files to framework features with span metadata."""

    __tablename__ = "code_confluence_file_framework_feature"
    __table_args__ = (
        ForeignKeyConstraint(
            ["file_path"],
            ["code_confluence_file.file_path"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["feature_language", "feature_library", "feature_key"],
            [
                "framework_feature.language",
                "framework_feature.library",
                "framework_feature.feature_key",
            ],
            ondelete="CASCADE",
        ),
        {"extend_existing": True},
    )

    file_path: Mapped[str] = mapped_column(primary_key=True)
    feature_language: Mapped[str] = mapped_column(primary_key=True)
    feature_library: Mapped[str] = mapped_column(primary_key=True)
    feature_key: Mapped[str] = mapped_column(primary_key=True)
    start_line: Mapped[int] = mapped_column(primary_key=True)
    end_line: Mapped[int] = mapped_column(primary_key=True)
    match_text: Mapped[Optional[str]] = mapped_column(Text, default=None)

    file: Mapped[UnoplatCodeConfluenceFile] = relationship(
        back_populates="framework_features"
    )
