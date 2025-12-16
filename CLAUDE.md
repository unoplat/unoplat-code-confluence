# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Unoplat-CodeConfluence is a universal code context engine that extracts, understands, and provides precise code context across repositories. It combines deterministic code grammar (using Tree-sitter) with LLM pipelines to achieve human-like understanding of codebases. The system uses a graph-based architecture to preserve relationships and context at every level.

## Monorepo Structure

This is a monorepo containing three main projects:

1. **unoplat-code-confluence-ingestion** - Backend services for code parsing and ingestion
2. **unoplat-code-confluence-frontend** - React-based web interface 
3. **unoplat-code-confluence-commons** - Shared Python models and utilities

## Common Development Commands

### MCP Tools (Optional)
```bash
# Launch all MCP tools in background
task launch-all-mcp

# Stop all MCP tools
task stop-all-mcp
```

### Docker Compose Commands
```bash
# Local development (builds from source)
docker-compose -f local-docker-compose.yml up -d

# Production (uses published images)
docker-compose -f prod-docker-compose.yml up -d

# Stop and clean up
docker-compose -f local-docker-compose.yml down --volumes
```

## Project-Specific Commands

### Backend (code-confluence-flow-bridge)
```bash
cd unoplat-code-confluence-ingestion/code-confluence-flow-bridge

# Setup and run
task dev              # Start all dependencies and run FastAPI
task start-dependencies  # Just start docker services
task run-dev         # Just run FastAPI (requires services running)

# Testing
task test            # Run tests with coverage
task generate-test-prerequisites  # Generate test data

# Code quality
task lint            # Run ruff linter
task typecheck       # Run mypy
task format          # Format code with ruff
```

### Frontend 
```bash
cd unoplat-code-confluence-frontend

# Development
yarn install         # Install dependencies
yarn dev            # Start dev server at http://localhost:5173

# Build
yarn build          # TypeScript check + production build
yarn preview        # Preview production build

# Code quality
yarn lint           # Run ESLint
```

### Commons
```bash
cd unoplat-code-confluence-commons

# Commands from Taskfile.yml (if exists)
task install        # Install dependencies
task test          # Run tests
```

## Architecture Overview

### System Components

1. **Neo4j Graph Database** - Stores code structure and relationships
   - Port: 7687 (Bolt), 7474 (Browser)
   - Default credentials: neo4j/password

2. **PostgreSQL** - Stores workflow execution data and metadata
   - Port: 5432
   - Default credentials: postgres/postgres

3. **Temporal** - Workflow orchestration engine
   - Port: 7233 (gRPC), 8080 (UI)
   - Manages repository ingestion workflows

4. **Elasticsearch/OpenSearch** - Used by Temporal for visibility
   - Port: 9200

### Code Flow

1. User submits GitHub repository URL via frontend
2. Frontend calls backend API (`/start-ingestion`)
3. Backend creates Temporal workflow to process repository
4. Workflow:
   - Clones repository
   - Detects codebases and package managers
   - Parses code using Tree-sitter (currently Python only)
   - Extracts dependencies and metadata
   - Stores results in Neo4j graph and PostgreSQL

### Key Technologies

- **Backend**: FastAPI, Temporal workflows, Tree-sitter, Neomodel
- **Frontend**: React 19, TanStack Router/Query, Tailwind CSS, shadcn/ui
- **Infrastructure**: Docker, Neo4j, PostgreSQL, Temporal
- **Languages**: Python (backend), TypeScript (frontend)
- **Package Managers**: uv (Python), yarn (JavaScript)

## Development Workflow

### Backend Development

1. Ensure dependencies are running:
   ```bash
   task start-dependencies
   ```

2. Run FastAPI in development mode:
   ```bash
   task run-dev
   ```

3. Submit a test job:
   ```bash
   task run-client
   ```

4. Monitor workflows at http://localhost:8080 (Temporal UI)

### Frontend Development

1. Set environment variables:
   ```bash
   export VITE_UNOPLAT_CODE_CONFLUENCE_API_BASE_URL=http://localhost:8000
   ```

2. Start development server:
   ```bash
   yarn dev
   ```

3. Access at http://localhost:5173

### Testing Workflow

Backend tests require services running:
```bash
task test  # Starts dependencies, runs tests, stops dependencies
```

Frontend tests:
```bash
yarn test  # If test script exists
```

## Important Patterns

### Backend Patterns

- **Envelope Pattern**: All Temporal workflow/activity parameters wrapped in envelope models
- **Factory Pattern**: Parser selection (codebase, package manager, linter)
- **Strategy Pattern**: Different strategies for package managers and linters
- **Async/Await**: Follow asyncio best practices (see asyncio-practices.md)

### Frontend Patterns

- **Data Tables**: Use DiceUI components built on TanStack Table
- **State Management**: Zustand for global state, TanStack Query for server state
- **Routing**: TanStack Router with file-based routing
- **Forms**: React Hook Form with Zod validation

## Environment Variables

### Backend
- `DB_HOST/PORT/USER/PASSWORD/NAME` - PostgreSQL connection
- `NEO4J_HOST/PORT/USERNAME/PASSWORD` - Neo4j connection
- `TEMPORAL_SERVER_ADDRESS` - Temporal server location
- `SCANNER_JAR_PATH` - Path to ArchGuard scanner JAR

### Frontend
- `VITE_UNOPLAT_CODE_CONFLUENCE_API_BASE_URL` - Backend API URL
- `VITE_WORKFLOW_ORCHESTRATOR_URL` - Temporal UI URL
- `VITE_KNOWLEDGE_GRAPH_URL` - Neo4j browser URL

## Current Limitations

- Only Python language parsing is implemented (Java in POC)
- Limited to GitHub repositories
- Requires manual configuration for private repositories
- TypeScript, Go support planned but not implemented

## Debugging Tips

1. Check Temporal UI (http://localhost:8080) for workflow status
2. Neo4j Browser (http://localhost:7474) to explore graph data
3. Backend logs: `docker logs <container-name>`
4. Frontend uses browser DevTools and React DevTools
5. Use trace IDs for debugging distributed operations

## Security Notes

- GitHub tokens are encrypted before storage
- Use environment variables for all sensitive configuration
- Bearer authentication required for token management endpoints
- CORS configured for frontend origin only

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
- Links to detailed guides for task creation, execution, and completion
- MCP tools reference

You MUST read the overview resource to understand the complete workflow. The information is NOT summarized here.

</CRITICAL_INSTRUCTION>

<!-- BACKLOG.MD MCP GUIDELINES END -->
