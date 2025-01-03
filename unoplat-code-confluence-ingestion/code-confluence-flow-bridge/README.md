# Code Confluence Flow Bridge


## Description

This is a bridge between Code Confluence User and Ingestion Workflow.

## Prerequisites

- [Temporal Server](https://docs.temporal.io/docs/get-started/set-up-a-local-server/)

Start Temporal Server with UI
```
temporal server start-dev --ui-port 8080
```

## Installation

```bash
uv sync 
```

## Run

Go to root directory where Taskfile.yml exists and run the following command.

```bash
task dev
```


## References

- [Package Structure](https://github.com/astral-sh/uv/issues/7341)