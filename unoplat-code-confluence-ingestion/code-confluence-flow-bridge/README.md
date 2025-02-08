# Code Confluence Flow Bridge


## Description

This is a bridge between Code Confluence User and Ingestion Workflow.

## Prerequisites

### Task

```
brew install go-task/tap/go-task
```

## Run Locally in Development Mode

Note - Directory to be in : unoplat-code-confluence-ingestion/code-confluence-flow-bridge

- task start-temporal
- task start-neo4j
- task dev
- 


```
temporal server start-dev --ui-port 8080 --log-level debug
```

Note: to debug temporal server, run the following command.

```
journalctl -u temporal.service
```

- Neo4j

```
        docker run \
    --name code-confluence-neo4j \
    -p 7474:7474 \
    -p 7687:7687 \
    -v $HOME/neo4j/data:/data \
    -v $HOME/neo4j/logs:/logs \
    -v $HOME/neo4j/import:/var/lib/neo4j/import \
    -v $HOME/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/password \
    --env NEO4J_PLUGINS='["apoc"]' \
    --env NEO4J_apoc_export_file_enabled=true \
    --env NEO4J_apoc_import_file_enabled=true \
    --env NEO4J_dbms_security_procedures_unrestricted='*' \
    graphstack/dozerdb:5.25.1.0-alpha.1
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


## Internal Dependency

uv add "git+https://github.com/unoplat/unoplat-code-confluence.git@unoplat-code-confluence-commons-v0.6.1#subdirectory=unoplat-code-confluence-commons"