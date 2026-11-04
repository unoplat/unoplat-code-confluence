# Git artifact schema cutover

> **Superseded execution path:** use the versioned Alembic environment in
> `../../alembic/README.md`. `001_git_artifacts_expand.sql` is retained as a historical
> specification, not a second way to deploy migrations. Do not execute it alongside
> Alembic. The expand operations live in revision `0002_git_artifacts_expand`.
>
> **`002_git_artifacts_contract.sql` is retired.** It no longer contains destructive
> statements and only raises an error. The contract is revision
> `0003_git_artifacts_contract`. The operator has selected preserving other application
> data and discarding old artifact contents, with no legacy application read fallback.
> The detailed pause/drain/backup requirements below still apply.

Services no longer run `create_all`; they only verify the Alembic revision at startup.

`001_git_artifacts_expand.sql` adds artifact metadata, copies repository activity progress only, gives the legacy document column an empty-object server default, and adds the active checkout reservation index. Historical SHA and manifest columns remain SQL NULL. No branch-head guesses or document backfill are allowed.

The ORM no longer maps `agent_md_output`, so that column exists only between the expand and contract revisions.

## Preconditions for expand

1. Pause new ingestion, refresh, generation, and update starts, including scheduled/manual triggers and queued admission. Keep starts paused through deployment and routing cutover.
2. Drain all affected Temporal parent and child histories. Confirm no old open histories remain. A different worker build ID does not make `AUTO_UPGRADE` histories compatible.
3. Reconcile stale `SUBMITTED`, `RUNNING`, and `RETRYING` parent rows against terminal Temporal state. Never clear reservations just to pass this migration. Resolve queued runs by draining or cancelling them through the supported workflow path.
4. Take and verify a database backup. Record the target database, schema/search path, release revision, and drain evidence in the deployment record.
5. Stop old writers for cutover. Keep any retained old workers non-current and without production traffic. Both services must deploy the same updated commons schema and checkout coordination implementation before starts resume.

The drain acknowledgement is an operator attestation. SQL cannot inspect Temporal histories, worker routing, or deployed consumers. The scripts also reject queued/active checkout-mutator rows while holding exclusive locks on both affected tables. That migration guard is intentionally stricter than the reservation index, which permits any number of `SUBMITTED` queued runs after deployment.

## Apply expand once

Run from the query-engine package directory. Use the configured PostgreSQL schema/search path explicitly. The example uses `public`; replace it if deployment uses another schema. Keep credentials in the usual connection configuration, not in a checked-in command.

```sh
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 \
  -c "SET search_path TO public; SET unoplat.git_artifacts_drained = 'true';" \
  -f scripts/migrations/001_git_artifacts_expand.sql
```

Each script owns its transaction and uses a five-second lock timeout. Do not wrap it in another transaction. On any error, stop and investigate; closing the psql connection rolls back the failed transaction. Do not remove the drain checks, use `CREATE INDEX CONCURRENTLY`, or add `IF NOT EXISTS` to hide a partially applied or mismatched schema. A successful application is not rerunnable. Record completion once.

Deploy the updated commons, API, workers, and frontend against the expanded schema. Explicitly promote the new immutable code-version worker build only after health checks. Startup of a recovery/non-current worker must not promote it. Then resume starts and verify the Git-backed flows and metadata-only consumers. A failed PR after SHA persistence must not remove artifact availability.

## Verify expand

Before resuming starts, inspect the resolved tables and constraints:

```sql
SELECT artifact_commit_sha, artifact_manifest, repository_activity_progress,
       artifact_publication_error
FROM repository_agent_md_snapshot;

SELECT conname, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'repository_agent_md_snapshot'::regclass;

SELECT indexdef FROM pg_indexes
WHERE schemaname = current_schema()
  AND indexname = 'uq_repository_active_checkout_mutator';
```

Confirm legacy rows have null SHA/manifest/error and object-valued progress. Compare progress with the old nested object where present, or `{}` for absent/non-object values. Statistics, run keys, timestamps, events, and PR metadata must remain unchanged. Confirm metadata-only inserts can omit the legacy column. The unique index must cover only `RUNNING`/`RETRYING` ingestion, generation, and update parents, not `SUBMITTED` or codebase child rows.

Database checks enforce field shape, not immutability or per-entry manifest validation. Services must validate typed entries and use locked first-write-wins updates for manifest and SHA.

## Contract gate

Contract requires a separate operational approval:

- Metadata-only consumers and Git-backed reads have been verified on the expanded schema.
- Old workers are retired. No old histories may reset/recover against the live database. This recovery cutoff is an explicit operational decision.
- Retain the old build and a verified pre-contract backup for isolated recovery.
- Pause starts and drain/reconcile again as above, including queued mutators and child workflows, even where the parent is already terminal. Take a fresh pre-contract backup.

Only after those gates pass, follow the staged order in `../../alembic/README.md`: apply `0003_git_artifacts_contract` with `-x drained=true -x discard_legacy_artifacts=true`. Verify the legacy column is absent and all metadata and event/progress rows survive before resuming starts. Do not use `CASCADE`; unexpected dependencies must block contract for review.

## Recovery boundary

Before contract, retain the expanded compatible schema if any gate is unresolved. An old binary alone is not a rollback strategy. Never run old ingestion workers against the new production checkout coordination or silently route incompatible histories to the new build.

After contract there is no in-place document rollback or backfill. Old-history recovery requires an isolated restored pre-contract database and isolated checkout, the retained old build, and explicit routing to its non-current version. Never route old SQL to the live contracted database. Preserve the live database's new artifact metadata separately from that recovery environment.
