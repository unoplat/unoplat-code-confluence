# Changelog

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
