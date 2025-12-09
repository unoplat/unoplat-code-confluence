"""Helper service to initialize Repository and RepositoryWorkflowRun records.

This ensures parent records exist before creating RepositoryAgentMdSnapshot,
satisfying the foreign key constraints in the database schema.
"""

from datetime import datetime, timezone

from loguru import logger
from unoplat_code_confluence_commons.credential_enums import ProviderKey
from unoplat_code_confluence_commons.repo_models import (
    Repository,
    RepositoryWorkflowOperation,
    RepositoryWorkflowRun,
)

from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session


async def ensure_workflow_run_exists(
    *,
    owner_name: str,
    repo_name: str,
    repository_workflow_run_id: str,
    repository_workflow_id: str | None = None,
    operation: RepositoryWorkflowOperation = RepositoryWorkflowOperation.AGENTS_GENERATION,
    provider_key: ProviderKey = ProviderKey.GITHUB_OPEN,
) -> None:
    """Ensure Repository and RepositoryWorkflowRun records exist.

    Creates parent records if they don't exist, satisfying foreign key
    constraints for RepositoryAgentMdSnapshot.

    Args:
        owner_name: Repository owner name (e.g., "unoplat")
        repo_name: Repository name (e.g., "unoplat-code-confluence")
        repository_workflow_run_id: Unique workflow run identifier
        repository_workflow_id: Optional workflow identifier (defaults to run_id)
        operation: Type of workflow operation being performed
        provider_key: Git provider for the repository
    """
    workflow_id = repository_workflow_id or repository_workflow_run_id

    async with get_startup_session() as session:
        # Check if Repository exists, create if not
        repository = await session.get(Repository, (repo_name, owner_name))
        if not repository:
            repository = Repository(
                repository_name=repo_name,
                repository_owner_name=owner_name,
                repository_provider=provider_key,
            )
            session.add(repository)
            logger.info(
                "Created Repository record for {}/{}",
                owner_name,
                repo_name,
            )

        # Check if RepositoryWorkflowRun exists, create if not
        workflow_run = await session.get(
            RepositoryWorkflowRun,
            (repo_name, owner_name, repository_workflow_run_id),
        )
        if not workflow_run:
            now = datetime.now(timezone.utc)
            workflow_run = RepositoryWorkflowRun(
                repository_name=repo_name,
                repository_owner_name=owner_name,
                repository_workflow_run_id=repository_workflow_run_id,
                repository_workflow_id=workflow_id,
                operation=operation,
                status="RUNNING",
                started_at=now,
            )
            session.add(workflow_run)
            logger.info(
                "Created RepositoryWorkflowRun record for {}/{} with run_id={}",
                owner_name,
                repo_name,
                repository_workflow_run_id,
            )


async def mark_workflow_run_completed(
    *,
    owner_name: str,
    repo_name: str,
    repository_workflow_run_id: str,
) -> None:
    """Mark a workflow run as completed.

    Args:
        owner_name: Repository owner name
        repo_name: Repository name
        repository_workflow_run_id: Workflow run identifier to mark complete
    """
    async with get_startup_session() as session:
        workflow_run = await session.get(
            RepositoryWorkflowRun,
            (repo_name, owner_name, repository_workflow_run_id),
        )
        if workflow_run:
            workflow_run.status = "COMPLETED"
            workflow_run.completed_at = datetime.now(timezone.utc)
            session.add(workflow_run)
            logger.info(
                "Marked RepositoryWorkflowRun as COMPLETED for {}/{} run_id={}",
                owner_name,
                repo_name,
                repository_workflow_run_id,
            )


async def mark_workflow_run_failed(
    *,
    owner_name: str,
    repo_name: str,
    repository_workflow_run_id: str,
    error_report: dict[str, object] | None = None,
) -> None:
    """Mark a workflow run as failed.

    Args:
        owner_name: Repository owner name
        repo_name: Repository name
        repository_workflow_run_id: Workflow run identifier to mark failed
        error_report: Optional error details to persist
    """
    async with get_startup_session() as session:
        workflow_run = await session.get(
            RepositoryWorkflowRun,
            (repo_name, owner_name, repository_workflow_run_id),
        )
        if workflow_run:
            workflow_run.status = "FAILED"
            workflow_run.completed_at = datetime.now(timezone.utc)
            if error_report:
                workflow_run.error_report = error_report
            session.add(workflow_run)
            logger.info(
                "Marked RepositoryWorkflowRun as FAILED for {}/{} run_id={}",
                owner_name,
                repo_name,
                repository_workflow_run_id,
            )


__all__ = [
    "ensure_workflow_run_exists",
    "mark_workflow_run_completed",
    "mark_workflow_run_failed",
]
