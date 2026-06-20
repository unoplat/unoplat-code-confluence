# Unoplat Code Confluence CLI

The `ucc` CLI starts and manages the local Unoplat Code Confluence app, adds repositories to your tracked list, opens setup pages in your browser, and generates AGENTS.md artifacts after refreshing the latest code.

## Service lifecycle commands

```bash
ucc service run
```

Starts the pinned local app release, installing it on first run.

```bash
ucc service update
```

Updates the pinned app release to the latest available release.

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

```bash
ucc setup token-repo-provider
```

Ensures the local app is running, then opens the repository token/provider setup page:

```text
http://localhost:3000/onboarding/github
```

```bash
ucc setup model-provider
```

Ensures the local app is running, then opens the model-provider setup page:

```text
http://localhost:3000/settings/model-providers
```

The setup-open commands emit JSON containing the setup target, opened URL, and whether Python's standard browser opener reported success. They do not persist provider identifiers, selected model-provider identifiers, or setup completion state.

`ucc repo add` verifies repository-provider setup before adding a repository. `ucc agent-md` verifies both repository-provider and model-provider setup before starting refresh and AGENTS.md generation.

## Frontend URL override

The frontend base URL defaults to `http://localhost:3000`. Override it with:

```bash
export UNOPLAT_CODE_CONFLUENCE_FRONTEND_URL="http://localhost:5173"
```

The setup commands append their route paths to this base URL.
