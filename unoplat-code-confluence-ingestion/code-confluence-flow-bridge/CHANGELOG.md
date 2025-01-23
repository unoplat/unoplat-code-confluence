# Changelog

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
