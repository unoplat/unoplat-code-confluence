# Agent Guidelines

## Commands
- **Test all**: `task test` (starts deps, runs tests with coverage, stops deps)
- **Test single**: `uv run --group test pytest tests/path/to/test_file.py::test_function_name -v`
- **Lint**: `task lint` (check) or `task lint-fix` (auto-fix)
- **Format**: `task format` (ruff formatter)
- **Type check**: `task typecheck` (basedpyright strict mode)
- **Dev server**: `task run-query-engine-backend-dev` (port 8001)

## Code Style
- **Imports**: Absolute only (no relative), use ruff for ordering (`task lint-fix`)
- **Types**: Always precise types - never use `Any`, use `typing` module generics
- **Functions**: No nested functions - keep flat structure at module level
- **Pydantic**: Use `model_dump_json()` for JSON serialization (not `json.dumps`)
- **Docstrings**: Google format, omit `ctx` param (dependency injection magic)
- **Sessions**: Always `session.begin()` but yield `AsyncSession` for auto-transactions
- **Error handling**: Use structured exceptions, add proper context/trace IDs
- **Tool verification**: Use context7 tool to verify API methods before implementation
- **Python commands**: Always use `uv run --group <group>` (e.g., `--group test` for tests)


## Caveats
1. When a shell command fails with "failed in sandbox", use the permission request tool (with 'with_escalated_permissions") to ask the user for approval before
retrying.
2. always when want to run python script open shell with 'uv run python'.
