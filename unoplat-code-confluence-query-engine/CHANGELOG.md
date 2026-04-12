# Changelog

## [0.40.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.39.1...unoplat-code-confluence-query-engine-v0.40.0) (2026-04-12)


### Features

* **add-detection-of-inbound-outbound-interfaces:** detect inbound an… ([0da9013](https://github.com/unoplat/unoplat-code-confluence/commit/0da9013c237c09d743e5e4bedee8f9d2076d20af))
* **add-detection-of-inbound-outbound-interfaces:** detect inbound and outbound interfaces ([0f2f866](https://github.com/unoplat/unoplat-code-confluence/commit/0f2f86609970fdcf3dde5386e3698858ba78906c))
* **add-model-provider:** add aws bedrock model provider (manually tested) and added native web search for all providers who do not support native web search or user has not configured exa ([6b2b4a1](https://github.com/unoplat/unoplat-code-confluence/commit/6b2b4a1f6990bcc79b214da749e0ce0d2e245388))
* **Add-model-provider:** aws bedrock support and enhanced cache for … ([aab9fe0](https://github.com/unoplat/unoplat-code-confluence/commit/aab9fe00022af711c9c0255ebc19a7d440518c52))
* **Add-model-provider:** aws bedrock support and enhanced cache for anthropic models on bedrock ([77e0a5e](https://github.com/unoplat/unoplat-code-confluence/commit/77e0a5e4a50003addddf0c4f83cb8862950ad839))
* **add-more-python-typescript-frameworks:** libs/frameworks added ([e632d6f](https://github.com/unoplat/unoplat-code-confluence/commit/e632d6f3438014ccef6f2e64aa236f5a20120860))
* **backend-app-feedback:** endpoint for app feedback ([7faec52](https://github.com/unoplat/unoplat-code-confluence/commit/7faec52256be6d81fd72c654c383ca0551470940))
* **call-expression-validation:** trust definition confidence and validate TS app interfaces ([add97d1](https://github.com/unoplat/unoplat-code-confluence/commit/add97d1449a033351cbe845d833f2692e69af721))
* **cancellation:** implement agent workflow cancellation across backend stack ([3fbf331](https://github.com/unoplat/unoplat-code-confluence/commit/3fbf331efe4d8ba08ef4b5372e9cf45b3feb45c6))
* **codex-oauth:** implement ChatGPT OAuth PKCE flow for Codex provider ([20f209d](https://github.com/unoplat/unoplat-code-confluence/commit/20f209d7c30b56cad1b6c11d09e048c7719f0d74))
* **confidence:** add schema and ingestion contracts for usage confidence metadata ([7596267](https://github.com/unoplat/unoplat-code-confluence/commit/7596267baabf9c902144b5bf4baa5c647cb3a7b5))
* **delete-model-config:** add UI to delete active model provider configuration ([227f030](https://github.com/unoplat/unoplat-code-confluence/commit/227f0307f89dbb4b6c6745cf586d7c983abd9e8f))
* **dependency-filter:** restrict dependency discovery to runtime-only group ([cee7605](https://github.com/unoplat/unoplat-code-confluence/commit/cee760500d34fdb7ac7eda2ffb264e51169419c6))
* **engineering-workflow:** simplify output schema and improve system prompts ([feaf516](https://github.com/unoplat/unoplat-code-confluence/commit/feaf5164551e8db16cc91ffb554cb6cc4a1ab5a6))
* **improved-development-workflow-agent-harness:** improved development workflow agent harness ([9fb1868](https://github.com/unoplat/unoplat-code-confluence/commit/9fb18683888648ad51e4689771343d93dabdba54))
* **migrate-postgres:** ingestion and query engine services ([91c760f](https://github.com/unoplat/unoplat-code-confluence/commit/91c760f326f452dda6cfff12f6865f577da1ca1f))
* **observability:** enhance event stream debugging and engineering workflow completion ([77ddaf7](https://github.com/unoplat/unoplat-code-confluence/commit/77ddaf72f393de7688db081bed23378122722dab))
* **query-engine-agents-md:** introduce dependency guide agent and also removed agent with context as we migrated to exa mcp tool. Also moved to pydantic fastmcp client for mcp servers ([66abe80](https://github.com/unoplat/unoplat-code-confluence/commit/66abe80f79e11402f749216c0b1b3de8e17ec666))
* **query-engine:** add agents-md updater agent with section-scoped tools and tests ([d883a00](https://github.com/unoplat/unoplat-code-confluence/commit/d883a00d311c6a0abaeb5909c75f2f7960ab593e))
* **query-engine:** add managed block bootstrap and git ref resolution for AGENTS.md ([24bcab8](https://github.com/unoplat/unoplat-code-confluence/commit/24bcab8dcbd94f93a75091c8fcb09b58ab76db2f))
* **query-engine:** add POST/GET repository-agent-md-pr endpoints with one-shot semantics ([d648bbb](https://github.com/unoplat/unoplat-code-confluence/commit/d648bbb9256b9d71c004f47d99cf1250c4a8875d))
* **query-engine:** adopt structured framework feature identity and remove dead baseline service ([cdd43a1](https://github.com/unoplat/unoplat-code-confluence/commit/cdd43a119b2eb60369e494114b91e840bfe94eae))
* **temporal:** add agent_assembly package with catalog, assembler, and agent definitions ([c4e0a66](https://github.com/unoplat/unoplat-code-confluence/commit/c4e0a66aecf20e2c6a4e80d192b19d5d6ac46e93))
* **typescript-beta:** strengthen typescript grammar detection and in… ([f6fbc5b](https://github.com/unoplat/unoplat-code-confluence/commit/f6fbc5b89febdec73ff1b65ab3bbfd34f1807986))
* **typescript-beta:** strengthen typescript grammar detection and include next js endpoint detection as a starting example ([ea440b2](https://github.com/unoplat/unoplat-code-confluence/commit/ea440b2ab090e035dfabea58ac7b62628557c125))
* **validation-spec-implementation:** introducing llm based validator for low confidence matches to ensure defects introduced through dids are rectified ([825fde8](https://github.com/unoplat/unoplat-code-confluence/commit/825fde8b8c4d553d996a3a203042520285452117))
* **validation-spec-implementation:** introducing llm based validator… ([08bb72c](https://github.com/unoplat/unoplat-code-confluence/commit/08bb72c415ee1ef7650035f9e6e4ca7cbaa1e589))
* **web-search:** support built-in web search for providers with native capability ([15a7558](https://github.com/unoplat/unoplat-code-confluence/commit/15a7558c6c4557c2d6612b45f6ab2a1768590fe4))


### Bug Fixes

* add utility that helps safe logging showing only first/last few chars of sensitive information ([570c8cb](https://github.com/unoplat/unoplat-code-confluence/commit/570c8cb01a3d82f2889c0e346df6af4560c7f61a))
* **agent-description:** improve system prompts and tool descriptions … ([0f6e3e7](https://github.com/unoplat/unoplat-code-confluence/commit/0f6e3e79b15ee1b485dca113b68c0a79f45799c8))
* **agent-description:** improve system prompts and tool descriptions and add output validator for open source models to work reliably. solved issues with minmax2.1 ([c9beb73](https://github.com/unoplat/unoplat-code-confluence/commit/c9beb73ae05c50b45ff88f84cb5b526273521803))
* **agent-md-section:** duplicate information across corresponding art… ([6e8fbae](https://github.com/unoplat/unoplat-code-confluence/commit/6e8fbae4e0bd64c2fdc76ff2b84dce49731061f3))
* **agent-md-section:** duplicate information across corresponding artifacts and agents.md ([0247a1e](https://github.com/unoplat/unoplat-code-confluence/commit/0247a1ebc92a10af32ba5ce34ed3ba97bd3b0b9f))
* **agent-names:** simplify agent names ([ef041e9](https://github.com/unoplat/unoplat-code-confluence/commit/ef041e9eb070578e99b64b4c5e34ae649e944488))
* **agents:** raise confidence threshold to 0.70 ([bed7dbd](https://github.com/unoplat/unoplat-code-confluence/commit/bed7dbd3a378e3c8bdfbc209625e80dfd4aa7d89))
* **bedrock:** stale key fix ([7643ce6](https://github.com/unoplat/unoplat-code-confluence/commit/7643ce6d4bca554ae2c15597655124008519f5e6))
* **binding-address:** change binding address back to 127.0.0.1 ([4a7f735](https://github.com/unoplat/unoplat-code-confluence/commit/4a7f735360088cb37cfac94e09a986894405fdfd))
* **chore:** add comment to release query engine docker ([fb9a470](https://github.com/unoplat/unoplat-code-confluence/commit/fb9a470a2761ab2a617dd3e73b56ae220a5a43ff))
* **chore:** comments to typescript implementation ([f1a60c0](https://github.com/unoplat/unoplat-code-confluence/commit/f1a60c084d8b3ef2b7c583995dc2a3be049c491d))
* **chore:** comments to typescript implementation ([fa967f6](https://github.com/unoplat/unoplat-code-confluence/commit/fa967f676a63b48832e668fd7fad3d4b1156d00b))
* **ci:** early detection of stale uv lock ([a55e860](https://github.com/unoplat/unoplat-code-confluence/commit/a55e860bebb584baaae80431768f96573f12147c))
* **ci:** refresh package uv lockfiles before python lock checks run ([4d956c7](https://github.com/unoplat/unoplat-code-confluence/commit/4d956c7a61ac42e3e6c50e8b8f1d01f9992a0c80))
* **ci:** refresh package uv lockfiles before python lock checks run ([3abd05a](https://github.com/unoplat/unoplat-code-confluence/commit/3abd05a7d650224e5070b5a8dd12bf4d3beb3f17))
* **ci:** refresh package uv lockfiles before python lock checks run ([c698a73](https://github.com/unoplat/unoplat-code-confluence/commit/c698a73fa80dba6115ecdb8a59033ca14b75540d))
* **ci:** refresh package uv lockfiles before python lock checks run ([8136498](https://github.com/unoplat/unoplat-code-confluence/commit/81364983bc95393ecdb100289d35fd00d69d46bb))
* **ci:** refresh package uv lockfiles before python lock checks run ([8575e45](https://github.com/unoplat/unoplat-code-confluence/commit/8575e45a6c990e25643d9207f4af8fd306f7ee60))
* code smells for model factory ([6b5e8d9](https://github.com/unoplat/unoplat-code-confluence/commit/6b5e8d9e0e18d530afad8d07f6cccead4c7fdfd0))
* **codebase-detection:** propagate workspace metadata through query engine models and services ([58dc98a](https://github.com/unoplat/unoplat-code-confluence/commit/58dc98ab0a6b27aded6e57128d6931405b94eb9d))
* **comments:** adding comment to trigger docker build ([bc3f037](https://github.com/unoplat/unoplat-code-confluence/commit/bc3f03766d5f924cdd814f96e90cf99424c45fe1))
* **comments:** adding comment to trigger docker build ([4712295](https://github.com/unoplat/unoplat-code-confluence/commit/4712295138740e81012b35cd5403e311f5eb59f0))
* **date-time-fixes-backend:** offset fixes ([42ada4a](https://github.com/unoplat/unoplat-code-confluence/commit/42ada4abf531bfbe4f353b3392d1e803ec0b5d40))
* **dependencies:** get rid of unused dependencies - neomodel ([1684a3f](https://github.com/unoplat/unoplat-code-confluence/commit/1684a3fd7c5cf9378d58009ad24c60ad6075a119))
* **dependencies:** split dependency guides into dedicated overview files ([2c7b347](https://github.com/unoplat/unoplat-code-confluence/commit/2c7b347b92ae2ba9018c4d7ee03131fe182b4a57))
* **dependency-version:** commons dependency version with model update… ([9cc244b](https://github.com/unoplat/unoplat-code-confluence/commit/9cc244bac5812d7bdf95dc118a67dc0370270f06))
* **dependency-version:** commons dependency version with model updates for ingestion/query services ([fd2ebdc](https://github.com/unoplat/unoplat-code-confluence/commit/fd2ebdc35410a1741eda44b29f0814ac8b2c7ec9))
* **docker:** pin uv image version for deterministic builds ([2cfe11d](https://github.com/unoplat/unoplat-code-confluence/commit/2cfe11d7590ea9a2bf537461986da15cecea1336))
* **docker:** pin uv image version for deterministic builds ([681624b](https://github.com/unoplat/unoplat-code-confluence/commit/681624b30f94c8aee9f6969f61d277aebc7c3763))
* **error-logging-model-provider:** enhance error details for model pr… ([bdcbe39](https://github.com/unoplat/unoplat-code-confluence/commit/bdcbe39470cca4a2c2c88b7e0d1082ed6fb48093))
* **error-logging-model-provider:** enhance error details for model provider issues ([a7058b5](https://github.com/unoplat/unoplat-code-confluence/commit/a7058b5eba90c50b151b71c30a37ca8270c7be1f))
* **file-update-tool:** enrich updater_apply_patch docstring with full patch format spec and add parser resilience ([5a78aaf](https://github.com/unoplat/unoplat-code-confluence/commit/5a78aaf42dcea393087cc059baf5c9a394688a35))
* **improve-system-prompt:** improve system prompt for getting library information to work more reliably with open source models ([c61d9ec](https://github.com/unoplat/unoplat-code-confluence/commit/c61d9ec74301fd152738f52dda2707893dc7558e))
* **mandatory-regional-argument:** region is not mandatory for bedrock ([9410252](https://github.com/unoplat/unoplat-code-confluence/commit/9410252a9374093e6f96c3c983a80be8390b55a7))
* **mcp-migration:** migration from standard fastapi mcp client ([2357d1b](https://github.com/unoplat/unoplat-code-confluence/commit/2357d1b0483866dcb3aceaee8bdfbfbb12b1cce7))
* **networking:** networking fixes for callback listener ([d06c416](https://github.com/unoplat/unoplat-code-confluence/commit/d06c416d17ccdfd39f2f8f0151c1004288cc3e73))
* **optimise-framework-schema:** switch ingestion and query paths to J… ([fd3046f](https://github.com/unoplat/unoplat-code-confluence/commit/fd3046f268168fd57d7d4f8bcfc2c2c2269fd5c3))
* **optimise-framework-schema:** switch ingestion and query paths to JSONB feature payload ([c3a44a2](https://github.com/unoplat/unoplat-code-confluence/commit/c3a44a2876937eec34a52490c23d8ff17c89e54b))
* **overhaul-events-view:** make it intuitve and store upto 100k of to… ([8821089](https://github.com/unoplat/unoplat-code-confluence/commit/8821089369d70bbc7ed55514fb6747691b329753))
* **overhaul-events-view:** make it intuitve and store upto 100k of tool result calls ([ec62f7f](https://github.com/unoplat/unoplat-code-confluence/commit/ec62f7ff904af8b789635000fe2e27ef843bded6))
* **overhaul-events-view:** make it intuitve and store upto 100k of tool result calls ([49fa302](https://github.com/unoplat/unoplat-code-confluence/commit/49fa302695585b9fcbaf5b103f835de11ef032e7))
* **perf:** virtual list and 3-phase schema for realtime sync using electric sql ([d4db047](https://github.com/unoplat/unoplat-code-confluence/commit/d4db047c9b8096f0ac5ecb3f3d9748907dcc78e9))
* **query-engine-docker-fixes:** docker cache optimisation and update commons version ([b572418](https://github.com/unoplat/unoplat-code-confluence/commit/b572418b5438754a99bc93e15708a9e3cbb47a24))
* **query-engine-test:** align snapshot tests with normalized event schema ([f82d539](https://github.com/unoplat/unoplat-code-confluence/commit/f82d539d137b1787b8ccd408246d8cac42240fdc))
* **query-engine-test:** breaking changes due to test containers v4 api ([8ba47d1](https://github.com/unoplat/unoplat-code-confluence/commit/8ba47d113a66326c6a0502e7332743f54fc4ab47))
* **query-engine:** add rest_api and scheduler to inbound feature mapping ([fef26e1](https://github.com/unoplat/unoplat-code-confluence/commit/fef26e1af4100ad90f4573b107c7163684af05a2))
* **query-engine:** scope monorepo toolset to TypeScript and enforce repo-root-relative config_file paths ([18d7e95](https://github.com/unoplat/unoplat-code-confluence/commit/18d7e952720c7a1235494885029d7073f71a7916))
* **query-engine:** update package description ([6a73d08](https://github.com/unoplat/unoplat-code-confluence/commit/6a73d08cafd27cd299fcf5c5da0f3dd950eb479c))
* **read-tool-call-pagination-issue:** align updater read clamp and no-op semantics ([df93429](https://github.com/unoplat/unoplat-code-confluence/commit/df9342981733438038f8bd91c830a01531a59660))
* **read-tool-call-pagination-issue:** align updater read clamp and no… ([a149c80](https://github.com/unoplat/unoplat-code-confluence/commit/a149c8067e9ae45ba8fb33d4b9284ce930d450af))
* **refactor:** reorganize temporal into modular packages and update all imports ([98dd777](https://github.com/unoplat/unoplat-code-confluence/commit/98dd777e6afdada73c26d66c045d45a21de5eef3))
* **stale-lock:** lock update ([85aa7d1](https://github.com/unoplat/unoplat-code-confluence/commit/85aa7d11bef394cff042f7573e41247e0dcf840e))
* **tool-retries:** increased tool retries and improved griffe based d… ([02def05](https://github.com/unoplat/unoplat-code-confluence/commit/02def05d12e3b922b44aa76a718bda416bfb7d7d))
* **tool-retries:** increased tool retries and improved griffe based description for open source models to make fewer mistakes ([7584f86](https://github.com/unoplat/unoplat-code-confluence/commit/7584f8629587a0eb1eeead9c9bf80e6556bc9f45))
* **typescript:** add concept enum in schema to support more typescript ([9bd1861](https://github.com/unoplat/unoplat-code-confluence/commit/9bd1861df81ce67135e3cb0d1a3a96dfc7ffc548))
* **typescript:** add concept enum in schema to support more typescript ([6642161](https://github.com/unoplat/unoplat-code-confluence/commit/66421610f5f7d68e378e8bdd4c41ec204b59a1a6))
* **ui-dependencies:** reduce dependency token churn by introducing fa… ([a66310b](https://github.com/unoplat/unoplat-code-confluence/commit/a66310bb3aa3403850ccdf3a22e9ea32034798fa))
* **ui-dependencies:** reduce dependency token churn by introducing family level filter for ui components' libs ([ee7ee24](https://github.com/unoplat/unoplat-code-confluence/commit/ee7ee24dccf22ba877ff86613240e62bf8675990))
* **wrong-version-commons:** upgrade commons version across flow bridg… ([a55fa82](https://github.com/unoplat/unoplat-code-confluence/commit/a55fa82f810b170370225ee9425642f7ce329d58))
* **wrong-version-commons:** upgrade commons version across flow bridge and query engine components to enable pr related functionality ([84ec4f9](https://github.com/unoplat/unoplat-code-confluence/commit/84ec4f9f5184ddcebc4367a35e517ff88fd6a3ff))


### Documentation

* **agents:** split dependency guides into dedicated overview files ([b63ab1c](https://github.com/unoplat/unoplat-code-confluence/commit/b63ab1c89f8e89e34095f16632e769b1af04a727))

## [0.39.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.39.0...unoplat-code-confluence-query-engine-v0.39.1) (2026-03-17)


### Bug Fixes

* **agent-md-section:** duplicate information across corresponding art… ([1ef311d](https://github.com/unoplat/unoplat-code-confluence/commit/1ef311ddc5d956880cb26501507bf419da32613c))
* **agent-md-section:** duplicate information across corresponding artifacts and agents.md ([333e1cd](https://github.com/unoplat/unoplat-code-confluence/commit/333e1cdb91ed8a2e6d66d61fadcf5a5dfe9cd879))

## [0.39.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.38.0...unoplat-code-confluence-query-engine-v0.39.0) (2026-03-13)


### Features

* **query-engine:** add managed block bootstrap and git ref resolution for AGENTS.md ([6d449f9](https://github.com/unoplat/unoplat-code-confluence/commit/6d449f90095d9070b372df5a7c4b5fa46a2d17ef))

## [0.38.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.37.6...unoplat-code-confluence-query-engine-v0.38.0) (2026-03-13)


### Features

* **cancellation:** implement agent workflow cancellation across backend stack ([0106cdf](https://github.com/unoplat/unoplat-code-confluence/commit/0106cdf07d0af116747adb1e5cb59f1268ff2ea9))

## [0.37.6](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.37.5...unoplat-code-confluence-query-engine-v0.37.6) (2026-03-09)


### Bug Fixes

* **ci:** refresh package uv lockfiles before python lock checks run ([f736085](https://github.com/unoplat/unoplat-code-confluence/commit/f736085fe502ab03370598987ab396324f23eba8))
* **comments:** adding comment to trigger docker build ([e45f67b](https://github.com/unoplat/unoplat-code-confluence/commit/e45f67bd8713041f6cc091805094669a5f86cf9f))
* **comments:** adding comment to trigger docker build ([20636cb](https://github.com/unoplat/unoplat-code-confluence/commit/20636cb932bf346231306311bbe90061bd98e67e))

## [0.37.5](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.37.4...unoplat-code-confluence-query-engine-v0.37.5) (2026-03-09)


### Bug Fixes

* **chore:** add comment to release query engine docker ([398a17b](https://github.com/unoplat/unoplat-code-confluence/commit/398a17b0db044133dc239e55938793d14eba1a6d))
* **ci:** early detection of stale uv lock ([d0aced9](https://github.com/unoplat/unoplat-code-confluence/commit/d0aced9a1688bea976070aca6adeeb45d13b4282))
* **stale-lock:** lock update ([091085d](https://github.com/unoplat/unoplat-code-confluence/commit/091085d861acc433ffc212f02e896a16ed4cf8b4))

## [0.37.4](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.37.3...unoplat-code-confluence-query-engine-v0.37.4) (2026-03-09)


### Bug Fixes

* **chore:** comments to typescript implementation ([0c9776f](https://github.com/unoplat/unoplat-code-confluence/commit/0c9776fb2795c9e2095dc951559e07f859e5b039))
* **chore:** comments to typescript implementation ([bd437f2](https://github.com/unoplat/unoplat-code-confluence/commit/bd437f24ff0ad14fc91800e97e33652ab1f60fad))

## [0.37.3](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.37.2...unoplat-code-confluence-query-engine-v0.37.3) (2026-03-09)


### Bug Fixes

* **docker:** pin uv image version for deterministic builds ([98fff39](https://github.com/unoplat/unoplat-code-confluence/commit/98fff397dacbc16d979cbf22b6cac375d8c016d7))
* **docker:** pin uv image version for deterministic builds ([dfe02f0](https://github.com/unoplat/unoplat-code-confluence/commit/dfe02f0a57aa35d4bd96fa95f448cb82e883fa70))

## [0.37.2](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.37.1...unoplat-code-confluence-query-engine-v0.37.2) (2026-03-09)


### Bug Fixes

* **query-engine-docker-fixes:** docker cache optimisation and update commons version ([e7bb376](https://github.com/unoplat/unoplat-code-confluence/commit/e7bb37698dd2a57591b9f9f57c5ffba58170ceaf))

## [0.37.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.37.0...unoplat-code-confluence-query-engine-v0.37.1) (2026-03-08)


### Bug Fixes

* **file-update-tool:** enrich updater_apply_patch docstring with full patch format spec and add parser resilience ([30e72ea](https://github.com/unoplat/unoplat-code-confluence/commit/30e72ea5bff9c21da0f85b6a8eb245af72a6556d))
* **perf:** virtual list and 3-phase schema for realtime sync using electric sql ([5748960](https://github.com/unoplat/unoplat-code-confluence/commit/5748960ac9a2b98792cee3ff715c412a3c1dfb3b))
* **query-engine-test:** align snapshot tests with normalized event schema ([7d27081](https://github.com/unoplat/unoplat-code-confluence/commit/7d270816929bd0ae778ddd4636718f3fd4ffdfff))
* **ui-dependencies:** reduce dependency token churn by introducing fa… ([5473831](https://github.com/unoplat/unoplat-code-confluence/commit/5473831a81739551d76eeea2bee906cab8ea5edf))
* **ui-dependencies:** reduce dependency token churn by introducing family level filter for ui components' libs ([1722e08](https://github.com/unoplat/unoplat-code-confluence/commit/1722e089775a339a23fccc64c1b166ecb0d070f9))

## [0.37.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.36.0...unoplat-code-confluence-query-engine-v0.37.0) (2026-03-08)


### Features

* **call-expression-validation:** trust definition confidence and validate TS app interfaces ([febc30f](https://github.com/unoplat/unoplat-code-confluence/commit/febc30fdaba1727a1b55dc08964fcb258b12fe87))

## [0.36.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.35.0...unoplat-code-confluence-query-engine-v0.36.0) (2026-03-06)


### Features

* **backend-app-feedback:** endpoint for app feedback ([3db4b77](https://github.com/unoplat/unoplat-code-confluence/commit/3db4b776f6e953e20d5fd69ea92c7d9d94443856))

## [0.35.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.34.2...unoplat-code-confluence-query-engine-v0.35.0) (2026-03-03)


### Features

* **add-detection-of-inbound-outbound-interfaces:** detect inbound an… ([69d3000](https://github.com/unoplat/unoplat-code-confluence/commit/69d300018c9205e948028368e3c11cec198defc1))
* **add-detection-of-inbound-outbound-interfaces:** detect inbound and outbound interfaces ([8c36c1d](https://github.com/unoplat/unoplat-code-confluence/commit/8c36c1d2363235e1cfdda4f3c004da8252b9ea88))
* **add-model-provider:** add aws bedrock model provider (manually tested) and added native web search for all providers who do not support native web search or user has not configured exa ([80336ed](https://github.com/unoplat/unoplat-code-confluence/commit/80336edfb27dc9e63049dba9e7d5efdf39123067))
* **Add-model-provider:** aws bedrock support and enhanced cache for … ([c7841bf](https://github.com/unoplat/unoplat-code-confluence/commit/c7841bff3b2e9de07a2ed042b98761ca6bfdaeaa))
* **Add-model-provider:** aws bedrock support and enhanced cache for anthropic models on bedrock ([13dccc3](https://github.com/unoplat/unoplat-code-confluence/commit/13dccc3e510a6f5930c9fea3ae85cf601b0c08d3))
* **codex-oauth:** implement ChatGPT OAuth PKCE flow for Codex provider ([9891b8e](https://github.com/unoplat/unoplat-code-confluence/commit/9891b8e7c0bf2bf46c2176d34722f484d22a1d31))
* **confidence:** add schema and ingestion contracts for usage confidence metadata ([f71b085](https://github.com/unoplat/unoplat-code-confluence/commit/f71b085d653de9c339f0ffb615a4d07863fadd98))
* **delete-model-config:** add UI to delete active model provider configuration ([81a46f6](https://github.com/unoplat/unoplat-code-confluence/commit/81a46f68189d669bd1718617865bd6b3cd44d413))
* **dependency-filter:** restrict dependency discovery to runtime-only group ([b54d554](https://github.com/unoplat/unoplat-code-confluence/commit/b54d55459fa782e2e58ea68c659bbdf5cd5014f3))
* **engineering-workflow:** simplify output schema and improve system prompts ([e8b970e](https://github.com/unoplat/unoplat-code-confluence/commit/e8b970ef7e81fe0000f23306528fc6cc596b9eb9))
* first draft of reliable auditable agent ([8a361c6](https://github.com/unoplat/unoplat-code-confluence/commit/8a361c611e97162dfb0a755bfce3a858042db491))
* first draft of reliable auditable agents ([9fc6eee](https://github.com/unoplat/unoplat-code-confluence/commit/9fc6eeec90432442d06742f223fde22606ff6c88))
* **improved-development-workflow-agent-harness:** improved development workflow agent harness ([226bcc5](https://github.com/unoplat/unoplat-code-confluence/commit/226bcc5a2ae783cfe3dae7967705ccba97d9e77b))
* **migrate-postgres:** ingestion and query engine services ([06edb7f](https://github.com/unoplat/unoplat-code-confluence/commit/06edb7fb05997754e73f5ba2104b8a764cba5e79))
* **observability:** enhance event stream debugging and engineering workflow completion ([595a363](https://github.com/unoplat/unoplat-code-confluence/commit/595a3636c67dc4b6347eb1fc2ed4bd2eab0ab6d0))
* **query-engine-agents-md:** introduce dependency guide agent and also removed agent with context as we migrated to exa mcp tool. Also moved to pydantic fastmcp client for mcp servers ([a3e6788](https://github.com/unoplat/unoplat-code-confluence/commit/a3e6788a54cbf5672967eafd142093d077d559a9))
* **query-engine:** add agents-md updater agent with section-scoped tools and tests ([a493c50](https://github.com/unoplat/unoplat-code-confluence/commit/a493c5044474385cffb0eea1e7c77a88c61c33fa))
* **query-engine:** add POST/GET repository-agent-md-pr endpoints with one-shot semantics ([d4945c3](https://github.com/unoplat/unoplat-code-confluence/commit/d4945c382ab87b955aa4a84924578624478b3de9))
* **typescript-beta:** strengthen typescript grammar detection and in… ([2a673ec](https://github.com/unoplat/unoplat-code-confluence/commit/2a673ec26aafd42c5a625f501af2242c41286e39))
* **typescript-beta:** strengthen typescript grammar detection and include next js endpoint detection as a starting example ([0489d94](https://github.com/unoplat/unoplat-code-confluence/commit/0489d94e0d4f3b72c3ac43859f7d97b54a3cc7c4))
* **validation-spec-implementation:** introducing llm based validator for low confidence matches to ensure defects introduced through dids are rectified ([05c1bb9](https://github.com/unoplat/unoplat-code-confluence/commit/05c1bb95481bf32e27fac39bad106ecbb84d8ba4))
* **validation-spec-implementation:** introducing llm based validator… ([ffddafb](https://github.com/unoplat/unoplat-code-confluence/commit/ffddafb41dd10abff0429470f45064a25e3a1d36))
* **web-search:** support built-in web search for providers with native capability ([05814a3](https://github.com/unoplat/unoplat-code-confluence/commit/05814a3ae675f33db50eac35e32a0f397c0582f6))


### Bug Fixes

* add utility that helps safe logging showing only first/last few chars of sensitive information ([1fdc947](https://github.com/unoplat/unoplat-code-confluence/commit/1fdc947fb78a83ba59c391956e0051f6fbf984a5))
* agent md persistence ([348b4d4](https://github.com/unoplat/unoplat-code-confluence/commit/348b4d440e05949fd24606dd6f3f1f72730d477c))
* **agent-description:** improve system prompts and tool descriptions … ([780b624](https://github.com/unoplat/unoplat-code-confluence/commit/780b624e5af02767bceb7212d8c62a43e2be511f))
* **agent-description:** improve system prompts and tool descriptions and add output validator for open source models to work reliably. solved issues with minmax2.1 ([8cb0968](https://github.com/unoplat/unoplat-code-confluence/commit/8cb096893c72b8626968234218b1a36db7367cf6))
* **agent-names:** simplify agent names ([0197723](https://github.com/unoplat/unoplat-code-confluence/commit/0197723b49549067ad930bf3a74cf9adc3da800f))
* alter tests fail cases (now being handled by workflow orchestrator) ([abb94f9](https://github.com/unoplat/unoplat-code-confluence/commit/abb94f93315ce17167955b05ab8d038be11e82eb))
* automatic error capture post exhausion of retries during ai work… ([415de05](https://github.com/unoplat/unoplat-code-confluence/commit/415de05f4c9785afe22264d5439f20f2819a19e8))
* automatic error capture post exhausion of retries during ai workflow for user to easily submit github issues with all details ([af42e1f](https://github.com/unoplat/unoplat-code-confluence/commit/af42e1f35d9ceb03462fd706f27d12b89ad32940))
* **bedrock:** stale key fix ([1e211ff](https://github.com/unoplat/unoplat-code-confluence/commit/1e211ff94e6910486ecf7c94325a000b2fee6d31))
* **binding-address:** change binding address back to 127.0.0.1 ([fc41fe4](https://github.com/unoplat/unoplat-code-confluence/commit/fc41fe4c18038466f5a883e629a6b3048685f8bc))
* code smells for model factory ([6de23a7](https://github.com/unoplat/unoplat-code-confluence/commit/6de23a7a0ab6b0c13d9e4e487519024ceeed6163))
* **connection-pool-recommendation-settings:** reuse stale connections and increase connection pool for postgres ([2935799](https://github.com/unoplat/unoplat-code-confluence/commit/2935799a5a1c160ebba5b6da76d4adbdcd73eadf))
* **date-time-fixes-backend:** offset fixes ([87165db](https://github.com/unoplat/unoplat-code-confluence/commit/87165dbc25ebda76a48cb1e4ca6cbf3cd1ebaee6))
* **dependencies:** get rid of unused dependencies - neomodel ([61e42a2](https://github.com/unoplat/unoplat-code-confluence/commit/61e42a202a7981a7e8cc1347e0b60e40131371ec))
* **dependencies:** split dependency guides into dedicated overview files ([77ee463](https://github.com/unoplat/unoplat-code-confluence/commit/77ee463fb1566ff4e96b337dab808371a57ed4dd))
* **dependency-version:** commons dependency version with model update… ([dbdd027](https://github.com/unoplat/unoplat-code-confluence/commit/dbdd02708a379d3277d50f62e19d3934ef4a82fe))
* **dependency-version:** commons dependency version with model updates for ingestion/query services ([890f4ca](https://github.com/unoplat/unoplat-code-confluence/commit/890f4cad1d3a5aaa3e1f4119f4ce122ab54b9d0d))
* **deps-version:** pin common lib dependencies version to latest ([e5d5db2](https://github.com/unoplat/unoplat-code-confluence/commit/e5d5db2c358fee88b4afae35ff7a8a68807836de))
* **deps-version:** pin common lib dependencies version to latest ([ed5b60f](https://github.com/unoplat/unoplat-code-confluence/commit/ed5b60f70f0ae254ea2a583a10f13a53b2df4740))
* **error-logging-model-provider:** enhance error details for model pr… ([a1633b9](https://github.com/unoplat/unoplat-code-confluence/commit/a1633b94475f1ce7b0f2ac466a294ac8aec5e052))
* **error-logging-model-provider:** enhance error details for model provider issues ([1c9298b](https://github.com/unoplat/unoplat-code-confluence/commit/1c9298bf65d007308e80b6180f9a50df09474b20))
* **improve-system-prompt:** improve system prompt for getting library information to work more reliably with open source models ([469a8e1](https://github.com/unoplat/unoplat-code-confluence/commit/469a8e10a411418197b3d4fbecdcfddf8868675a))
* improving ai engine structure (first step towards improving prim… ([9e5b00b](https://github.com/unoplat/unoplat-code-confluence/commit/9e5b00bfad87027198fb51a9c5f6696e0dc4df44))
* improving ai engine structure (first step towards improving primitives) ([b2950bc](https://github.com/unoplat/unoplat-code-confluence/commit/b2950bccba8c034b175a407eddd65599f4d666c0))
* insert based on repository workflow run id ([0a298b4](https://github.com/unoplat/unoplat-code-confluence/commit/0a298b4e00864e6b116198b4aeffaa02f480e41a))
* **mandatory-regional-argument:** region is not mandatory for bedrock ([729f4f7](https://github.com/unoplat/unoplat-code-confluence/commit/729f4f7f53959dd0b0ce93531d112c92ed08236d))
* **mcp-migration:** migration from standard fastapi mcp client ([9a87bb9](https://github.com/unoplat/unoplat-code-confluence/commit/9a87bb91d645868fd36397162800ba326af1d283))
* **mcp-toolset-fix:** fix for getting library data ([9540acf](https://github.com/unoplat/unoplat-code-confluence/commit/9540acfeb17a917d6eac40026c9d838af971a07a))
* **model-config:** do two phase operation for model config upsert and worker upgrade ensuring one does not affect anothert ([bd3be65](https://github.com/unoplat/unoplat-code-confluence/commit/bd3be653a203385e43fcd338a346c66bab053727))
* **networking:** networking fixes for callback listener ([4edec57](https://github.com/unoplat/unoplat-code-confluence/commit/4edec57361e84da54b09aa4d1066467d65361dc9))
* **optimise-framework-schema:** switch ingestion and query paths to J… ([be0462c](https://github.com/unoplat/unoplat-code-confluence/commit/be0462c8bc0df22458dfff7026288b145370a38c))
* **optimise-framework-schema:** switch ingestion and query paths to JSONB feature payload ([c2f6c15](https://github.com/unoplat/unoplat-code-confluence/commit/c2f6c153a6694666806fadb867652d56ab616472))
* **overhaul-events-view:** make it intuitve and store upto 100k of to… ([0092204](https://github.com/unoplat/unoplat-code-confluence/commit/00922043a7145963859d0f3df8cb6f1f0d5f4206))
* **overhaul-events-view:** make it intuitve and store upto 100k of tool result calls ([0b08bbd](https://github.com/unoplat/unoplat-code-confluence/commit/0b08bbdd301bd9f00284a76f93ecea2fe83dc860))
* **overhaul-events-view:** make it intuitve and store upto 100k of tool result calls ([844b782](https://github.com/unoplat/unoplat-code-confluence/commit/844b782f8ffba60fefa2a2aeb40b486659df1ecd))
* **perf:** parallelism per codebase agent md in monorepo ([d71e0e4](https://github.com/unoplat/unoplat-code-confluence/commit/d71e0e4d19fe2ec8ba6707e098ed36a58969676f))
* **perf:** parallelism per codebase agent md in monorepo ([7ae3ad8](https://github.com/unoplat/unoplat-code-confluence/commit/7ae3ad8c98612cd30e52753b7b0d78f3442beb14))
* **post-processing-business-domain:** workflow orchestrator services/worker responsibilities clean up and post processing fix for agent md ([d21c465](https://github.com/unoplat/unoplat-code-confluence/commit/d21c4655328e29a6cbde1e98f1638834e199a768))
* **query-engine-test:** breaking changes due to test containers v4 api ([d0e401b](https://github.com/unoplat/unoplat-code-confluence/commit/d0e401b760114d5bf739c54283b7885e74e990eb))
* **read-tool-call-pagination-issue:** align updater read clamp and no-op semantics ([e108880](https://github.com/unoplat/unoplat-code-confluence/commit/e108880d340ef26dd89e4cdc5be872e319e7c9ab))
* **read-tool-call-pagination-issue:** align updater read clamp and no… ([b6574a0](https://github.com/unoplat/unoplat-code-confluence/commit/b6574a0f826f44dfe3f9f1cf59d1543e053e21b8))
* regression for package manager and programming language metadata ([5b705e9](https://github.com/unoplat/unoplat-code-confluence/commit/5b705e91ac4d308fd588cc30ee8b33026bd1b477))
* **regression-eza:** add eza to dockerfile of query engine for direct… ([d1bbd38](https://github.com/unoplat/unoplat-code-confluence/commit/d1bbd3874a7ba3566bd331cda522aa72b50b5a90))
* **regression-eza:** add eza to dockerfile of query engine for directory tree tool and remove old commented code ([4282fea](https://github.com/unoplat/unoplat-code-confluence/commit/4282feaa9f61b20211c99b22346710eda405492a))
* removal of duplicate status column for agent snapshot tracking ([24d2b40](https://github.com/unoplat/unoplat-code-confluence/commit/24d2b40642643eb149db68fbeae2a4bbbf6a610e))
* statistics calculation ([d549274](https://github.com/unoplat/unoplat-code-confluence/commit/d5492746c114bcee255dc3e12c04f2789d586123))
* statistics persistence ([6c03e05](https://github.com/unoplat/unoplat-code-confluence/commit/6c03e0587775fb5e8e7c8c2e102f7ec3e2184d4d))
* test with repository workflow run id ([d011ed7](https://github.com/unoplat/unoplat-code-confluence/commit/d011ed7dac7397de0dcf3e6e0a40277fe99ce98b))
* tests ([26ab79d](https://github.com/unoplat/unoplat-code-confluence/commit/26ab79d76d8ccf9835909fb2fb3bab3764bd5d90))
* tests ([46b087a](https://github.com/unoplat/unoplat-code-confluence/commit/46b087acaa06f155903b99bf46cd3ea4cd420b8f))
* **tool-retries:** increased tool retries and improved griffe based d… ([b0ebd42](https://github.com/unoplat/unoplat-code-confluence/commit/b0ebd422bededaa12d567f71225cabaa00eef033))
* **tool-retries:** increased tool retries and improved griffe based description for open source models to make fewer mistakes ([0bb9b0b](https://github.com/unoplat/unoplat-code-confluence/commit/0bb9b0b47ee4ff5be70f9b24f5521b113359caec))
* **typescript:** add concept enum in schema to support more typescript ([4195eb2](https://github.com/unoplat/unoplat-code-confluence/commit/4195eb21f5fd080f3e923cb53162136ff57f7a1b))
* **typescript:** add concept enum in schema to support more typescript ([7cfe956](https://github.com/unoplat/unoplat-code-confluence/commit/7cfe9566ee97c4e3e2d016c72942ea4c0749bd43))
* **version-upgrade:** update pydantic ai with various fixes ([035e91a](https://github.com/unoplat/unoplat-code-confluence/commit/035e91ae59c44e961452bf6a40f224796f8b8913))
* **wrong-version-commons:** upgrade commons version across flow bridg… ([40c994a](https://github.com/unoplat/unoplat-code-confluence/commit/40c994a8172c766bdddeb3f6f8a6021fbdf426c4))
* **wrong-version-commons:** upgrade commons version across flow bridge and query engine components to enable pr related functionality ([207c29e](https://github.com/unoplat/unoplat-code-confluence/commit/207c29e1c9cb719489d955df7757764b2894c7b5))


### Documentation

* **agents:** split dependency guides into dedicated overview files ([59e7cfb](https://github.com/unoplat/unoplat-code-confluence/commit/59e7cfbd9412ece74d41b42b723d11cd60648aaa))

## [0.34.2](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.34.1...unoplat-code-confluence-query-engine-v0.34.2) (2026-03-03)


### Bug Fixes

* **overhaul-events-view:** make it intuitve and store upto 100k of tool result calls ([0b08bbd](https://github.com/unoplat/unoplat-code-confluence/commit/0b08bbdd301bd9f00284a76f93ecea2fe83dc860))

## [0.34.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.34.0...unoplat-code-confluence-query-engine-v0.34.1) (2026-03-03)


### Bug Fixes

* **overhaul-events-view:** make it intuitve and store upto 100k of to… ([0092204](https://github.com/unoplat/unoplat-code-confluence/commit/00922043a7145963859d0f3df8cb6f1f0d5f4206))
* **overhaul-events-view:** make it intuitve and store upto 100k of tool result calls ([844b782](https://github.com/unoplat/unoplat-code-confluence/commit/844b782f8ffba60fefa2a2aeb40b486659df1ecd))

## [0.34.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.33.0...unoplat-code-confluence-query-engine-v0.34.0) (2026-03-02)


### Features

* **typescript-beta:** strengthen typescript grammar detection and in… ([2a673ec](https://github.com/unoplat/unoplat-code-confluence/commit/2a673ec26aafd42c5a625f501af2242c41286e39))
* **typescript-beta:** strengthen typescript grammar detection and include next js endpoint detection as a starting example ([0489d94](https://github.com/unoplat/unoplat-code-confluence/commit/0489d94e0d4f3b72c3ac43859f7d97b54a3cc7c4))

## [0.33.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.32.0...unoplat-code-confluence-query-engine-v0.33.0) (2026-02-28)


### Features

* **validation-spec-implementation:** introducing llm based validator for low confidence matches to ensure defects introduced through dids are rectified ([05c1bb9](https://github.com/unoplat/unoplat-code-confluence/commit/05c1bb95481bf32e27fac39bad106ecbb84d8ba4))
* **validation-spec-implementation:** introducing llm based validator… ([ffddafb](https://github.com/unoplat/unoplat-code-confluence/commit/ffddafb41dd10abff0429470f45064a25e3a1d36))

## [0.32.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.31.2...unoplat-code-confluence-query-engine-v0.32.0) (2026-02-28)


### Features

* **confidence:** add schema and ingestion contracts for usage confidence metadata ([f71b085](https://github.com/unoplat/unoplat-code-confluence/commit/f71b085d653de9c339f0ffb615a4d07863fadd98))


### Bug Fixes

* **typescript:** add concept enum in schema to support more typescript ([4195eb2](https://github.com/unoplat/unoplat-code-confluence/commit/4195eb21f5fd080f3e923cb53162136ff57f7a1b))
* **typescript:** add concept enum in schema to support more typescript ([7cfe956](https://github.com/unoplat/unoplat-code-confluence/commit/7cfe9566ee97c4e3e2d016c72942ea4c0749bd43))

## [0.31.2](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.31.1...unoplat-code-confluence-query-engine-v0.31.2) (2026-02-24)


### Bug Fixes

* **dependencies:** split dependency guides into dedicated overview files ([77ee463](https://github.com/unoplat/unoplat-code-confluence/commit/77ee463fb1566ff4e96b337dab808371a57ed4dd))


### Documentation

* **agents:** split dependency guides into dedicated overview files ([59e7cfb](https://github.com/unoplat/unoplat-code-confluence/commit/59e7cfbd9412ece74d41b42b723d11cd60648aaa))

## [0.31.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.31.0...unoplat-code-confluence-query-engine-v0.31.1) (2026-02-24)


### Bug Fixes

* **optimise-framework-schema:** switch ingestion and query paths to J… ([be0462c](https://github.com/unoplat/unoplat-code-confluence/commit/be0462c8bc0df22458dfff7026288b145370a38c))
* **optimise-framework-schema:** switch ingestion and query paths to JSONB feature payload ([c2f6c15](https://github.com/unoplat/unoplat-code-confluence/commit/c2f6c153a6694666806fadb867652d56ab616472))

## [0.31.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.30.2...unoplat-code-confluence-query-engine-v0.31.0) (2026-02-20)


### Features

* **add-detection-of-inbound-outbound-interfaces:** detect inbound an… ([69d3000](https://github.com/unoplat/unoplat-code-confluence/commit/69d300018c9205e948028368e3c11cec198defc1))
* **add-detection-of-inbound-outbound-interfaces:** detect inbound and outbound interfaces ([8c36c1d](https://github.com/unoplat/unoplat-code-confluence/commit/8c36c1d2363235e1cfdda4f3c004da8252b9ea88))
* **codex-oauth:** implement ChatGPT OAuth PKCE flow for Codex provider ([9891b8e](https://github.com/unoplat/unoplat-code-confluence/commit/9891b8e7c0bf2bf46c2176d34722f484d22a1d31))
* **config:** Update dependencies and refactor MCP server management (temp fix for concurrent access to subagents cuasing asyncio issues - moving to async workflow engine with better isolation same as ingestion( ([ef1725c](https://github.com/unoplat/unoplat-code-confluence/commit/ef1725c800affc63015641068ab6d5d876d8fab4))
* **delete-model-config:** add UI to delete active model provider configuration ([81a46f6](https://github.com/unoplat/unoplat-code-confluence/commit/81a46f68189d669bd1718617865bd6b3cd44d413))
* **dependency-filter:** restrict dependency discovery to runtime-only group ([b54d554](https://github.com/unoplat/unoplat-code-confluence/commit/b54d55459fa782e2e58ea68c659bbdf5cd5014f3))
* **engineering-workflow:** simplify output schema and improve system prompts ([e8b970e](https://github.com/unoplat/unoplat-code-confluence/commit/e8b970ef7e81fe0000f23306528fc6cc596b9eb9))
* enhance api endpoints and processing logic to support multiple repository providers starting with github enterprise , introduce oauth utils and also assign intuitive names for agents for easier experiment tracking with workflow monitoring solution ([ba05d6b](https://github.com/unoplat/unoplat-code-confluence/commit/ba05d6ba13eb951ab43f8d0553622582fced7b4b))
* first draft of reliable auditable agent ([8a361c6](https://github.com/unoplat/unoplat-code-confluence/commit/8a361c611e97162dfb0a755bfce3a858042db491))
* first draft of reliable auditable agents ([9fc6eee](https://github.com/unoplat/unoplat-code-confluence/commit/9fc6eeec90432442d06742f223fde22606ff6c88))
* **improved-development-workflow-agent-harness:** improved development workflow agent harness ([226bcc5](https://github.com/unoplat/unoplat-code-confluence/commit/226bcc5a2ae783cfe3dae7967705ccba97d9e77b))
* **migrate-postgres:** ingestion and query engine services ([06edb7f](https://github.com/unoplat/unoplat-code-confluence/commit/06edb7fb05997754e73f5ba2104b8a764cba5e79))
* **observability:** enhance event stream debugging and engineering workflow completion ([595a363](https://github.com/unoplat/unoplat-code-confluence/commit/595a3636c67dc4b6347eb1fc2ed4bd2eab0ab6d0))
* **query-engine-agents-md:** introduce dependency guide agent and also removed agent with context as we migrated to exa mcp tool. Also moved to pydantic fastmcp client for mcp servers ([a3e6788](https://github.com/unoplat/unoplat-code-confluence/commit/a3e6788a54cbf5672967eafd142093d077d559a9))
* **query-engine:** add agents-md updater agent with section-scoped tools and tests ([a493c50](https://github.com/unoplat/unoplat-code-confluence/commit/a493c5044474385cffb0eea1e7c77a88c61c33fa))
* **query-engine:** add POST/GET repository-agent-md-pr endpoints with one-shot semantics ([d4945c3](https://github.com/unoplat/unoplat-code-confluence/commit/d4945c382ab87b955aa4a84924578624478b3de9))
* support more repository providers starting with github enterprise. Improved Frontend Architecture and onboarding and some bugs squashed ([0974c76](https://github.com/unoplat/unoplat-code-confluence/commit/0974c76fe9df68b86fb1b180db1b41e04a16c9dd))
* **web-search:** support built-in web search for providers with native capability ([05814a3](https://github.com/unoplat/unoplat-code-confluence/commit/05814a3ae675f33db50eac35e32a0f397c0582f6))


### Bug Fixes

* add utility that helps safe logging showing only first/last few chars of sensitive information ([1fdc947](https://github.com/unoplat/unoplat-code-confluence/commit/1fdc947fb78a83ba59c391956e0051f6fbf984a5))
* agent md persistence ([348b4d4](https://github.com/unoplat/unoplat-code-confluence/commit/348b4d440e05949fd24606dd6f3f1f72730d477c))
* **agent-description:** improve system prompts and tool descriptions … ([780b624](https://github.com/unoplat/unoplat-code-confluence/commit/780b624e5af02767bceb7212d8c62a43e2be511f))
* **agent-description:** improve system prompts and tool descriptions and add output validator for open source models to work reliably. solved issues with minmax2.1 ([8cb0968](https://github.com/unoplat/unoplat-code-confluence/commit/8cb096893c72b8626968234218b1a36db7367cf6))
* **agent-names:** simplify agent names ([0197723](https://github.com/unoplat/unoplat-code-confluence/commit/0197723b49549067ad930bf3a74cf9adc3da800f))
* alter tests fail cases (now being handled by workflow orchestrator) ([abb94f9](https://github.com/unoplat/unoplat-code-confluence/commit/abb94f93315ce17167955b05ab8d038be11e82eb))
* automatic error capture post exhausion of retries during ai work… ([415de05](https://github.com/unoplat/unoplat-code-confluence/commit/415de05f4c9785afe22264d5439f20f2819a19e8))
* automatic error capture post exhausion of retries during ai workflow for user to easily submit github issues with all details ([af42e1f](https://github.com/unoplat/unoplat-code-confluence/commit/af42e1f35d9ceb03462fd706f27d12b89ad32940))
* **binding-address:** change binding address back to 127.0.0.1 ([fc41fe4](https://github.com/unoplat/unoplat-code-confluence/commit/fc41fe4c18038466f5a883e629a6b3048685f8bc))
* code smells for model factory ([6de23a7](https://github.com/unoplat/unoplat-code-confluence/commit/6de23a7a0ab6b0c13d9e4e487519024ceeed6163))
* **connection-pool-recommendation-settings:** reuse stale connections and increase connection pool for postgres ([2935799](https://github.com/unoplat/unoplat-code-confluence/commit/2935799a5a1c160ebba5b6da76d4adbdcd73eadf))
* **date-time-fixes-backend:** offset fixes ([87165db](https://github.com/unoplat/unoplat-code-confluence/commit/87165dbc25ebda76a48cb1e4ca6cbf3cd1ebaee6))
* **dependencies:** get rid of unused dependencies - neomodel ([61e42a2](https://github.com/unoplat/unoplat-code-confluence/commit/61e42a202a7981a7e8cc1347e0b60e40131371ec))
* **dependency-version:** commons dependency version with model update… ([dbdd027](https://github.com/unoplat/unoplat-code-confluence/commit/dbdd02708a379d3277d50f62e19d3934ef4a82fe))
* **dependency-version:** commons dependency version with model updates for ingestion/query services ([890f4ca](https://github.com/unoplat/unoplat-code-confluence/commit/890f4cad1d3a5aaa3e1f4119f4ce122ab54b9d0d))
* **deps-version:** pin common lib dependencies version to latest ([e5d5db2](https://github.com/unoplat/unoplat-code-confluence/commit/e5d5db2c358fee88b4afae35ff7a8a68807836de))
* **deps-version:** pin common lib dependencies version to latest ([ed5b60f](https://github.com/unoplat/unoplat-code-confluence/commit/ed5b60f70f0ae254ea2a583a10f13a53b2df4740))
* **error-logging-model-provider:** enhance error details for model pr… ([a1633b9](https://github.com/unoplat/unoplat-code-confluence/commit/a1633b94475f1ce7b0f2ac466a294ac8aec5e052))
* **error-logging-model-provider:** enhance error details for model provider issues ([1c9298b](https://github.com/unoplat/unoplat-code-confluence/commit/1c9298bf65d007308e80b6180f9a50df09474b20))
* **improve-system-prompt:** improve system prompt for getting library information to work more reliably with open source models ([469a8e1](https://github.com/unoplat/unoplat-code-confluence/commit/469a8e10a411418197b3d4fbecdcfddf8868675a))
* improving ai engine structure (first step towards improving prim… ([9e5b00b](https://github.com/unoplat/unoplat-code-confluence/commit/9e5b00bfad87027198fb51a9c5f6696e0dc4df44))
* improving ai engine structure (first step towards improving primitives) ([b2950bc](https://github.com/unoplat/unoplat-code-confluence/commit/b2950bccba8c034b175a407eddd65599f4d666c0))
* insert based on repository workflow run id ([0a298b4](https://github.com/unoplat/unoplat-code-confluence/commit/0a298b4e00864e6b116198b4aeffaa02f480e41a))
* **mcp-migration:** migration from standard fastapi mcp client ([9a87bb9](https://github.com/unoplat/unoplat-code-confluence/commit/9a87bb91d645868fd36397162800ba326af1d283))
* **mcp-toolset-fix:** fix for getting library data ([9540acf](https://github.com/unoplat/unoplat-code-confluence/commit/9540acfeb17a917d6eac40026c9d838af971a07a))
* **model-config:** do two phase operation for model config upsert and worker upgrade ensuring one does not affect anothert ([bd3be65](https://github.com/unoplat/unoplat-code-confluence/commit/bd3be653a203385e43fcd338a346c66bab053727))
* **networking:** networking fixes for callback listener ([4edec57](https://github.com/unoplat/unoplat-code-confluence/commit/4edec57361e84da54b09aa4d1066467d65361dc9))
* **perf:** parallelism per codebase agent md in monorepo ([d71e0e4](https://github.com/unoplat/unoplat-code-confluence/commit/d71e0e4d19fe2ec8ba6707e098ed36a58969676f))
* **perf:** parallelism per codebase agent md in monorepo ([7ae3ad8](https://github.com/unoplat/unoplat-code-confluence/commit/7ae3ad8c98612cd30e52753b7b0d78f3442beb14))
* **post-processing-business-domain:** workflow orchestrator services/worker responsibilities clean up and post processing fix for agent md ([d21c465](https://github.com/unoplat/unoplat-code-confluence/commit/d21c4655328e29a6cbde1e98f1638834e199a768))
* **query-engine-test:** breaking changes due to test containers v4 api ([d0e401b](https://github.com/unoplat/unoplat-code-confluence/commit/d0e401b760114d5bf739c54283b7885e74e990eb))
* **read-tool-call-pagination-issue:** align updater read clamp and no-op semantics ([e108880](https://github.com/unoplat/unoplat-code-confluence/commit/e108880d340ef26dd89e4cdc5be872e319e7c9ab))
* **read-tool-call-pagination-issue:** align updater read clamp and no… ([b6574a0](https://github.com/unoplat/unoplat-code-confluence/commit/b6574a0f826f44dfe3f9f1cf59d1543e053e21b8))
* regression for package manager and programming language metadata ([5b705e9](https://github.com/unoplat/unoplat-code-confluence/commit/5b705e91ac4d308fd588cc30ee8b33026bd1b477))
* **regression-eza:** add eza to dockerfile of query engine for direct… ([d1bbd38](https://github.com/unoplat/unoplat-code-confluence/commit/d1bbd3874a7ba3566bd331cda522aa72b50b5a90))
* **regression-eza:** add eza to dockerfile of query engine for directory tree tool and remove old commented code ([4282fea](https://github.com/unoplat/unoplat-code-confluence/commit/4282feaa9f61b20211c99b22346710eda405492a))
* removal of duplicate status column for agent snapshot tracking ([24d2b40](https://github.com/unoplat/unoplat-code-confluence/commit/24d2b40642643eb149db68fbeae2a4bbbf6a610e))
* statistics calculation ([d549274](https://github.com/unoplat/unoplat-code-confluence/commit/d5492746c114bcee255dc3e12c04f2789d586123))
* statistics persistence ([6c03e05](https://github.com/unoplat/unoplat-code-confluence/commit/6c03e0587775fb5e8e7c8c2e102f7ec3e2184d4d))
* test with repository workflow run id ([d011ed7](https://github.com/unoplat/unoplat-code-confluence/commit/d011ed7dac7397de0dcf3e6e0a40277fe99ce98b))
* tests ([26ab79d](https://github.com/unoplat/unoplat-code-confluence/commit/26ab79d76d8ccf9835909fb2fb3bab3764bd5d90))
* tests ([46b087a](https://github.com/unoplat/unoplat-code-confluence/commit/46b087acaa06f155903b99bf46cd3ea4cd420b8f))
* **tool-retries:** increased tool retries and improved griffe based d… ([b0ebd42](https://github.com/unoplat/unoplat-code-confluence/commit/b0ebd422bededaa12d567f71225cabaa00eef033))
* **tool-retries:** increased tool retries and improved griffe based description for open source models to make fewer mistakes ([0bb9b0b](https://github.com/unoplat/unoplat-code-confluence/commit/0bb9b0b47ee4ff5be70f9b24f5521b113359caec))
* **version-upgrade:** update pydantic ai with various fixes ([035e91a](https://github.com/unoplat/unoplat-code-confluence/commit/035e91ae59c44e961452bf6a40f224796f8b8913))
* **wrong-version-commons:** upgrade commons version across flow bridg… ([40c994a](https://github.com/unoplat/unoplat-code-confluence/commit/40c994a8172c766bdddeb3f6f8a6021fbdf426c4))
* **wrong-version-commons:** upgrade commons version across flow bridge and query engine components to enable pr related functionality ([207c29e](https://github.com/unoplat/unoplat-code-confluence/commit/207c29e1c9cb719489d955df7757764b2894c7b5))


### Dependencies

* Bump unoplat-code-confluence-commons to v0.34.1 ([75b3e48](https://github.com/unoplat/unoplat-code-confluence/commit/75b3e489496005a5cc6f7281a63c14ea9b9db7e4))

## [0.30.2](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.30.1...unoplat-code-confluence-query-engine-v0.30.2) (2026-02-20)


### Bug Fixes

* **read-tool-call-pagination-issue:** align updater read clamp and no-op semantics ([e108880](https://github.com/unoplat/unoplat-code-confluence/commit/e108880d340ef26dd89e4cdc5be872e319e7c9ab))
* **read-tool-call-pagination-issue:** align updater read clamp and no… ([b6574a0](https://github.com/unoplat/unoplat-code-confluence/commit/b6574a0f826f44dfe3f9f1cf59d1543e053e21b8))

## [0.30.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.30.0...unoplat-code-confluence-query-engine-v0.30.1) (2026-02-17)


### Bug Fixes

* **wrong-version-commons:** upgrade commons version across flow bridg… ([40c994a](https://github.com/unoplat/unoplat-code-confluence/commit/40c994a8172c766bdddeb3f6f8a6021fbdf426c4))
* **wrong-version-commons:** upgrade commons version across flow bridge and query engine components to enable pr related functionality ([207c29e](https://github.com/unoplat/unoplat-code-confluence/commit/207c29e1c9cb719489d955df7757764b2894c7b5))

## [0.30.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.29.1...unoplat-code-confluence-query-engine-v0.30.0) (2026-02-15)


### Features

* **query-engine:** add agents-md updater agent with section-scoped tools and tests ([a493c50](https://github.com/unoplat/unoplat-code-confluence/commit/a493c5044474385cffb0eea1e7c77a88c61c33fa))
* **query-engine:** add POST/GET repository-agent-md-pr endpoints with one-shot semantics ([d4945c3](https://github.com/unoplat/unoplat-code-confluence/commit/d4945c382ab87b955aa4a84924578624478b3de9))

## [0.29.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.29.0...unoplat-code-confluence-query-engine-v0.29.1) (2026-02-10)


### Bug Fixes

* **agent-names:** simplify agent names ([0197723](https://github.com/unoplat/unoplat-code-confluence/commit/0197723b49549067ad930bf3a74cf9adc3da800f))
* **networking:** networking fixes for callback listener ([4edec57](https://github.com/unoplat/unoplat-code-confluence/commit/4edec57361e84da54b09aa4d1066467d65361dc9))

## [0.29.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.28.0...unoplat-code-confluence-query-engine-v0.29.0) (2026-02-09)


### Features

* **codex-oauth:** implement ChatGPT OAuth PKCE flow for Codex provider ([9891b8e](https://github.com/unoplat/unoplat-code-confluence/commit/9891b8e7c0bf2bf46c2176d34722f484d22a1d31))
* **delete-model-config:** add UI to delete active model provider configuration ([81a46f6](https://github.com/unoplat/unoplat-code-confluence/commit/81a46f68189d669bd1718617865bd6b3cd44d413))
* **dependency-filter:** restrict dependency discovery to runtime-only group ([b54d554](https://github.com/unoplat/unoplat-code-confluence/commit/b54d55459fa782e2e58ea68c659bbdf5cd5014f3))
* **engineering-workflow:** simplify output schema and improve system prompts ([e8b970e](https://github.com/unoplat/unoplat-code-confluence/commit/e8b970ef7e81fe0000f23306528fc6cc596b9eb9))
* **observability:** enhance event stream debugging and engineering workflow completion ([595a363](https://github.com/unoplat/unoplat-code-confluence/commit/595a3636c67dc4b6347eb1fc2ed4bd2eab0ab6d0))
* **web-search:** support built-in web search for providers with native capability ([05814a3](https://github.com/unoplat/unoplat-code-confluence/commit/05814a3ae675f33db50eac35e32a0f397c0582f6))


### Bug Fixes

* **binding-address:** change binding address back to 127.0.0.1 ([fc41fe4](https://github.com/unoplat/unoplat-code-confluence/commit/fc41fe4c18038466f5a883e629a6b3048685f8bc))
* code smells for model factory ([6de23a7](https://github.com/unoplat/unoplat-code-confluence/commit/6de23a7a0ab6b0c13d9e4e487519024ceeed6163))

## [0.28.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.27.1...unoplat-code-confluence-query-engine-v0.28.0) (2026-02-06)


### Features

* **improved-development-workflow-agent-harness:** improved development workflow agent harness ([226bcc5](https://github.com/unoplat/unoplat-code-confluence/commit/226bcc5a2ae783cfe3dae7967705ccba97d9e77b))

## [0.27.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.27.0...unoplat-code-confluence-query-engine-v0.27.1) (2026-02-06)


### Bug Fixes

* **error-logging-model-provider:** enhance error details for model pr… ([a1633b9](https://github.com/unoplat/unoplat-code-confluence/commit/a1633b94475f1ce7b0f2ac466a294ac8aec5e052))
* **error-logging-model-provider:** enhance error details for model provider issues ([1c9298b](https://github.com/unoplat/unoplat-code-confluence/commit/1c9298bf65d007308e80b6180f9a50df09474b20))

## [0.27.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.26.1...unoplat-code-confluence-query-engine-v0.27.0) (2026-02-04)


### Features

* **add-detection-of-inbound-outbound-interfaces:** detect inbound an… ([69d3000](https://github.com/unoplat/unoplat-code-confluence/commit/69d300018c9205e948028368e3c11cec198defc1))
* **add-detection-of-inbound-outbound-interfaces:** detect inbound and outbound interfaces ([8c36c1d](https://github.com/unoplat/unoplat-code-confluence/commit/8c36c1d2363235e1cfdda4f3c004da8252b9ea88))

## [0.26.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-query-engine-v0.26.0...unoplat-code-confluence-query-engine-v0.26.1) (2026-01-30)


### Bug Fixes

* **tool-retries:** increased tool retries and improved griffe based d… ([b0ebd42](https://github.com/unoplat/unoplat-code-confluence/commit/b0ebd422bededaa12d567f71225cabaa00eef033))
* **tool-retries:** increased tool retries and improved griffe based description for open source models to make fewer mistakes ([0bb9b0b](https://github.com/unoplat/unoplat-code-confluence/commit/0bb9b0b47ee4ff5be70f9b24f5521b113359caec))

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
