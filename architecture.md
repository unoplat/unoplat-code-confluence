# Current architecture

The browser-delivered frontend invokes the flow bridge and query engine APIs. The flow bridge coordinates ingestion through Temporal, persists application data in PostgreSQL, and triggers query-engine processing. The query engine also uses Temporal and PostgreSQL, and its agent and feedback capabilities call configured AI model providers and GitHub. GitHub can also invoke the flow bridge webhook.

```mermaid
architecture-beta
    group consumers[Consumers and entry points]
    group backend[Backend services]
    group platform[Platform and infrastructure]
    group external[External services]

    service browser(internet)[Browser] in consumers
    service frontend(server)[Web frontend] in consumers
    service flow_bridge(server)[Flow bridge] in backend
    service query_engine(server)[Query engine] in backend
    service temporal(server)[Temporal workflow service] in platform
    service postgresql(database)[PostgreSQL] in platform
    service github(internet)[GitHub] in external
    service model_provider(cloud)[Configured AI model provider] in external

    browser:R --> L:frontend
    frontend:R --> L:flow_bridge
    frontend:R --> L:query_engine
    flow_bridge:R --> L:query_engine
    flow_bridge:R --> L:temporal
    flow_bridge:R --> L:postgresql
    query_engine:R --> L:temporal
    query_engine:R --> L:postgresql
    temporal:R --> L:postgresql
    flow_bridge:R <--> L:github
    query_engine:R --> L:github
    query_engine:R --> L:model_provider

    align column flow_bridge query_engine
```
