"""
Integration tests for RepositoryAgentSnapshotWriter.

Tests verify that the RepositoryAgentSnapshotWriter correctly manipulates
the repository_agent_md_snapshot table under real Postgres conditions.
"""

from decimal import Decimal
from typing import Dict, Optional

import pytest
from sqlalchemy import text

from unoplat_code_confluence_commons.repo_models import RepoAgentSnapshotStatus
from unoplat_code_confluence_query_engine.db.repository_agent_snapshot_service import (
    RepositoryAgentSnapshotWriter,
)
from unoplat_code_confluence_query_engine.models.agent_events import (
    AgentEventPayload,
    CodebaseEventDelta,
    RepositoryAgentEventDelta,
)
from tests.utils.sync_db_utils import get_sync_postgres_session, cleanup_postgresql_sync


# Test constants
TEST_OWNER = "test-owner"
TEST_REPO = "test-repo"
TEST_WORKFLOW_RUN_ID = "test-workflow-run-123"
TEST_CODEBASE_1 = "backend"
TEST_CODEBASE_2 = "frontend"


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
        {"owner": owner, "name": name}
    )
    sync_session.commit()


def get_snapshot_data(sync_session, owner: str, name: str) -> Optional[Dict]:
    """Fetch complete row from repository_agent_md_snapshot."""
    result = sync_session.execute(
        text("""
            SELECT events, agent_md_output, statistics, status, created_at, modified_at
            FROM repository_agent_md_snapshot
            WHERE repository_owner_name = :owner AND repository_name = :name
        """),
        {"owner": owner, "name": name}
    )
    row = result.fetchone()
    if row:
        return {
            "events": row[0],
            "agent_md_output": row[1],
            "statistics": row[2],
            "status": row[3],
            "created_at": row[4],
            "modified_at": row[5]
        }
    return None


def count_snapshot_rows(sync_session, owner: str, name: str) -> int:
    """Count rows in repository_agent_md_snapshot for given repo."""
    result = sync_session.execute(
        text("""
            SELECT COUNT(*) FROM repository_agent_md_snapshot
            WHERE repository_owner_name = :owner AND repository_name = :name
        """),
        {"owner": owner, "name": name}
    )
    return result.scalar()


# ──────────────────────────────────────────────────────────────────────────────
# FIXTURES
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def writer(db_connections):
    """Create RepositoryAgentSnapshotWriter instance for testing."""
    return RepositoryAgentSnapshotWriter(TEST_OWNER, TEST_REPO)


@pytest.fixture
def seeded_db(service_ports, test_database_tables):
    """Provide database with minimal seed data."""
    with get_sync_postgres_session(service_ports["postgresql"]) as session:
        cleanup_postgresql_sync(session)
        create_test_repository(session, TEST_OWNER, TEST_REPO)

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
        assert count_snapshot_rows(session, TEST_OWNER, TEST_REPO) == 0

    # Execute begin_run
    await writer.begin_run(
        repository_qualified_name=f"{TEST_OWNER}/{TEST_REPO}",
        repository_workflow_run_id=TEST_WORKFLOW_RUN_ID,
        codebase_names=[TEST_CODEBASE_1, TEST_CODEBASE_2],
    )

    # Verify snapshot row created with correct values
    with get_sync_postgres_session(seeded_db["postgresql"]) as session:
        assert count_snapshot_rows(session, TEST_OWNER, TEST_REPO) == 1

        snapshot = get_snapshot_data(session, TEST_OWNER, TEST_REPO)
        assert snapshot is not None

        # Check status
        assert snapshot["status"] == RepoAgentSnapshotStatus.RUNNING.value

        # Check agent_md_output is empty dict
        assert snapshot["agent_md_output"] == {}

        # Check events structure
        events = snapshot["events"]
        assert events["repository_name"] == f"{TEST_OWNER}/{TEST_REPO}"
        assert events["repository_workflow_run_id"] == TEST_WORKFLOW_RUN_ID
        assert events["overall_progress"] == 0.0
        assert len(events["codebases"]) == 2

        # Check timestamps are set
        assert snapshot["created_at"] is not None
        assert snapshot["modified_at"] is not None


@pytest.mark.integration
@pytest.mark.asyncio(loop_scope="session")
async def test_begin_run_upserts_existing_row(seeded_db, writer):
    """Test that begin_run updates existing row instead of creating duplicate."""
    # First begin_run
    await writer.begin_run(
        repository_qualified_name=f"{TEST_OWNER}/{TEST_REPO}",
        repository_workflow_run_id=TEST_WORKFLOW_RUN_ID,
        codebase_names=[TEST_CODEBASE_1],
    )

    # Get initial timestamps
    with get_sync_postgres_session(seeded_db["postgresql"]) as session:
        initial_snapshot = get_snapshot_data(session, TEST_OWNER, TEST_REPO)
        initial_created_at = initial_snapshot["created_at"]

    # Second begin_run with different data
    await writer.begin_run(
        repository_qualified_name=f"{TEST_OWNER}/{TEST_REPO}",
        repository_workflow_run_id="different-run-id",
        codebase_names=[TEST_CODEBASE_1, TEST_CODEBASE_2],
    )

    # Verify still only one row, but updated
    with get_sync_postgres_session(seeded_db["postgresql"]) as session:
        assert count_snapshot_rows(session, TEST_OWNER, TEST_REPO) == 1

        snapshot = get_snapshot_data(session, TEST_OWNER, TEST_REPO)

        # Check updated values
        assert snapshot["events"]["repository_workflow_run_id"] == "different-run-id"
        assert len(snapshot["events"]["codebases"]) == 2

        # created_at should remain the same, modified_at should change
        assert snapshot["created_at"] == initial_created_at
        assert snapshot["modified_at"] > initial_created_at


@pytest.mark.integration
@pytest.mark.asyncio(loop_scope="session")
async def test_append_event_updates_events_json_and_timestamp(seeded_db, writer):
    """Test that append_event correctly updates events JSON and modified_at timestamp."""
    # Setup: initialize snapshot
    await writer.begin_run(
        repository_qualified_name=f"{TEST_OWNER}/{TEST_REPO}",
        repository_workflow_run_id=TEST_WORKFLOW_RUN_ID,
        codebase_names=[TEST_CODEBASE_1],
    )

    # Get initial state
    with get_sync_postgres_session(seeded_db["postgresql"]) as session:
        initial_snapshot = get_snapshot_data(session, TEST_OWNER, TEST_REPO)
        initial_modified_at = initial_snapshot["modified_at"]

    # Append an event
    event_payload = AgentEventPayload(
        id="event-1",
        event="processing_step",
        phase="result",
        message="Step completed"
    )

    codebase_delta = CodebaseEventDelta(
        codebase_name=TEST_CODEBASE_1,
        progress=Decimal("50.0"),
        new_event=event_payload
    )

    repo_delta = RepositoryAgentEventDelta(
        repository_name=f"{TEST_OWNER}/{TEST_REPO}",
        overall_progress=Decimal("50.0"),
        codebase_delta=codebase_delta
    )

    await writer.append_event(repo_delta)

    # Verify updates
    with get_sync_postgres_session(seeded_db["postgresql"]) as session:
        snapshot = get_snapshot_data(session, TEST_OWNER, TEST_REPO)

        # Check events updated
        events = snapshot["events"]
        assert events["overall_progress"] == 50.0

        codebase = events["codebases"][0]
        assert codebase["progress"] == 50.0
        assert len(codebase["events"]) == 1
        assert codebase["events"][0]["id"] == "event-1"

        # Check timestamp updated
        assert snapshot["modified_at"] > initial_modified_at

        # Status should still be RUNNING
        assert snapshot["status"] == RepoAgentSnapshotStatus.RUNNING.value


@pytest.mark.integration
@pytest.mark.asyncio(loop_scope="session")
async def test_complete_run_updates_status_and_output(seeded_db, writer):
    """Test that complete_run updates status to COMPLETED and sets agent_md_output and statistics."""
    # Setup: initialize snapshot
    await writer.begin_run(
        repository_qualified_name=f"{TEST_OWNER}/{TEST_REPO}",
        repository_workflow_run_id=TEST_WORKFLOW_RUN_ID,
        codebase_names=[TEST_CODEBASE_1],
    )

    # Get initial modified_at
    with get_sync_postgres_session(seeded_db["postgresql"]) as session:
        initial_snapshot = get_snapshot_data(session, TEST_OWNER, TEST_REPO)
        initial_modified_at = initial_snapshot["modified_at"]

    # Complete the run with statistics
    final_payload = {
        "agents_md": {
            "architecture": "Clean architecture pattern",
            "security": "OAuth2 authentication"
        },
        "summary": "Analysis completed"
    }

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
                "estimated_cost_usd": 0.05
            }
        }
    }

    await writer.complete_run(final_payload=final_payload, statistics_payload=statistics_payload)

    # Verify updates
    with get_sync_postgres_session(seeded_db["postgresql"]) as session:
        snapshot = get_snapshot_data(session, TEST_OWNER, TEST_REPO)

        # Check status updated
        assert snapshot["status"] == RepoAgentSnapshotStatus.COMPLETED.value

        # Check agent_md_output updated
        assert snapshot["agent_md_output"] == final_payload

        # Check statistics updated
        assert snapshot["statistics"] is not None
        assert snapshot["statistics"]["total_requests"] == 5
        assert snapshot["statistics"]["total_tool_calls"] == 12
        assert snapshot["statistics"]["total_tokens"] == 2300
        assert snapshot["statistics"]["total_estimated_cost_usd"] == 0.05
        assert TEST_CODEBASE_1 in snapshot["statistics"]["by_codebase"]

        # Check timestamp updated
        assert snapshot["modified_at"] > initial_modified_at


@pytest.mark.integration
@pytest.mark.asyncio(loop_scope="session")
async def test_fail_run_updates_status_and_output(seeded_db, writer):
    """Test that fail_run updates status to ERROR and sets agent_md_output."""
    # Setup: initialize snapshot
    await writer.begin_run(
        repository_qualified_name=f"{TEST_OWNER}/{TEST_REPO}",
        repository_workflow_run_id=TEST_WORKFLOW_RUN_ID,
        codebase_names=[TEST_CODEBASE_1],
    )

    # Fail the run
    error_payload = {
        "error": "TimeoutError",
        "message": "Processing timed out",
        "details": {"step": "code_analysis"}
    }

    await writer.fail_run(error_payload=error_payload)

    # Verify updates
    with get_sync_postgres_session(seeded_db["postgresql"]) as session:
        snapshot = get_snapshot_data(session, TEST_OWNER, TEST_REPO)

        # Check status updated
        assert snapshot["status"] == RepoAgentSnapshotStatus.ERROR.value

        # Check agent_md_output updated
        assert snapshot["agent_md_output"] == error_payload


@pytest.mark.integration
@pytest.mark.asyncio(loop_scope="session")
async def test_fail_run_with_no_payload_sets_empty_dict(seeded_db, writer):
    """Test that fail_run with no error_payload sets empty dict."""
    # Setup: initialize snapshot
    await writer.begin_run(
        repository_qualified_name=f"{TEST_OWNER}/{TEST_REPO}",
        repository_workflow_run_id=TEST_WORKFLOW_RUN_ID,
        codebase_names=[TEST_CODEBASE_1],
    )

    # Fail the run without payload
    await writer.fail_run()

    # Verify updates
    with get_sync_postgres_session(seeded_db["postgresql"]) as session:
        snapshot = get_snapshot_data(session, TEST_OWNER, TEST_REPO)

        # Check status updated
        assert snapshot["status"] == RepoAgentSnapshotStatus.ERROR.value

        # Check agent_md_output is empty dict
        assert snapshot["agent_md_output"] == {}


