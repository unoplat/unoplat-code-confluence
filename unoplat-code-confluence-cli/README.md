# Unoplat Code Confluence CLI

The `unoplat` CLI starts the local Unoplat Code Confluence app and opens setup pages in your browser.

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
