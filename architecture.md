# Current architecture

The deployed web frontend and CLI invoke the Flow Bridge and Query Engine APIs. Flow Bridge manages repository ingestion workflows and invokes the Query Engine after a refresh; both services use Temporal and PostgreSQL. Both backend services call GitHub, and the Query Engine also performs model-provider inference.

```mermaid
architecture-beta
    group consumers[Consumers and entry points]
    group backend[Backend services]
    group platform[Platform and infrastructure]
    group external[External services]

    service cli(server)[CLI] in consumers
    service frontend(server)[Web frontend] in consumers

    service flow_bridge(server)[Flow Bridge API] in backend
    service query_engine(server)[Query Engine API] in backend

    service temporal(server)[Temporal workflow service] in platform
    service postgresql(database)[PostgreSQL] in platform

    service github(internet)[GitHub API] in external
    service model_provider(cloud)[Model provider] in external

    cli:B --> T:flow_bridge
    cli:B --> T:query_engine
    frontend:B --> T:flow_bridge
    frontend:B --> T:query_engine
    flow_bridge:B --> T:query_engine
    flow_bridge:B <--> T:github
    flow_bridge:B --> T:temporal
    flow_bridge:B --> T:postgresql
    query_engine:B --> T:github
    query_engine:B --> T:model_provider
    query_engine:B --> T:temporal
    query_engine:B --> T:postgresql
    temporal:B --> T:postgresql

    align row cli frontend
    align row flow_bridge query_engine
    align row temporal postgresql
    align row github model_provider
```

Evidence: the frontend HTTP clients target both backend APIs; the CLI has concrete Flow Bridge and Query Engine clients. Flow Bridge exposes GitHub webhook endpoints, calls GitHub and the Query Engine, starts Temporal workflows, and writes with SQLAlchemy. Query Engine exposes its API and workflow activities, uses PostgreSQL, calls GitHub, and runs LLM agents. The deployment Compose configuration supplies the Flow Bridge, Query Engine, Temporal, and PostgreSQL services.
