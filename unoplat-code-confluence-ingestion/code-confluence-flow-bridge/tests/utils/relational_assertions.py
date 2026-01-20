"""
Relational assertion utilities for integration tests.

These helpers validate repository cleanup in PostgreSQL relational tables
after calling the delete-repository endpoint.
"""

from typing import Any, Dict, List

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from unoplat_code_confluence_commons.base_models import Framework, FrameworkFeature
from unoplat_code_confluence_commons.relational_models import (
    UnoplatCodeConfluenceCodebase,
    UnoplatCodeConfluenceCodebaseFramework,
    UnoplatCodeConfluenceFile,
    UnoplatCodeConfluenceFileFrameworkFeature,
    UnoplatCodeConfluenceGitRepository,
    UnoplatCodeConfluencePackageManagerMetadata,
)


def _count(session: Session, stmt) -> int:
    return int(session.execute(stmt).scalar_one())


def _get_codebase_qualified_names(
    session: Session, repo_qualified_name: str
) -> List[str]:
    result = session.execute(
        select(UnoplatCodeConfluenceCodebase.qualified_name).where(
            UnoplatCodeConfluenceCodebase.repository_qualified_name
            == repo_qualified_name
        )
    )
    return [row[0] for row in result.all()]


def capture_relational_state_snapshot(
    session: Session, repo_qualified_name: str
) -> Dict[str, Any]:
    """
    Capture counts of relational rows for a repository.

    The snapshot is scoped to a repository qualified_name and is safe
    to use in tests that run with a single repository in the database.
    """
    codebase_names = _get_codebase_qualified_names(session, repo_qualified_name)

    repo_count = _count(
        session,
        select(func.count())
        .select_from(UnoplatCodeConfluenceGitRepository)
        .where(UnoplatCodeConfluenceGitRepository.qualified_name == repo_qualified_name),
    )
    codebase_count = _count(
        session,
        select(func.count())
        .select_from(UnoplatCodeConfluenceCodebase)
        .where(
            UnoplatCodeConfluenceCodebase.repository_qualified_name
            == repo_qualified_name
        ),
    )

    if codebase_names:
        file_count = _count(
            session,
            select(func.count())
            .select_from(UnoplatCodeConfluenceFile)
            .where(UnoplatCodeConfluenceFile.codebase_qualified_name.in_(codebase_names)),
        )
        package_metadata_count = _count(
            session,
            select(func.count())
            .select_from(UnoplatCodeConfluencePackageManagerMetadata)
            .where(
                UnoplatCodeConfluencePackageManagerMetadata.codebase_qualified_name.in_(
                    codebase_names
                )
            ),
        )
        codebase_framework_count = _count(
            session,
            select(func.count())
            .select_from(UnoplatCodeConfluenceCodebaseFramework)
            .where(
                UnoplatCodeConfluenceCodebaseFramework.codebase_qualified_name.in_(
                    codebase_names
                )
            ),
        )
        file_framework_feature_count = _count(
            session,
            select(func.count())
            .select_from(UnoplatCodeConfluenceFileFrameworkFeature)
            .join(
                UnoplatCodeConfluenceFile,
                UnoplatCodeConfluenceFileFrameworkFeature.file_path
                == UnoplatCodeConfluenceFile.file_path,
            )
            .where(UnoplatCodeConfluenceFile.codebase_qualified_name.in_(codebase_names)),
        )
    else:
        file_count = 0
        package_metadata_count = 0
        codebase_framework_count = 0
        file_framework_feature_count = 0

    return {
        "repo_qualified_name": repo_qualified_name,
        "counts": {
            "git_repository": repo_count,
            "codebases": codebase_count,
            "files": file_count,
            "package_manager_metadata": package_metadata_count,
            "codebase_framework_links": codebase_framework_count,
            "file_framework_feature_links": file_framework_feature_count,
        },
    }


def assert_relational_repository_deleted(
    session: Session, repo_qualified_name: str
) -> None:
    snapshot = capture_relational_state_snapshot(session, repo_qualified_name)
    remaining = {
        key: count for key, count in snapshot["counts"].items() if count > 0
    }
    assert not remaining, (
        "Relational data still present after deletion "
        f"for {repo_qualified_name}: {remaining}"
    )


def get_framework_catalog_counts(session: Session) -> Dict[str, int]:
    return {
        "frameworks": _count(
            session, select(func.count()).select_from(Framework)
        ),
        "framework_features": _count(
            session, select(func.count()).select_from(FrameworkFeature)
        ),
    }
