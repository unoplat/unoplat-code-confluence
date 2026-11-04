-- One-time expand migration. See README.md for the mandatory drain procedure.
-- No historical artifact identity is inferred from documents or branch heads.
BEGIN;
SET LOCAL lock_timeout = '5s';

DO $$
BEGIN
  IF current_setting('unoplat.git_artifacts_drained', true) IS DISTINCT FROM 'true' THEN
    RAISE EXCEPTION 'Pause starts, drain affected Temporal histories, reconcile DB rows, then acknowledge unoplat.git_artifacts_drained=true';
  END IF;
END;
$$;

-- Block concurrent admissions/writers while checking and changing the schema.
-- Operators must keep starts paused beyond this transaction through cutover.
LOCK TABLE repository_workflow_run, repository_agent_md_snapshot
  IN ACCESS EXCLUSIVE MODE;

DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM repository_workflow_run
    WHERE status IN ('SUBMITTED', 'RUNNING', 'RETRYING')
      AND operation IN ('INGESTION', 'AGENTS_GENERATION', 'AGENT_MD_UPDATE')
  ) THEN
    RAISE EXCEPTION 'Drain queued/active checkout mutators and reconcile stale rows against Temporal before expand';
  END IF;
END;
$$;

ALTER TABLE repository_agent_md_snapshot
  ADD COLUMN artifact_commit_sha VARCHAR(40) NULL,
  ADD COLUMN artifact_manifest JSONB NULL,
  ADD COLUMN repository_activity_progress JSONB NOT NULL DEFAULT '{}'::jsonb,
  ADD COLUMN artifact_publication_error JSONB NULL;

-- Copy progress only. Keep legacy documents in their original column until contract.
UPDATE repository_agent_md_snapshot
SET repository_activity_progress = CASE
  WHEN jsonb_typeof(agent_md_output -> 'repository_activity_progress') = 'object'
    THEN agent_md_output -> 'repository_activity_progress'
  ELSE '{}'::jsonb
END;

ALTER TABLE repository_agent_md_snapshot
  ALTER COLUMN agent_md_output SET DEFAULT '{}'::jsonb,
  ADD CONSTRAINT ck_artifact_commit_sha_format CHECK (
    artifact_commit_sha IS NULL OR artifact_commit_sha ~ '^[0-9a-f]{40}$'
  ),
  ADD CONSTRAINT ck_artifact_manifest_array CHECK (
    artifact_manifest IS NULL OR jsonb_typeof(artifact_manifest) = 'array'
  ),
  ADD CONSTRAINT ck_artifact_sha_has_manifest CHECK (
    artifact_commit_sha IS NULL
    OR (artifact_manifest IS NOT NULL AND artifact_manifest <> '[]'::jsonb)
  ),
  ADD CONSTRAINT ck_repository_activity_progress_object CHECK (
    jsonb_typeof(repository_activity_progress) = 'object'
  ),
  ADD CONSTRAINT ck_artifact_publication_error_object CHECK (
    artifact_publication_error IS NULL
    OR jsonb_typeof(artifact_publication_error) = 'object'
  );

-- SUBMITTED is a queue, not a checkout reservation. Child workflows are unaffected.
CREATE UNIQUE INDEX uq_repository_active_checkout_mutator
ON repository_workflow_run (repository_owner_name, repository_name)
WHERE status IN ('RUNNING', 'RETRYING')
  AND operation IN ('INGESTION', 'AGENTS_GENERATION', 'AGENT_MD_UPDATE');

COMMIT;
