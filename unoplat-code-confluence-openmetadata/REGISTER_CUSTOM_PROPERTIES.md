# Register Code Confluence Custom Properties

OpenMetadata rejects extension fields until the custom properties are registered on the target entity types. Register these fields before running the Code Confluence ingestion workflow.

## Required Order

1. Start OpenMetadata and the `openmetadata_ingestion` container.
2. Install the Code Confluence OpenMetadata wheel in `openmetadata_ingestion`.
3. Copy the workflow YAML into the container.
4. Register the custom properties below.
5. Run `metadata ingest -c /tmp/code-confluence-workflow.yaml`.

## Properties

Register these string custom properties on `APICollection`:

- `codeConfluenceDevelopmentWorkflow`
- `codeConfluenceDependencies`
- `codeConfluenceBusinessLogic`
- `codeConfluenceInboundConstructs`
- `codeConfluenceOutboundConstructs`
- `codeConfluenceInternalConstructs`

Register this string custom property on `APIEndpoint`:

- `codeConfluenceHttpEndpoint`

The connector stores structured Code Confluence metadata as compact JSON strings in these properties.

## Registration Command

Run this from the host after `/tmp/code-confluence-workflow.yaml` exists inside `openmetadata_ingestion` and points at `http://openmetadata-server:8585/api`:

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

## Ingestion Command

After registration, run:

```bash
docker exec openmetadata_ingestion metadata ingest -c /tmp/code-confluence-workflow.yaml
```

For ingestion from inside Docker, keep these workflow URLs:

- `workflowConfig.openMetadataServerConfig.hostPort: "http://openmetadata-server:8585/api"`
- `source.serviceConnection.config.connectionOptions.codeConfluenceApiBaseUrl: "http://host.docker.internal:8001"`
