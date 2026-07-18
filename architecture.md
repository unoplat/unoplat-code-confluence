# Current architecture

The deployed web frontend calls the flow bridge and query engine APIs. The flow bridge receives GitHub App webhooks, calls the query engine after refresh, and both backend services use Temporal and PostgreSQL. The query engine also calls GitHub for feedback issues and agent-change pull requests.

```mermaid
architecture-beta
    group consumers[Consumers and entry points]
    group backend[Backend services]
    group platform[Platform and infrastructure]
    group external[External services]

    service browser(internet)[Browser] in consumers
    service frontend(server)[Web frontend] in consumers
    service flow_bridge(server)[Flow bridge API] in backend
    service query_engine(server)[Query engine API] in backend
    service temporal(server)[Temporal workflow service] in platform
    service postgresql(database)[PostgreSQL] in platform
    service github(internet)[GitHub] in external

    browser:R --> L:frontend
    frontend:R --> L:flow_bridge
    frontend:R --> L:query_engine
    github:R --> L:flow_bridge
    flow_bridge:R --> L:query_engine
    flow_bridge:R --> L:temporal
    flow_bridge:R --> L:postgresql
    query_engine:R --> L:temporal
    query_engine:R --> L:postgresql
    query_engine:R --> L:github
    temporal:R --> L:postgresql

    align column flow_bridge query_engine
```
