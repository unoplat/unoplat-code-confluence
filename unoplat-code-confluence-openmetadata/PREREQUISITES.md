# Prerequisites

Use this checklist before running the Code Confluence OpenMetadata ingestion workflow.

## Services

- OpenMetadata Docker Compose is running.
- The `openmetadata_server` container is healthy.
- The `openmetadata_ingestion` container is running.
- The Code Confluence query-engine is running and reachable from the host at `http://localhost:8001`.
- From inside Docker, the query-engine is reachable at `http://host.docker.internal:8001`.

## Connector Wheel

Build the connector package from the host:

```bash
uv build --package unoplat-code-confluence-openmetadata
```

Copy the wheel into the ingestion container:

```bash
docker cp unoplat-code-confluence-openmetadata/dist/unoplat_code_confluence_openmetadata-0.1.0-py3-none-any.whl openmetadata_ingestion:/tmp/unoplat_code_confluence_openmetadata-0.1.0-py3-none-any.whl
```

Install it in the ingestion container with `python -m pip`:

```bash
docker exec openmetadata_ingestion python -m pip install --no-deps /tmp/unoplat_code_confluence_openmetadata-0.1.0-py3-none-any.whl
```

Verify the connector imports:

```bash
docker exec openmetadata_ingestion python -c "from unoplat_code_confluence_openmetadata.source import CodeConfluenceSource; print(CodeConfluenceSource.__name__)"
```

## Personal Access Token

Create a Personal Access Token in the OpenMetadata UI before running ingestion.

1. Open the OpenMetadata UI at `http://localhost:8585`.
2. Sign in as an admin user.
3. Open the user profile or settings menu.
4. Go to the Personal Access Token section.
5. Create a new token for the ingestion workflow.
6. Copy the token immediately.
7. Replace `<OPENMETADATA_PERSONAL_ACCESS_TOKEN>` in a local workflow copy with the token.

Do not commit the real token. Keep `examples/workflow.yaml` as a template with the placeholder value.

## Required URLs

When running ingestion inside `openmetadata_ingestion`, the workflow should use these URLs:

- `workflowConfig.openMetadataServerConfig.hostPort: "http://openmetadata-server:8585/api"`
- `source.serviceConnection.config.connectionOptions.codeConfluenceApiBaseUrl: "http://host.docker.internal:8001"`

When running ingestion from the Mac host instead, use these host URLs:

- `workflowConfig.openMetadataServerConfig.hostPort: "http://localhost:8585/api"`
- `source.serviceConnection.config.connectionOptions.codeConfluenceApiBaseUrl: "http://localhost:8001"`

## Custom Properties

Register the Code Confluence custom properties before running ingestion. See `REGISTER_CUSTOM_PROPERTIES.md`.
