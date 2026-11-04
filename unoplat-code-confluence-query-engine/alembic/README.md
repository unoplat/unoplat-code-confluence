# Application database migrations

One Alembic history owns the shared application schema: commons tables **and**
query-engine's `ai_model_config`. Temporal's own database is not managed here.
Run commands from `unoplat-code-confluence-query-engine/`.

## Status and policy

- Alembic is installed in the `migrations` uv dependency group (not dev-only).
- `0001_application_baseline` freezes the 19 pre-artifact tables. It is a
  **candidate baseline**, not an assertion about an inspected deployed database.
- `0002_git_artifacts_expand` adds the four metadata/progress columns, checks and
  active-checkout index, copying progress only. The ORM intentionally no longer maps
  the legacy column, so **`alembic check` reports a difference at this revision**.
- `0003_git_artifacts_contract` scrubs historical agent event text and drops
  `agent_md_output`. It is the release target and the only revision where
  `alembic check` is expected to pass. It is **irreversible**.
- **Other application data must be preserved. Historical generated artifacts will
  be discarded, not backfilled into Git. No application legacy-column fallback is
  authorized.** Old runs lacking Git identity must report artifacts unavailable.
- Application callers no longer use `agent_md_output`. Retaining it at the expand
  revision during a staged rollout is not a read-fallback design.
- Neither service runs DDL at startup. Before serving requests or polling Temporal,
  each one verifies the exact release revision (`schema_readiness.py` in commons)
  through a read-only transaction on its own engine. A missing, multiple-head or
  different revision blocks startup. There is no readiness bypass, autostamp or
  autoupgrade. `RELEASE_SCHEMA_REVISION` (`0003_git_artifacts_contract`) is the only
  revision a build accepts by default. `APPLICATION_SCHEMA_STAGED_REVISION` can select
  `0002_git_artifacts_expand` explicitly; the baseline and unknown revisions are refused.
- Backend services support the `public` schema only. `ALEMBIC_SCHEMA` exists for
  migrator reference builds; a service whose connection resolves elsewhere fails.

## Connection and ownership

```sh
uv sync --locked --group migrations
# Set via your secret manager/shell, not checked-in files or command history:
# ALEMBIC_DATABASE_URL = postgresql://<user>:<password>@<host>/<application_db>
# ALEMBIC_SCHEMA = public (default; existing schemas only)
uv run --locked --group migrations alembic history
```

The async environment uses `asyncpg`, `NullPool`, an explicitly supplied URL and
one transaction, with a transaction-local schema search path. It first takes a
transaction-scoped advisory lock, waiting at most 60 seconds, before Alembic reads
or creates its version table, so concurrent jobs run one at a time. Commit, rollback
or a lost connection releases the lock. Later lock waits use a 5-second timeout. It
refuses the `temporal` and `temporal_visibility` databases. No application
startup, implicit `.env` loading, database creation, or fallback connection target
is used. URL-encode reserved characters in passwords. Never point these commands
at Temporal's database. Autogenerate filters unrelated tables rather than proposing
their removal; deletion of an owned table requires explicit review/manual revision.
Only the known unchanged JSONB expression index spelling is normalized for
PostgreSQL reflection; index comparisons are not broadly disabled.

## Required cutover before upgrading

Read `../scripts/migrations/README.md` for the detailed operational evidence.
Pause ingestion/refresh/generation/update starts and admissions, including scheduled
and manual triggers. Drain affected parent **and child** Temporal histories;
reconcile queued/active DB rows against Temporal. Verify a backup, stop old writers,
record the schema/release/drain evidence, and keep starts paused through coordinated
application/worker deployment. SQL cannot prove that Temporal histories are drained.

`-x drained=true` is an **operator attestation**, not an automatic drain. The
revision separately rejects SUBMITTED/RUNNING/RETRYING mutators while holding both
affected tables exclusively and uses a five-second lock timeout. Errors roll back
the version and schema changes. Do not bypass guards or clear rows to pass them.

## Fresh empty database

Have an operator create the application database/schema first, supply its URL, then:

```sh
uv run --locked --group migrations alembic -x drained=true -x discard_legacy_artifacts=true upgrade 0003_git_artifacts_contract
uv run --locked --group migrations alembic current
uv run --locked --group migrations alembic check
```

This replays the baseline, expand and contract in one transaction. It does not
create-and-stamp ORM metadata. A new database has nothing to discard, but direct Alembic commands still require
both acknowledgements. Compose supplies both by default as described below.
Repeated upgrade at the target is a no-op, so later starts need no attestation.
Offline review is available with
`alembic -x drained=true -x discard_legacy_artifacts=true upgrade 0003_git_artifacts_contract --sql`.
Generated SQL carries only the attestations you passed and fails its own gates without
them. Executing it is not a second deployment mechanism. Prefer online Alembic so
versioning and schema share a transaction and operational errors stop the deployment.

## Existing unversioned database — verify before stamping

1. Restore a verified backup into an isolated clone. Inventory its full schema and
   whether either older standalone SQL script was applied. Do **not** infer this
   from the current code or from the README's implementation-time status.
2. In another empty disposable DB, run `alembic upgrade 0001_application_baseline`.
   Compare the clone to this frozen reference: tables/columns, types/nullability,
   server defaults, PK/FK/check definitions, delete actions, indexes (including
   expressions, INCLUDE, operator classes and partial predicates), sequence
   ownership and schema/search path. Schema-only `pg_dump` plus catalog inspection
   can support the audit; never use a data dump in a checked-in report.
3. Only an exact verified baseline may be registered as revision 0001. Record
   audit evidence and run on the intended database during the paused cutover:

   ```sh
   uv run --locked --group migrations alembic -x baseline_verified=true stamp 0001_application_baseline
   uv run --locked --group migrations alembic -x drained=true upgrade 0002_git_artifacts_expand
   uv run --locked --group migrations alembic current
   ```

   Do not expect `alembic check` to pass here. Run it after the contract revision.

   `baseline_verified=true` acknowledges the audit; **it does not perform it**.
   Unacknowledged stamp steps are rejected and rolled back. Alembic stamping only
   records a revision; it neither creates tables nor validates their structure.
4. If already expanded, build a separate expanded reference, verify its exact
   schema **and progress-copy invariants**, then explicitly stamp
   `0002_git_artifacts_expand` with the same audit attestation. Do not replay expand.
   Never stamp `0003_git_artifacts_contract` or `head`: stamping skips the scrub and
   would hide partial migrations or unknown drift. Mismatches need
   a reviewed, data-preserving reconciliation revision; stop rather than guessing.
5. Verify non-document data is preserved, progress is object-valued and historical
   SHA/manifest/error remain NULL. Never invent Git identity from branch heads.

The real deployed baseline has **not** been inspected or stamped as part of setup.
The baseline reflects this repository's pre-artifact model definitions; deployed
schema variants may need explicit reconciliation before adoption.

## Contract revision

`0003_git_artifacts_contract` runs in the same single Alembic transaction as any
earlier revision it follows. Any failure rolls back its schema and data changes and
leaves the version unchanged.

**Gates, in order.** Each one stops the transaction before any row changes:

1. Lock timeout of 5 seconds, and a 30-minute limit per statement.
2. `-x drained=true`: you paused admissions, drained parent and child Temporal
   histories and reconciled rows.
3. `-x discard_legacy_artifacts=true`: you verified a fresh backup, audited a clone,
   confirmed caller removal, retired old workers and ended live old-history recovery.
   Direct Alembic commands require it explicitly; Compose stacks default it to true.
4. `ACCESS EXCLUSIVE` locks on `repository_workflow_run`, `codebase_workflow_run`,
   `repository_agent_md_snapshot` and `repository_agent_event`.
5. No `SUBMITTED`, `RUNNING` or `RETRYING` parent mutator, and no such child row
   **whatever its parent's status**. Old code could mark a parent `ERROR` while its
   siblings still ran, so a parent-only check is not enough. Reconcile these against
   Temporal. Never edit rows just to pass.
6. Exact expected columns and types for the affected tables.

The flags are attestations, and SQL cannot prove a Temporal drain.

**What changes:**

| Data | Result |
| --- | --- |
| `repository_agent_md_snapshot.agent_md_output` | Dropped without CASCADE. An unexpected dependency stops the revision for review |
| `repository_agent_event.tool_args`, `tool_result_content` | NULL |
| `repository_agent_event.message` | Static message for the phase; `Agent event recorded` for an unknown phase |
| `repository_agent_event.tool_name`, `tool_call_id` | Kept if they meet the runtime pattern, otherwise NULL |
| `repository_agent_event.event`, `phase` | Kept if they are bounded identifiers, otherwise `unknown` |

**What does not change:** all rows, keys, event IDs and ordering, event `created_at`,
workflow timestamps, statistics, activity and codebase progress, saved SHA and manifest,
`artifact_publication_error`, PR metadata, `issue_tracking`, repository, credential and
configuration records, and `error_report` on both workflow run tables (full
message, stack trace and metadata are kept so users can submit complete errors).
Nothing else is backfilled, and no Git identity is guessed.

**Recovery.** Before this revision, stay on the expanded schema if any gate is
unresolved. After it commits, there is no in-place recovery: `alembic downgrade` raises,
and recreating an empty column would not restore data. Recover only in an isolated
restored pre-contract backup with its retained compatible build, and never route old
code to the live contracted database. Baseline and expand downgrades likewise refuse
destructive removal of application data or artifact identity.

**Limits.** Text already copied to Temporal history, backups, logs or Electric's shape
log is not reached by this revision. Handle backups under your retention policy.

## Deployment job and release inputs

`application-migrator` is the only schema writer in every Compose stack. It runs once,
with an explicit revision, and both backends wait for it to complete. It uses its own
lightweight image, `Dockerfile.migrator`: `python:3.13-slim` plus only the locked
`migrations` group (Alembic, SQLAlchemy, asyncpg and commons), the Alembic files and
the ORM metadata modules `env.py` imports. It has none of the query engine's runtime
toolchain, so it neither waits for nor ships Chromium, Node, Bun, Poetry or D2. Keep
the `migrations` group a complete closure: the image installs it with
`uv sync --only-group migrations`, without the query-engine dependencies. Its default target is `0003_git_artifacts_contract`, and
`ALEMBIC_TARGET_REVISION` overrides it. All four Compose stacks (production, local,
Tilt and dependencies with flow-bridge) default `ALEMBIC_ATTEST_DRAINED` and
`ALEMBIC_ATTEST_DISCARD_LEGACY_ARTIFACTS` to `true`. An explicit `false` overrides
either default and withholds that attestation. Consequently a normal Compose/Tilt
startup can apply the irreversible contract without additional shell flags.

**Before starting against existing data**, pause admissions, drain/reconcile parent
and child workflows, verify a backup, and retire old writers. The defaults do not
perform those operations. Database row guards still run, but cannot prove Temporal
drainage or backup readiness. Keep both variables explicitly `false` until those
preconditions are met. Direct Alembic commands and `task migrate-dependencies` still
require explicit attestations; `baseline_verified=true` is only ever passed by hand
to an audited stamp. Never stamp `head`, and never target `head` in a release.

Published tags from before this release (flow-bridge 0.87.0, query-engine 0.49.1,
frontend 1.60.0) do not contain these files or checks and are not migration-ready.
`prod-docker-compose.yml` therefore fails until release inputs are supplied:

```sh
# All three must be built from one commit, using the repository root as the backend
# build context, by publish_release_management.yaml or by hand:
docker build -f unoplat-code-confluence-query-engine/Dockerfile -t <registry>/query-engine:<tag> .
docker build -f unoplat-code-confluence-query-engine/Dockerfile.migrator -t <registry>/query-engine-migrator:<tag> .
docker build -f unoplat-code-confluence-ingestion/code-confluence-flow-bridge/Dockerfile -t <registry>/flow-bridge:<tag> .

export QUERY_ENGINE_RELEASE_TAG=<new> FLOW_BRIDGE_RELEASE_TAG=<new> FRONTEND_RELEASE_TAG=<new>
```

An app release must replace these variables with literal versions in its release
commit. `promote_app_release.yaml` rejects anything else, and requires the migrator
to use `unoplat-code-confluence-query-engine-migrator` with the query engine's tag.
Both images are published together from one query-engine release commit.

| Stack | First bootstrap of an empty database |
| --- | --- |
| Production Compose | `docker compose -f prod-docker-compose.yml up -d` (release tags required) |
| Local Compose | `docker compose -f local-docker-compose.yml up` |
| Tilt | `tilt up` |
| Dependencies with flow-bridge | `task start-dependencies` |
| Infrastructure only, service on host | `task start-dependencies-without-flow-bridge`, then `ALEMBIC_ATTEST_DRAINED=true ALEMBIC_ATTEST_DISCARD_LEGACY_ARTIFACTS=true task migrate-dependencies ALEMBIC_TARGET_REVISION=0003_git_artifacts_contract` |

These simple startup examples are for a new empty database. Existing databases follow
the staged order below, explicitly withholding attestations until each gate is met.
Temporal keeps its own databases and is never migrated here.

The `ucc` CLI inherits your shell and uses the Compose defaults, so `ucc service run`
performs the same first bootstrap. The CLI itself never sets the attestations.

These stacks use project-scoped networks. Run a disposable copy with an explicit
`docker compose -p <unique-name>`; never add a fixed network name, which would let
two projects resolve each other's `postgresql` and `temporal`.

### Commons changes and backend images

Backend images embed commons from the component's release tag and are built only when
that component is released. A commons release alone does not rebuild them, and an
existing version tag must never be rebuilt or overwritten.

When a backend needs a commons change, including a new `RELEASE_SCHEMA_REVISION`, raise
`unoplat-code-confluence-commons` in that backend's `pyproject.toml` and refresh its
`uv.lock`, in a releasable commit (`fix:` or `feat:`) under that backend's path. For a
schema release, do this for both backends in the same merge so both release tags contain
the same commons. A mismatched pair fails closed: the backend expecting another revision
stops at its startup check.

## Staged order for an existing database

This requires separate authorization for each database. Run Compose steps with the
release inputs above, from a stopped application stack.

1. **Audit a clone.** Restore a verified backup into an isolated clone and compare it
   with the frozen reference as described above. Stop on any difference.
2. **Attest the baseline.** During the paused cutover, on the intended database:

   ```sh
   docker compose -f prod-docker-compose.yml run --rm --no-deps application-migrator \
     alembic -x baseline_verified=true stamp 0001_application_baseline
   ```

3. **Drain.** Pause admissions and triggers, drain parent and child Temporal histories,
   reconcile rows against Temporal, stop old writers and verify the backup.
4. **Expand.** Attest only after step 3:

   ```sh
   ALEMBIC_ATTEST_DRAINED=true ALEMBIC_ATTEST_DISCARD_LEGACY_ARTIFACTS=false \
   ALEMBIC_TARGET_REVISION=0002_git_artifacts_expand \
     docker compose -f prod-docker-compose.yml up --no-deps application-migrator
   docker compose -f prod-docker-compose.yml run --rm --no-deps application-migrator alembic current
   ```

5. **Metadata-only build.** Start the coordinated services and verify them. A build
   whose release revision is newer than the database must opt in explicitly, for
   every backend replica, to a revision listed in `STAGED_SCHEMA_REVISIONS`. Pin the
   migrator target too. Otherwise its default is the contract and Compose's default
   attestations permit that irreversible step before this separate approval point. Expect `alembic check` to
   report the legacy column at this stage:

   ```sh
   APPLICATION_SCHEMA_STAGED_REVISION=0002_git_artifacts_expand \
   ALEMBIC_TARGET_REVISION=0002_git_artifacts_expand \
   ALEMBIC_ATTEST_DRAINED=false ALEMBIC_ATTEST_DISCARD_LEGACY_ARTIFACTS=false \
     docker compose -f prod-docker-compose.yml up -d
   ```

6. **Contract, at a separate approval point.** Time the revision on the audited clone
   first; each statement is limited to 30 minutes. Stop the backends so nothing writes
   during the cleanup. Pause and drain again, reconcile child rows, take a fresh backup,
   retire old workers, then apply the job with both attestations:

   ```sh
   docker compose -f prod-docker-compose.yml stop code-confluence-flow-bridge unoplat-code-confluence-query-engine
   ALEMBIC_ATTEST_DRAINED=true ALEMBIC_ATTEST_DISCARD_LEGACY_ARTIFACTS=true \
   ALEMBIC_TARGET_REVISION=0003_git_artifacts_contract \
     docker compose -f prod-docker-compose.yml up --no-deps application-migrator
   docker compose -f prod-docker-compose.yml run --rm --no-deps application-migrator alembic current
   docker compose -f prod-docker-compose.yml run --rm --no-deps application-migrator alembic check
   ```

   `alembic check` must pass here. Then start services with
   `APPLICATION_SCHEMA_STAGED_REVISION` and both attestations unset.
7. **Electric.** The contract changes the snapshot table and rewrites event
   rows, and Electric's existing shape logs can still hold pre-scrub text. These stacks
   give Electric no named volume, so recreating the container discards its logs. If your
   deployment persists Electric storage, clear that storage as well. Recreate it before
   the backends and frontend serve users, and confirm browsers resubscribe with new
   shape handles before reopening admissions:

   ```sh
   docker compose -f prod-docker-compose.yml up -d --force-recreate --no-deps electric
   ```

## Validation and future revisions

```sh
# Application fixtures own a per-run Compose project and migrate its new database.
# Stop any local stack first: fixed host ports make the run fail rather than share it.
# Starts/removes only its own disposable PostgreSQL 17 container, no existing DBs:
uv run --locked --group test --group migrations pytest tests_migrations -v
uv run --locked --group dev ruff check alembic tests_migrations src/unoplat_code_confluence_query_engine/db/postgres/migration_metadata.py
# Against an explicitly supplied disposable migrated DB:
uv run --locked --group migrations alembic check
uv run --locked --group migrations alembic revision --autogenerate -m "describe the schema change"
```

Review generated candidates, particularly CHECK constraints, data migrations and
PostgreSQL expression/partial indexes. Revisions freeze schema definitions and must
not import changing ORM classes. Tests outside the main `tests/` tree intentionally
avoid its application/database startup fixtures.

Official references:
- https://alembic.sqlalchemy.org/en/latest/front.html#installation
- https://alembic.sqlalchemy.org/en/latest/cookbook.html#using-asyncio-with-alembic
- https://alembic.sqlalchemy.org/en/latest/autogenerate.html
- https://alembic.sqlalchemy.org/en/latest/api/commands.html#alembic.command.stamp
- https://alembic.sqlalchemy.org/en/latest/api/runtime.html#alembic.runtime.environment.EnvironmentContext.configure.params.on_version_apply
