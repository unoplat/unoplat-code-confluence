# Code Confluence Flow Bridge


## Description

This is a bridge between Code Confluence User and Ingestion Workflow.

## Prerequisites

### Task

```
brew install go-task/tap/go-task
```


## Installation

```bash
uv sync 
```

## Run Locally in Development Mode

Note - Directory to be in : unoplat-code-confluence-ingestion/code-confluence-flow-bridge

- task start-temporal
- task start-neo4j
- task dev
- task run-client

Then go to localhost:7687 and you will be able to visualise the codebase data in graphical form.


## Run Locally in Production Mode

```bash
docker compose -f local-docker-compose.yml up
```