# Current architecture

The web frontend and CLI call the flow bridge and query engine APIs. The flow bridge receives GitHub App webhooks, calls GitHub and the query engine, and runs ingestion workflows through Temporal. The query engine runs Temporal agent workflows, persists application data, and calls GitHub and an AI model provider. Both backend services use PostgreSQL; Temporal is configured to use PostgreSQL.

```mermaid
architecture-beta
    group consumers[Consumers and entry points]
    group backend[Backend services]
    group platform[Platform and infrastructure]
    group external[External services]

    service frontend(server)[Web frontend] in consumers
    service cli(server)[CLI] in consumers
    service flow_bridge(server)[Flow bridge API] in backend
    service query_engine(server)[Query engine API] in backend
    service temporal(server)[Temporal workflow service] in platform
    service postgresql(database)[PostgreSQL] in platform
    service github(internet)[GitHub] in external
    service model_provider(cloud)[AI model provider] in external

    frontend:R --> L:flow_bridge
    frontend:R --> L:query_engine
    cli:R --> L:flow_bridge
    cli:R --> L:query_engine
    github:R <--> L:flow_bridge
    flow_bridge:R --> L:query_engine
    flow_bridge:R --> L:temporal
    flow_bridge:R --> L:postgresql
    query_engine:R --> L:temporal
    query_engine:R --> L:postgresql
    query_engine:R --> L:github
    query_engine:R --> L:model_provider
    temporal:R --> L:postgresql
```