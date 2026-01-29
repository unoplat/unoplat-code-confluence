# Code Confluence Flow Bridge

## Description

This is a bridge between Code Confluence User and Ingestion Workflow.

## Prerequisites

### Task

```bash
brew install go-task/tap/go-task
```

## Installation

```bash
uv sync
```

## Run Locally in Development Mode

Note - Directory to be in : unoplat-code-confluence-ingestion/code-confluence-flow-bridge

- task start-dependencies
- task dev
- task run-client


## Run Locally in Production Mode

```bash
docker compose -f local-docker-compose.yml up
```

## OTEL Logging important links

- [OpenTelemetry Python Issue #3615](https://github.com/open-telemetry/opentelemetry-python/issues/3615)
- [OpenTelemetry Loguru Telegram](https://github.com/s71m/opentelemetry-loguru-telegram)

## Environment Variables

### Temporal Worker Configuration

The following environment variables can be used to configure the Temporal worker concurrency settings:

- `UNOPLAT_TEMPORAL_MAX_CONCURRENT_ACTIVITIES`: Sets the maximum number of activity tasks that the worker will execute concurrently (default: 4)
- `UNOPLAT_TEMPORAL_MAX_CONCURRENT_ACTIVITY_TASK_POLLS`: Sets the maximum number of concurrent poll requests the worker will make to the Temporal service for activity tasks (default: 2)

Tuning tips:

- If your worker is not fully utilizing its execution slots, consider increasing the number of pollers.
- If you see high CPU or memory usage, you may want to decrease the number of concurrent activities.
- The number of pollers should generally be less than or equal to the number of execution slots to avoid unnecessary polling overhead.