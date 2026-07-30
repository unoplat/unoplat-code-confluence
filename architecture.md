# Current architecture

The deployed web frontend calls the FastAPI flow bridge and query engine. The flow bridge starts ingestion workflows and invokes the query engine for AGENTS.md updates; both services use Temporal and PostgreSQL. GitHub exchanges webhooks and repository-provider requests with the flow bridge, and the query engine uses GitHub for feedback and pull-request operations.

```mermaid
architecture-beta
    group consumers[Consumers and entry points]
    group backend[Backend services]
    group platform[Platform and infrastructure]
    group external[External services]

    service frontend(server)[Web frontend] in consumers
    service flow_bridge(server)[Flow bridge API] in backend
    service query_engine(server)[Query engine API] in backend
    service temporal(server)[Temporal] in platform
    service postgresql(database)[PostgreSQL] in platform
    service github(internet)[GitHub] in external

    frontend:R --> L:flow_bridge
    flow_bridge:R --> L:query_engine
    flow_bridge:B --> T:temporal
    query_engine:R --> L:postgresql
    github:B --> T:flow_bridge

    align column temporal postgresql
```
