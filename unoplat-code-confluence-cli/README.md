# Unoplat Code Confluence CLI

The `unoplat` CLI starts and manages the local Unoplat Code Confluence app, ingests repositories, opens setup pages in your browser, and generates AGENTS.md artifacts for ingested repositories.

## Service lifecycle commands

```bash
unoplat service run
```

Starts the pinned local app release, installing it on first run.

```bash
unoplat service update
```

Updates the pinned app release to the latest available release.

```bash
unoplat service stop
```

Runs Docker Compose down for the pinned app stack without deleting volumes.

```bash
unoplat service destroy
```

Runs Docker Compose down with volume deletion for the pinned app stack.

## Repository ingestion

Before ingesting repositories from the CLI, complete repository-provider token setup:

```bash
unoplat setup token-repo-provider
```

Then start ingestion with the repository git remote URL, for example from `git remote get-url origin`:

```bash
unoplat ingest https://github.com/unoplat/unoplat-code-confluence.git
```

SSH remotes are also accepted:

```bash
unoplat ingest git@github.com:unoplat/unoplat-code-confluence.git
```

The CLI sends only the git remote URL to Flow Bridge's `/start-ingestion` endpoint. Flow Bridge derives the repository owner, repository name, and provider from that URL, then returns JSON containing the Temporal workflow/run identifiers.

## AGENTS.md operations

Generate or update AGENTS.md artifacts for an ingested repository with the repository git remote URL:

```bash
unoplat agent-md generate-update https://github.com/unoplat/unoplat-code-confluence.git
```

After an AGENTS.md operation completes, create a pull request for the latest completed run:

```bash
unoplat agent-md pr https://github.com/unoplat/unoplat-code-confluence.git
```

Both commands also accept SSH remotes such as `git@github.com:unoplat/unoplat-code-confluence.git`. The `pr` command always targets the most recent completed AGENTS.md run for the repository.

## Setup commands

```bash
unoplat setup token-repo-provider
```

Ensures the local app is running, then opens the repository token/provider setup page:

```text
http://localhost:3000/onboarding/github
```

```bash
unoplat setup model-provider
```

Ensures the local app is running, then opens the model-provider setup page:

```text
http://localhost:3000/settings/model-providers
```

Both commands emit JSON containing the setup target, opened URL, and whether Python's standard browser opener reported success. They do not persist provider identifiers, selected model-provider identifiers, or setup completion state.

## Frontend URL override

The frontend base URL defaults to `http://localhost:3000`. Override it with:

```bash
export UNOPLAT_CODE_CONFLUENCE_FRONTEND_URL="http://localhost:5173"
```

The setup commands append their route paths to this base URL.
