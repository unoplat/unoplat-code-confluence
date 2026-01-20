"""PostgreSQL ingestion helpers for Code Confluence relational models."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from unoplat_code_confluence_commons.base_models import (
    Framework,
    FrameworkFeature,
)
from unoplat_code_confluence_commons.relational_models import (
    UnoplatCodeConfluenceCodebase,
    UnoplatCodeConfluenceCodebaseFramework,
    UnoplatCodeConfluenceFile,
    UnoplatCodeConfluenceFileFrameworkFeature,
    UnoplatCodeConfluenceGitRepository,
    UnoplatCodeConfluencePackageManagerMetadata,
)

from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_codebase import (
    UnoplatCodebase,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_file import (
    UnoplatFile,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_git_repository import (
    UnoplatGitRepository,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_package_manager_metadata import (
    UnoplatPackageManagerMetadata,
)


def _dump_model(value: Any) -> Any:
    """Convert pydantic models to dicts for JSONB storage."""
    if value is None:
        return None
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return value


def _build_package_manager_metadata_payload(
    metadata: UnoplatPackageManagerMetadata,
) -> Dict[str, Any]:
    """Build JSON payloads for package manager metadata storage."""
    dependencies_payload: Dict[str, Dict[str, Any]] = {}
    for group, packages in metadata.dependencies.items():
        dependencies_payload[group] = {
            name: dep.model_dump() for name, dep in packages.items()
        }

    other_fields: Dict[str, Any] = {}
    field_mapping = {
        "programming_language_version": metadata.programming_language_version,
        "project_version": metadata.project_version,
        "description": metadata.description,
        "license": metadata.license,
        "package_name": metadata.package_name,
        "entry_points": metadata.entry_points,
        "scripts": metadata.scripts,
        "binaries": metadata.binaries,
        "authors": metadata.authors,
        "homepage": metadata.homepage,
        "repository": metadata.repository,
        "documentation": metadata.documentation,
        "keywords": metadata.keywords,
        "maintainers": metadata.maintainers,
        "readme": metadata.readme,
        "manifest_path": metadata.manifest_path,
    }

    for key, value in field_mapping.items():
        if value is not None and value != [] and value != {}:
            other_fields[key] = value

    return {
        "dependencies": dependencies_payload,
        "other_metadata": other_fields,
        "package_manager": metadata.package_manager,
        "programming_language": metadata.programming_language,
    }


class CodeConfluenceRelationalIngestion:
    """Ingestion utilities for writing Code Confluence data to PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert_repository(self, git_repo: UnoplatGitRepository) -> str:
        qualified_name = (
            f"{git_repo.github_organization}_{git_repo.repository_name}"
        )
        payload = {
            "qualified_name": qualified_name,
            "repository_url": git_repo.repository_url,
            "repository_name": git_repo.repository_name,
            "repository_metadata": git_repo.repository_metadata,
            "readme": git_repo.readme,
            "domain": git_repo.domain,
            "github_organization": git_repo.github_organization,
        }

        stmt = insert(UnoplatCodeConfluenceGitRepository).values(**payload)
        stmt = stmt.on_conflict_do_update(
            index_elements=["qualified_name"],
            set_=payload,
        )
        await self.session.execute(stmt)
        return qualified_name

    async def upsert_codebases(
        self,
        repo_qualified_name: str,
        codebases: Iterable[UnoplatCodebase],
        *,
        include_package_metadata: bool = True,
    ) -> List[str]:
        qualified_names: List[str] = []
        for codebase in codebases:
            codebase_qualified_name = f"{repo_qualified_name}_{codebase.name}"
            qualified_names.append(codebase_qualified_name)
            payload = {
                "qualified_name": codebase_qualified_name,
                "repository_qualified_name": repo_qualified_name,
                "name": codebase.name,
                "readme": codebase.readme,
                "root_packages": codebase.root_packages,
                "codebase_path": codebase.codebase_path,
                "codebase_folder": codebase.codebase_folder,
                "programming_language": codebase.programming_language,
            }

            stmt = insert(UnoplatCodeConfluenceCodebase).values(**payload)
            stmt = stmt.on_conflict_do_update(
                index_elements=["qualified_name"],
                set_=payload,
            )
            await self.session.execute(stmt)

            if include_package_metadata:
                await self.upsert_package_manager_metadata(
                    codebase_qualified_name, codebase.package_manager_metadata
                )

        return qualified_names

    async def upsert_package_manager_metadata(
        self,
        codebase_qualified_name: str,
        metadata: UnoplatPackageManagerMetadata,
    ) -> None:
        payload = _build_package_manager_metadata_payload(metadata)
        stmt = insert(UnoplatCodeConfluencePackageManagerMetadata).values(
            codebase_qualified_name=codebase_qualified_name,
            **payload,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["codebase_qualified_name"],
            set_=payload,
        )
        await self.session.execute(stmt)

    async def upsert_files(
        self,
        codebase_qualified_name: str,
        files: Iterable[UnoplatFile],
    ) -> None:
        for file_item in files:
            payload = {
                "file_path": file_item.file_path,
                "codebase_qualified_name": codebase_qualified_name,
                "checksum": file_item.checksum,
                "structural_signature": _dump_model(file_item.structural_signature),
                "imports": file_item.imports or [],
                "has_data_model": file_item.has_data_model,
                "data_model_positions": _dump_model(file_item.data_model_positions),
            }

            stmt = insert(UnoplatCodeConfluenceFile).values(**payload)
            stmt = stmt.on_conflict_do_update(
                index_elements=["file_path"],
                set_=payload,
            )
            await self.session.execute(stmt)

    async def upsert_codebase_frameworks(
        self,
        codebase_qualified_name: str,
        frameworks: Iterable[tuple[str, str]],
    ) -> None:
        for language, library in frameworks:
            payload = {
                "codebase_qualified_name": codebase_qualified_name,
                "framework_language": language,
                "framework_library": library,
            }
            stmt = insert(UnoplatCodeConfluenceCodebaseFramework).values(**payload)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=[
                    "codebase_qualified_name",
                    "framework_language",
                    "framework_library",
                ]
            )
            await self.session.execute(stmt)

    async def upsert_file_features(
        self,
        file_path: str,
        feature_rows: Iterable[Dict[str, Any]],
    ) -> None:
        for feature_row in feature_rows:
            payload = {
                "file_path": file_path,
                "feature_language": feature_row["feature_language"],
                "feature_library": feature_row["feature_library"],
                "feature_key": feature_row["feature_key"],
                "start_line": feature_row["start_line"],
                "end_line": feature_row["end_line"],
                "match_text": feature_row.get("match_text"),
            }
            stmt = insert(UnoplatCodeConfluenceFileFrameworkFeature).values(**payload)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=[
                    "file_path",
                    "feature_language",
                    "feature_library",
                    "feature_key",
                    "start_line",
                    "end_line",
                ]
            )
            await self.session.execute(stmt)

    async def get_framework_libraries_for_language(
        self, language: str
    ) -> List[str]:
        stmt = select(Framework.library).where(Framework.language == language)
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all()]

    async def get_framework_features_for_language(
        self, language: str
    ) -> List[tuple[str, str]]:
        stmt = select(
            FrameworkFeature.library, FrameworkFeature.feature_key
        ).where(FrameworkFeature.language == language)
        result = await self.session.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]
