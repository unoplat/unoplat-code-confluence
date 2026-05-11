"""
Integration tests for RepositoryAgentSnapshotWriter.

Tests verify that the RepositoryAgentSnapshotWriter correctly manipulates
the repository_agent_md_snapshot, repository_agent_codebase_progress, and
repository_agent_event tables under real Postgres conditions.
"""

from datetime import datetime
from decimal import Decimal
from typing import TypedDict

import pytest
from sqlalchemy import text

from tests.utils.sync_db_utils import cleanup_postgresql_sync, get_sync_postgres_session
from unoplat_code_confluence_query_engine.services.tracking.repository_agent_snapshot_service import (
    RepositoryAgentSnapshotWriter,
)

# Test constants
TEST_OWNER = "test-owner"
TEST_REPO = "test-repo"
TEST_WORKFLOW_RUN_ID = "test-workflow-run-123"
TEST_CODEBASE_1 = "backend"
TEST_CODEBASE_2 = "frontend"


class SnapshotData(TypedDict):
    overall_progress: Decimal | None
    latest_event_at: datetime | None
    agent_md_output: dict[str, object]
    statistics: dict[str, object] | None
    created_at: datetime
    modified_at: datetime


class ProgressData(TypedDict):
    codebase_name: str
    next_event_id: int
    latest_event_id: int | None
    event_count: int
    progress: Decimal
    completed_namespaces: list[str]
    latest_event_at: datetime | None
    created_at: datetime
    modified_at: datetime


class EventData(TypedDict):
    event_id: int
    event: str
    phase: str
    message: str | None
    tool_name: str | None
    tool_call_id: str | None
    tool_args: dict[str, object] | None
    tool_result_content: str | None
    created_at: datetime


# ──────────────────────────────────────────────────────────────────────────────
# SEED DATA HELPERS
# ──────────────────────────────────────────────────────────────────────────────


def create_test_repository(sync_session, owner: str, name: str) -> None:
    """Create minimal repository row for testing."""
    sync_session.execute(
        text("""
            INSERT INTO repository (repository_owner_name, repository_name, repository_provider)
            VALUES (:owner, :name, 'github_open')
            ON CONFLICT DO NOTHING
        """),
        {"owner": owner, "name": name},
    )
    sync_session.commit()


def create_test_repository_workflow_run(
    sync_session, owner: str, name: str, workflow_run_id: str
) -> None:
    """Create minimal repository_workflow_run row for testing (required by FK constraint)."""
    sync_session.execute(
        text("""
            INSERT INTO repository_workflow_run (
                repository_owner_name,
                repository_name,
                repository_workflow_run_id,
                repository_workflow_id,
                operation,
                status,
                started_at
            )
            VALUES (:owner, :name, :run_id, 'test-workflow-id', 'AGENTS_GENERATION', 'RUNNING', NOW())
            ON CONFLICT DO NOTHING
        """),
        {"owner": owner, "name": name, "run_id": workflow_run_id},
    )
    sync_session.commit()


def get_snapshot_data(
    sync_session,
    owner: str,
    name: str,
    workflow_run_id: str,
) -> SnapshotData | None:
    """Fetch complete row from repository_agent_md_snapshot.

    Snapshot rows are keyed by (owner, repo, workflow_run_id).
    """
    result = sync_session.execute(
        text("""
            SELECT
                overall_progress,
                latest_event_at,
                agent_md_output,
                statistics,
                created_at,
                modified_at
            FROM repository_agent_md_snapshot
            WHERE repository_owner_name = :owner
              AND repository_name = :name
              AND repository_workflow_run_id = :run_id
        """),
        {"owner": owner, "name": name, "run_id": workflow_run_id},
    )
    row = result.fetchone()
    if row:
        return {
            "overall_progress": row[0],
            "latest_event_at": row[1],
            "agent_md_output": row[2],
            "statistics": row[3],
            "created_at": row[4],
            "modified_at": row[5],
        }
    return None


def count_snapshot_rows(
    sync_session, owner: str, name: str, workflow_run_id: str
) -> int:
    """Count rows in repository_agent_md_snapshot for given repo."""
    result = sync_session.execute(
        text("""
            SELECT COUNT(*) FROM repository_agent_md_snapshot
            WHERE repository_owner_name = :owner
              AND repository_name = :name
              AND repository_workflow_run_id = :run_id
        """),
        {"owner": owner, "name": name, "run_id": workflow_run_id},
    )
    return result.scalar()


def list_codebase_progress_rows(
    sync_session,
    owner: str,
    name: str,
    workflow_run_id: str,
) -> list[ProgressData]:
    """Fetch all codebase progress rows for a repository workflow run."""
    result = sync_session.execute(
        text("""
            SELECT
                codebase_name,
                next_event_id,
                latest_event_id,
                event_count,
                progress,
                completed_namespaces,
                latest_event_at,
                created_at,
                modified_at
            FROM repository_agent_codebase_progress
            WHERE repository_owner_name = :owner
              AND repository_name = :name
              AND repository_workflow_run_id = :run_id
            ORDER BY codebase_name
        """),
        {"owner": owner, "name": name, "run_id": workflow_run_id},
    )
    return [
        {
            "codebase_name": row[0],
            "next_event_id": row[1],
            "latest_event_id": row[2],
            "event_count": row[3],
            "progress": row[4],
            "completed_namespaces": row[5],
            "latest_event_at": row[6],
            "created_at": row[7],
            "modified_at": row[8],
        }
        for row in result.fetchall()
    ]


def list_codebase_events(
    sync_session,
    owner: str,
    name: str,
    workflow_run_id: str,
    codebase_name: str,
) -> list[EventData]:
    """Fetch persisted event rows for a codebase stream in order."""
    result = sync_session.execute(
        text("""
            SELECT
                event_id,
                event,
                phase,
                message,
                tool_name,
                tool_call_id,
                tool_args,
                tool_result_content,
                created_at
            FROM repository_agent_event
            WHERE repository_owner_name = :owner
              AND repository_name = :name
              AND repository_workflow_run_id = :run_id
              AND codebase_name = :codebase_name
            ORDER BY event_id
        """),
        {
            "owner": owner,
            "name": name,
            "run_id": workflow_run_id,
            "codebase_name": codebase_name,
        },
    )
    return [
        {
            "event_id": row[0],
            "event": row[1],
            "phase": row[2],
            "message": row[3],
            "tool_name": row[4],
            "tool_call_id": row[5],
            "tool_args": row[6],
            "tool_result_content": row[7],
            "created_at": row[8],
        }
        for row in result.fetchall()
    ]


# ──────────────────────────────────────────────────────────────────────────────
# FIXTURES
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def writer(db_connections):
    """Create RepositoryAgentSnapshotWriter instance for testing."""
    return RepositoryAgentSnapshotWriter()


@pytest.fixture
def seeded_db(service_ports, test_database_tables):
    """Provide database with minimal seed data."""
    with get_sync_postgres_session(service_ports["postgresql"]) as session:
        cleanup_postgresql_sync(session)
        create_test_repository(session, TEST_OWNER, TEST_REPO)
        create_test_repository_workflow_run(
            session, TEST_OWNER, TEST_REPO, TEST_WORKFLOW_RUN_ID
        )

    yield service_ports

    # Cleanup after test
    with get_sync_postgres_session(service_ports["postgresql"]) as session:
        cleanup_postgresql_sync(session)


# ──────────────────────────────────────────────────────────────────────────────
# INTEGRATION TESTS
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio(loop_scope="session")
async def test_begin_run_creates_snapshot_row(seeded_db, writer):
    """Test that begin_run creates repository_agent_md_snapshot row with correct initial values."""
    # Before: no snapshot should exist
    with get_sync_postgres_session(seeded_db["postgresql"]) as session:
        assert (
            count_snapshot_rows(session, TEST_OWNER, TEST_REPO, TEST_WORKFLOW_RUN_ID)
            == 0
        )

    # Execute begin_run
    await writer.begin_run(
        owner_name=TEST_OWNER,
        repo_name=TEST_REPO,
        repository_qualified_name=f"{TEST_OWNER}/{TEST_REPO}",
        repository_workflow_run_id=TEST_WORKFLOW_RUN_ID,
        codebase_names=[TEST_CODEBASE_1, TEST_CODEBASE_2],
    )

    # Verify snapshot row created with correct values
    with get_sync_postgres_session(seeded_db["postgresql"]) as session:
        assert (
            count_snapshot_rows(session, TEST_OWNER, TEST_REPO, TEST_WORKFLOW_RUN_ID)
            == 1
        )

        snapshot = get_snapshot_data(
            session,
            TEST_OWNER,
            TEST_REPO,
            TEST_WORKFLOW_RUN_ID,
        )
        assert snapshot is not None

        assert snapshot["overall_progress"] == Decimal("0.00")
        assert snapshot["latest_event_at"] is None

        # Check agent_md_output has the initialized repository snapshot shape
        assert snapshot["agent_md_output"] == {
            "repository": f"{TEST_OWNER}/{TEST_REPO}",
            "codebases": {},
        }
        assert snapshot["statistics"] is None

        progress_rows = list_codebase_progress_rows(
            session,
            TEST_OWNER,
            TEST_REPO,
            TEST_WORKFLOW_RUN_ID,
        )
        assert len(progress_rows) == 2
        assert [row["codebase_name"] for row in progress_rows] == [
            TEST_CODEBASE_1,
            TEST_CODEBASE_2,
        ]
        for row in progress_rows:
            assert row["next_event_id"] == 1
            assert row["latest_event_id"] is None
            assert row["event_count"] == 0
            assert row["progress"] == Decimal("0.00")
            assert row["completed_namespaces"] == []
            assert row["latest_event_at"] is None

        # Check timestamps are set
        assert snapshot["created_at"] is not None
        assert snapshot["modified_at"] is not None


@pytest.mark.integration
@pytest.mark.asyncio(loop_scope="session")
async def test_begin_run_upserts_existing_row(seeded_db, writer):
    """Test that begin_run updates existing row instead of creating duplicate.

    With the current schema, rows are keyed by (owner, repo, workflow_run_id),
    so upsert happens when begin_run is called with the same workflow_run_id.
    """
    # First begin_run with one codebase
    await writer.begin_run(
        owner_name=TEST_OWNER,
        repo_name=TEST_REPO,
        repository_qualified_name=f"{TEST_OWNER}/{TEST_REPO}",
        repository_workflow_run_id=TEST_WORKFLOW_RUN_ID,
        codebase_names=[TEST_CODEBASE_1],
    )

    # Get initial timestamps
    with get_sync_postgres_session(seeded_db["postgresql"]) as session:
        initial_snapshot = get_snapshot_data(
            session,
            TEST_OWNER,
            TEST_REPO,
            TEST_WORKFLOW_RUN_ID,
        )
        assert initial_snapshot is not None
        initial_created_at = initial_snapshot["created_at"]
        initial_modified_at = initial_snapshot["modified_at"]
        assert (
            len(
                list_codebase_progress_rows(
                    session,
                    TEST_OWNER,
                    TEST_REPO,
                    TEST_WORKFLOW_RUN_ID,
                )
            )
            == 1
        )

    # Second begin_run with SAME workflow_run_id but different codebases
    await writer.begin_run(
        owner_name=TEST_OWNER,
        repo_name=TEST_REPO,
        repository_qualified_name=f"{TEST_OWNER}/{TEST_REPO}",
        repository_workflow_run_id=TEST_WORKFLOW_RUN_ID,
        codebase_names=[TEST_CODEBASE_1, TEST_CODEBASE_2],
    )

    # Verify still only one snapshot row and codebase progress rows are merged
    with get_sync_postgres_session(seeded_db["postgresql"]) as session:
        assert (
            count_snapshot_rows(session, TEST_OWNER, TEST_REPO, TEST_WORKFLOW_RUN_ID)
            == 1
        )

        snapshot = get_snapshot_data(
            session,
            TEST_OWNER,
            TEST_REPO,
            TEST_WORKFLOW_RUN_ID,
        )
        assert snapshot is not None

        progress_rows = list_codebase_progress_rows(
            session,
            TEST_OWNER,
            TEST_REPO,
            TEST_WORKFLOW_RUN_ID,
        )
        assert len(progress_rows) == 2
        assert [row["codebase_name"] for row in progress_rows] == [
            TEST_CODEBASE_1,
            TEST_CODEBASE_2,
        ]

        # Snapshot insert is idempotent and should not update timestamps on conflict.
        assert snapshot["created_at"] == initial_created_at
        assert snapshot["modified_at"] == initial_modified_at


@pytest.mark.integration
@pytest.mark.asyncio(loop_scope="session")
async def test_append_event_updates_progress_and_timestamp(seeded_db, writer):
    """Test that append_event_atomic stores event rows and updates progress timestamps."""
    # Setup: initialize snapshot
    await writer.begin_run(
        owner_name=TEST_OWNER,
        repo_name=TEST_REPO,
        repository_qualified_name=f"{TEST_OWNER}/{TEST_REPO}",
        repository_workflow_run_id=TEST_WORKFLOW_RUN_ID,
        codebase_names=[TEST_CODEBASE_1],
    )

    # Get initial state
    with get_sync_postgres_session(seeded_db["postgresql"]) as session:
        initial_snapshot = get_snapshot_data(
            session,
            TEST_OWNER,
            TEST_REPO,
            TEST_WORKFLOW_RUN_ID,
        )
        assert initial_snapshot is not None
        initial_modified_at = initial_snapshot["modified_at"]

    # Append an event atomically.
    event_id = await writer.append_event_atomic(
        owner_name=TEST_OWNER,
        repo_name=TEST_REPO,
        codebase_name=TEST_CODEBASE_1,
        agent_name="processing_step",
        phase="result",
        message="Step completed",
        completion_namespaces={"processing_step", "final_review"},
        repository_workflow_run_id=TEST_WORKFLOW_RUN_ID,
    )
    assert event_id == 1

    # Verify updates
    with get_sync_postgres_session(seeded_db["postgresql"]) as session:
        events = list_codebase_events(
            session,
            TEST_OWNER,
            TEST_REPO,
            TEST_WORKFLOW_RUN_ID,
            TEST_CODEBASE_1,
        )
        assert len(events) == 1
        assert events[0]["event_id"] == 1
        assert events[0]["event"] == "processing_step"
        assert events[0]["phase"] == "result"
        assert events[0]["message"] == "Step completed"
        assert events[0]["tool_name"] is None
        assert events[0]["tool_call_id"] is None
        assert events[0]["tool_args"] is None
        assert events[0]["tool_result_content"] is None

        progress_rows = list_codebase_progress_rows(
            session,
            TEST_OWNER,
            TEST_REPO,
            TEST_WORKFLOW_RUN_ID,
        )
        assert len(progress_rows) == 1
        progress = progress_rows[0]
        assert progress["codebase_name"] == TEST_CODEBASE_1
        assert progress["next_event_id"] == 2
        assert progress["latest_event_id"] == 1
        assert progress["event_count"] == 1
        assert progress["progress"] == Decimal("50.00")
        assert progress["completed_namespaces"] == ["processing_step"]
        assert progress["latest_event_at"] is not None

        snapshot = get_snapshot_data(
            session,
            TEST_OWNER,
            TEST_REPO,
            TEST_WORKFLOW_RUN_ID,
        )
        assert snapshot is not None
        assert snapshot["overall_progress"] == Decimal("50.00")
        assert snapshot["latest_event_at"] is not None

        # Check timestamp updated
        assert snapshot["modified_at"] > initial_modified_at


@pytest.mark.integration
@pytest.mark.asyncio(loop_scope="session")
async def test_patch_codebase_output_atomically_merges_sections(seeded_db, writer):
    """Test that patch_codebase_output merges one codebase object without overwriting siblings."""
    await writer.begin_run(
        owner_name=TEST_OWNER,
        repo_name=TEST_REPO,
        repository_qualified_name=f"{TEST_OWNER}/{TEST_REPO}",
        repository_workflow_run_id=TEST_WORKFLOW_RUN_ID,
        codebase_names=[TEST_CODEBASE_1, TEST_CODEBASE_2],
    )

    with get_sync_postgres_session(seeded_db["postgresql"]) as session:
        initial_snapshot = get_snapshot_data(
            session,
            TEST_OWNER,
            TEST_REPO,
            TEST_WORKFLOW_RUN_ID,
        )
        assert initial_snapshot is not None
        initial_modified_at = initial_snapshot["modified_at"]

    await writer.patch_codebase_output(
        owner_name=TEST_OWNER,
        repo_name=TEST_REPO,
        repository_workflow_run_id=TEST_WORKFLOW_RUN_ID,
        codebase_name=TEST_CODEBASE_1,
        codebase_patch={
            "codebase_name": TEST_CODEBASE_1,
            "programming_language_metadata": {
                "primary_language": "python",
                "package_manager": "uv",
            },
            "engineering_workflow": None,
            "dependency_guide": None,
        },
    )
    await writer.patch_codebase_output(
        owner_name=TEST_OWNER,
        repo_name=TEST_REPO,
        repository_workflow_run_id=TEST_WORKFLOW_RUN_ID,
        codebase_name=TEST_CODEBASE_1,
        codebase_patch={
            "engineering_workflow": {"commands": ["uv run pytest"]},
        },
    )
    await writer.patch_codebase_output(
        owner_name=TEST_OWNER,
        repo_name=TEST_REPO,
        repository_workflow_run_id=TEST_WORKFLOW_RUN_ID,
        codebase_name=TEST_CODEBASE_2,
        codebase_patch={
            "codebase_name": TEST_CODEBASE_2,
            "dependency_guide": {"dependencies": []},
        },
    )

    with get_sync_postgres_session(seeded_db["postgresql"]) as session:
        snapshot = get_snapshot_data(
            session,
            TEST_OWNER,
            TEST_REPO,
            TEST_WORKFLOW_RUN_ID,
        )
        assert snapshot is not None
        assert snapshot["modified_at"] > initial_modified_at

        agent_md_output = snapshot["agent_md_output"]
        assert agent_md_output["repository"] == f"{TEST_OWNER}/{TEST_REPO}"
        codebases = agent_md_output["codebases"]
        assert codebases[TEST_CODEBASE_1] == {
            "codebase_name": TEST_CODEBASE_1,
            "programming_language_metadata": {
                "primary_language": "python",
                "package_manager": "uv",
            },
            "engineering_workflow": {"commands": ["uv run pytest"]},
            "dependency_guide": None,
        }
        assert codebases[TEST_CODEBASE_2] == {
            "codebase_name": TEST_CODEBASE_2,
            "dependency_guide": {"dependencies": []},
        }


@pytest.mark.integration
@pytest.mark.asyncio(loop_scope="session")
async def test_complete_run_updates_statistics_without_overwriting_output(
    seeded_db, writer
):
    """Test that complete_run persists statistics without replacing partial agent_md_output."""
    await writer.begin_run(
        owner_name=TEST_OWNER,
        repo_name=TEST_REPO,
        repository_qualified_name=f"{TEST_OWNER}/{TEST_REPO}",
        repository_workflow_run_id=TEST_WORKFLOW_RUN_ID,
        codebase_names=[TEST_CODEBASE_1],
    )
    await writer.patch_codebase_output(
        owner_name=TEST_OWNER,
        repo_name=TEST_REPO,
        repository_workflow_run_id=TEST_WORKFLOW_RUN_ID,
        codebase_name=TEST_CODEBASE_1,
        codebase_patch={
            "codebase_name": TEST_CODEBASE_1,
            "engineering_workflow": {"commands": ["uv run pytest"]},
        },
    )

    with get_sync_postgres_session(seeded_db["postgresql"]) as session:
        initial_snapshot = get_snapshot_data(
            session,
            TEST_OWNER,
            TEST_REPO,
            TEST_WORKFLOW_RUN_ID,
        )
        assert initial_snapshot is not None
        initial_modified_at = initial_snapshot["modified_at"]
        initial_agent_md_output = initial_snapshot["agent_md_output"]

    statistics_payload = {
        "total_requests": 5,
        "total_tool_calls": 12,
        "total_input_tokens": 1500,
        "total_output_tokens": 800,
        "total_cache_write_tokens": 200,
        "total_cache_read_tokens": 300,
        "total_tokens": 2300,
        "total_estimated_cost_usd": 0.05,
        "by_codebase": {
            TEST_CODEBASE_1: {
                "requests": 5,
                "tool_calls": 12,
                "input_tokens": 1500,
                "output_tokens": 800,
                "cache_write_tokens": 200,
                "cache_read_tokens": 300,
                "total_tokens": 2300,
                "estimated_cost_usd": 0.05,
            }
        },
    }

    await writer.complete_run(
        owner_name=TEST_OWNER,
        repo_name=TEST_REPO,
        repository_workflow_run_id=TEST_WORKFLOW_RUN_ID,
        statistics_payload=statistics_payload,
    )

    with get_sync_postgres_session(seeded_db["postgresql"]) as session:
        snapshot = get_snapshot_data(
            session,
            TEST_OWNER,
            TEST_REPO,
            TEST_WORKFLOW_RUN_ID,
        )
        assert snapshot is not None
        assert snapshot["agent_md_output"] == initial_agent_md_output

        assert snapshot["statistics"] is not None
        statistics = snapshot["statistics"]
        assert isinstance(statistics, dict)
        assert statistics["total_requests"] == 5
        assert statistics["total_tool_calls"] == 12
        assert statistics["total_tokens"] == 2300
        assert statistics["total_estimated_cost_usd"] == 0.05

        by_codebase = statistics["by_codebase"]
        assert isinstance(by_codebase, dict)
        assert TEST_CODEBASE_1 in by_codebase

        assert snapshot["modified_at"] > initial_modified_at
