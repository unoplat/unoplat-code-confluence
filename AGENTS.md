# Unoplat Code Confluence Agent Instructions

## Project Command Requirements

- **TypeScript/JavaScript projects:** Before running any project-related command, inspect the nearest applicable `package.json`. Use its declared `packageManager` and scripts, and run the command from the package directory unless the script explicitly targets a workspace root. Do not guess install, build, test, lint, type-check, format, dev-server, or code-generation commands.
- **Python projects:** Use `uv` for all Python dependency and project commands. Run Python tools through `uv run` (for example, `uv run python`, `uv run pytest`, and `uv run ruff`) rather than invoking `python`, `pip`, `pytest`, or other Python executables directly. Inspect the applicable `pyproject.toml` and project task configuration before selecting command arguments or dependency groups.
