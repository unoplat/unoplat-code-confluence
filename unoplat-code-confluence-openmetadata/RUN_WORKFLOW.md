# Run Workflow YAML

This workflow runs the Code Confluence OpenMetadata connector from the `openmetadata_ingestion` container.

## Prepare Workflow Copy

Keep `examples/workflow.yaml` as a reusable template. Create a runtime copy and insert the OpenMetadata Personal Access Token into that copy only.

```bash
cp unoplat-code-confluence-openmetadata/examples/workflow.yaml /tmp/code-confluence-workflow.yaml
```

Edit `/tmp/code-confluence-workflow.yaml` and replace:

```yaml
jwtToken: "<OPENMETADATA_PERSONAL_ACCESS_TOKEN>"
```

with the token created in OpenMetadata.

For container execution, confirm these values are present:

```yaml
source:
  serviceConnection:
    config:
      connectionOptions:
        codeConfluenceApiBaseUrl: "http://host.docker.internal:8001"

workflowConfig:
  openMetadataServerConfig:
    hostPort: "http://openmetadata-server:8585/api"
```

## Copy Workflow Into Container

```bash
docker cp /tmp/code-confluence-workflow.yaml openmetadata_ingestion:/tmp/code-confluence-workflow.yaml
```

## Register Custom Properties

Run the registration step before the first ingestion run:

```bash
docker exec -i openmetadata_ingestion python - <<'PY'
from pathlib import Path
import yaml

from metadata.generated.schema.api.data.createCustomProperty import CreateCustomPropertyRequest
from metadata.generated.schema.entity.data.apiCollection import APICollection
from metadata.generated.schema.entity.data.apiEndpoint import APIEndpoint
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import OpenMetadataConnection
from metadata.generated.schema.type.basic import EntityName, Markdown
from metadata.ingestion.models.custom_properties import CustomPropertyDataTypes, OMetaCustomProperties
from metadata.ingestion.ometa.ometa_api import OpenMetadata

workflow = yaml.safe_load(Path("/tmp/code-confluence-workflow.yaml").read_text())
metadata = OpenMetadata(
    OpenMetadataConnection.model_validate(
        workflow["workflowConfig"]["openMetadataServerConfig"]
    )
)
string_property_type = metadata.get_property_type_ref(CustomPropertyDataTypes.STRING)

properties = {
    APICollection: [
        "codeConfluenceDevelopmentWorkflow",
        "codeConfluenceDependencies",
        "codeConfluenceBusinessLogic",
        "codeConfluenceInboundConstructs",
        "codeConfluenceOutboundConstructs",
        "codeConfluenceInternalConstructs",
    ],
    APIEndpoint: ["codeConfluenceHttpEndpoint"],
}

for entity_type, names in properties.items():
    for name in names:
        request = CreateCustomPropertyRequest(
            name=EntityName(name),
            displayName=name,
            description=Markdown("Code Confluence JSON metadata stored as a string."),
            propertyType=string_property_type,
        )
        metadata.create_or_update_custom_property(
            OMetaCustomProperties(
                entity_type=entity_type,
                createCustomPropertyRequest=request,
            )
        )
        print(f"registered {entity_type.__name__}.{name}")
PY
```

You can also follow `REGISTER_CUSTOM_PROPERTIES.md` for the same registration process.

## Run Ingestion

```bash
docker exec openmetadata_ingestion metadata ingest -c /tmp/code-confluence-workflow.yaml
```

A successful run should report `Workflow Success %: 100.0` and no `Unknown custom field` errors.

## Verify Entities

The run should create or update:

- An OpenMetadata API service for the Code Confluence repository.
- API collections for repository codebases/modules.
- API endpoints only for discovered HTTP endpoints.
- Code Confluence metadata in the registered `codeConfluence*` custom properties.
