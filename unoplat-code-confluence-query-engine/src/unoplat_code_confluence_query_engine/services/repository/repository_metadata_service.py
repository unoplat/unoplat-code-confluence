from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException
from loguru import logger
from sqlalchemy import select
from unoplat_code_confluence_commons.base_models import (
    CodebaseConfigSQLModel,
    Repository,
)

from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session
from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    CodebaseMetadata,
    RepositoryRulesetMetadata,
)
from unoplat_code_confluence_query_engine.services.repository.codebase_path_resolver import (
    CodebasePathResolver,
)
from unoplat_code_confluence_query_engine.services.repository.package_manager_metadata_service import (
    fetch_programming_language_metadata,
)

_VALID_PACKAGE_MANAGER_PROVENANCE = frozenset({"local", "inherited"})


def _normalize_optional_repo_relative_path(
    raw_value: object,
    *,
    allow_dot: bool,
    field_name: str,
) -> Optional[str]:
    """Normalize repo-relative POSIX metadata paths and reject malformed values."""
    if not isinstance(raw_value, str):
        return None

    candidate = raw_value.strip()
    if not candidate:
        return None

    if "\\" in candidate:
        logger.warning(
            "Rejecting malformed {} '{}' because it is not POSIX-formatted",
            field_name,
            candidate,
        )
        return None

    if candidate.startswith("/"):
        logger.warning(
            "Rejecting malformed {} '{}' because it is absolute",
            field_name,
            candidate,
        )
        return None

    normalized = PurePosixPath(candidate).as_posix()
    if ".." in PurePosixPath(normalized).parts:
        logger.warning(
            "Rejecting malformed {} '{}' because it escapes the repository root",
            field_name,
            candidate,
        )
        return None

    if normalized == ".":
        if allow_dot:
            return "."
        logger.warning(
            "Rejecting malformed {} '{}' because '.' is not allowed",
            field_name,
            candidate,
        )
        return None

    return normalized


def _extract_provenance_fields(
    raw_plm: Dict[str, Any],
) -> Tuple[Optional[str], Optional[str]]:
    """Extract package_manager_provenance and workspace_root from JSONB metadata.

    Only returns values when stored as strings; otherwise returns None.
    """
    raw_provenance: object = raw_plm.get("package_manager_provenance")
    provenance: Optional[str] = None
    if isinstance(raw_provenance, str):
        normalized_provenance = raw_provenance.strip().lower()
        if normalized_provenance in _VALID_PACKAGE_MANAGER_PROVENANCE:
            provenance = normalized_provenance
        else:
            logger.warning(
                "Rejecting malformed package_manager_provenance '{}' from stored metadata",
                raw_provenance,
            )

    ws_root = _normalize_optional_repo_relative_path(
        raw_plm.get("workspace_root"),
        allow_dot=True,
        field_name="workspace_root",
    )

    return provenance, ws_root


def _derive_workspace_root_path(
    absolute_path: str,
    relative_path: str,
    workspace_root: Optional[str],
) -> Optional[str]:
    """Derive absolute workspace root path from codebase paths and workspace_root.

    Args:
        absolute_path: Absolute or relative-fallback path to the codebase.
        relative_path: Repo-relative path (codebase_folder).
        workspace_root: Repo-relative workspace root from JSONB. None for standalone.

    Returns:
        Absolute path to workspace root, or None if derivation is not possible.
    """
    if workspace_root is None:
        return None

    normalized_relative_path = _normalize_optional_repo_relative_path(
        relative_path,
        allow_dot=True,
        field_name="codebase_folder",
    )
    if normalized_relative_path is None:
        logger.warning(
            "Cannot derive workspace_root_path: codebase_folder '{}' is malformed",
            relative_path,
        )
        return None

    # (d) Derive repo_root_path only when absolute_path is absolute
    if not Path(absolute_path).is_absolute():
        logger.warning(
            "Cannot derive workspace_root_path: absolute_path '{}' is not absolute",
            absolute_path,
        )
        return None

    # Compute repo root by walking up from codebase absolute path
    if normalized_relative_path == ".":
        repo_root_path = Path(absolute_path)
    else:
        depth = len(PurePosixPath(normalized_relative_path).parts)
        repo_root_path = Path(absolute_path)
        for _ in range(depth):
            repo_root_path = repo_root_path.parent

    # (f) Derive absolute workspace root
    if workspace_root == ".":
        return str(repo_root_path)

    return str(repo_root_path / PurePosixPath(workspace_root))


async def fetch_repository_metadata(
    owner_name: str, repo_name: str
) -> RepositoryRulesetMetadata:
    """
    Fetch repository and codebase configuration data from PostgreSQL and resolve
    absolute paths from PostgreSQL.

    Args:
        owner_name: Repository owner name
        repo_name: Repository name
    Returns:
        RepositoryRulesetMetadata with populated codebase metadata including
        absolute paths

    Raises:
        HTTPException: If repository is not found or a database error occurs
    """
    try:
        # First, fetch repository and codebase configurations from PostgreSQL
        codebase_configs = None
        async with get_startup_session() as session:
            # Fetch repository
            repository_stmt = select(Repository).where(
                Repository.repository_name == repo_name,
                Repository.repository_owner_name == owner_name,
            )
            repository_result = await session.execute(repository_stmt)
            repository = repository_result.scalar_one_or_none()

            if not repository:
                raise HTTPException(
                    status_code=404,
                    detail=f"Repository not found: {owner_name}/{repo_name}",
                )

            # Fetch codebase configurations for this repository
            codebase_configs_stmt = select(CodebaseConfigSQLModel).where(
                CodebaseConfigSQLModel.repository_name == repo_name,
                CodebaseConfigSQLModel.repository_owner_name == owner_name,
            )
            codebase_configs_result = await session.execute(codebase_configs_stmt)
            codebase_configs = codebase_configs_result.scalars().all()

            if not codebase_configs:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"No codebase configurations found for repository: "
                        f"{owner_name}/{repo_name}"
                    ),
                )

        # Extract relative paths for codebase path resolution
        relative_paths = [config.codebase_folder for config in codebase_configs]

        # Resolve absolute paths from PostgreSQL using qualified name format: {owner_name}_{repo_name}
        repository_qualified_name = f"{owner_name}_{repo_name}"
        path_resolver = CodebasePathResolver()

        try:
            path_mapping = await path_resolver.resolve_codebase_absolute_paths(
                repository_qualified_name, relative_paths
            )
        except Exception as e:
            logger.warning("Failed to resolve absolute paths from Postgres: {}", e)
            # Create empty mapping - will use relative paths as fallback
            path_mapping = {path: None for path in relative_paths}

        # Convert to CodebaseMetadata objects
        codebase_metadata_list: List[CodebaseMetadata] = []
        for config in codebase_configs:
            # Get absolute path from Postgres mapping, fallback to relative path if not found
            relative_path = config.codebase_folder
            absolute_path = path_mapping.get(relative_path)

            if absolute_path is None:
                logger.warning(
                    "No absolute path found for codebase {}, using relative path as fallback",
                    relative_path,
                )
                absolute_path = relative_path

            # Fetch programming language metadata using absolute path
            prog_lang_metadata = await fetch_programming_language_metadata(
                absolute_path
            )

            logger.info(
                "Fetched programming language metadata for {}/{}: {}",
                repository_qualified_name,
                relative_path,
                prog_lang_metadata.model_dump_json() if prog_lang_metadata else "None",
            )

            if not prog_lang_metadata:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Programming language metadata not found for codebase: "
                        f"{relative_path}"
                    ),
                )

            # (b) Extract provenance fields from JSONB metadata
            raw_plm: Dict[str, Any] = config.programming_language_metadata  # type: ignore[assignment]
            provenance, workspace_root = _extract_provenance_fields(raw_plm)

            # (c-g) Derive absolute workspace root path
            workspace_root_path = _derive_workspace_root_path(
                absolute_path, relative_path, workspace_root
            )

            codebase_metadata = CodebaseMetadata(
                codebase_name=relative_path,
                codebase_path=absolute_path,
                codebase_programming_language=prog_lang_metadata.primary_language,
                codebase_package_manager=prog_lang_metadata.package_manager,
                codebase_package_manager_provenance=provenance,
                codebase_workspace_root=workspace_root,
                codebase_workspace_root_path=workspace_root_path,
            )
            codebase_metadata_list.append(codebase_metadata)

        # Create and return RepositoryRulesetMetadata with proper qualified name format
        return RepositoryRulesetMetadata(
            repository_qualified_name=f"{owner_name}/{repo_name}",
            codebase_metadata=codebase_metadata_list,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error while fetching repository metadata: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch repository metadata: {str(e)}"
        )
