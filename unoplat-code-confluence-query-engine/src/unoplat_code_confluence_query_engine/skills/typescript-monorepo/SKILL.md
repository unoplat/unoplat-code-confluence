---
name: typescript-monorepo
description: >-
  Guidance for TypeScript monorepos with mixed package managers.
  Use when codebase has inherited package manager and a workspace root.
---

## TypeScript Monorepo Workflow Guidance

### Install Commands
- Workspace-scoped install runs from workspace root, not leaf
- bun: `bun install` at workspace root
- pnpm: `pnpm install` at workspace root
- npm: `npm ci` at workspace root
- working_directory = workspace root (repo-relative)

### Workspace Root Discovery
- If `workspace_root` is present, use it as the direct hint for workspace-owned commands
- If `workspace_root` is missing but provenance is inherited, walk upward from `codebase_path` to find the nearest owning workspace root
- Inspect parent directories one level at a time with absolute paths using `get_directory_tree` and `read_file_content`
- Stop when you find the nearest workspace-owned signals such as `pnpm-workspace.yaml`, a root `package.json` with `workspaces`, a lockfile, `turbo.json`, or `nx.json`
- Do not assume the leaf owns install/build commands just because the exact workspace root was not precomputed

### Build Commands
- Turborepo: `turbo run build` or `bun run build` at workspace root
- Individual: `bun run build --filter <package>` from workspace root
- Check turbo.json or nx.json for build pipeline configuration
- working_directory = workspace root

### Test/Lint/TypeCheck Commands
- Usually leaf-specific: run from codebase root (omit working_directory)
- Some monorepos configure workspace-level lint/test via turbo.json/nx.json
- Inspect the leaf's package.json scripts section for available commands

### Working Directory Rules
- working_directory = workspace root for install/build commands
- working_directory = omit (None) for leaf-local test/lint/type_check
- working_directory = "." when command must run from repository root
- If both workspace-level and leaf-level commands exist for same stage, emit both with distinct working_directory

### Upward Discovery Example
- Given `codebase_path = /opt/unoplat/repositories/acme/infra/services/apps/api` and inherited provenance with no `workspace_root`
- Inspect `/opt/unoplat/repositories/acme/infra/services/apps/api`, then `/opt/unoplat/repositories/acme/infra/services/apps`, then `/opt/unoplat/repositories/acme/infra/services`
- If `/opt/unoplat/repositories/acme/infra/services/pnpm-workspace.yaml` exists, use repo-relative `infra/services` as the workspace root
- Then emit workspace-owned commands like install/build with `working_directory = "infra/services"`

### Package Manager Inheritance
- Leaf inherits manager from nearest workspace aggregator
- Commands use the inherited manager's CLI (bun, pnpm, npm, yarn)
- Lock files live at workspace root, not leaf
- If leaf has its own local manager, provenance=local and no workspace root
