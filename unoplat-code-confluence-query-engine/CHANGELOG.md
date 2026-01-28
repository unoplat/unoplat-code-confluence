# Changelog

## [0.26.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.25.1...unoplat-code-confluence-query-engine-v0.26.0) (2026-01-28)


### Features

* **query-engine-agents-md:** introduce dependency guide agent and also removed agent with context as we migrated to exa mcp tool. Also moved to pydantic fastmcp client for mcp servers ([a3e6788](https://github.com/unoplat/unoplat-code-confluence/commit/a3e6788a54cbf5672967eafd142093d077d559a9))


### Bug Fixes

* add utility that helps safe logging showing only first/last few chars of sensitive information ([1fdc947](https://github.com/unoplat/unoplat-code-confluence/commit/1fdc947fb78a83ba59c391956e0051f6fbf984a5))
* **date-time-fixes-backend:** offset fixes ([87165db](https://github.com/unoplat/unoplat-code-confluence/commit/87165dbc25ebda76a48cb1e4ca6cbf3cd1ebaee6))
* **mcp-migration:** migration from standard fastapi mcp client ([9a87bb9](https://github.com/unoplat/unoplat-code-confluence/commit/9a87bb91d645868fd36397162800ba326af1d283))
* **query-engine-test:** breaking changes due to test containers v4 api ([d0e401b](https://github.com/unoplat/unoplat-code-confluence/commit/d0e401b760114d5bf739c54283b7885e74e990eb))

## [0.25.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.25.0...unoplat-code-confluence-query-engine-v0.25.1) (2026-01-20)


### Bug Fixes

* **dependency-version:** commons dependency version with model update… ([dbdd027](https://github.com/unoplat/unoplat-code-confluence/commit/dbdd02708a379d3277d50f62e19d3934ef4a82fe))
* **dependency-version:** commons dependency version with model updates for ingestion/query services ([890f4ca](https://github.com/unoplat/unoplat-code-confluence/commit/890f4cad1d3a5aaa3e1f4119f4ce122ab54b9d0d))

## [0.25.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.24.9...unoplat-code-confluence-query-engine-v0.25.0) (2026-01-20)


### Features

* **migrate-postgres:** ingestion and query engine services ([06edb7f](https://github.com/unoplat/unoplat-code-confluence/commit/06edb7fb05997754e73f5ba2104b8a764cba5e79))


### Bug Fixes

* **dependencies:** get rid of unused dependencies - neomodel ([61e42a2](https://github.com/unoplat/unoplat-code-confluence/commit/61e42a202a7981a7e8cc1347e0b60e40131371ec))

## [0.24.9](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.24.8...unoplat-code-confluence-query-engine-v0.24.9) (2026-01-20)


### Bug Fixes

* **improve-system-prompt:** improve system prompt for getting library information to work more reliably with open source models ([469a8e1](https://github.com/unoplat/unoplat-code-confluence/commit/469a8e10a411418197b3d4fbecdcfddf8868675a))

## [0.24.8](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.24.7...unoplat-code-confluence-query-engine-v0.24.8) (2026-01-09)


### Bug Fixes

* **agent-description:** improve system prompts and tool descriptions … ([780b624](https://github.com/unoplat/unoplat-code-confluence/commit/780b624e5af02767bceb7212d8c62a43e2be511f))
* **agent-description:** improve system prompts and tool descriptions and add output validator for open source models to work reliably. solved issues with minmax2.1 ([8cb0968](https://github.com/unoplat/unoplat-code-confluence/commit/8cb096893c72b8626968234218b1a36db7367cf6))

## [0.24.7](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.24.6...unoplat-code-confluence-query-engine-v0.24.7) (2025-12-22)


### Bug Fixes

* **regression-eza:** add eza to dockerfile of query engine for direct… ([d1bbd38](https://github.com/unoplat/unoplat-code-confluence/commit/d1bbd3874a7ba3566bd331cda522aa72b50b5a90))
* **regression-eza:** add eza to dockerfile of query engine for directory tree tool and remove old commented code ([4282fea](https://github.com/unoplat/unoplat-code-confluence/commit/4282feaa9f61b20211c99b22346710eda405492a))

## [0.24.6](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.24.5...unoplat-code-confluence-query-engine-v0.24.6) (2025-12-22)


### Bug Fixes

* alter tests fail cases (now being handled by workflow orchestrator) ([abb94f9](https://github.com/unoplat/unoplat-code-confluence/commit/abb94f93315ce17167955b05ab8d038be11e82eb))
* **deps-version:** pin common lib dependencies version to latest ([e5d5db2](https://github.com/unoplat/unoplat-code-confluence/commit/e5d5db2c358fee88b4afae35ff7a8a68807836de))
* **deps-version:** pin common lib dependencies version to latest ([ed5b60f](https://github.com/unoplat/unoplat-code-confluence/commit/ed5b60f70f0ae254ea2a583a10f13a53b2df4740))

## [0.24.5](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.24.4...unoplat-code-confluence-query-engine-v0.24.5) (2025-12-16)


### Bug Fixes

* **mcp-toolset-fix:** fix for getting library data ([9540acf](https://github.com/unoplat/unoplat-code-confluence/commit/9540acfeb17a917d6eac40026c9d838af971a07a))
* **post-processing-business-domain:** workflow orchestrator services/worker responsibilities clean up and post processing fix for agent md ([d21c465](https://github.com/unoplat/unoplat-code-confluence/commit/d21c4655328e29a6cbde1e98f1638834e199a768))
* **version-upgrade:** update pydantic ai with various fixes ([035e91a](https://github.com/unoplat/unoplat-code-confluence/commit/035e91ae59c44e961452bf6a40f224796f8b8913))

## [0.24.4](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.24.3...unoplat-code-confluence-query-engine-v0.24.4) (2025-12-16)


### Bug Fixes

* automatic error capture post exhausion of retries during ai work… ([415de05](https://github.com/unoplat/unoplat-code-confluence/commit/415de05f4c9785afe22264d5439f20f2819a19e8))
* automatic error capture post exhausion of retries during ai workflow for user to easily submit github issues with all details ([af42e1f](https://github.com/unoplat/unoplat-code-confluence/commit/af42e1f35d9ceb03462fd706f27d12b89ad32940))
* **connection-pool-recommendation-settings:** reuse stale connections and increase connection pool for postgres ([2935799](https://github.com/unoplat/unoplat-code-confluence/commit/2935799a5a1c160ebba5b6da76d4adbdcd73eadf))
* **model-config:** do two phase operation for model config upsert and worker upgrade ensuring one does not affect anothert ([bd3be65](https://github.com/unoplat/unoplat-code-confluence/commit/bd3be653a203385e43fcd338a346c66bab053727))
* regression for package manager and programming language metadata ([5b705e9](https://github.com/unoplat/unoplat-code-confluence/commit/5b705e91ac4d308fd588cc30ee8b33026bd1b477))

## [0.24.3](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.24.2...unoplat-code-confluence-query-engine-v0.24.3) (2025-12-11)


### Bug Fixes

* **perf:** parallelism per codebase agent md in monorepo ([d71e0e4](https://github.com/unoplat/unoplat-code-confluence/commit/d71e0e4d19fe2ec8ba6707e098ed36a58969676f))
* **perf:** parallelism per codebase agent md in monorepo ([7ae3ad8](https://github.com/unoplat/unoplat-code-confluence/commit/7ae3ad8c98612cd30e52753b7b0d78f3442beb14))

## [0.24.2](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.24.1...unoplat-code-confluence-query-engine-v0.24.2) (2025-12-11)


### Bug Fixes

* statistics calculation ([d549274](https://github.com/unoplat/unoplat-code-confluence/commit/d5492746c114bcee255dc3e12c04f2789d586123))
* statistics persistence ([6c03e05](https://github.com/unoplat/unoplat-code-confluence/commit/6c03e0587775fb5e8e7c8c2e102f7ec3e2184d4d))

## [0.24.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.24.0...unoplat-code-confluence-query-engine-v0.24.1) (2025-12-10)


### Bug Fixes

* agent md persistence ([348b4d4](https://github.com/unoplat/unoplat-code-confluence/commit/348b4d440e05949fd24606dd6f3f1f72730d477c))
* insert based on repository workflow run id ([0a298b4](https://github.com/unoplat/unoplat-code-confluence/commit/0a298b4e00864e6b116198b4aeffaa02f480e41a))
* removal of duplicate status column for agent snapshot tracking ([24d2b40](https://github.com/unoplat/unoplat-code-confluence/commit/24d2b40642643eb149db68fbeae2a4bbbf6a610e))
* test with repository workflow run id ([d011ed7](https://github.com/unoplat/unoplat-code-confluence/commit/d011ed7dac7397de0dcf3e6e0a40277fe99ce98b))

## [0.24.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.23.1...unoplat-code-confluence-query-engine-v0.24.0) (2025-12-10)


### Features

* first draft of reliable auditable agent ([8a361c6](https://github.com/unoplat/unoplat-code-confluence/commit/8a361c611e97162dfb0a755bfce3a858042db491))
* first draft of reliable auditable agents ([9fc6eee](https://github.com/unoplat/unoplat-code-confluence/commit/9fc6eeec90432442d06742f223fde22606ff6c88))


### Bug Fixes

* tests ([26ab79d](https://github.com/unoplat/unoplat-code-confluence/commit/26ab79d76d8ccf9835909fb2fb3bab3764bd5d90))
* tests ([46b087a](https://github.com/unoplat/unoplat-code-confluence/commit/46b087acaa06f155903b99bf46cd3ea4cd420b8f))

## [0.23.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.23.0...unoplat-code-confluence-query-engine-v0.23.1) (2025-12-01)


### Bug Fixes

* improving ai engine structure (first step towards improving prim… ([9e5b00b](https://github.com/unoplat/unoplat-code-confluence/commit/9e5b00bfad87027198fb51a9c5f6696e0dc4df44))
* improving ai engine structure (first step towards improving primitives) ([b2950bc](https://github.com/unoplat/unoplat-code-confluence/commit/b2950bccba8c034b175a407eddd65599f4d666c0))

## [0.23.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.22.0...unoplat-code-confluence-query-engine-v0.23.0) (2025-11-21)


### Features

* support more repository providers starting with github enterprise. Improved Frontend Architecture and onboarding and some bugs squashed ([0974c76](https://github.com/unoplat/unoplat-code-confluence/commit/0974c76fe9df68b86fb1b180db1b41e04a16c9dd))

## [0.22.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.21.0...unoplat-code-confluence-query-engine-v0.22.0) (2025-11-21)


### Features

* **config:** Update dependencies and refactor MCP server management (temp fix for concurrent access to subagents cuasing asyncio issues - moving to async workflow engine with better isolation same as ingestion( ([ef1725c](https://github.com/unoplat/unoplat-code-confluence/commit/ef1725c800affc63015641068ab6d5d876d8fab4))

## [0.21.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.20.0...unoplat-code-confluence-query-engine-v0.21.0) (2025-11-10)


### Features

* enhance api endpoints and processing logic to support multiple repository providers starting with github enterprise , introduce oauth utils and also assign intuitive names for agents for easier experiment tracking with workflow monitoring solution ([ba05d6b](https://github.com/unoplat/unoplat-code-confluence/commit/ba05d6ba13eb951ab43f8d0553622582fced7b4b))


### Dependencies

* Bump unoplat-code-confluence-commons to v0.34.1 ([75b3e48](https://github.com/unoplat/unoplat-code-confluence/commit/75b3e489496005a5cc6f7281a63c14ea9b9db7e4))

## [0.20.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.19.0...unoplat-code-confluence-query-engine-v0.20.0) (2025-11-03)


### Features

* **workflow:** Enhance agent execution with usage statistics tracking ([c68e53e](https://github.com/unoplat/unoplat-code-confluence/commit/c68e53ef83243b55a8fbb0dc330891517b80d086))

## [0.19.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.18.0...unoplat-code-confluence-query-engine-v0.19.0) (2025-11-03)


### Features

* **code:** allow sections of agents.md per codebase to be collapsed and copied ([859bbc7](https://github.com/unoplat/unoplat-code-confluence/commit/859bbc734789996aa1c1b8cabb88c4c5fd15ffa8))

## [0.18.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.17.2...unoplat-code-confluence-query-engine-v0.18.0) (2025-10-30)


### Features

* **code-confluence:** Enhance data model file retrieval and processing to reduce context by minimum of 2x for better result of understanding domain ([31c3eb4](https://github.com/unoplat/unoplat-code-confluence/commit/31c3eb4817e035159f6561965ce2d937c3a4e588))


### Bug Fixes

* **provider_catalog:** fix inference providers for hugging face ([728547c](https://github.com/unoplat/unoplat-code-confluence/commit/728547c8bb20ae5b7fa53c3d6c7554b675a84673))


### Documentation

* **readme:** Enhance development setup and troubleshooting guide ([03be005](https://github.com/unoplat/unoplat-code-confluence/commit/03be0050ad24157fcc71adcaec89722aa142fdf6))

## [0.17.2](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.17.1...unoplat-code-confluence-query-engine-v0.17.2) (2025-10-23)


### Bug Fixes

* **parser:** Refactor GenericCodebaseParser to focus on file insertion ([be17754](https://github.com/unoplat/unoplat-code-confluence/commit/be17754ab8a80b276820b205e37f0c9859e2b6b2))
* **parser:** Refactor parser to focus on file insertion ([c0bd597](https://github.com/unoplat/unoplat-code-confluence/commit/c0bd5974bbe8298b1a8e9a6931bf0eae850c1cca))

## [0.17.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.17.0...unoplat-code-confluence-query-engine-v0.17.1) (2025-10-16)


### Bug Fixes

* update schema , improved local dev experience through tasks Add better logging. ([ffd98e9](https://github.com/unoplat/unoplat-code-confluence/commit/ffd98e96afc32553ce4b30de1908f44993965d3d))
* update schema , improved local dev experience through tasks Add better logging. ([73d1a24](https://github.com/unoplat/unoplat-code-confluence/commit/73d1a241c75394839e853d5de9e4ec0fdf48fe08))

## [0.17.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.16.0...unoplat-code-confluence-query-engine-v0.17.0) (2025-10-06)


### Features

* **package-manager:** Optimize metadata storage and serialization ([21130a9](https://github.com/unoplat/unoplat-code-confluence/commit/21130a93fc17949986aa0c5ece151886ad2c5045))


### Bug Fixes

* **package-metadata:** Parse programming language version from JSON ([c7b2fd5](https://github.com/unoplat/unoplat-code-confluence/commit/c7b2fd5f55a35ec77c89f0c18d9f578b4867ea89))

## [0.16.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.15.2...unoplat-code-confluence-query-engine-v0.16.0) (2025-10-04)


### Features

* **package-manager:** Add TypeScript package manager detection ([9cff38b](https://github.com/unoplat/unoplat-code-confluence/commit/9cff38bbf0349556a714402b3cfe7bc371c3a2fb))
* **package-manager:** Add TypeScript package manager detection ([ab4d9a5](https://github.com/unoplat/unoplat-code-confluence/commit/ab4d9a55dbdb05122631b24672df235736508a4d))

## [0.15.2](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.15.1...unoplat-code-confluence-query-engine-v0.15.2) (2025-09-30)


### Bug Fixes

* **unoplat-code-confluence-query-engine:** raw strings for system prompts and also modified dockerfile to now use official postgresql instead of bitnami ([896b1ef](https://github.com/unoplat/unoplat-code-confluence/commit/896b1ef30dcf9b750c282efd70b3fcf7cf3d079d))

## [0.15.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.15.0...unoplat-code-confluence-query-engine-v0.15.1) (2025-09-29)


### Bug Fixes

* **deps:** update cohere, openai, pydantic-ai, and related packages ([85ee9c7](https://github.com/unoplat/unoplat-code-confluence/commit/85ee9c7fee9b6fde9bc40c74085ca09c60035da0))
* **deps:** update cohere, openai, pydantic-ai, and related packages ([f10a05b](https://github.com/unoplat/unoplat-code-confluence/commit/f10a05b64e167a98c9d85aae4b5c3ed184b2ecd3))

## [0.15.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.14.0...unoplat-code-confluence-query-engine-v0.15.0) (2025-09-29)


### Features

* **api:** update AI model config endpoints ([3db21d3](https://github.com/unoplat/unoplat-code-confluence/commit/3db21d3f6ee311c40f416460dd32de1480ca25ae))


### Bug Fixes

* **docker:** update PostgreSQL image and configuration ([e51f4ea](https://github.com/unoplat/unoplat-code-confluence/commit/e51f4eaed01ccb310c3ca2fc4a08dd29d5cb4cb0))

## [0.14.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.13.0...unoplat-code-confluence-query-engine-v0.14.0) (2025-09-26)


### Features

* **ui-optimistic-realtime-updates:** enable real time sync between frontend and backend ([b220132](https://github.com/unoplat/unoplat-code-confluence/commit/b220132e74a693febb56d99a199c54d3e9ca9d60))
* **ui-optimistic-realtime-updates:** enable real time sync between frontend and backend ([629e453](https://github.com/unoplat/unoplat-code-confluence/commit/629e453dd4e84bb118cc4ee67da45380c8479f34))

## [0.13.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.12.0...unoplat-code-confluence-query-engine-v0.13.0) (2025-09-23)


### Features

* move to local sync based workflow for real time updates for agent based workflows ([e4e4288](https://github.com/unoplat/unoplat-code-confluence/commit/e4e4288caed30e80a6417e2837b64e3305e702a4))
* move to local sync based workflow for real time updates for agent based workflows ([bb7970d](https://github.com/unoplat/unoplat-code-confluence/commit/bb7970d56bab6941e2600bb3244bc7b6bfd1f603))

## [0.12.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.11.0...unoplat-code-confluence-query-engine-v0.12.0) (2025-09-17)


### Features

* **agent_md_output:** upgrade unoplat-code-confluence-commons to v0.28.0 and endpoint for retrieval ([1cda97f](https://github.com/unoplat/unoplat-code-confluence/commit/1cda97fab3cf571290940b89415c0942f22b5c64))
* **agent_md_output:** upgrade unoplat-code-confluence-commons to v0.28.0 and endpoint for retrieval ([8c9903b](https://github.com/unoplat/unoplat-code-confluence/commit/8c9903b0e7ab9939c81c1900c6955d9b1f49a9b6))

## [0.11.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.10.0...unoplat-code-confluence-query-engine-v0.11.0) (2025-09-15)


### Features

* **config:** improve config hot reload handling and introduce mock sse endpoint for ui testing as not all providers support prompt caching ([d2d8dcb](https://github.com/unoplat/unoplat-code-confluence/commit/d2d8dcb5952405cd0c5a44718974422a29cb15d9))
* **config:** improve config hot reload handling and introduce mock sse endpoint for ui testing as not all providers support prompt caching ([7808688](https://github.com/unoplat/unoplat-code-confluence/commit/78086884d580d4e90e07732b28ea2ebe24b5287a))
* **experiments:** add mock SSE server ([7808688](https://github.com/unoplat/unoplat-code-confluence/commit/78086884d580d4e90e07732b28ea2ebe24b5287a))


### Bug Fixes

* **models:** correct typo in app_interfaces field ([7808688](https://github.com/unoplat/unoplat-code-confluence/commit/78086884d580d4e90e07732b28ea2ebe24b5287a))

## [0.10.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.9.0...unoplat-code-confluence-query-engine-v0.10.0) (2025-09-15)


### Features

* **local-dependencies-docker-compose.yml:** Bump code-confluence-flow-bridge to 0.51.0 ([3452505](https://github.com/unoplat/unoplat-code-confluence/commit/3452505c79635de89895adddeae51e18c6d6999e))
* **yak/yaak.rq_UvGqPcvBGu.yaml:** Update request name ([3452505](https://github.com/unoplat/unoplat-code-confluence/commit/3452505c79635de89895adddeae51e18c6d6999e))


### Bug Fixes

* Serialize model to JSON in codebase_agent_rules ([8624093](https://github.com/unoplat/unoplat-code-confluence/commit/86240933c3c830ce7615c3e0ee81cf818d64c3ed))
* **unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py:** Exclude optional fields with None values ([3452505](https://github.com/unoplat/unoplat-code-confluence/commit/3452505c79635de89895adddeae51e18c6d6999e))
* **unoplat-code-confluence-query-engine:** Bump version to 0.9.0 ([a3ea5e5](https://github.com/unoplat/unoplat-code-confluence/commit/a3ea5e5a1389cc280a0789238220d09404ed02fe))
* **unoplat-code-confluence-query-engine:** Bump version to 0.9.0 ([3452505](https://github.com/unoplat/unoplat-code-confluence/commit/3452505c79635de89895adddeae51e18c6d6999e))

## [0.9.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.8.0...unoplat-code-confluence-query-engine-v0.9.0) (2025-09-13)


### Features

* introduce retriable client and fixed stale data for provider w.r.t additional arguments ([7551fa9](https://github.com/unoplat/unoplat-code-confluence/commit/7551fa9a1e80519dd7cc24724eedac80ddcc76c3))
* introduce retriable client and fixed stale data for provider w.r.t additional arguments ([c209d2d](https://github.com/unoplat/unoplat-code-confluence/commit/c209d2d1bded1b5c4d968a3edb621578317fd230))

## [0.8.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.7.0...unoplat-code-confluence-query-engine-v0.8.0) (2025-09-10)


### Features

* **agent-prompt:** enhance business logic domain agent ([48ffc7a](https://github.com/unoplat/unoplat-code-confluence/commit/48ffc7a73184c6be50bde8008e3151c5a0de6519))
* **agent-prompt:** enhance business logic domain agent ([7d3c464](https://github.com/unoplat/unoplat-code-confluence/commit/7d3c464f5204e04e99a2343980e41399417f29a9))

## [0.7.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.6.0...unoplat-code-confluence-query-engine-v0.7.0) (2025-09-09)


### Features

* **agent_md_output_development_workflow:** optimise development workflow sub agent ([9cbbd56](https://github.com/unoplat/unoplat-code-confluence/commit/9cbbd5619a5e64af62b216a3dbea6d569b0420b9))
* **agent_md_output_development_workflow:** optimise development workflow sub agent ([86e0e28](https://github.com/unoplat/unoplat-code-confluence/commit/86e0e28c8083a3b692fd288952759ccb99b855d1))

## [0.6.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.5.0...unoplat-code-confluence-query-engine-v0.6.0) (2025-09-09)


### Features

* **codebase-agent-rules:** Update project configuration agent handling ([049b41a](https://github.com/unoplat/unoplat-code-confluence/commit/049b41a6804c1512151428da8d01f12a68abcc61))
* **codebase-agent-rules:** Update project configuration agent handling ([7a35b7c](https://github.com/unoplat/unoplat-code-confluence/commit/7a35b7c591da646c06b7b616273d977638ebee13))
* initial  query engine for agents md ([2e32951](https://github.com/unoplat/unoplat-code-confluence/commit/2e32951845f4652d5f0ae971ad54c8b663fb685a))
* initial  query engine for agents md ([fe17e3d](https://github.com/unoplat/unoplat-code-confluence/commit/fe17e3d6c7ce7ebfa06cd67271da948fb8f10b14))


### Bug Fixes

* git pull explicit no rebase ([dfbbc26](https://github.com/unoplat/unoplat-code-confluence/commit/dfbbc26be5fc790127fb5b731568fa05f119bf9d))
* main entry point ([52126fb](https://github.com/unoplat/unoplat-code-confluence/commit/52126fb65c7169f0c40ed94cdc3fb9dfa9187bac))
* main entry point ([ca93eb5](https://github.com/unoplat/unoplat-code-confluence/commit/ca93eb528a682487ac65d3117e33a56ccb4e92a3))
* update todo simplify the pipeline to read file by file ([2231879](https://github.com/unoplat/unoplat-code-confluence/commit/2231879288439661521c0514a40b089e9214cecf))
* update todo simplify the pipeline to read file by file ([a728e7f](https://github.com/unoplat/unoplat-code-confluence/commit/a728e7f8d0cbef7d24e767b63964ab257e7abbca))

## [0.5.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.4.0...unoplat-code-confluence-query-engine-v0.5.0) (2025-09-09)


### Features

* **codebase-agent-rules:** Update project configuration agent handling ([049b41a](https://github.com/unoplat/unoplat-code-confluence/commit/049b41a6804c1512151428da8d01f12a68abcc61))
* **codebase-agent-rules:** Update project configuration agent handling ([7a35b7c](https://github.com/unoplat/unoplat-code-confluence/commit/7a35b7c591da646c06b7b616273d977638ebee13))
* initial  query engine for agents md ([2e32951](https://github.com/unoplat/unoplat-code-confluence/commit/2e32951845f4652d5f0ae971ad54c8b663fb685a))
* initial  query engine for agents md ([fe17e3d](https://github.com/unoplat/unoplat-code-confluence/commit/fe17e3d6c7ce7ebfa06cd67271da948fb8f10b14))


### Bug Fixes

* git pull explicit no rebase ([dfbbc26](https://github.com/unoplat/unoplat-code-confluence/commit/dfbbc26be5fc790127fb5b731568fa05f119bf9d))
* main entry point ([52126fb](https://github.com/unoplat/unoplat-code-confluence/commit/52126fb65c7169f0c40ed94cdc3fb9dfa9187bac))
* main entry point ([ca93eb5](https://github.com/unoplat/unoplat-code-confluence/commit/ca93eb528a682487ac65d3117e33a56ccb4e92a3))
* update todo simplify the pipeline to read file by file ([2231879](https://github.com/unoplat/unoplat-code-confluence/commit/2231879288439661521c0514a40b089e9214cecf))
* update todo simplify the pipeline to read file by file ([a728e7f](https://github.com/unoplat/unoplat-code-confluence/commit/a728e7f8d0cbef7d24e767b63964ab257e7abbca))

## [0.4.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.3.0...unoplat-code-confluence-query-engine-v0.4.0) (2025-09-09)


### Features

* **codebase-agent-rules:** Update project configuration agent handling ([049b41a](https://github.com/unoplat/unoplat-code-confluence/commit/049b41a6804c1512151428da8d01f12a68abcc61))
* **codebase-agent-rules:** Update project configuration agent handling ([7a35b7c](https://github.com/unoplat/unoplat-code-confluence/commit/7a35b7c591da646c06b7b616273d977638ebee13))
* initial  query engine for agents md ([2e32951](https://github.com/unoplat/unoplat-code-confluence/commit/2e32951845f4652d5f0ae971ad54c8b663fb685a))

### Bug Fixes

* git pull explicit no rebase ([dfbbc26](https://github.com/unoplat/unoplat-code-confluence/commit/dfbbc26be5fc790127fb5b731568fa05f119bf9d))
* main entry point ([52126fb](https://github.com/unoplat/unoplat-code-confluence/commit/52126fb65c7169f0c40ed94cdc3fb9dfa9187bac))


## [0.2.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.2.0...unoplat-code-confluence-query-engine-v0.2.1) (2025-08-30)


### Bug Fixes

* main entry point ([52126fb](https://github.com/unoplat/unoplat-code-confluence/commit/52126fb65c7169f0c40ed94cdc3fb9dfa9187bac))
* main entry point ([ca93eb5](https://github.com/unoplat/unoplat-code-confluence/commit/ca93eb528a682487ac65d3117e33a56ccb4e92a3))

## [0.2.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.1.1...unoplat-code-confluence-query-engine-v0.2.0) (2025-08-30)


### Features

* initial  query engine for agents md ([2e32951](https://github.com/unoplat/unoplat-code-confluence/commit/2e32951845f4652d5f0ae971ad54c8b663fb685a))
* initial  query engine for agents md ([fe17e3d](https://github.com/unoplat/unoplat-code-confluence/commit/fe17e3d6c7ce7ebfa06cd67271da948fb8f10b14))

## [0.1.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.1.0...unoplat-code-confluence-query-engine-v0.1.1) (2025-08-28)


### Bug Fixes

* git pull explicit no rebase ([dfbbc26](https://github.com/unoplat/unoplat-code-confluence/commit/dfbbc26be5fc790127fb5b731568fa05f119bf9d))
