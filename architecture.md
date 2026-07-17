# Current architecture

The local Compose deployment runs the frontend, flow bridge, query engine, Temporal, and PostgreSQL. The frontend has separate HTTP clients for the flow bridge and query engine; both backend applications expose FastAPI endpoints. The flow bridge processes GitHub repositories and runs ingestion workflows, while the query engine can use configured MCP servers.

```mermaid
architecture-beta
    group compose[Local Compose deployment]
    service frontend(server)[Web frontend] in compose
    service flow_bridge(server)[Flow bridge API and ingestion worker] in compose
    service query_engine(server)[Query engine API and worker] in compose
    service temporal(server)[Temporal service] in compose
    service postgres(database)[PostgreSQL] in compose
    service user(internet)[Browser user]
    service github(internet)[GitHub]
    service mcp_servers(server)[Configured MCP servers]

    user:R --> L:frontend
    frontend:R --> L:flow_bridge
    frontend:B --> T:query_engine
    github:R <--> L:flow_bridge
    flow_bridge:R --> L:temporal
    query_engine:R --> B:temporal
    flow_bridge:B --> T:postgres
    query_engine:B --> T:postgres
    temporal:R --> L:postgres
    query_engine:R --> L:mcp_servers
```
