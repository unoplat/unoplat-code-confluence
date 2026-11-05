# Unoplat Code Confluence CLI

The `ucc` CLI starts and manages the local Unoplat Code Confluence app, adds repositories to your tracked list, opens setup pages in your browser, and generates AGENTS.md artifacts after refreshing the latest code.

## Service lifecycle commands

```bash
ucc service run
```

Starts the pinned local app release, installing it on first run. Upgrading the `ucc` package does **not** upgrade the installed app. Later runs keep using the cached release snapshot and report newer app releases with the command to apply them.

In app releases that include `application-migrator`, that one-time Alembic job runs before the backends start. The current production Compose defaults both `ALEMBIC_ATTEST_DRAINED` and `ALEMBIC_ATTEST_DISCARD_LEGACY_ARTIFACTS` to `true`; the CLI inherits your shell and does not set them itself. A new, empty database can bootstrap with plain `ucc service run`.

**Before starting against existing data**, withhold both attestations by setting them to `false` until you have completed the [migration guide's](../unoplat-code-confluence-query-engine/alembic/README.md) backup, schema audit, workflow drain and old-writer retirement. The defaults do not perform those operations, and the contract migration irreversibly discards legacy generated content and raw agent event text. The CLI never audits or stamps an existing database automatically.

```bash
ucc service update
```

Downloads the latest app release's manifest and full Compose snapshot **before** pulling images and applying the stack. This includes new services such as `application-migrator` and their startup dependencies, not just image tags for existing containers. Explicit updates also re-download the pinned assets when no newer version is available, repairing a stale or missing cache without downgrading.

The migrator must be included in a **published app release's Compose asset**. A CLI package release or changes to Compose on `dev`/`main` alone do not deliver it. Publish a new app release with the migration-ready backend and matching migrator images; do not patch an old release with incompatible images. If the latest app release predates the migrator, `service update` cannot add it.

Existing unversioned databases must follow the audited adoption procedure in the [migration guide](../unoplat-code-confluence-query-engine/alembic/README.md). Merely pulling the migrator image does not make an existing schema safe to migrate.

```bash
ucc service stop
```

Runs Docker Compose down for the pinned app stack without deleting volumes.

```bash
ucc service destroy
```

Runs Docker Compose down with volume deletion for the pinned app stack.

## Repository setup

Before adding repositories from the CLI, complete repository-provider token setup:

```bash
ucc setup token-repo-provider
```

Then add a repository with its git remote URL, for example from `git remote get-url origin`:

```bash
ucc repo add https://github.com/unoplat/unoplat-code-confluence.git
```

SSH remotes are also accepted:

```bash
ucc repo add git@github.com:unoplat/unoplat-code-confluence.git
```

For convenience, the top-level alias is also available:

```bash
ucc add-repository https://github.com/unoplat/unoplat-code-confluence.git
```

The CLI sends only the git remote URL to Flow Bridge's lightweight `/repositories` endpoint. Flow Bridge derives the repository owner, repository name, and provider from that URL. Adding a repository does not run ingestion; duplicate adds are idempotent and report that the repository is already added.

## AGENTS.md operations

Generate or update AGENTS.md artifacts for a repository with the repository git remote URL:

```bash
ucc agent-md https://github.com/unoplat/unoplat-code-confluence.git
```

The command also accepts SSH remotes such as `git@github.com:unoplat/unoplat-code-confluence.git`. It idempotently adds the repository if needed, calls Flow Bridge `/refresh-repository` to refresh/ingest the latest code, and the backend triggers AGENTS.md generation after refresh completes. A pull request with the generated artifacts is published automatically when the run completes.

## Setup commands

Check whether repository-provider and model-provider setup are complete:

```bash
ucc setup status
```

This verifies the repository-provider token through Flow Bridge's `/user-details` endpoint and model-provider configuration through Query Engine's `/v1/model-config` endpoint. The output includes whether the model configuration has a stored credential.

`ucc service status` performs the same checks. By default, status auto-starts the **pinned** app and waits for readiness; it is not an app upgrade. Set `UNOPLAT_CODE_CONFLUENCE_AUTO_START=false` to check an already-running deployment without pulling or starting Docker containers. For older Query Engine releases without `/ready`, readiness falls back to the read-only, database-backed `/v1/flags` endpoint only on HTTP 404. A real unhealthy response is not bypassed.

```bash
ucc setup token-repo-provider
```

Ensures the local app is running, then opens the repository token/provider setup page:

```text
http://127.0.0.1:3000/onboarding/github
```

```bash
ucc setup model-provider
```

Ensures the local app is running, then opens the model-provider setup page:

```text
http://127.0.0.1:3000/settings/model-providers
```

The setup-open commands emit JSON containing the setup target, opened URL, and whether Python's standard browser opener reported success. They do not persist provider identifiers, selected model-provider identifiers, or setup completion state.

`ucc repo add` verifies repository-provider setup before adding a repository. `ucc agent-md` verifies both repository-provider and model-provider setup before starting refresh and AGENTS.md generation.

## Frontend URL override

The frontend base URL defaults to `http://127.0.0.1:3000`. Override it with:

```bash
export UNOPLAT_CODE_CONFLUENCE_FRONTEND_URL="http://localhost:5173"
```

The setup commands append their route paths to this base URL.
