# Instructions

you should always raise for approval while in read mode that way you will be allowed to run all commands post approval.

<!-- BACKLOG.MD MCP GUIDELINES START -->

<CRITICAL_INSTRUCTION>

## BACKLOG WORKFLOW INSTRUCTIONS

This project uses Backlog.md MCP for all task and project management activities.

**CRITICAL GUIDANCE**

- If your client supports MCP resources, read `backlog://workflow/overview` to understand when and how to use Backlog for this project.
- If your client only supports tools or the above request fails, call `backlog.get_workflow_overview()` tool to load the tool-oriented overview (it lists the matching guide tools).

- **First time working here?** Read the overview resource IMMEDIATELY to learn the workflow
- **Already familiar?** You should have the overview cached ("## Backlog.md Overview (MCP)")
- **When to read it**: BEFORE creating tasks, or when you're unsure whether to track work

These guides cover:
- Decision framework for when to create tasks
- Search-first workflow to avoid duplicates
- Links to detailed guides for task creation, execution, and finalization
- MCP tools reference

You MUST read the overview resource to understand the complete workflow. The information is NOT summarized here.

</CRITICAL_INSTRUCTION>

<!-- BACKLOG.MD MCP GUIDELINES END -->

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->
<CRITICAL_INSTRUCTION>

> Generated from branch `add-firebase-discovery` at commit `37583f31bdfacc9cc83eef0b71ac3a555889238d` (2026-04-02). Content may become stale as new commits land.

</CRITICAL_INSTRUCTION>

## Engineering Workflow
- **Launch all MCP tools**: `task launch-all-mcp` (config: `Taskfile.yml`) — starts browser-tools and think-mcp servers in background.
- **Launch browser tools (foreground)**: `task launch-browser-tools` (config: `Taskfile.yml`).
- **Launch browser tools (background)**: `task launch-browser-tools-bg` (config: `Taskfile.yml`).
- **Stop browser tools**: `task stop-browser-tools` (config: `Taskfile.yml`).
- **Launch think MCP (foreground)**: `task launch-think-mcp` (config: `Taskfile.yml`).
- **Launch think MCP (background)**: `task launch-think-mcp-bg` (config: `Taskfile.yml`).
- **Stop think MCP**: `task stop-think-mcp` (config: `Taskfile.yml`).
- **Stop all MCP tools**: `task stop-all-mcp` (config: `Taskfile.yml`).
- **Install act**: `task install-act` (config: `Taskfile.yml`) — installs act for local GitHub Actions testing.
- **List CI jobs**: `task act-list-jobs` (config: `Taskfile.yml`).
- **Run CI tests locally**: `task act-test-uv-projects` (config: `Taskfile.yml`) — requires Docker + `GITHUB_PAT_TOKEN`.
- **Dry-run CI tests**: `task act-test-uv-projects-dry` (config: `Taskfile.yml`).
- **Verbose CI tests**: `task act-test-uv-projects-verbose` (config: `Taskfile.yml`).
- **Setup CI env file**: `task act-setup-env` (config: `Taskfile.yml`) — creates `.env` template for act.

## Dependency Guide

## Business Logic Domain

## App Interfaces

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->
