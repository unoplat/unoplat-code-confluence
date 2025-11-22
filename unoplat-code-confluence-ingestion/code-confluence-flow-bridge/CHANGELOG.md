# Changelog

## [0.62.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.62.0...code-confluence-flow-bridge-v0.62.1) (2025-11-22)


### Bug Fixes

* **graph-db:** Update CodeConfluenceGitRepository node creation to not cause cypher merge conflicts ([bde1103](https://github.com/unoplat/unoplat-code-confluence/commit/bde1103e6a744a6c3024e204bc5b5393232c0f30))
* **graph-db:** Update CodeConfluenceGitRepository node creation to not cause cypher merge conflicts ([dd15257](https://github.com/unoplat/unoplat-code-confluence/commit/dd1525719cd5d4b7ab07528a0621023cd935d6e9))

## [0.62.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.61.1...code-confluence-flow-bridge-v0.62.0) (2025-11-21)


### Features

* support more repository providers starting with github enterprise. Improved Frontend Architecture and onboarding and some bugs squashed ([0974c76](https://github.com/unoplat/unoplat-code-confluence/commit/0974c76fe9df68b86fb1b180db1b41e04a16c9dd))

## [0.61.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.61.0...code-confluence-flow-bridge-v0.61.1) (2025-11-21)


### Bug Fixes

* **graph-db:** Remove redundant qualified_name update in repository node ([151afd1](https://github.com/unoplat/unoplat-code-confluence/commit/151afd1ddd475943011e0929cf8ba686d7e61df3))

## [0.61.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.60.0...code-confluence-flow-bridge-v0.61.0) (2025-11-18)


### Features

* **repository:** Enhance repository refresh and provider management and update temporal from 1.12 to 1.19 for better performance reliability etc ([685a31c](https://github.com/unoplat/unoplat-code-confluence/commit/685a31cb315995e80acc0b88a440ce9e371be0bf))
* **repository:** Enhance repository refresh and provider management and update temporal from 1.12 to 1.19 for better performance reliability etc ([b8f8cff](https://github.com/unoplat/unoplat-code-confluence/commit/b8f8cfff91c99a32cfa999f6cbcc64b0ff14fd4a))

## [0.60.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.59.0...code-confluence-flow-bridge-v0.60.0) (2025-11-10)


### Features

* enhance api endpoints and processing logic to support multiple repository providers starting with github enterprise , introduce oauth utils and also assign intuitive names for agents for easier experiment tracking with workflow monitoring solution ([ba05d6b](https://github.com/unoplat/unoplat-code-confluence/commit/ba05d6ba13eb951ab43f8d0553622582fced7b4b))


### Dependencies

* Bump unoplat-code-confluence-commons to v0.34.1 ([75b3e48](https://github.com/unoplat/unoplat-code-confluence/commit/75b3e489496005a5cc6f7281a63c14ea9b9db7e4))

## [0.59.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.58.0...code-confluence-flow-bridge-v0.59.0) (2025-11-03)


### Features

* **workflow:** Enhance agent execution with usage statistics tracking ([c68e53e](https://github.com/unoplat/unoplat-code-confluence/commit/c68e53ef83243b55a8fbb0dc330891517b80d086))
* **workflow:** Enhance agent execution with usage statistics tracking ([b05ce65](https://github.com/unoplat/unoplat-code-confluence/commit/b05ce659a701763dbc561539146c40c65635c5af))

## [0.58.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.57.1...code-confluence-flow-bridge-v0.58.0) (2025-10-30)


### Features

* enable typescript native data model extraction grammar support with start line and end line ([8efe033](https://github.com/unoplat/unoplat-code-confluence/commit/8efe033c484e6941037a7e282a8ae45a3815d0fc))
* **github-app:** Add GitHub App manifest and webhook handling (not integrated with frontend and not tested yet) ([988ffe5](https://github.com/unoplat/unoplat-code-confluence/commit/988ffe519a9f85b7a3a1d6887a8a228f6993f0db))


### Bug Fixes

* **detection:** Simplify codebase detection and remove SSE streaming ([6fec78b](https://github.com/unoplat/unoplat-code-confluence/commit/6fec78b1633966f281c3b241aa099fd1cd4055dc))
* remove support for local repository parsing ([2f8be69](https://github.com/unoplat/unoplat-code-confluence/commit/2f8be69c2a1de7ab8b631822a1214ac9699fcf65))

## [0.57.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.57.0...code-confluence-flow-bridge-v0.57.1) (2025-10-23)


### Bug Fixes

* **parser:** Refactor GenericCodebaseParser to focus on file insertion ([be17754](https://github.com/unoplat/unoplat-code-confluence/commit/be17754ab8a80b276820b205e37f0c9859e2b6b2))
* **parser:** Refactor parser to focus on file insertion ([c0bd597](https://github.com/unoplat/unoplat-code-confluence/commit/c0bd5974bbe8298b1a8e9a6931bf0eae850c1cca))

## [0.57.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.56.3...code-confluence-flow-bridge-v0.57.0) (2025-10-18)


### Features

* **python-typescript-grammar-context-engineering:** Extract precise data model positions for TypeScript and Python files for precise ([2297666](https://github.com/unoplat/unoplat-code-confluence/commit/22976661260330303504f898c56937ed971ba3ae))
* **python-typescript-grammar-context-engineering:** Extract precise data model positions for TypeScript and Python files for precise ([3682393](https://github.com/unoplat/unoplat-code-confluence/commit/368239331cedc8409b25b975160284ebdc7ad6f9))


### Bug Fixes

* test assertions ([82f2810](https://github.com/unoplat/unoplat-code-confluence/commit/82f2810ef38769438b3bc2015920e0d970e31f76))

## [0.56.3](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.56.2...code-confluence-flow-bridge-v0.56.3) (2025-10-17)


### Bug Fixes

* **package-manager:** common data parsing for typescript across yarn , bun , pnpm and npm and comprehensive package manager tests for TypeScript ([26611b9](https://github.com/unoplat/unoplat-code-confluence/commit/26611b9955516b93e431847e4afbffd5e645eab5))
* **package-manager:** common data parsing for typescript across yarn , bun , pnpm and npm and comprehensive package manager tests for TypeScript ([5dc1a0b](https://github.com/unoplat/unoplat-code-confluence/commit/5dc1a0b64cd290111f1f6337f150c3f8205ff228))

## [0.56.2](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.56.1...code-confluence-flow-bridge-v0.56.2) (2025-10-16)


### Bug Fixes

* **typescript:** Improve TypeScript project detection ([77a47c3](https://github.com/unoplat/unoplat-code-confluence/commit/77a47c3ce2f4948655ca62b523c9f5d112226893))
* **typescript:** Improve TypeScript project detection ([98103ac](https://github.com/unoplat/unoplat-code-confluence/commit/98103ace7290a086f23b1661207669834916b7d6))

## [0.56.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.56.0...code-confluence-flow-bridge-v0.56.1) (2025-10-16)


### Bug Fixes

* **version:** update ignore rules for reliable codebase detection across typescript and python ([7caa4d2](https://github.com/unoplat/unoplat-code-confluence/commit/7caa4d24aecf7aea24ac97c576aa469bd7bb893f))

## [0.56.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.55.0...code-confluence-flow-bridge-v0.56.0) (2025-10-16)


### Features

* **parser:** Add base language processor and context classes , improved design to extend code grammar, add npm, yarn, bun common core package metadata parsing and ingestion and updated tree sitter language pack apis for better reliability for new versions ([124d693](https://github.com/unoplat/unoplat-code-confluence/commit/124d6932b1c8e9ff360ed96e5879d1e48edb56d5))
* **parser:** Add base language processor and context classes , improved design to extend code grammar, add npm, yarn, bun common core package metadata parsing and ingestion and updated tree sitter language pack apis for better reliability for new versions ([4c46e4a](https://github.com/unoplat/unoplat-code-confluence/commit/4c46e4a166f6ad0ddda3e058f9755c7ef1d7432c))


### Bug Fixes

* Update unoplat-code-confluence-commons to v0.31.2 ([956b029](https://github.com/unoplat/unoplat-code-confluence/commit/956b0293bcbc554d8772a9f1ca0a3b5b0a64ff8b))

## [0.55.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.54.0...code-confluence-flow-bridge-v0.55.0) (2025-10-06)


### Features

* **package-manager:** Optimize metadata storage and serialization ([21130a9](https://github.com/unoplat/unoplat-code-confluence/commit/21130a93fc17949986aa0c5ece151886ad2c5045))


### Bug Fixes

* **pip:** migrate to grouped dependencies, add PEP 503/735 normalization, fix -r includes mis-grouping bug ([855405b](https://github.com/unoplat/unoplat-code-confluence/commit/855405b5f5402b886729578a155c00b46f7d7327))
* **poetry:** migrate to grouped dependency structure and add Poetry 1.2+  include-groups support ([3aae96a](https://github.com/unoplat/unoplat-code-confluence/commit/3aae96a4ca08ee3d83d7b9c014f8ee26fe9d4bb7))
* **uv:** migrate to grouped dependency structure and add dependency-groups section support and modify tests ([379d203](https://github.com/unoplat/unoplat-code-confluence/commit/379d203f4c764936f0d2eb5d16ffb6bb5c971b4d))

## [0.54.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.53.1...code-confluence-flow-bridge-v0.54.0) (2025-10-04)


### Features

* **package-manager:** Add TypeScript package manager detection ([9cff38b](https://github.com/unoplat/unoplat-code-confluence/commit/9cff38bbf0349556a714402b3cfe7bc371c3a2fb))
* **package-manager:** Add TypeScript package manager detection ([ab4d9a5](https://github.com/unoplat/unoplat-code-confluence/commit/ab4d9a55dbdb05122631b24672df235736508a4d))


### Bug Fixes

* Update function signature test for generate events method ([008eebc](https://github.com/unoplat/unoplat-code-confluence/commit/008eebc2bb18824932606fdb7b39ed5b74c5c818))

## [0.53.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.53.0...code-confluence-flow-bridge-v0.53.1) (2025-09-30)


### Bug Fixes

* **docker:** update PostgreSQL image and configuration ([2b5a90b](https://github.com/unoplat/unoplat-code-confluence/commit/2b5a90be535500921eed96c8a97deaa85e5358be))
* **docker:** Update PostgreSQL image and configuration ([95d9242](https://github.com/unoplat/unoplat-code-confluence/commit/95d92421f2a79e6d6b658e44fd91b27e165a43f1))
* **github_helper:** Improve handling of local branch and uncommitted changes ([c5959f3](https://github.com/unoplat/unoplat-code-confluence/commit/c5959f3d98971af38992eada893ef4077f3d3449))

## [0.53.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.52.0...code-confluence-flow-bridge-v0.53.0) (2025-09-22)


### Features

* Upgrade unoplat-code-confluence-commons to v0.29.0 ([b1fc6ed](https://github.com/unoplat/unoplat-code-confluence/commit/b1fc6ed3af1d4eac0a45f51e1145fca33729e8a1))
* Upgrade unoplat-code-confluence-commons to v0.29.0 ([328eab0](https://github.com/unoplat/unoplat-code-confluence/commit/328eab045ef62e808c2cfc0e2d000ab27ac12e1e))

## [0.52.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.51.0...code-confluence-flow-bridge-v0.52.0) (2025-09-17)


### Features

* **agent_md_output:** upgrade unoplat-code-confluence-commons to v0.28.0 and endpoint for retrieval ([1cda97f](https://github.com/unoplat/unoplat-code-confluence/commit/1cda97fab3cf571290940b89415c0942f22b5c64))
* **agent_md_output:** upgrade unoplat-code-confluence-commons to v0.28.0 and endpoint for retrieval ([8c9903b](https://github.com/unoplat/unoplat-code-confluence/commit/8c9903b0e7ab9939c81c1900c6955d9b1f49a9b6))

## [0.51.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.50.2...code-confluence-flow-bridge-v0.51.0) (2025-09-12)


### Features

* **github:** add codebase metadata API endpoint ([b16d5ee](https://github.com/unoplat/unoplat-code-confluence/commit/b16d5ee5291656ebb516da167740b221b1144753))
* **github:** add codebase metadata API endpoint ([35a4f03](https://github.com/unoplat/unoplat-code-confluence/commit/35a4f031f2556c9633178f875b49b2279a7fc82d))

## [0.50.2](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.50.1...code-confluence-flow-bridge-v0.50.2) (2025-08-29)


### Bug Fixes

* **code-confluence-flow-bridge:** Fix single edge for similar feature to file relationships in graph ([d10ebc0](https://github.com/unoplat/unoplat-code-confluence/commit/d10ebc0a5ce1bf043b3fa5775f025d53f757498a))
* **code-confluence-flow-bridge:** Fix single edge for similar feature to file relationships in graph ([bd0df4d](https://github.com/unoplat/unoplat-code-confluence/commit/bd0df4dc6dcefaa8c820224dd3036e5f73dd64d3))

## [0.50.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.50.0...code-confluence-flow-bridge-v0.50.1) (2025-08-29)


### Bug Fixes

* **sqlbase:** move to sqlbase from sqlmodel for better typing support ([5d9ff91](https://github.com/unoplat/unoplat-code-confluence/commit/5d9ff91bb4d9d038aa1f5b5e58c92f7b592a9412))
* **sqlbase:** move to sqlbase from sqlmodel for better typing support ([e5d00e6](https://github.com/unoplat/unoplat-code-confluence/commit/e5d00e68e4ed99016909f96adff0b901c323060f))
* tests based on new sqlachemy base model integration ([515896a](https://github.com/unoplat/unoplat-code-confluence/commit/515896aeed9bdda49ac2617b35d4b328adb31f45))

## [0.50.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.49.1...code-confluence-flow-bridge-v0.50.0) (2025-08-28)


### Features

* **framework-definitions:** add descriptions for framework definitions ([312e8d6](https://github.com/unoplat/unoplat-code-confluence/commit/312e8d64645716c09e9ffc185598922b15ae2728))
* **framework-definitions:** add descriptions for framework definitions ([91bfd85](https://github.com/unoplat/unoplat-code-confluence/commit/91bfd8583b82f2afed7dae5929ab40ad024e1637))
* Simplify pydantic description in framework-definitions ([70d8d48](https://github.com/unoplat/unoplat-code-confluence/commit/70d8d48a7c8723f824512f514245557dda26bfef))

## [0.49.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.49.0...code-confluence-flow-bridge-v0.49.1) (2025-08-25)


### Bug Fixes

* Add Flag model to code-confluence-flow-bridge ([ec980e9](https://github.com/unoplat/unoplat-code-confluence/commit/ec980e99eeeb06a75b451ebadb277ebc2f2598b2))
* Add Flag model to code-confluence-flow-bridge ([8e88530](https://github.com/unoplat/unoplat-code-confluence/commit/8e885300e8e1e4c205017d1faf1a3d53044e6a18))

## [0.49.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.48.0...code-confluence-flow-bridge-v0.49.0) (2025-08-23)


### Features

* **deps:** upgrade unoplat-code-confluence-commons to v0.25.0 ([eda30ed](https://github.com/unoplat/unoplat-code-confluence/commit/eda30ed2bb457dd0ee112347f3f6ae90bbd8db48))
* **deps:** upgrade unoplat-code-confluence-commons to v0.25.0 ([6f17cc7](https://github.com/unoplat/unoplat-code-confluence/commit/6f17cc744f259d40ebcd46389d903a94e3b9b327))

## [0.48.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.47.2...code-confluence-flow-bridge-v0.48.0) (2025-08-22)


### Features

* **credentials:** Add support for multi-key credentials to support ai model providers secrets' ([d6abf29](https://github.com/unoplat/unoplat-code-confluence/commit/d6abf29e82cd6e88c97d98bf23780985262e7c70))
* **credentials:** Add support for multi-key credentials to support ai model providers secrets' ([d1b43f0](https://github.com/unoplat/unoplat-code-confluence/commit/d1b43f01abf15d3ea61a047b7b6e59115673f7df))

## [0.47.2](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.47.1...code-confluence-flow-bridge-v0.47.2) (2025-08-20)


### Bug Fixes

* Update unoplat-code-confluence-commons dependency to v0.24.1 ([4bf1637](https://github.com/unoplat/unoplat-code-confluence/commit/4bf163756674d5bf74b6641f5c2f1f9cc247e1dd))
* Update unoplat-code-confluence-commons dependency to v0.24.1 ([976e08b](https://github.com/unoplat/unoplat-code-confluence/commit/976e08b1a584e29b697a4a12817557a9ad135250))

## [0.47.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.47.0...code-confluence-flow-bridge-v0.47.1) (2025-08-20)


### Bug Fixes

* **code-confluence-file:** change to `has_data_model` property from is_data_model ([d26a5e9](https://github.com/unoplat/unoplat-code-confluence/commit/d26a5e9091432397f1aad00d228de7eeb3f10d80))
* **code-confluence-file:** change to `has_data_model` property from is_data_model ([7152410](https://github.com/unoplat/unoplat-code-confluence/commit/7152410a4c37bdea8467299f260a6af45536bca2))

## [0.47.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.46.1...code-confluence-flow-bridge-v0.47.0) (2025-08-14)


### Features

* **codebase-parsing:** Improve package and file parsing ([a72a29b](https://github.com/unoplat/unoplat-code-confluence/commit/a72a29bf7970e9719dac3c2a95f21a7aaa7554b7))
* **codebase-parsing:** Improve package and file parsing ([efcd5df](https://github.com/unoplat/unoplat-code-confluence/commit/efcd5dfc28f6b0afdcb38f1947765a667d01a3bc))


### Bug Fixes

* Improve dataclass detection and update .gitignore ([3c23a7c](https://github.com/unoplat/unoplat-code-confluence/commit/3c23a7cb71398134b082b61a2c912556387ecd08))

## [0.46.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.46.0...code-confluence-flow-bridge-v0.46.1) (2025-08-09)


### Bug Fixes

* **configuration:** Set default Neo4j connection settings ([1a73090](https://github.com/unoplat/unoplat-code-confluence/commit/1a73090376d579cbc0c97d0271043774e4c128b6))
* docker security posture update , regression fixes for delete/refresh endpoints, update volume mount directory to sync across macos/linux ([96981da](https://github.com/unoplat/unoplat-code-confluence/commit/96981da0ca1df987eecd1c773a2cee8640087192))
* docker security posture update , regression fixes for delete/refresh endpoints, update volume mount directory to sync across macos/linux ([d4ff81c](https://github.com/unoplat/unoplat-code-confluence/commit/d4ff81c7dd3dc9b43022617eafbf4e011da219d5))

## [0.46.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.45.0...code-confluence-flow-bridge-v0.46.0) (2025-08-08)


### Features

* **code-confluence-flow-bridge:** Update dependencies and imports ([0e24964](https://github.com/unoplat/unoplat-code-confluence/commit/0e24964638eb86078cf9694ce0b7549c0a55f9db))
* **code-confluence-flow-bridge:** Update dependencies and imports ([223d6d0](https://github.com/unoplat/unoplat-code-confluence/commit/223d6d011d1f900f193ea001c61fcdf7928308ec))


### Bug Fixes

* **code-confluence-flow-bridge:** Move repository and codebase config models to commons package ([e6cd2a5](https://github.com/unoplat/unoplat-code-confluence/commit/e6cd2a50a2af49f1839da59ec2cb4681217e5cfc))

## [0.45.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.44.3...code-confluence-flow-bridge-v0.45.0) (2025-08-08)


### Features

* **sse:** Improve SSE implementation using sse-starlette ([fce33c4](https://github.com/unoplat/unoplat-code-confluence/commit/fce33c44a0e8a548a8044204357224f552ed19a2))
* **sse:** Improve SSE implementation using sse-starlette ([69bb582](https://github.com/unoplat/unoplat-code-confluence/commit/69bb582da06ea34f65e73f305ba11fc7744fdfb8))

## [0.44.3](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.44.2...code-confluence-flow-bridge-v0.44.3) (2025-08-06)


### Bug Fixes

* Add SSE response headers for better performance ([9b67aeb](https://github.com/unoplat/unoplat-code-confluence/commit/9b67aeb31075b2ee3d892ce4b02776aafe0ef255))
* Improve SSE response and add error handling ([3722534](https://github.com/unoplat/unoplat-code-confluence/commit/37225349231001390ddfeaa63109ed0928ff6e40))
* Improve SSE response and add error handling ([f2e25cd](https://github.com/unoplat/unoplat-code-confluence/commit/f2e25cdd02412dac5be10511d46ddf460bdee9b6))

## [0.44.2](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.44.1...code-confluence-flow-bridge-v0.44.2) (2025-08-06)


### Bug Fixes

* linting moved the annotation import ([8e0f17c](https://github.com/unoplat/unoplat-code-confluence/commit/8e0f17c731a1f63de4a668e1f3d4b65066754d6a))
* linting moved the annotation import ([e2a3978](https://github.com/unoplat/unoplat-code-confluence/commit/e2a3978f396838e7c3ae165512734bb19601243d))
* Reorder import sections in ruff.toml ([39a50cb](https://github.com/unoplat/unoplat-code-confluence/commit/39a50cba86d21a233b91033b5ab929c9a9c10c87))

## [0.44.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.44.0...code-confluence-flow-bridge-v0.44.1) (2025-08-05)


### Bug Fixes

* deletion fixes, codebase detection perf improvements and misc refactoring ([70cfe88](https://github.com/unoplat/unoplat-code-confluence/commit/70cfe88dcd9810b33436b79ac3ea722856012cb7))
* deletion fixes, codebase detection perf improvements and misc refactoring ([9e2d40f](https://github.com/unoplat/unoplat-code-confluence/commit/9e2d40f4eda22a1542df88697356b96fd89dcbd9))

## [0.44.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.43.0...code-confluence-flow-bridge-v0.44.0) (2025-08-01)


### Features

* **code-confluence-flow-bridge:** Improve logging and performance ([21b40e0](https://github.com/unoplat/unoplat-code-confluence/commit/21b40e09c65428cb76d463c26b5df53d43af73e8))
* **code-confluence-flow-bridge:** Improve logging and performance ([1a32106](https://github.com/unoplat/unoplat-code-confluence/commit/1a32106fd19cbee69cdf9d9b164b73a305a7b110))

## [0.43.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.42.1...code-confluence-flow-bridge-v0.43.0) (2025-08-01)


### Features

* **perf:** perf and reliability improvements across neo4j/postgres ([9a93104](https://github.com/unoplat/unoplat-code-confluence/commit/9a931047ffcb525935984d13cb20741de667e358))
* **perf:** perf and reliability improvements across neo4j/postgres ([4f2b57f](https://github.com/unoplat/unoplat-code-confluence/commit/4f2b57f66a09fb1a743bd060010e86e344a4c9d6))

## [0.42.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.42.0...code-confluence-flow-bridge-v0.42.1) (2025-07-30)


### Bug Fixes

* **activity-executor:** Set default executor for asyncio loop ([5d6f63a](https://github.com/unoplat/unoplat-code-confluence/commit/5d6f63a208a7dd3bc63b2db28e357a786eb03745))
* **codebase-processing:** Improve type annotations and logging ([f88878d](https://github.com/unoplat/unoplat-code-confluence/commit/f88878d190f46bc89212d8a5a2f40374211b1eaa))
* **db-operations:** Make asynchronous context manager for postgres handle commit/rollback instead of individual functions ([b213a9c](https://github.com/unoplat/unoplat-code-confluence/commit/b213a9cbaff7c067305ab5c8320575eef81f24ce))
* **db-operations:** Make asynchronous context manager for postgres handle commit/rollback instead of individual functions ([3350a99](https://github.com/unoplat/unoplat-code-confluence/commit/3350a9967a84a2e0928f34a22390a486dc822ebc))
* **issue-tracking:** Annotate return type for issue tracking endpoint ([5d6f63a](https://github.com/unoplat/unoplat-code-confluence/commit/5d6f63a208a7dd3bc63b2db28e357a786eb03745))
* **sse-endpoint:** Annotate return type for SSE endpoint ([5d6f63a](https://github.com/unoplat/unoplat-code-confluence/commit/5d6f63a208a7dd3bc63b2db28e357a786eb03745))

## [0.42.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.41.0...code-confluence-flow-bridge-v0.42.0) (2025-07-25)


### Features

* **engine-models:** Add pydantic models for custom grammar detection engine ([c31e710](https://github.com/unoplat/unoplat-code-confluence/commit/c31e71065d8093c3fe68277ca130bea0d122ba4c))
* **package-metadata:** sync frameworks outside of Neo4j transaction ([070f25e](https://github.com/unoplat/unoplat-code-confluence/commit/070f25ed3a538eb97055a68c8d6b1a4fba19f79e))


### Bug Fixes

* bug for finding packages ([bd90a6a](https://github.com/unoplat/unoplat-code-confluence/commit/bd90a6adbee95b01c635ddeea51fb5cc154ce689))
* path for local docker compose ([39a47e3](https://github.com/unoplat/unoplat-code-confluence/commit/39a47e32489f2122be19215d3873f0ae6f2c2b7c))
* remove dependency on actual code and just keep binary also remove need for building package ([c7498f6](https://github.com/unoplat/unoplat-code-confluence/commit/c7498f6c5eeacb52753798a022157d5e3e4967e7))
* tests move to sync fixtures to avoid conflicts with session async event loop of main class, moved to python 3.13 for better async per from 3.11 ([4ccc66e](https://github.com/unoplat/unoplat-code-confluence/commit/4ccc66efde505503e058ccb4ed399f68f2a0bba3))

## [0.41.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.40.0...code-confluence-flow-bridge-v0.41.0) (2025-07-18)


### Features

* **custom-grammar-metadata:** Optimize bulk insert and improve parsing logic ([18bef75](https://github.com/unoplat/unoplat-code-confluence/commit/18bef7579392af9e3f2e9d29d42d80c60a7aff82))
* **framework-query-service:** Enhance framework feature retrieval ([26df750](https://github.com/unoplat/unoplat-code-confluence/commit/26df75021ab9629aa7cb00994cc711ab58f94e85))
* **graph-ingestion:** sync framework nodes based on dependencies ([94c968b](https://github.com/unoplat/unoplat-code-confluence/commit/94c968bb30d175ad767b883e824b0984ff1079e7))
* **parser:** update structural signature and also added framework detection logic and related tests ([37188f4](https://github.com/unoplat/unoplat-code-confluence/commit/37188f42e634865cadb63692a451f382b1e172eb))

## [0.40.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.39.4...code-confluence-flow-bridge-v0.40.0) (2025-07-02)


### Features

* Add database cleanup utilities and fixtures ([889e271](https://github.com/unoplat/unoplat-code-confluence/commit/889e27116a2ddb3c922b4fe52a06fa1de7c0a8ad))
* Add utility function to construct local repository path ([fdb118a](https://github.com/unoplat/unoplat-code-confluence/commit/fdb118a562c47094d19b3bee7f4ae143121ddc35))
* **graph-db:** add verbose logging to aid debugging CI-only failures ([917ad0d](https://github.com/unoplat/unoplat-code-confluence/commit/917ad0d67745e79eef6ec6b2563014e90efc8b5f))
* **IngestedRepositoriesDataTable:** improve data fetching ([396e036](https://github.com/unoplat/unoplat-code-confluence/commit/396e036111fd8474cf9a35a017709f3e73840bec))
* **ingestion:** Reduce token ingestion wait time ([7da6de2](https://github.com/unoplat/unoplat-code-confluence/commit/7da6de26a8b399b37333407e615ff999cfdc2811))
* local folder support ([ac56073](https://github.com/unoplat/unoplat-code-confluence/commit/ac56073502515c73208cc3e1122ab676aa0ed7e6))
* local git support ([5959c0d](https://github.com/unoplat/unoplat-code-confluence/commit/5959c0ddd0f177ad402e595a61c068b1506b4c05))
* **local-docker-compose.yml:** add repositories volume mount ([396e036](https://github.com/unoplat/unoplat-code-confluence/commit/396e036111fd8474cf9a35a017709f3e73840bec))
* **SubmittedJobsDataTable:** improve data fetching ([396e036](https://github.com/unoplat/unoplat-code-confluence/commit/396e036111fd8474cf9a35a017709f3e73840bec))
* **tanstack-table.d.ts:** add custom column and table meta ([396e036](https://github.com/unoplat/unoplat-code-confluence/commit/396e036111fd8474cf9a35a017709f3e73840bec))
* **unoplat-code-confluence-commons:** update to v0.19.0 ([ce5f69e](https://github.com/unoplat/unoplat-code-confluence/commit/ce5f69ed3d4e14f57d7483ff4510cbc331903a67))


### Bug Fixes

* **Taskfile.yml:** run pytest with test group ([396e036](https://github.com/unoplat/unoplat-code-confluence/commit/396e036111fd8474cf9a35a017709f3e73840bec))
* **test_start_ingestion.py:** handle local repository paths ([396e036](https://github.com/unoplat/unoplat-code-confluence/commit/396e036111fd8474cf9a35a017709f3e73840bec))

## [0.39.4](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.39.3...code-confluence-flow-bridge-v0.39.4) (2025-06-26)


### Bug Fixes

* dependencies and docker file ([70d2fe2](https://github.com/unoplat/unoplat-code-confluence/commit/70d2fe27a81ca2b744535cb685c760550834698f))
* dependencies and docker file ([ed79a58](https://github.com/unoplat/unoplat-code-confluence/commit/ed79a5879bfd073c026fb596ad7f8ac83c7c190c))

## [0.39.3](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.39.2...code-confluence-flow-bridge-v0.39.3) (2025-06-26)


### Bug Fixes

* do not ingest content ([e2f1978](https://github.com/unoplat/unoplat-code-confluence/commit/e2f1978bfc931d4a6cbd9e7d4901f464307b970c))
* remove content as we do have it available on host storage ([e4cef4e](https://github.com/unoplat/unoplat-code-confluence/commit/e4cef4e7e7a087eb917a38b97e81f1f2458a1f45))

## [0.39.2](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.39.1...code-confluence-flow-bridge-v0.39.2) (2025-06-21)


### Bug Fixes

* change the dotted path to full path for packages too ([b6277e0](https://github.com/unoplat/unoplat-code-confluence/commit/b6277e0b2a5247080feace1a6becc24225813a91))
* use local folder reference for schema to fastrack schema changes ([d23a3c8](https://github.com/unoplat/unoplat-code-confluence/commit/d23a3c8169798a2d335cc2a71d6a44492c1bb7ff))

## [0.39.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.39.0...code-confluence-flow-bridge-v0.39.1) (2025-06-20)


### Bug Fixes

* git pull explicit no rebase ([dfbbc26](https://github.com/unoplat/unoplat-code-confluence/commit/dfbbc26be5fc790127fb5b731568fa05f119bf9d))
* git pull fix explicit no rebase ([6e4e8e6](https://github.com/unoplat/unoplat-code-confluence/commit/6e4e8e6306688e9c9e7c5e413a09be024cbaeafb))
* git pull fix explicit no rebase ([ebbf28e](https://github.com/unoplat/unoplat-code-confluence/commit/ebbf28eb22db7a1a4aa01200c08257965c3f2efa))

## [0.39.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.38.1...code-confluence-flow-bridge-v0.39.0) (2025-06-18)


### Features

* refresh changes and bugs fix ([8e0230a](https://github.com/unoplat/unoplat-code-confluence/commit/8e0230acfc162ca9eec8f4495cab102224a68472))
* **revamp:** complete revamp to shift to tree sitter for core symbol extraction for queries and sse endpoint for auto codebase detection ([c3c6f89](https://github.com/unoplat/unoplat-code-confluence/commit/c3c6f89064c63ecca6e6314a70348b8780d1b6ee))
* **revamp:** complete revamp to shift to tree sitter for core symbol extraction for queries and sse endpoint for auto codebase detection ([5130bc7](https://github.com/unoplat/unoplat-code-confluence/commit/5130bc7a2f18f4dbbb10c30d5750b54149258e44))
* support repository operations including deletion ([f68e03d](https://github.com/unoplat/unoplat-code-confluence/commit/f68e03d14cbcd413062f4f45863fbf1af686153f))


### Bug Fixes

* clean up async event loop so test client does not coconflict ([aba2433](https://github.com/unoplat/unoplat-code-confluence/commit/aba2433df97093180083d9e04e0329d8e056dbab))
* clean up async loop ([853b785](https://github.com/unoplat/unoplat-code-confluence/commit/853b785259e4495899fc6f6496a52a0f408ceffd))
* close multiple asynchronous connection loop ([079bfcf](https://github.com/unoplat/unoplat-code-confluence/commit/079bfcf08c8c510519d2e69e6a079dba571f6ba2))
* docker compose and taskfile ([09cb051](https://github.com/unoplat/unoplat-code-confluence/commit/09cb05187784e2545070fd36747418e6021065f7))
* docs updated for schema ([591d00b](https://github.com/unoplat/unoplat-code-confluence/commit/591d00bd7f1d96f87176d4388c4c2ca840275e2f))
* remove tests dependent on old code ([d4c14a9](https://github.com/unoplat/unoplat-code-confluence/commit/d4c14a9532928d61b950f78ea348511efb65b438))
* remove unused models ([4aea88b](https://github.com/unoplat/unoplat-code-confluence/commit/4aea88bad99d523cd92707acd02cf4215017c6a5))
* removed code that is not required ([5315cc2](https://github.com/unoplat/unoplat-code-confluence/commit/5315cc21740bc8a1e06581e116089eb0254bddb6))
* squashed bugs ([7ac7d05](https://github.com/unoplat/unoplat-code-confluence/commit/7ac7d058ee8ee8b2170912e91f10a80376567d73))
* test duration ([8ed3c52](https://github.com/unoplat/unoplat-code-confluence/commit/8ed3c520084b82f40374cfc60a3142e6d4a28ca4))

## [0.38.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.38.0...code-confluence-flow-bridge-v0.38.1) (2025-06-14)


### Bug Fixes

* remove java, archguard related dependencies ([b554b9d](https://github.com/unoplat/unoplat-code-confluence/commit/b554b9dd00972e26b79874aa82b4463ce0bae8ef))
* remove java, archguard related dependencies ([bd7d11c](https://github.com/unoplat/unoplat-code-confluence/commit/bd7d11c70581ed9e231f7385b8708ede787b37dc))

## [0.38.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.37.0...code-confluence-flow-bridge-v0.38.0) (2025-06-06)


### Features

* update schema in accordance with auto detection of codebases ([20e2391](https://github.com/unoplat/unoplat-code-confluence/commit/20e2391b1c6dffa5e06fd069536a1c447e98719f))
* update schema in accordance with auto detection of codebases ([b2ea676](https://github.com/unoplat/unoplat-code-confluence/commit/b2ea6765df00bf70a1881f96dbe692e27d35aa28))


### Documentation

* updated docs and api collection for yak ([5266a9d](https://github.com/unoplat/unoplat-code-confluence/commit/5266a9da1c751475dc0a8be456fb33bd8705c99b))

## [0.37.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.36.1...code-confluence-flow-bridge-v0.37.0) (2025-05-29)


### Features

* add code quality tasks and remove pydantic converter ([530e1d2](https://github.com/unoplat/unoplat-code-confluence/commit/530e1d2b993c12f1cba7e6f438987258acafc6b9))
* add code quality tasks and remove pydantic converter ([e1dc759](https://github.com/unoplat/unoplat-code-confluence/commit/e1dc7595316a521b3ce02fbb4d6725aaf6b59e60))

## [0.36.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.36.0...code-confluence-flow-bridge-v0.36.1) (2025-05-29)


### Bug Fixes

* **graph_ingestion:** graceful ingestion in case of existing nodes and relationships and add idempotency tests for repo and package metadata ([82a40f9](https://github.com/unoplat/unoplat-code-confluence/commit/82a40f9cb20266d4b41a76b44555d74599da10a4))
* **graph_ingestion:** graceful ingestion in case of existing nodes and relationships and add idempotency tests for repo and package metadata ([69339da](https://github.com/unoplat/unoplat-code-confluence/commit/69339da7f82b7232f6ed65c5d65da9fc1c3d97e5))

## [0.36.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.35.1...code-confluence-flow-bridge-v0.36.0) (2025-05-28)


### Features

* **ui:** UI overhaul with new design system and support dark/lig ([4b344f5](https://github.com/unoplat/unoplat-code-confluence/commit/4b344f5c85f94f6b062ea0dfd21e66ebcc38a056))
* **ui:** UI overhaul with new design system and support dark/lig ([0bbb67a](https://github.com/unoplat/unoplat-code-confluence/commit/0bbb67ae62472e66c9c9484ac93bad0717123fcc))

## [0.35.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.35.0...code-confluence-flow-bridge-v0.35.1) (2025-05-27)


### Bug Fixes

* make process_git_activity synchronous in git activity processor ([cc9e0d7](https://github.com/unoplat/unoplat-code-confluence/commit/cc9e0d76004d38bbe1f39c32726e0088a940390f))
* per for temporal ([376ef08](https://github.com/unoplat/unoplat-code-confluence/commit/376ef08d8fdd1a40b520e553010470eda50cf405))

## [0.35.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.34.0...code-confluence-flow-bridge-v0.35.0) (2025-05-26)


### Features

* **package-manager:** add automatic package manager detection ([0aa88bd](https://github.com/unoplat/unoplat-code-confluence/commit/0aa88bd65d46c1a3df35c6bf02d769c2a5548585))
* **parser:** improve package manager metadata handling and license parsing ([62bc9ce](https://github.com/unoplat/unoplat-code-confluence/commit/62bc9ce286f5d4610e4ce837febfe4b11cc8a57c))

## [0.34.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.33.1...code-confluence-flow-bridge-v0.34.0) (2025-05-26)


### Features

* updated schema to have intermediate file node while coming in from package and then to individual class/procedural nodes. ([2e66110](https://github.com/unoplat/unoplat-code-confluence/commit/2e661103729426104d0dafb8a33fbd659ae6f3ed))
* updated schema to have intermediate file node while coming in from package and then to individual class/procedural nodes. ([df0add2](https://github.com/unoplat/unoplat-code-confluence/commit/df0add2354876e1d0a07ab98401c2ef239e36065))

## [0.33.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.33.0...code-confluence-flow-bridge-v0.33.1) (2025-05-20)


### Documentation

* **rules:** add think-tool-usage rule for reasoning workflow ([1058a7a](https://github.com/unoplat/unoplat-code-confluence/commit/1058a7a91ca97c7f5fd03f1dc4d2d23551936ea8))

## [0.33.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.32.1...code-confluence-flow-bridge-v0.33.0) (2025-05-17)


### Features

* add OpenTelemetry dependencies and improve logging ([1cd5d64](https://github.com/unoplat/unoplat-code-confluence/commit/1cd5d6496552320a364e45dd017b93536cb163a5))
* **api:** add endpoint to fetch all parent workflow jobs ([80e5629](https://github.com/unoplat/unoplat-code-confluence/commit/80e562974cc563b87ec6e0e95e1337a988fa993c))
* **api:** add endpoint to fetch repository workflow run ([cfffa4c](https://github.com/unoplat/unoplat-code-confluence/commit/cfffa4c1efe6585d6291f66432195a8fbbb392d9))
* **errorhandling:** enhance logger context with activity_name and improve error handling ([90fc7e2](https://github.com/unoplat/unoplat-code-confluence/commit/90fc7e26684040e8e78c8b990667d5e6c66ff300))
* **github:** add issue_tracking field to workflow run models ([bae3dce](https://github.com/unoplat/unoplat-code-confluence/commit/bae3dce1fda2565be40c7f47d21050bdd4a4b5b0))
* improve logging context and workflow child handling ([e859e6d](https://github.com/unoplat/unoplat-code-confluence/commit/e859e6d06048e8aa8c9c61f2f3941d77f686ee10))
* improve repository data handling and refactor codebase workflow ([80d0d0a](https://github.com/unoplat/unoplat-code-confluence/commit/80d0d0ad68f69015d534c3ba487e4c0fc229a6a1))
* **issue-tracking:** add GitHub issue creation endpoint ([eaa7147](https://github.com/unoplat/unoplat-code-confluence/commit/eaa71471008c90fbe14f91a62704c4719d506cb3))
* **job-status-table:** add job status data table columns component ([42ae4a1](https://github.com/unoplat/unoplat-code-confluence/commit/42ae4a18522cfafeaf3f84f0a2553b6868ad9230))
* **logging:** enhance logger context with workflow and activity IDs ([d8e11d2](https://github.com/unoplat/unoplat-code-confluence/commit/d8e11d27917b82bd94f50acf9aaa532b1a882f62))
* **perf:** use async session methods and update dependencies ([d6a9711](https://github.com/unoplat/unoplat-code-confluence/commit/d6a97119097330779d9f1d0f8b9649ef1ed42d13))
* refactor GitHub repo models and add child workflow DB activity ([ee07cb3](https://github.com/unoplat/unoplat-code-confluence/commit/ee07cb3c72e8a36d96d46f888c231ea85fb1777d))
* **workflow:** add retry policies to critical activities ([7669523](https://github.com/unoplat/unoplat-code-confluence/commit/766952382859fb7f48b4443440db8d39e7f234da))


### Bug Fixes

* **db:** enhance error context and improve UI button styles ([d4d8003](https://github.com/unoplat/unoplat-code-confluence/commit/d4d8003636766df29005ca897e43e4c374a1a17b))
* **db:** handle empty repository metadata and preserve failed status ([02fd624](https://github.com/unoplat/unoplat-code-confluence/commit/02fd624d536836cd3110539156553d21f5ca4b19))
* **logging:** unify trace_id key to app_trace_id in logging context ([095af97](https://github.com/unoplat/unoplat-code-confluence/commit/095af97c631c5b15523113af5a40c9b6caddcc5a))
* **parent_workflow_interceptor:** clear error_report on parent failure ([1a2e773](https://github.com/unoplat/unoplat-code-confluence/commit/1a2e773bf417d754ff40995fe51796b64727dc2f))
* **parser:** remove artificial bug causing ZeroDivisionError ([6c7097b](https://github.com/unoplat/unoplat-code-confluence/commit/6c7097b7a97183fba6b0835b88918dd10812cbb2))
* **parser:** remove artificial bug causing ZeroDivisionError ([0c07083](https://github.com/unoplat/unoplat-code-confluence/commit/0c070830016337beb60603ecdb4f5a09bc5393ea))
* **parser:** remove artificial bug causing ZeroDivisionError ([1eeb568](https://github.com/unoplat/unoplat-code-confluence/commit/1eeb568ae13a3f3ea5c5c4b6c89cd833402d33c0))

## [0.32.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.32.0...code-confluence-flow-bridge-v0.32.1) (2025-04-24)


### Bug Fixes

* update frontend image and flow-bridge version ([f927f0c](https://github.com/unoplat/unoplat-code-confluence/commit/f927f0c60331c9bd3853c04b36728e9a7dc1a279))
* update frontend image and flow-bridge version ([2c91515](https://github.com/unoplat/unoplat-code-confluence/commit/2c91515128f5e4767a3334a63b9490f1c0de93a9))

## [0.32.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.31.1...code-confluence-flow-bridge-v0.32.0) (2025-04-24)


### Features

* **logging:** standardize and enhance logging details ([b1cf05b](https://github.com/unoplat/unoplat-code-confluence/commit/b1cf05b0f97cc7d5be56a4de57a8dc6c6d8b2436))
* **logging:** standardize and enhance logging details ([74cebaf](https://github.com/unoplat/unoplat-code-confluence/commit/74cebaf475f11e1a6273e0e694989cb27c995a7a))

## [0.31.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.31.0...code-confluence-flow-bridge-v0.31.1) (2025-04-23)


### Bug Fixes

* **logging:** set default log level to INFO from DEBUG ([242f883](https://github.com/unoplat/unoplat-code-confluence/commit/242f883d9642eac86bd8f91ec31b91f9389ec036))
* **logging:** set default log level to INFO from DEBUG ([cd0219d](https://github.com/unoplat/unoplat-code-confluence/commit/cd0219d9047a878462505522068ac036a2b68380))

## [0.31.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.30.0...code-confluence-flow-bridge-v0.31.0) (2025-04-23)


### Features

* improve function-class connection and add debug logging ([2abe131](https://github.com/unoplat/unoplat-code-confluence/commit/2abe1311d90bfe7b2d5190e4cc28dbbadf2d58e0))
* improve function-class connection and add debug logging ([ced3e85](https://github.com/unoplat/unoplat-code-confluence/commit/ced3e857caba9d64ead78e3472ba72e2813a092f))


### Bug Fixes

* **logging:** change success logs to debug for ingestion steps ([da4b40a](https://github.com/unoplat/unoplat-code-confluence/commit/da4b40adc19f5774279d70dfffb7397941fd172e))

## [0.30.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.29.1...code-confluence-flow-bridge-v0.30.0) (2025-04-22)


### Features

* **author-utils:** add normalize_authors to unify author formats ([54c2123](https://github.com/unoplat/unoplat-code-confluence/commit/54c212318cfb89608a32bebe3c13fd08077e64ae))
* **author-utils:** add normalize_authors to unify author formats ([7aa2a72](https://github.com/unoplat/unoplat-code-confluence/commit/7aa2a7246f31ebcd0e659b10a56482b4c96aa8ab))

## [0.29.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.29.0...code-confluence-flow-bridge-v0.29.1) (2025-04-21)


### Bug Fixes

* uv lock for flow-bridge ([ccc1a9e](https://github.com/unoplat/unoplat-code-confluence/commit/ccc1a9e62a106276eac57e245356a1070629bb54))
* uv lock for flow-bridge ([fcdf838](https://github.com/unoplat/unoplat-code-confluence/commit/fcdf8388974a8683fbbf979de344e0498c57299b))

## [0.29.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.28.0...code-confluence-flow-bridge-v0.29.0) (2025-04-21)


### Features

* **settings:** sidebar perfection ([c4bc34b](https://github.com/unoplat/unoplat-code-confluence/commit/c4bc34b6cce9dae065364e213960c57c612bbb68))


### Bug Fixes

* github token close properly ([dab6b78](https://github.com/unoplat/unoplat-code-confluence/commit/dab6b78368e522f05b7a6de6db346b85b5c098b1))

## [0.28.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.27.0...code-confluence-flow-bridge-v0.28.0) (2025-04-17)


### Features

* add workflow status models and PostgreSQL DB setup ([63ac90b](https://github.com/unoplat/unoplat-code-confluence/commit/63ac90bcbdb5abf25d35c105763a9fdd8b7030d4))
* add workflow status models and PostgreSQL DB setup ([0dab3bb](https://github.com/unoplat/unoplat-code-confluence/commit/0dab3bb3b650dc05282f8e067eec43b934ae4876))


### Bug Fixes

* update GitHub helper tests to use GitHubRepoRequestConfigurationf ([b945578](https://github.com/unoplat/unoplat-code-confluence/commit/b9455783afa9e5367823097452a076da07a8a0d3))

## [0.27.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.26.1...code-confluence-flow-bridge-v0.27.0) (2025-04-10)


### Features

* update repository filtering and pagination logic ([36dc786](https://github.com/unoplat/unoplat-code-confluence/commit/36dc78666d4074dc36f319674515a43670e8c3ea))
* update repository filtering and pagination logic ([d14e59f](https://github.com/unoplat/unoplat-code-confluence/commit/d14e59fd465cf849d6c491a1fd854ddb4d403b65))

## [0.26.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.26.0...code-confluence-flow-bridge-v0.26.1) (2025-04-09)


### Bug Fixes

* github token popup ([2c3c99d](https://github.com/unoplat/unoplat-code-confluence/commit/2c3c99da6f1c6e8f47f62fdf65b3ecfff23c5885))
* github token popup ([ea8d353](https://github.com/unoplat/unoplat-code-confluence/commit/ea8d353b1e549b4b0fc64608d99d469ffa8d66c8))

## [0.26.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.25.0...code-confluence-flow-bridge-v0.26.0) (2025-04-08)


### Features

* migrate to dice ui data table + router  + query ([c961b7a](https://github.com/unoplat/unoplat-code-confluence/commit/c961b7a49d8a7f0448d76efc36764cc8fbcdd8d2))
* migrate to dice ui data table + router  + query ([9eae225](https://github.com/unoplat/unoplat-code-confluence/commit/9eae2255881913201cad76cdb598fc84b3cf27b6))

## [0.25.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.24.0...code-confluence-flow-bridge-v0.25.0) (2025-04-03)


### Features

* support server side filtering and pagination by switching to graphql based github apis ([318f96e](https://github.com/unoplat/unoplat-code-confluence/commit/318f96e39d99d061a4077947a1da356d09f45252))
* support server side filtering and pagination by switching to graphql based github apis ([fe7f921](https://github.com/unoplat/unoplat-code-confluence/commit/fe7f9212ad04ca551e0ff78d26e0c83f69062a03))

## [0.24.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.23.0...code-confluence-flow-bridge-v0.24.0) (2025-04-02)


### Features

* support frontend flag management ([e93d9ce](https://github.com/unoplat/unoplat-code-confluence/commit/e93d9ce7b5b2352f938209f41a6d1e78d0c1714c))
* support frontend flag management ([cd54ab9](https://github.com/unoplat/unoplat-code-confluence/commit/cd54ab9d92b6a368abe37d081faa277a1d7d9198))

## [0.23.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.22.0...code-confluence-flow-bridge-v0.23.0) (2025-04-02)


### Features

* enhanced app name typography and improved icons for sidebar navigation ([0c73525](https://github.com/unoplat/unoplat-code-confluence/commit/0c7352504814ffb3948b382a0159388f3c90fb8b))


### Documentation

* add llm docs for shadcn and tanstack ([cdba490](https://github.com/unoplat/unoplat-code-confluence/commit/cdba4909846eb8fddac65da7dad2fe15c732412a))

## [0.22.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.21.1...code-confluence-flow-bridge-v0.22.0) (2025-04-01)


### Features

* added delete user endpoint ([54bcfd0](https://github.com/unoplat/unoplat-code-confluence/commit/54bcfd0d13af22ce2bc9e828355e77485d90f2f4))
* added delete user endpoint ([768b2d1](https://github.com/unoplat/unoplat-code-confluence/commit/768b2d1314b5904ca72f3971cb8c0f6aff5ea889))

## [0.21.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.21.0...code-confluence-flow-bridge-v0.21.1) (2025-04-01)


### Bug Fixes

* dummy commit for docker publish ([64a250a](https://github.com/unoplat/unoplat-code-confluence/commit/64a250a211438601ec956b4cf2f165360a59421c))
* dummy commit for docker publish ([d7d005b](https://github.com/unoplat/unoplat-code-confluence/commit/d7d005bb12aba7b35bad6e0ec7cd44b471a74cd6))

## [0.21.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.20.0...code-confluence-flow-bridge-v0.21.0) (2025-04-01)


### Features

* abandon child workflows as they are long running and we aggregate information in neo4j ([99123b6](https://github.com/unoplat/unoplat-code-confluence/commit/99123b6c72bdba2de7ad04b72c10c0e35f236a75))
* Add additional metadata fields to UnoplatPackageManagerMetadata and enhance poetry strategy parsing. Updated tests to validate new fields including homepage, repository, documentation, keywords, maintainers, and readme. Improved dependency parsing to include all groups from pyproject.toml. ([51c0a15](https://github.com/unoplat/unoplat-code-confluence/commit/51c0a153a81ecb96ff485ee5f7d456ab83797fbb))
* Add configuration for code-confluence-flow-bridge ingestion and update workflows for testing. Introduced new release configuration and updated manifest to include flow-bridge package. Enhanced Python build workflow to support testing for the new project, ensuring proper setup and dependency management. ([baaebab](https://github.com/unoplat/unoplat-code-confluence/commit/baaebab7cc91c542117981d9453eb30311455ad3))
* add CORS middleware to FastAPI application ([fc9124f](https://github.com/unoplat/unoplat-code-confluence/commit/fc9124f858664c5e0be4df77a505cdb5dba3841a))
* add database initialization and CORS configuration ([9dc2094](https://github.com/unoplat/unoplat-code-confluence/commit/9dc209451489a394a4bc4fa6ff1d3696446d8db1))
* Add Docker and development infrastructure for code confluence flow bridge ([fd1ab9c](https://github.com/unoplat/unoplat-code-confluence/commit/fd1ab9c79fc7bb35891bd8ae89990d7b524c5181))
* add file based logging and terminal logging with colors ([ec8df8c](https://github.com/unoplat/unoplat-code-confluence/commit/ec8df8ce7c1131aa78e723c610c3768eb26dff18))
* add PostgreSQL connection and session management ([55f122b](https://github.com/unoplat/unoplat-code-confluence/commit/55f122b3de809e6743b2cc10f938663126733f71))
* add PostgreSQL connection and session management ([d3081b5](https://github.com/unoplat/unoplat-code-confluence/commit/d3081b53033b2f80b51780b59634aa269557951e))
* Add Python function call extraction and instantiation detection ([fe40aa1](https://github.com/unoplat/unoplat-code-confluence/commit/fe40aa1570432113f471f4cec1f1b1f8bbe81e4d))
* Add Scanner CLI download to GitHub Actions workflow ([82d8a72](https://github.com/unoplat/unoplat-code-confluence/commit/82d8a724afb454c7079fc727a4b656041d7e76fc))
* Add test data and infrastructure for code confluence ingestion ([8025b5e](https://github.com/unoplat/unoplat-code-confluence/commit/8025b5e66d38dcec778abfdee7b9322e2bccdeed))
* added code parsing code and test for one activity of parent workflow- cloning ([6aaf0a8](https://github.com/unoplat/unoplat-code-confluence/commit/6aaf0a81dafaaf89608781576d209c5e553156a6))
* added fast api based bridge to handle ingestion requests coming in from user ([71c505c](https://github.com/unoplat/unoplat-code-confluence/commit/71c505c0460d6311e8be579364af13c4257fbc3a))
* added git token acceptance and onboarding/settings screens ([9401425](https://github.com/unoplat/unoplat-code-confluence/commit/9401425ba0795805a6d634ee11a855008c08c2e8))
* added git token acceptance and onboarding/settings screens ([114802d](https://github.com/unoplat/unoplat-code-confluence/commit/114802d8659171d9a192e2429409aa325b831be2))
* added relationships for annotation ([3c97e15](https://github.com/unoplat/unoplat-code-confluence/commit/3c97e1521134022c6dbcfcba7ae8293621eae378))
* child workflow poc complete with package manager metadata for next step that is to apply isort and ruff ([cef8d8f](https://github.com/unoplat/unoplat-code-confluence/commit/cef8d8f98ba00be53eb813d408b4523f197a15a3))
* **db:** read echo setting from environment variable ([c7988c6](https://github.com/unoplat/unoplat-code-confluence/commit/c7988c67f4ccaf5b3842fc639c547e33f0c11dfd))
* **docker:** add PostgreSQL and Elasticsearch and Frontend related services ([db51f81](https://github.com/unoplat/unoplat-code-confluence/commit/db51f81269dd1a842782597dec274e6b80ecb683))
* **docker:** add PostgreSQL and Elasticsearch and Frontend related services ([0fc7618](https://github.com/unoplat/unoplat-code-confluence/commit/0fc761826125c9ae5aa0c8a47cbd09ef4125129c))
* enhance codebase processing with linting, archguard analysis, and package parsing ([0310a37](https://github.com/unoplat/unoplat-code-confluence/commit/0310a37518d29a5e9be5b91e62163071c08911e2))
* Enhance dependency parsing and metadata extraction in PipStrategy and SetupParser, update UnoplatProjectDependency model with default values and descriptions, improve PipStrategy to handle multiple requirement file patterns and merge constraints, enhance SetupParser to parse setup.py files robustly including extras and environment markers, add comprehensive tests for requirements parsing, VCS dependencies, and setup.py metadata extraction, update .gitignore to exclude additional test artifacts. ([8803124](https://github.com/unoplat/unoplat-code-confluence/commit/88031243b118e55e0b7f78a51dcf3d7eb533bcdb))
* Enhance Docker Compose Configuration for Code Confluence Flow B… ([9e96442](https://github.com/unoplat/unoplat-code-confluence/commit/9e9644244a7bf31a4a5b4c49f3db76c2133de59d))
* Enhance Docker Compose Configuration for Code Confluence Flow Bridge ([dcdc313](https://github.com/unoplat/unoplat-code-confluence/commit/dcdc313c1d1531a3eea88e87121b5de49c3acbef))
* Enhance Docker Release Workflow for Code Confluence Flow Bridge ([792560e](https://github.com/unoplat/unoplat-code-confluence/commit/792560e35052c37e927ec11bbbcfdab5b58cc82b))
* Enhance Docker Workflow and Scanner CLI Integration ([fcf6ab3](https://github.com/unoplat/unoplat-code-confluence/commit/fcf6ab31e4a79c25551f4869ae4f13df7b0eb3ec))
* Enhance HomepageFeatures component with new features and modals ([9755836](https://github.com/unoplat/unoplat-code-confluence/commit/975583689e968a307173918c04f6e50c5e0c8a9e))
* Enhance ingestion workflow with Neo4j integration and environment settings- Added Neo4j database connection support with new configuration parameters.- Implemented ConfluenceGitGraph for ingesting Git repo data into Neo4j, with refactored workflows.- Updated Taskfile for Temporal server setup and .gitignore for additional cache exclusions. ([b7035e3](https://github.com/unoplat/unoplat-code-confluence/commit/b7035e3fed991ea28f19fb829a6652d0dd2dc896))
* Enhance logging and error handling across workflows and activities. Added contextual logging for workflow execution, improved error messages with detailed context, and ensured consistent use of activity logger in Git and package metadata processing. This refactor aims to improve traceability and debugging capabilities during the ingestion process. ([0bf6ba4](https://github.com/unoplat/unoplat-code-confluence/commit/0bf6ba49c55b31227ed1ed0c26a55db1b531151a))
* Enhance test infrastructure with Scanner CLI and GitHub Actions ([9d9371a](https://github.com/unoplat/unoplat-code-confluence/commit/9d9371a3fba7d86cd0b3e6eab10d6d90d2ace055))
* improved contact us responsiveness and basic layout ([5337d51](https://github.com/unoplat/unoplat-code-confluence/commit/5337d51bdbb51a34c2d4218498fb4bcf3e2055f8))
* included test coverage for static classes in same file and across codebase/external ([adce2e0](https://github.com/unoplat/unoplat-code-confluence/commit/adce2e06ec5d655a0cf82bc5beacbf083a712037))
* Introduce specifier field in UnoplatVersion model and refactor version constraint parsing. Updated PythonPoetryStrategy and UvStrategy to utilize the new specifier field for version constraints, simplifying the parsing logic. Enhanced tests to validate changes and added a new test case for unoplat project metadata processing. ([a701217](https://github.com/unoplat/unoplat-code-confluence/commit/a7012177f7c2ddefc3f62f159df68ecd88f90c65))
* Introduce UV package manager strategy for enhanced metadata extraction and dependency parsing from pyproject.toml. Added support for optional dependencies, git sources, and environment markers. Updated tests to validate new functionality and ensure comprehensive coverage for UV strategy. Refactored existing tests to improve structure and maintainability. ([7f289e4](https://github.com/unoplat/unoplat-code-confluence/commit/7f289e40d73e817a5767f28670faef76e59de2f5))
* made git clone operation async to not block the event loop ([d13b440](https://github.com/unoplat/unoplat-code-confluence/commit/d13b440babbe3f5880e4fac36ead40e7504e30ce))
* merge ci/cd changes and changelog ([19a9afa](https://github.com/unoplat/unoplat-code-confluence/commit/19a9afa2b38c4979824e30d5d6b5490689a63714))
* milestone 2 d2 basic architecture ([cf2af7a](https://github.com/unoplat/unoplat-code-confluence/commit/cf2af7a977ed61b80fb23ef211dfffec73d3ac75))
* Refactor codebase ingestion workflow by introducing PackageManagerMetadataIngestion for handling package manager metadata, updating activity signatures, and enhancing the ParentChildCloneMetadata model for improved clarity and functionality. Added tests for package manager metadata insertion to ensure data integrity. ([85650e7](https://github.com/unoplat/unoplat-code-confluence/commit/85650e79849ab2812f2e73aa247970d2c4db6c42))
* support function calls for procedural node ([5134d37](https://github.com/unoplat/unoplat-code-confluence/commit/5134d3777dad6e7e6163ec46c1441d842856f450))
* support function calls for single class node ([088b105](https://github.com/unoplat/unoplat-code-confluence/commit/088b105536a35db0f075fd99b8b12c5965165fa9))
* support nested functions linkage ([51ee3af](https://github.com/unoplat/unoplat-code-confluence/commit/51ee3afb167474d0c4086344a5fc02589fdd37fe))
* support nested functions linkage ([9c5e6c1](https://github.com/unoplat/unoplat-code-confluence/commit/9c5e6c1618fd484abcba14e8838054c74406ad1c))
* support node with 1..n class nodes ([597d721](https://github.com/unoplat/unoplat-code-confluence/commit/597d721869e53de427c81ae77f73099b17463df0))
* update dependencies and add nested function detection ([17ceb7c](https://github.com/unoplat/unoplat-code-confluence/commit/17ceb7c0b176caf71da66b5ce0b0e45ef7e6a63e))
* update dependencies and add nested function detection ([f5adfe2](https://github.com/unoplat/unoplat-code-confluence/commit/f5adfe2eff9efafc92dfd72d97025e52392d6777))
* Update Development Setup and Local Workflow for Code Confluence Flow Bridge ([89f13d6](https://github.com/unoplat/unoplat-code-confluence/commit/89f13d6722c9e9c723949afe859fe65749a1222a))
* update latest archguard jar to get right spaces and indentations in function blocks ([c9a1f00](https://github.com/unoplat/unoplat-code-confluence/commit/c9a1f00479201c1eb4b89ccd1b938e276e025dec))
* updated jar versions in docker files ([aad52d7](https://github.com/unoplat/unoplat-code-confluence/commit/aad52d783481b0893ab02a19298a1377d7f5d610))
* updated neomodel based graph lib to support local path attribute for codebase node ([e5edc4f](https://github.com/unoplat/unoplat-code-confluence/commit/e5edc4ff26ab5ee7f21ef2d5004fa787857d6da9))
* upgraded archguard jars ([0b7499e](https://github.com/unoplat/unoplat-code-confluence/commit/0b7499e1ce2704c951f4e22a8551ec962c978f13))
* use a neo4j connection pool across activities and async implementation ([4cf8a0c](https://github.com/unoplat/unoplat-code-confluence/commit/4cf8a0c1bc4c1c1f3053a247edfb23f5d07b1d66))
* we now support nodes with procedural methods and 1..n classes ([dae64c6](https://github.com/unoplat/unoplat-code-confluence/commit/dae64c61a194b5a488e4543084d0ed73c7fb5bfe))


### Bug Fixes

* added do linkage call in python codebase parser ([c02602f](https://github.com/unoplat/unoplat-code-confluence/commit/c02602f09caa419c33c26dd58dae624817f9d074))
* added do linkage call in python codebase parser ([531abfa](https://github.com/unoplat/unoplat-code-confluence/commit/531abfaf6e07fe889fbd862c31059d279aa50c03))
* added pytest in main dependencies so that we are able to run in vscode ([d5a3caa](https://github.com/unoplat/unoplat-code-confluence/commit/d5a3caac5f86e0bf2baa3ee7bab2fc889020ba08))
* concurrent submission and waiting of child workflows ([a06e784](https://github.com/unoplat/unoplat-code-confluence/commit/a06e784d5bd08f5bb3b82c8456220890167c8dde))
* file name should not be removed otherwise we will not be able to match imports with actual file nodes ([b2536ae](https://github.com/unoplat/unoplat-code-confluence/commit/b2536ae4429c9b1c1e301a81a75903ad5097eac0))
* file name should not be removed otherwise we will not be able to… ([50b9c42](https://github.com/unoplat/unoplat-code-confluence/commit/50b9c42163fb19c93fe350e49003abe391189207))
* fix schema not handling local path of codebase node in neo4j ([9d5e7d2](https://github.com/unoplat/unoplat-code-confluence/commit/9d5e7d2bd6cd2d24505ec2cc6e0febd58875191a))
* fixed relationship direction for git repo and codebase ([4851728](https://github.com/unoplat/unoplat-code-confluence/commit/4851728d26f96eaae3ae99a925bd02aa3c8f376b))
* function call to extract function calls ([754b362](https://github.com/unoplat/unoplat-code-confluence/commit/754b36250e1dd2c2e3a889aa18eaa923f8cd0608))
* git url for frontend ([c058b37](https://github.com/unoplat/unoplat-code-confluence/commit/c058b3778cc8255c1e72a39ecf18134d8912b263))
* improved error messages ([f91b32f](https://github.com/unoplat/unoplat-code-confluence/commit/f91b32f22b0963777236769490363b3a644ffa1c))
* improved error messages ([31f26e0](https://github.com/unoplat/unoplat-code-confluence/commit/31f26e0704955d34f5bfb934791e40f8230f0e4d))
* ingestion with relation ([1b6f743](https://github.com/unoplat/unoplat-code-confluence/commit/1b6f743fe33d2d7b53c10b7f754a90de8098d459))
* install schema before proceeding ([7fcf2c0](https://github.com/unoplat/unoplat-code-confluence/commit/7fcf2c08f27efa1aa2bf151902d31a8d407ee813))
* move git clone to async operation to not block fix tests and fix browser url link in docs ([0f2a7ac](https://github.com/unoplat/unoplat-code-confluence/commit/0f2a7acc5bbfae2a9f5bafe061d936d60cba3929))
* package manager metadata wrong path ([c33cca3](https://github.com/unoplat/unoplat-code-confluence/commit/c33cca3eb0c8858c5a94d4b3e1a806a5b637c389))
* removed condition that was added by llm which can never be true … ([bd47fc8](https://github.com/unoplat/unoplat-code-confluence/commit/bd47fc8028bae52ddddf6c972cc9887e82b3b429))
* removed condition that was added by llm which can never be true for cross referencing procedural functions ([5175b80](https://github.com/unoplat/unoplat-code-confluence/commit/5175b80f961b9715443ce6f4813cd2e51a6c99ed))
* test updates ([2171011](https://github.com/unoplat/unoplat-code-confluence/commit/21710113ed919e290a5abfdc011b26156f7480e0))
* update Dockerfile and clean up imports in main.py ([9cdf33d](https://github.com/unoplat/unoplat-code-confluence/commit/9cdf33d7f7c6012f23a616055b11822a916d260c))
* update Dockerfile and clean up imports in main.py ([8e93f12](https://github.com/unoplat/unoplat-code-confluence/commit/8e93f123417ac89bcdfc14c01837bc75f304e5c1))
* update release to get the right updated jar ([4e298ea](https://github.com/unoplat/unoplat-code-confluence/commit/4e298ea19e95491b4370710435fee668d2213b22))
* updated right jar name ([167b47a](https://github.com/unoplat/unoplat-code-confluence/commit/167b47a4c5430a36486beea0779747bed124fe85))


### Documentation

* improve the local development ([7d7d80e](https://github.com/unoplat/unoplat-code-confluence/commit/7d7d80e6de15c76387df9e716fec92cb5be248a3))
* improvement in docs ([0b8f858](https://github.com/unoplat/unoplat-code-confluence/commit/0b8f8588cd80976007d520b62eeb8a8f6b1d77f0))
* prereq for code confluence bridge ([56fea07](https://github.com/unoplat/unoplat-code-confluence/commit/56fea078fe2dd86341d289619091a63c09b692e0))
* update for flow for milestone 2 ([96b0306](https://github.com/unoplat/unoplat-code-confluence/commit/96b0306f3b014e04f7fcc0748fd0030055ec8a7a))
* updated docs for running fastapi based project ([191c295](https://github.com/unoplat/unoplat-code-confluence/commit/191c2952147866c09c320353af7b4330a61f88a9))

## [0.20.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.19.0...code-confluence-flow-bridge-v0.20.0) (2025-03-31)


### Features

* added git token acceptance and onboarding/settings screens ([9401425](https://github.com/unoplat/unoplat-code-confluence/commit/9401425ba0795805a6d634ee11a855008c08c2e8))
* added git token acceptance and onboarding/settings screens ([114802d](https://github.com/unoplat/unoplat-code-confluence/commit/114802d8659171d9a192e2429409aa325b831be2))

## [0.19.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.18.1...code-confluence-flow-bridge-v0.19.0) (2025-03-31)


### Features

* **docker:** add PostgreSQL and Elasticsearch and Frontend related services ([db51f81](https://github.com/unoplat/unoplat-code-confluence/commit/db51f81269dd1a842782597dec274e6b80ecb683))
* **docker:** add PostgreSQL and Elasticsearch and Frontend related services ([0fc7618](https://github.com/unoplat/unoplat-code-confluence/commit/0fc761826125c9ae5aa0c8a47cbd09ef4125129c))

## [0.18.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.18.0...code-confluence-flow-bridge-v0.18.1) (2025-03-29)


### Bug Fixes

* update Dockerfile and clean up imports in main.py ([9cdf33d](https://github.com/unoplat/unoplat-code-confluence/commit/9cdf33d7f7c6012f23a616055b11822a916d260c))
* update Dockerfile and clean up imports in main.py ([8e93f12](https://github.com/unoplat/unoplat-code-confluence/commit/8e93f123417ac89bcdfc14c01837bc75f304e5c1))

## [0.18.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.17.0...code-confluence-flow-bridge-v0.18.0) (2025-03-29)


### Features

* add CORS middleware to FastAPI application ([fc9124f](https://github.com/unoplat/unoplat-code-confluence/commit/fc9124f858664c5e0be4df77a505cdb5dba3841a))
* add database initialization and CORS configuration ([9dc2094](https://github.com/unoplat/unoplat-code-confluence/commit/9dc209451489a394a4bc4fa6ff1d3696446d8db1))
* **db:** read echo setting from environment variable ([c7988c6](https://github.com/unoplat/unoplat-code-confluence/commit/c7988c67f4ccaf5b3842fc639c547e33f0c11dfd))

## [0.17.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.16.0...code-confluence-flow-bridge-v0.17.0) (2025-03-29)


### Features

* add PostgreSQL connection and session management ([55f122b](https://github.com/unoplat/unoplat-code-confluence/commit/55f122b3de809e6743b2cc10f938663126733f71))
* add PostgreSQL connection and session management ([d3081b5](https://github.com/unoplat/unoplat-code-confluence/commit/d3081b53033b2f80b51780b59634aa269557951e))

## [0.16.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.15.1...code-confluence-flow-bridge-v0.16.0) (2025-03-25)


### Features

* update dependencies and add nested function detection ([17ceb7c](https://github.com/unoplat/unoplat-code-confluence/commit/17ceb7c0b176caf71da66b5ce0b0e45ef7e6a63e))
* update dependencies and add nested function detection ([f5adfe2](https://github.com/unoplat/unoplat-code-confluence/commit/f5adfe2eff9efafc92dfd72d97025e52392d6777))

## [0.15.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.15.0...code-confluence-flow-bridge-v0.15.1) (2025-02-28)


### Bug Fixes

* added do linkage call in python codebase parser ([531abfa](https://github.com/unoplat/unoplat-code-confluence/commit/531abfaf6e07fe889fbd862c31059d279aa50c03))

## [0.15.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.14.2...code-confluence-flow-bridge-v0.15.0) (2025-02-28)


### Features

* support nested functions linkage ([9c5e6c1](https://github.com/unoplat/unoplat-code-confluence/commit/9c5e6c1618fd484abcba14e8838054c74406ad1c))

## [0.14.2](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.14.1...code-confluence-flow-bridge-v0.14.2) (2025-02-28)


### Bug Fixes

* removed condition that was added by llm which can never be true for cross referencing procedural functions ([5175b80](https://github.com/unoplat/unoplat-code-confluence/commit/5175b80f961b9715443ce6f4813cd2e51a6c99ed))

## [0.14.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.14.0...code-confluence-flow-bridge-v0.14.1) (2025-02-27)


### Bug Fixes

* file name should not be removed otherwise we will not be able to match imports with actual file nodes ([b2536ae](https://github.com/unoplat/unoplat-code-confluence/commit/b2536ae4429c9b1c1e301a81a75903ad5097eac0))

## [0.14.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.13.0...code-confluence-flow-bridge-v0.14.0) (2025-02-27)


### Features

* Add Python function call extraction and instantiation detection ([fe40aa1](https://github.com/unoplat/unoplat-code-confluence/commit/fe40aa1570432113f471f4cec1f1b1f8bbe81e4d))
* included test coverage for static classes in same file and across codebase/external ([adce2e0](https://github.com/unoplat/unoplat-code-confluence/commit/adce2e06ec5d655a0cf82bc5beacbf083a712037))
* support function calls for procedural node ([5134d37](https://github.com/unoplat/unoplat-code-confluence/commit/5134d3777dad6e7e6163ec46c1441d842856f450))
* support function calls for single class node ([088b105](https://github.com/unoplat/unoplat-code-confluence/commit/088b105536a35db0f075fd99b8b12c5965165fa9))
* support node with 1..n class nodes ([597d721](https://github.com/unoplat/unoplat-code-confluence/commit/597d721869e53de427c81ae77f73099b17463df0))
* we now support nodes with procedural methods and 1..n classes ([dae64c6](https://github.com/unoplat/unoplat-code-confluence/commit/dae64c61a194b5a488e4543084d0ed73c7fb5bfe))


### Bug Fixes

* function call to extract function calls ([754b362](https://github.com/unoplat/unoplat-code-confluence/commit/754b36250e1dd2c2e3a889aa18eaa923f8cd0608))
* updated right jar name ([167b47a](https://github.com/unoplat/unoplat-code-confluence/commit/167b47a4c5430a36486beea0779747bed124fe85))

## [0.13.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.12.0...code-confluence-flow-bridge-v0.13.0) (2025-02-20)


### Features

* update latest archguard jar to get right spaces and indentations in function blocks ([c9a1f00](https://github.com/unoplat/unoplat-code-confluence/commit/c9a1f00479201c1eb4b89ccd1b938e276e025dec))
* updated jar versions in docker files ([aad52d7](https://github.com/unoplat/unoplat-code-confluence/commit/aad52d783481b0893ab02a19298a1377d7f5d610))
* upgraded archguard jars ([0b7499e](https://github.com/unoplat/unoplat-code-confluence/commit/0b7499e1ce2704c951f4e22a8551ec962c978f13))


### Bug Fixes

* update release to get the right updated jar ([4e298ea](https://github.com/unoplat/unoplat-code-confluence/commit/4e298ea19e95491b4370710435fee668d2213b22))

## [0.12.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.11.1...code-confluence-flow-bridge-v0.12.0) (2025-02-19)


### Features

* made git clone operation async to not block the event loop ([d13b440](https://github.com/unoplat/unoplat-code-confluence/commit/d13b440babbe3f5880e4fac36ead40e7504e30ce))


### Bug Fixes

* move git clone to async operation to not block fix tests and fix browser url link in docs ([0f2a7ac](https://github.com/unoplat/unoplat-code-confluence/commit/0f2a7acc5bbfae2a9f5bafe061d936d60cba3929))
* test updates ([2171011](https://github.com/unoplat/unoplat-code-confluence/commit/21710113ed919e290a5abfdc011b26156f7480e0))

## [0.11.1](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.11.0...code-confluence-flow-bridge-v0.11.1) (2025-02-09)


### Documentation

* improvement in docs ([0b8f858](https://github.com/unoplat/unoplat-code-confluence/commit/0b8f8588cd80976007d520b62eeb8a8f6b1d77f0))

## [0.11.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.10.0...code-confluence-flow-bridge-v0.11.0) (2025-02-08)


### Features

* Update Development Setup and Local Workflow for Code Confluence Flow Bridge ([89f13d6](https://github.com/unoplat/unoplat-code-confluence/commit/89f13d6722c9e9c723949afe859fe65749a1222a))


### Documentation

* improve the local development ([7d7d80e](https://github.com/unoplat/unoplat-code-confluence/commit/7d7d80e6de15c76387df9e716fec92cb5be248a3))

## [0.10.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.9.0...code-confluence-flow-bridge-v0.10.0) (2025-02-08)


### Features

* Add Scanner CLI download to GitHub Actions workflow ([82d8a72](https://github.com/unoplat/unoplat-code-confluence/commit/82d8a724afb454c7079fc727a4b656041d7e76fc))
* Enhance Docker Workflow and Scanner CLI Integration ([fcf6ab3](https://github.com/unoplat/unoplat-code-confluence/commit/fcf6ab31e4a79c25551f4869ae4f13df7b0eb3ec))

## [0.9.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.8.0...code-confluence-flow-bridge-v0.9.0) (2025-02-08)


### Features

* Enhance Docker Compose Configuration for Code Confluence Flow Bridge ([dcdc313](https://github.com/unoplat/unoplat-code-confluence/commit/dcdc313c1d1531a3eea88e87121b5de49c3acbef))

## [0.8.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.7.0...code-confluence-flow-bridge-v0.8.0) (2025-02-08)


### Features

* Add Docker and development infrastructure for code confluence flow bridge ([fd1ab9c](https://github.com/unoplat/unoplat-code-confluence/commit/fd1ab9c79fc7bb35891bd8ae89990d7b524c5181))
* Enhance Docker Release Workflow for Code Confluence Flow Bridge ([792560e](https://github.com/unoplat/unoplat-code-confluence/commit/792560e35052c37e927ec11bbbcfdab5b58cc82b))

## [0.7.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.6.0...code-confluence-flow-bridge-v0.7.0) (2025-02-05)


### Features

* Enhance test infrastructure with Scanner CLI and GitHub Actions ([9d9371a](https://github.com/unoplat/unoplat-code-confluence/commit/9d9371a3fba7d86cd0b3e6eab10d6d90d2ace055))

## [0.6.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.5.0...code-confluence-flow-bridge-v0.6.0) (2025-02-04)


### Features

* Add test data and infrastructure for code confluence ingestion ([8025b5e](https://github.com/unoplat/unoplat-code-confluence/commit/8025b5e66d38dcec778abfdee7b9322e2bccdeed))


### Bug Fixes

* package manager metadata wrong path ([c33cca3](https://github.com/unoplat/unoplat-code-confluence/commit/c33cca3eb0c8858c5a94d4b3e1a806a5b637c389))

## [0.5.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.4.0...code-confluence-flow-bridge-v0.5.0) (2025-02-02)


### Features

* enhance codebase processing with linting, archguard analysis, and package parsing ([0310a37](https://github.com/unoplat/unoplat-code-confluence/commit/0310a37518d29a5e9be5b91e62163071c08911e2))
* improved contact us responsiveness and basic layout ([5337d51](https://github.com/unoplat/unoplat-code-confluence/commit/5337d51bdbb51a34c2d4218498fb4bcf3e2055f8))

## [0.4.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.3.0...code-confluence-flow-bridge-v0.4.0) (2025-01-23)


### Features

* Enhance HomepageFeatures component with new features and modals ([9755836](https://github.com/unoplat/unoplat-code-confluence/commit/975583689e968a307173918c04f6e50c5e0c8a9e))

## [0.3.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.2.0...code-confluence-flow-bridge-v0.3.0) (2025-01-21)


### Features

* abandon child workflows as they are long running and we aggregate information in neo4j ([99123b6](https://github.com/unoplat/unoplat-code-confluence/commit/99123b6c72bdba2de7ad04b72c10c0e35f236a75))
* Add additional metadata fields to UnoplatPackageManagerMetadata and enhance poetry strategy parsing. Updated tests to validate new fields including homepage, repository, documentation, keywords, maintainers, and readme. Improved dependency parsing to include all groups from pyproject.toml. ([51c0a15](https://github.com/unoplat/unoplat-code-confluence/commit/51c0a153a81ecb96ff485ee5f7d456ab83797fbb))
* Add configuration for code-confluence-flow-bridge ingestion and update workflows for testing. Introduced new release configuration and updated manifest to include flow-bridge package. Enhanced Python build workflow to support testing for the new project, ensuring proper setup and dependency management. ([baaebab](https://github.com/unoplat/unoplat-code-confluence/commit/baaebab7cc91c542117981d9453eb30311455ad3))
* add file based logging and terminal logging with colors ([ec8df8c](https://github.com/unoplat/unoplat-code-confluence/commit/ec8df8ce7c1131aa78e723c610c3768eb26dff18))
* added code parsing code and test for one activity of parent workflow- cloning ([6aaf0a8](https://github.com/unoplat/unoplat-code-confluence/commit/6aaf0a81dafaaf89608781576d209c5e553156a6))
* added fast api based bridge to handle ingestion requests coming in from user ([71c505c](https://github.com/unoplat/unoplat-code-confluence/commit/71c505c0460d6311e8be579364af13c4257fbc3a))
* added relationships for annotation ([3c97e15](https://github.com/unoplat/unoplat-code-confluence/commit/3c97e1521134022c6dbcfcba7ae8293621eae378))
* child workflow poc complete with package manager metadata for next step that is to apply isort and ruff ([cef8d8f](https://github.com/unoplat/unoplat-code-confluence/commit/cef8d8f98ba00be53eb813d408b4523f197a15a3))
* Enhance dependency parsing and metadata extraction in PipStrategy and SetupParser, update UnoplatProjectDependency model with default values and descriptions, improve PipStrategy to handle multiple requirement file patterns and merge constraints, enhance SetupParser to parse setup.py files robustly including extras and environment markers, add comprehensive tests for requirements parsing, VCS dependencies, and setup.py metadata extraction, update .gitignore to exclude additional test artifacts. ([8803124](https://github.com/unoplat/unoplat-code-confluence/commit/88031243b118e55e0b7f78a51dcf3d7eb533bcdb))
* Enhance ingestion workflow with Neo4j integration and environment settings- Added Neo4j database connection support with new configuration parameters.- Implemented ConfluenceGitGraph for ingesting Git repo data into Neo4j, with refactored workflows.- Updated Taskfile for Temporal server setup and .gitignore for additional cache exclusions. ([b7035e3](https://github.com/unoplat/unoplat-code-confluence/commit/b7035e3fed991ea28f19fb829a6652d0dd2dc896))
* Introduce UV package manager strategy for enhanced metadata extraction and dependency parsing from pyproject.toml. Added support for optional dependencies, git sources, and environment markers. Updated tests to validate new functionality and ensure comprehensive coverage for UV strategy. Refactored existing tests to improve structure and maintainability. ([7f289e4](https://github.com/unoplat/unoplat-code-confluence/commit/7f289e40d73e817a5767f28670faef76e59de2f5))
* milestone 2 d2 basic architecture ([cf2af7a](https://github.com/unoplat/unoplat-code-confluence/commit/cf2af7a977ed61b80fb23ef211dfffec73d3ac75))
* Refactor codebase ingestion workflow by introducing PackageManagerMetadataIngestion for handling package manager metadata, updating activity signatures, and enhancing the ParentChildCloneMetadata model for improved clarity and functionality. Added tests for package manager metadata insertion to ensure data integrity. ([85650e7](https://github.com/unoplat/unoplat-code-confluence/commit/85650e79849ab2812f2e73aa247970d2c4db6c42))
* use a neo4j connection pool across activities and async implementation ([4cf8a0c](https://github.com/unoplat/unoplat-code-confluence/commit/4cf8a0c1bc4c1c1f3053a247edfb23f5d07b1d66))


### Bug Fixes

* added pytest in main dependencies so that we are able to run in vscode ([d5a3caa](https://github.com/unoplat/unoplat-code-confluence/commit/d5a3caac5f86e0bf2baa3ee7bab2fc889020ba08))
* concurrent submission and waiting of child workflows ([a06e784](https://github.com/unoplat/unoplat-code-confluence/commit/a06e784d5bd08f5bb3b82c8456220890167c8dde))
* fix schema not handling local path of codebase node in neo4j ([9d5e7d2](https://github.com/unoplat/unoplat-code-confluence/commit/9d5e7d2bd6cd2d24505ec2cc6e0febd58875191a))
* fixed relationship direction for git repo and codebase ([4851728](https://github.com/unoplat/unoplat-code-confluence/commit/4851728d26f96eaae3ae99a925bd02aa3c8f376b))
* ingestion with relation ([1b6f743](https://github.com/unoplat/unoplat-code-confluence/commit/1b6f743fe33d2d7b53c10b7f754a90de8098d459))
* install schema before proceeding ([7fcf2c0](https://github.com/unoplat/unoplat-code-confluence/commit/7fcf2c08f27efa1aa2bf151902d31a8d407ee813))


### Documentation

* prereq for code confluence bridge ([56fea07](https://github.com/unoplat/unoplat-code-confluence/commit/56fea078fe2dd86341d289619091a63c09b692e0))
* update for flow for milestone 2 ([96b0306](https://github.com/unoplat/unoplat-code-confluence/commit/96b0306f3b014e04f7fcc0748fd0030055ec8a7a))
* updated docs for running fastapi based project ([191c295](https://github.com/unoplat/unoplat-code-confluence/commit/191c2952147866c09c320353af7b4330a61f88a9))

## [0.2.0](https://github.com/unoplat/unoplat-code-confluence/compare/code-confluence-flow-bridge-v0.1.0...code-confluence-flow-bridge-v0.2.0) (2025-01-20)


### Features

* abandon child workflows as they are long running and we aggregate information in neo4j ([99123b6](https://github.com/unoplat/unoplat-code-confluence/commit/99123b6c72bdba2de7ad04b72c10c0e35f236a75))
* Add additional metadata fields to UnoplatPackageManagerMetadata and enhance poetry strategy parsing. Updated tests to validate new fields including homepage, repository, documentation, keywords, maintainers, and readme. Improved dependency parsing to include all groups from pyproject.toml. ([51c0a15](https://github.com/unoplat/unoplat-code-confluence/commit/51c0a153a81ecb96ff485ee5f7d456ab83797fbb))
* Add configuration for code-confluence-flow-bridge ingestion and update workflows for testing. Introduced new release configuration and updated manifest to include flow-bridge package. Enhanced Python build workflow to support testing for the new project, ensuring proper setup and dependency management. ([baaebab](https://github.com/unoplat/unoplat-code-confluence/commit/baaebab7cc91c542117981d9453eb30311455ad3))
* add file based logging and terminal logging with colors ([ec8df8c](https://github.com/unoplat/unoplat-code-confluence/commit/ec8df8ce7c1131aa78e723c610c3768eb26dff18))
* added code parsing code and test for one activity of parent workflow- cloning ([6aaf0a8](https://github.com/unoplat/unoplat-code-confluence/commit/6aaf0a81dafaaf89608781576d209c5e553156a6))
* added fast api based bridge to handle ingestion requests coming in from user ([71c505c](https://github.com/unoplat/unoplat-code-confluence/commit/71c505c0460d6311e8be579364af13c4257fbc3a))
* added relationships for annotation ([3c97e15](https://github.com/unoplat/unoplat-code-confluence/commit/3c97e1521134022c6dbcfcba7ae8293621eae378))
* child workflow poc complete with package manager metadata for next step that is to apply isort and ruff ([cef8d8f](https://github.com/unoplat/unoplat-code-confluence/commit/cef8d8f98ba00be53eb813d408b4523f197a15a3))
* Enhance dependency parsing and metadata extraction in PipStrategy and SetupParser, update UnoplatProjectDependency model with default values and descriptions, improve PipStrategy to handle multiple requirement file patterns and merge constraints, enhance SetupParser to parse setup.py files robustly including extras and environment markers, add comprehensive tests for requirements parsing, VCS dependencies, and setup.py metadata extraction, update .gitignore to exclude additional test artifacts. ([8803124](https://github.com/unoplat/unoplat-code-confluence/commit/88031243b118e55e0b7f78a51dcf3d7eb533bcdb))
* Enhance ingestion workflow with Neo4j integration and environment settings- Added Neo4j database connection support with new configuration parameters.- Implemented ConfluenceGitGraph for ingesting Git repo data into Neo4j, with refactored workflows.- Updated Taskfile for Temporal server setup and .gitignore for additional cache exclusions. ([b7035e3](https://github.com/unoplat/unoplat-code-confluence/commit/b7035e3fed991ea28f19fb829a6652d0dd2dc896))
* Introduce UV package manager strategy for enhanced metadata extraction and dependency parsing from pyproject.toml. Added support for optional dependencies, git sources, and environment markers. Updated tests to validate new functionality and ensure comprehensive coverage for UV strategy. Refactored existing tests to improve structure and maintainability. ([7f289e4](https://github.com/unoplat/unoplat-code-confluence/commit/7f289e40d73e817a5767f28670faef76e59de2f5))
* milestone 2 d2 basic architecture ([cf2af7a](https://github.com/unoplat/unoplat-code-confluence/commit/cf2af7a977ed61b80fb23ef211dfffec73d3ac75))
* Refactor codebase ingestion workflow by introducing PackageManagerMetadataIngestion for handling package manager metadata, updating activity signatures, and enhancing the ParentChildCloneMetadata model for improved clarity and functionality. Added tests for package manager metadata insertion to ensure data integrity. ([85650e7](https://github.com/unoplat/unoplat-code-confluence/commit/85650e79849ab2812f2e73aa247970d2c4db6c42))
* use a neo4j connection pool across activities and async implementation ([4cf8a0c](https://github.com/unoplat/unoplat-code-confluence/commit/4cf8a0c1bc4c1c1f3053a247edfb23f5d07b1d66))


### Bug Fixes

* added pytest in main dependencies so that we are able to run in vscode ([d5a3caa](https://github.com/unoplat/unoplat-code-confluence/commit/d5a3caac5f86e0bf2baa3ee7bab2fc889020ba08))
* concurrent submission and waiting of child workflows ([a06e784](https://github.com/unoplat/unoplat-code-confluence/commit/a06e784d5bd08f5bb3b82c8456220890167c8dde))
* fix schema not handling local path of codebase node in neo4j ([9d5e7d2](https://github.com/unoplat/unoplat-code-confluence/commit/9d5e7d2bd6cd2d24505ec2cc6e0febd58875191a))
* fixed relationship direction for git repo and codebase ([4851728](https://github.com/unoplat/unoplat-code-confluence/commit/4851728d26f96eaae3ae99a925bd02aa3c8f376b))
* ingestion with relation ([1b6f743](https://github.com/unoplat/unoplat-code-confluence/commit/1b6f743fe33d2d7b53c10b7f754a90de8098d459))
* install schema before proceeding ([7fcf2c0](https://github.com/unoplat/unoplat-code-confluence/commit/7fcf2c08f27efa1aa2bf151902d31a8d407ee813))


### Documentation

* prereq for code confluence bridge ([56fea07](https://github.com/unoplat/unoplat-code-confluence/commit/56fea078fe2dd86341d289619091a63c09b692e0))
* update for flow for milestone 2 ([96b0306](https://github.com/unoplat/unoplat-code-confluence/commit/96b0306f3b014e04f7fcc0748fd0030055ec8a7a))
* updated docs for running fastapi based project ([191c295](https://github.com/unoplat/unoplat-code-confluence/commit/191c2952147866c09c320353af7b4330a61f88a9))
