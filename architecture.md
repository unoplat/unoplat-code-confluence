# Current architecture

The web frontend and CLI invoke the flow bridge and query engine HTTP APIs. The flow bridge and query engine use Temporal workflows and PostgreSQL; the flow bridge triggers query-engine agent updates. GitHub delivers webhooks to the flow bridge and is used by both backend services, while the query engine also invokes a configured AI model provider.

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

    frontend:B --> T:flow_bridge
    frontend:B --> T:query_engine
    cli:B --> T:flow_bridge
    cli:B --> T:query_engine
    flow_bridge:R --> L:query_engine
    flow_bridge:B --> T:temporal
    flow_bridge:B --> T:postgresql
    query_engine:B --> T:temporal
    query_engine:B --> T:postgresql
    temporal:B --> T:postgresql
    flow_bridge:B <--> T:github
    query_engine:B --> T:github
    query_engine:B --> T:model_provider

    align row frontend cli
    align row flow_bridge query_engine
    align row temporal postgresql
    align row github model_provider
```
