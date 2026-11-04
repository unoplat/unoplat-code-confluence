"""Cross-service checkout admission and publication locks.

Public contract:
* repository_lock_key(owner, repository) and publisher_lock_key(owner, repository,
  run_id) return stable signed PostgreSQL bigint keys, with separate namespaces.
* session_advisory_lock(engine_or_connection, key, timeout=30, poll_interval=.1)
  yields the pinned AsyncConnection. Connections supplied by callers must be idle,
  exclusively owned, and must not be closed inside the guard. Transactions may
  commit inside it; the session lock survives those commits. Cleanup rolls back
  unfinished transactions and unlocks, or invalidates the connection on failure.
* publisher_lock(bind, owner, repository, run_id) serializes a run's publishers.
  Always acquire this BEFORE repository_capture_guard or a repository lock.
* update_repository_run_status(session, envelope, confirm_terminal=None) requires
  the repository lock and a session.begin() transaction. SUBMITTED creates the
  queue row. RUNNING returns False while another parent owns admission; RETRYING
  may only retain an existing admission. Terminal writes release admission.
* validate_checkout_access(session, owner, repository, run_id, original=True)
  requires the repository lock. Original work requires this active admitted run.
  Manual capture requires a completed agent run, no active parent and no later
  non-SUBMITTED mutator row. File/manifest provenance remains the publisher's job.
* repository_capture_guard(bind, owner, repository, run_id, original=True)
  validates access in a short transaction, then yields the connection with only
  the repository session lock held. Copy bytes before exiting; do not do network
  publication inside this guard.

Publisher usage, with a single dedicated connection and the required lock order::

    async with publisher_lock(engine, owner, repository, run_id) as connection:
        async with repository_capture_guard(connection, owner, repository, run_id):
            captured = copy_managed_file_bytes()
        # Repository lock is released; per-run lock is still held.
        await publish_captured_bytes(captured)

confirm_terminal(workflow_id, run_id) must describe the EXACT Temporal execution
and return a terminal JobStatus only when proven. Missing/unknown executions and
unavailable Temporal state must never be interpreted as terminal.
"""

from unoplat_code_confluence_commons.repo_models import (
    Repository,
    RepositoryWorkflowOperation,
    RepositoryWorkflowRun,
)
from unoplat_code_confluence_commons.workflow_envelopes import (
    ParentWorkflowDbActivityEnvelope,
)
from unoplat_code_confluence_commons.workflow_models import JobStatus

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import hashlib
import time

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession

__all__ = [
    "CheckoutAdmissionError",
    "TerminalRunConfirmation",
    "publisher_lock",
    "publisher_lock_key",
    "repository_capture_guard",
    "repository_lock_key",
    "session_advisory_lock",
    "update_repository_run_status",
    "validate_checkout_access",
]

TerminalRunConfirmation = Callable[[str, str], Awaitable[JobStatus | None]]
ACTIVE_STATUSES = (JobStatus.RUNNING.value, JobStatus.RETRYING.value)
TERMINAL_STATUSES = (
    JobStatus.COMPLETED.value,
    JobStatus.FAILED.value,
    JobStatus.ERROR.value,
    JobStatus.CANCELLED.value,
    JobStatus.TIMED_OUT.value,
)
MUTATING_OPERATIONS = tuple(RepositoryWorkflowOperation)
AGENT_OPERATIONS = (
    RepositoryWorkflowOperation.AGENTS_GENERATION,
    RepositoryWorkflowOperation.AGENT_MD_UPDATE,
)


class CheckoutAdmissionError(RuntimeError):
    """Checkout work was requested without a valid admission/provenance guard."""


def _lock_key(namespace: str, *parts: str) -> int:
    digest = hashlib.sha256()
    for part in ("unoplat-checkout-v1", namespace, *parts):
        encoded = part.encode("utf-8")
        digest.update(len(encoded).to_bytes(4, "big"))
        digest.update(encoded)
    return int.from_bytes(digest.digest()[:8], "big", signed=True)


def repository_lock_key(owner: str, repository: str) -> int:
    """Return the common admission/capture lock key used by both services."""
    return _lock_key("repository", owner, repository)


def publisher_lock_key(owner: str, repository: str, run_id: str) -> int:
    """Return the per-run publication key, distinct from the repository key."""
    return _lock_key("publisher", owner, repository, run_id)


async def _release_connection_lock(connection: AsyncConnection, key: int) -> None:
    try:
        await connection.rollback()
        await connection.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": key})
        await connection.commit()
    except BaseException:
        # A pooled session must never retain an advisory lock after failed cleanup.
        await connection.invalidate()
        raise


@asynccontextmanager
async def session_advisory_lock(
    bind: AsyncEngine | AsyncConnection,
    key: int,
    *,
    timeout: float = 30.0,
    poll_interval: float = 0.1,
) -> AsyncIterator[AsyncConnection]:
    """Hold a session lock on a dedicated connection, including across commits."""
    if timeout <= 0 or poll_interval <= 0:
        raise ValueError("Lock timeout and poll interval must be positive")
    owned = isinstance(bind, AsyncEngine)
    connection = await bind.connect() if isinstance(bind, AsyncEngine) else bind
    if connection.in_transaction():
        if owned:
            await connection.close()
        raise ValueError("Advisory lock connection must not have an open transaction")
    attempted = False
    try:
        deadline = time.monotonic() + timeout
        while True:
            # Nonblocking SQL avoids a server-side wait continuing after cancellation.
            # Even if the response is lost, finally unlocks the attempted key.
            attempted = True
            result = await connection.execute(
                text("SELECT pg_try_advisory_lock(:key)"), {"key": key}
            )
            acquired = bool(result.scalar_one())
            await connection.commit()
            if acquired:
                break
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("Repository coordination lock timed out")
            await asyncio.sleep(min(poll_interval, remaining))
        yield connection
    finally:
        try:
            if attempted:
                cleanup = asyncio.create_task(_release_connection_lock(connection, key))
                cancelled_while_releasing = False
                while not cleanup.done():
                    try:
                        await asyncio.shield(cleanup)
                    except asyncio.CancelledError:
                        cancelled_while_releasing = True
                cleanup.result()
                if cancelled_while_releasing:
                    raise asyncio.CancelledError
        finally:
            if owned:
                await connection.close()


@asynccontextmanager
async def publisher_lock(
    bind: AsyncEngine | AsyncConnection, owner: str, repository: str, run_id: str
) -> AsyncIterator[AsyncConnection]:
    """Serialize remote side effects; acquire before any repository guard."""
    async with session_advisory_lock(
        bind, publisher_lock_key(owner, repository, run_id)
    ) as connection:
        yield connection


async def _active_runs(
    session: AsyncSession, owner: str, repository: str
) -> list[RepositoryWorkflowRun]:
    result = await session.execute(
        select(RepositoryWorkflowRun).where(
            RepositoryWorkflowRun.repository_owner_name == owner,
            RepositoryWorkflowRun.repository_name == repository,
            RepositoryWorkflowRun.operation.in_(MUTATING_OPERATIONS),
            RepositoryWorkflowRun.status.in_(ACTIVE_STATUSES),
        )
    )
    return list(result.scalars().all())


async def update_repository_run_status(
    session: AsyncSession,
    envelope: ParentWorkflowDbActivityEnvelope,
    confirm_terminal: TerminalRunConfirmation | None = None,
) -> bool:
    """Write lifecycle state under the repository lock; False means still queued."""
    if not envelope.workflow_id:
        raise CheckoutAdmissionError("Parent workflow ID is required")
    owner, repository = envelope.repository_owner_name, envelope.repository_name
    status = JobStatus(envelope.status)
    now = datetime.now(timezone.utc)
    run = await session.get(
        RepositoryWorkflowRun, (repository, owner, envelope.workflow_run_id)
    )
    if run is None:
        if status in (JobStatus.RUNNING, JobStatus.RETRYING):
            raise CheckoutAdmissionError("Record SUBMITTED before requesting admission")
        if await session.get(Repository, (repository, owner)) is None:
            session.add(
                Repository(
                    repository_name=repository,
                    repository_owner_name=owner,
                    repository_provider=envelope.provider_key,
                )
            )
            await session.flush()
        run = RepositoryWorkflowRun(
            repository_name=repository,
            repository_owner_name=owner,
            repository_workflow_run_id=envelope.workflow_run_id,
            repository_workflow_id=envelope.workflow_id,
            operation=envelope.operation,
            status=JobStatus.SUBMITTED.value,
            started_at=now,
        )
        session.add(run)
    elif run.repository_workflow_id != envelope.workflow_id:
        raise CheckoutAdmissionError("Only the owning parent may change its admission")

    if run.status in TERMINAL_STATUSES:
        # Delayed/retried activities cannot resurrect a released reservation.
        if status.value in ACTIVE_STATUSES:
            raise CheckoutAdmissionError(
                "Terminal run cannot reacquire checkout admission"
            )
        return True
    if status == JobStatus.SUBMITTED:
        return True
    if status == JobStatus.RETRYING and run.status not in ACTIVE_STATUSES:
        raise CheckoutAdmissionError("RETRYING requires an admitted parent")
    if status == JobStatus.RUNNING:
        active = await _active_runs(session, owner, repository)
        for other in active:
            if other.repository_workflow_run_id == envelope.workflow_run_id:
                continue
            confirmed = (
                await confirm_terminal(
                    other.repository_workflow_id, other.repository_workflow_run_id
                )
                if confirm_terminal is not None
                else None
            )
            if confirmed is None or confirmed.value not in TERMINAL_STATUSES:
                return False
            other.status = confirmed.value
            other.completed_at = now
        # Flush stale releases before acquiring the partial-unique-index slot.
        await session.flush()
        if run.status == JobStatus.SUBMITTED.value:
            run.started_at = now
    run.status = status.value
    if status.value in TERMINAL_STATUSES:
        run.completed_at = now
    if envelope.error_report is not None:
        run.error_report = envelope.error_report.model_dump()
    await session.flush()
    return True


async def validate_checkout_access(
    session: AsyncSession,
    owner: str,
    repository: str,
    run_id: str,
    *,
    original: bool = True,
) -> None:
    """Fail closed unless the caller owns admission, or a manual retry is safe."""
    run = await session.get(RepositoryWorkflowRun, (repository, owner, run_id))
    active = await _active_runs(session, owner, repository)
    if original:
        if (
            run is None
            or run.status not in ACTIVE_STATUSES
            or len(active) != 1
            or active[0].repository_workflow_run_id != run_id
        ):
            raise CheckoutAdmissionError(
                "Checkout mutation/capture requires this admitted parent"
            )
        return
    if (
        run is None
        or run.status != JobStatus.COMPLETED.value
        or run.operation not in AGENT_OPERATIONS
        or active
    ):
        raise CheckoutAdmissionError(
            "Manual capture requires a completed agent run and idle checkout"
        )
    # SUBMITTED rows have not touched files. Conservatively reject newer terminal
    # rows too: timestamps alone cannot prove a cancelled run was never admitted.
    newer = await session.execute(
        select(RepositoryWorkflowRun.repository_workflow_run_id)
        .where(
            RepositoryWorkflowRun.repository_owner_name == owner,
            RepositoryWorkflowRun.repository_name == repository,
            RepositoryWorkflowRun.operation.in_(MUTATING_OPERATIONS),
            RepositoryWorkflowRun.repository_workflow_run_id != run_id,
            RepositoryWorkflowRun.status != JobStatus.SUBMITTED.value,
            RepositoryWorkflowRun.started_at >= run.started_at,
        )
        .limit(1)
    )
    if newer.scalar_one_or_none() is not None:
        raise CheckoutAdmissionError(
            "A newer mutator invalidates checkout provenance; regenerate"
        )


@asynccontextmanager
async def repository_capture_guard(
    bind: AsyncEngine | AsyncConnection,
    owner: str,
    repository: str,
    run_id: str,
    *,
    original: bool = True,
) -> AsyncIterator[AsyncConnection]:
    """Validate admission, then keep the checkout locked only through byte copying."""
    async with session_advisory_lock(
        bind, repository_lock_key(owner, repository)
    ) as connection:
        async with AsyncSession(bind=connection, expire_on_commit=False) as session:
            async with session.begin():
                await validate_checkout_access(
                    session, owner, repository, run_id, original=original
                )
        yield connection
