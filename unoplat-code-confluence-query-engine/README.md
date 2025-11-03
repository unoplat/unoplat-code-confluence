# Code Confluence Query Engine

## What This Does

This tool analyzes any codebase using AI agents and generates comprehensive documentation in markdown format. The AI agents examine your repository's structure, business logic, frameworks, and development workflows to create detailed insights about your codebase.

## Prerequisites

Before you start, make sure you have:
- [Task](https://taskfile.dev) installed for running project commands
- [Yaak](https://yaak.app) installed for API testing (free HTTP client)
- A valid API key for an AI provider (OpenAI, Anthropic, etc.)

## Quick Start Guide

### 1. Start the Development Environment

#### Option A: Full Docker Setup (Recommended for Quick Start)
```bash
task dev
```
This starts all the necessary services (databases, APIs, flow-bridge) in Docker containers.

#### Option B: Local Development Setup (For Development/Debugging)
Run services from source for easier debugging:

**Terminal 1 - Start Dependencies:**
```bash
task dev-local
```
This starts only the Docker dependencies (PostgreSQL, Neo4j, Temporal, etc.) with flow-bridge.

**Terminal 2 - Run Flow-Bridge Locally:**
```bash
cd ../unoplat-code-confluence-ingestion/code-confluence-flow-bridge && task run-dev-core
```

**Terminal 3 - Run Query Engine Locally:**
```bash
task run-dev
```

This setup avoids duplicate Docker dependencies and allows you to run both servers from source.

### 2. Set Up API Testing
1. Open **Yaak** (the HTTP client)
2. Click **"Sync Project"** in the bottom-left corner - select root of the project - yaak folder for the same.
3. This loads all the pre-configured API requests for this project

### 3. Generate Authentication Token
In Yaak, navigate to **"code confluence flow bridge"** section:
1. Create a new request based on the token generation template
2. Replace the template name with your actual name (e.g., `john-ingest-token`)
3. Run the token generation request
4. Run the ingestion request (wait 5 seconds for processing)

### 4. Configure AI Model
In Yaak, navigate to **"code-confluence-query-engine"** section:
1. Run **"get providers"** to see available AI providers (OpenAI, Anthropic, etc.)
2. Create a new model configuration request with your name (e.g., `john-set-model-provider`)
3. Set your preferred AI provider and API key
4. Run the configuration request

### 5. Generate Codebase Analysis
Run the **"test-agents-md-agent"** request to start the AI analysis of your codebase.

## What You'll Get

The tool generates detailed markdown documentation including:
- **Project Structure**: Key directories and configuration files
- **Business Logic**: Core functionality and domain models  
- **Framework Analysis**: Technologies and libraries used
- **Development Workflow**: Build processes, testing, and deployment setup

## Troubleshooting

- **Services not starting**: Ensure Docker is running and ports 5432, 7687, 8000 are available
- **Docker issues**: Try the local development setup (Option B) to run services from source
- **Token errors**: Make sure you've completed step 3 before proceeding to step 4
- **AI model errors**: Verify your API key is valid and has sufficient credits
- **Analysis taking too long**: Large codebases may take several minutes to analyze
- **Port conflicts**: If port 8000 or 8001 is in use, stop conflicting services or use the local setup to debug

## Next Steps

Once the analysis completes, check the generated markdown files for insights about your codebase structure and recommendations for improvement.