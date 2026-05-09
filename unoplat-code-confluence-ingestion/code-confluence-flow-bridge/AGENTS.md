# AGENTS.md - Code Confluence Flow Bridge Agent Guide

## Engineering Workflow

- Install: `uv sync` (source: pyproject.toml, confidence: 0.95)
- Dev: `uv run fastapi dev` (source: pyproject.toml, confidence: 0.85)
- Test: `uv run --python 3.13 --group test pytest --cov=src/code_confluence_flow_bridge --cov-report=html:coverage_reports tests/ -v` (source: pyproject.toml, confidence: 0.8)
- Lint: `uv run ruff check src/` (source: ruff.toml, confidence: 0.9)
- Type check: `uv run --group dev basedpyright src/` (source: pyproject.toml, confidence: 0.85)

## Dependency Guide

- Package manager: `uv`.
- **packaging**: Reusable core utilities for Python Packaging interoperability specifications, implementing specs with a single correct behavior (e.g., PEP 440 and PEP 425). Provides modules for version handling and specifiers, letting tools parse and evaluate version constraints consistently. Includes support for markers, requirements, tags, metadata, lockfiles, and helper utilities used by Python packaging tooling.
- **passlib**: Passlib is a password hashing library for Python that provides cross-platform implementations of over 30 password hashing algorithms and a framework for managing existing password hashes. It supports many hashing schemes and lets you verify and update stored hashes in a consistent way across platforms. It is designed for tasks ranging from validating hashes from system sources to providing strong password hashing in multi-user applications.
- **pydantic-settings**: Provides optional Pydantic features for loading a settings/config class from environment variables or secrets files. It lets you define settings models that inherit from BaseSettings, so missing field values are populated from environment variables while defaults still apply. It supports settings sources like environment variables, secrets files, and related configuration options to manage application configuration cleanly.
- **sqlalchemy**: SQLAlchemy is the Python SQL toolkit and Object Relational Mapper, a comprehensive set of tools for working with databases and Python. It provides Core and a SQL Expression Language to build composable SQL statements and execute queries and DML against databases. It also includes an ORM built on Core that maps Python objects to database schemas and automates persistence and object-centric querying.
- **asyncpg**: asyncpg is a database interface library designed specifically for PostgreSQL and Python/asyncio, implementing the PostgreSQL server binary protocol for use with asyncio. It provides an efficient, native PostgreSQL protocol driver for asyncio-based applications and supports Python 3.9+ with PostgreSQL 9.5–18. It includes features such as prepared statements, transactions, cursors, connection pools, and rich type conversion for PostgreSQL data types.
- **loguru**: Loguru provides a pre-instanced logger to facilitate dealing with logging in Python, available directly via `from loguru import logger`. It offers a single pre-configured logger that you can immediately use to log messages and manage sinks with methods like add(), remove(), and configure(). It supports multiple severity levels and advanced capabilities such as structured logging, contextual data binding, exception handling, and log parsing.
- **fastapi**: FastAPI is a modern, fast (high‑performance) web framework for building APIs with Python based on standard Python type hints. It builds APIs around standard Python type hints with automatic data validation and schema generation via OpenAPI/JSON Schema, and provides interactive API docs by default. It delivers high performance through its Starlette foundation and supports features like WebSockets, background tasks, and dependency injection for production-ready services.
- **temporalio**: Temporal Python SDK for building and running workflows and activities on the Temporal platform. It provides client and worker APIs to connect to Temporal, execute workflows, and run activities with data conversion and runtime support. The package includes workflow/activity decorators plus modules for configuration, exceptions, testing, and optional contrib integrations.
- **tomlkit**: Style-preserving TOML library for Python that is 1.0.0-compliant, with a parser that preserves comments, indentation, whitespace, and element ordering for editable access via an intuitive API. It parses TOML while preserving formatting and exposes the structure so you can edit values, comments, and ordering without losing style. It also provides helpers to create new TOML documents from scratch and work with TOML data programmatically.
- **sqlmodel**: SQLModel is a library for interacting with SQL databases from Python code using Python objects, designed to be intuitive, easy to use, highly compatible, and robust. It is based on Python type annotations and powered by Pydantic and SQLAlchemy. It provides a unified model layer that works as both SQLAlchemy models and Pydantic models, reducing duplication while retaining full access to both ecosystems’ capabilities. It is designed for strong editor support and compatibility with FastAPI and other applications, with sensible defaults that simplify defining tables and working with sessions and queries.
- **greenlet**: Greenlet is a library for lightweight concurrent programming, providing greenlets (lightweight coroutines) for in-process sequential concurrency. It provides cooperatively scheduled coroutines that let you explicitly switch execution between greenlets within a single OS thread. Greenlets can be used directly or by higher-level frameworks (e.g., event-loop integrations) to build custom scheduling, advanced control flow, and synchronous-style code over asynchronous tasks.
- **gitpython**: GitPython is a Python library used to interact with Git repositories at a high level like git-porcelain or a low level like git-plumbing. It provides abstractions of Git objects for easy access to repository data, with options to access repositories via a pure Python implementation or the faster Git command implementation. It offers high- and low-level repository operations by exposing Git objects and repository data through Python abstractions, while supporting both pure Python access and direct invocation of the Git command line for faster operations. Its object database implementation is optimized for large quantities of objects and large datasets through low-level structures and data streaming.
- **opentelemetry-exporter-otlp**: Convenience package that installs all supported OpenTelemetry Collector OTLP exporters for Python, including gRPC and HTTP/protobuf variants. It bundles the OTLP exporter implementations so you can export traces, metrics, and logs to an OpenTelemetry Collector or other OTLP-compatible endpoints using either gRPC or HTTP/protobuf. It also serves as a meta-package, while recommending that you install the specific protocol package once you choose your preferred transport.
- **tiktoken**: Fast byte pair encoding (BPE) tokenizer for use with OpenAI’s models, providing model-specific encodings and a simple encode/decode API. Provides built-in encodings such as o200k_base and lets you select the appropriate tokenizer for a specific OpenAI model via encoding_for_model. Includes utilities for encoding/decoding text and an educational submodule to explore BPE behavior and training workflows.
- **requirements-parser**: Small Python module for parsing Pip requirement files, with the goal of parsing everything in the Pip requirement file format spec. It can parse requirement data from file-like objects or text strings and returns structured requirement entries. It supports common requirement file features such as editables, version control URLs, extras, egg hashes/subdirectories, and direct URLs.
- **opentelemetry-sdk**: Reference implementation of the OpenTelemetry Python API (the SDK) used by applications to produce telemetry data such as traces, metrics, and logs. Applications depend on opentelemetry-sdk to initialize OpenTelemetry and emit telemetry from their code, while libraries typically depend only on the API. The SDK provides the concrete providers and pipeline pieces (e.g., tracer/meter providers, processors, and exporters) that implement the OpenTelemetry API for Python.
- **opentelemetry-api**: OpenTelemetry is an observability framework—an API, SDK, and tools designed to help generate and collect application telemetry data such as metrics, logs, and traces for OpenTelemetry Python. Provides the OpenTelemetry API interfaces and context propagation used to instrument Python code for tracing, metrics, and logs. Libraries depend on this API package to define telemetry they emit, which becomes active when an application configures the OpenTelemetry SDK.
- **typing-extensions**: The typing_extensions module complements the standard-library typing module by providing runtime support for type hints defined in PEP 484 and later PEPs, especially on older Python versions. It backports newer typing features so code can use type system additions to enable early adoption by type checkers and users.
- **opentelemetry-instrumentation-logging**: OpenTelemetry logging integration that automatically injects tracing context into log statements by registering a custom log record factory with Python’s standard logging module. It injects trace and span context fields (such as trace ID, span ID, service name, and sampling flag) into log records so logs can be correlated with traces. The integration can optionally configure logging with a default format including those fields, and it is enabled by setting the OTEL_PYTHON_LOG_CORRELATION environment variable to true.
- **gql**: GQL is a GraphQL client for Python that is compatible with GraphQL implementations following the specification and built on GraphQL-core. It provides a top-level package with the gql query parser and a Client entry point to execute GraphQL requests. It supports executing queries, mutations, and subscriptions through sync or async transports, with the Client able to run requests directly or provide sync/async sessions. It can fetch or use schemas for validation and offers multiple transport options (such as HTTP and WebSockets) to communicate with GraphQL backends.
- **pyyaml**: PyYAML is a YAML parser and emitter for the Python programming language. It provides a complete YAML 1.1 parser with Unicode support and both pure-Python and LibYAML-based parsing/emitting implementations. It offers a low-level event-based API plus a high-level API to serialize and deserialize native Python objects, with extensible type handling.
- **aiofile**: AIOFile is a Python library that provides real asynchronous file operations with asyncio support. It offers both a high-level async file-like interface via helpers like async_open and a low-level AIOFile class with explicit offset and chunk size control for concurrent I/O. It automatically selects an appropriate backend (Linux libaio when available, threadpool or pure‑Python fallbacks on other platforms) to perform async file operations across systems.
- **psycopg2-binary**: Pre-compiled binary distribution of Psycopg 2, the PostgreSQL adapter for Python, intended to let users install and use Psycopg without build prerequisites. It provides the same psycopg2 module interface as the source package, including DB-API 2.0 compliance and libpq-backed PostgreSQL connectivity. The binary wheel bundles required client libraries, enabling quick installation and immediate use of connections, cursors, and data type adaptation in Python applications.
- **tree-sitter-language-pack**: Bundles a comprehensive collection of tree-sitter languages as both source distributions and pre-built wheels for Python. Provides access to 165+ tree-sitter language grammars with prebuilt binaries for easy installation. Exposes helper functions to retrieve language bindings, Language objects, and Parser instances for specific languages.
- **pydantic**: Pydantic is a data validation library for Python that lets you define how data should be in pure, canonical Python and validate it with Pydantic. It is fast and extensible, providing runtime enforcement of type annotations for Python 3.9+. It validates and parses data using Python type hints, supports standard library types like dataclasses and TypedDict, and allows custom validators and serializers. It can emit JSON Schema and offers strict or lax validation modes to control type coercion behavior.
- **validate-pyproject**: Validation library and CLI tool for checking pyproject.toml files using JSON Schema, ensuring compliance with packaging standards and PEPs. It validates pyproject.toml content against JSON Schema definitions covering PEP 517, PEP 518, and PEP 621 and can be extended with additional schemas. It offers a command-line interface as well as a Python API centered on a Validator class for programmatic validation.
- **grpcio**: grpcio is the gRPC runtime package for Python used to build gRPC client and server applications, installable via pip. It lets you define services in Protocol Buffers and uses protoc with the gRPC plugin to generate Python client and server code. It provides a high-performance RPC framework with features such as streaming and pluggable authentication, load balancing, tracing, and health checking for connecting services across environments.

## Business Logic Domain

- The domain models describe the Git repository ingestion pipeline, including repositories, codebases, files, imports, structural signatures, and package-manager metadata across languages.
- Workflow/run tracking models capture orchestration state, ingestion status, and issue/feedback records used for monitoring and follow-up actions.
- GitHub App onboarding and repository metadata are represented by dedicated integration schemas for manifest/installation flows.
- Key data structures and schemas (parsing, workflow tracking, GitHub integration) are cataloged in `business_logic_references.md`.

## App Interfaces

- **FastAPI HTTP endpoints** live in `src/code_confluence_flow_bridge/main.py`, `src/code_confluence_flow_bridge/github_app/router.py`, and `src/code_confluence_flow_bridge/routers/github_issues/router.py`.
- Ingestion/admin endpoints cover token management (`/ingest-token`, `/update-token`, `/delete-token`), repository lifecycle (`/start-ingestion`, `/repository-status`, `/repository-data`, `/refresh-repository`, `/delete-repository`), and metadata access (`/codebase-metadata`, `/parent-workflow-jobs`, `/get/ingestedRepositories`).
- Feature flag and user lookup routes are `/flags`, `/flags/{flag_name}`, and `/user-details`.
- GitHub App integration exposes `/app-manifest`, `/app-manifest/callback`, and `/webhook`.
- Issue feedback endpoints live under the GitHub issues router (`/issues`, `/feedback`).
- Detailed interface inventory with response models is maintained in `app_interfaces.md`.

## Build/Lint/Test Commands

```bash
# Development
task dev                          # Start dependencies + run FastAPI
task sync                         # Install dependencies with uv

# Testing
task test                         # Run all tests with coverage
uv run --group test pytest tests/path/to/test_file.py::test_function_name  # Single test

# Code Quality
task lint                         # Run ruff linter
task lint-fix                     # Auto-fix lint issues
task typecheck                    # Run basedpyright type checker
task format                       # Format code with ruff
task code-quality                 # Run all checks (lint + typecheck + schema validation)
```

## Code Style Guidelines

**Imports**: Absolute imports only (no relative). Use top-level imports. Ruff enforces: I, F401, F403, F405, TID (ban-relative-imports). Order: future, standard-library, third-party, first-party, local-folder.

**Formatting**: Line length 88. Use `uv run ruff format` - never fix import order manually. Python >=3.13 required.

**Types**: Always define precise types. No `Any` types. Use basedpyright strict mode. For Pydantic JSON: use `model_dump_json()` not manual serialization.

**Naming**: Follow Python PEP 8. Use descriptive names. Avoid nested functions (not preferred in this codebase).

**Error Handling**: Use `@logger.catch` decorator. PostgreSQL sessions: use `session.begin()` but yield `AsyncSession` for automatic transactions.

**Logging**: Use Loguru's native formatting `logger.info("msg {}", var)` NOT f-strings `logger.info(f"msg {var}")`. For expensive ops: `logger.opt(lazy=True).debug("Result: {}", lambda: expensive_fn())`. Context injection arg `ctx` excluded from docstrings (Google format).

**Database**: All Postgres operations auto-transactional via `session.begin()`. Use asyncpg for async operations.

**Testing**: Use `uv run --group test pytest` for tests. Mark integration tests with `@pytest.mark.integration`. Session-scoped fixtures for async.

**Dependencies**: Use `uv` commands exclusively. Test dependencies in `[dependency-groups]` section. Activate shell: `uv run python`.

## Implementation Workflow

**API Verification**: Before implementing framework/library features, verify API methods with official documentation using Context7 tool.

**Post-Implementation**: ALWAYS run `task typecheck` after implementation. Fix all type errors before considering work complete.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->
<CRITICAL_INSTRUCTION>

> Generated from branch `dev` at commit `e1d9b8966ae6d91f530e642d0fb01662c3cf2760` (2026-05-09). Content may become stale as new commits land.

</CRITICAL_INSTRUCTION>

## Engineering Workflow
### Install
- `uv sync` — config_file: `pyproject.toml`, working_directory: `.`
### Build
- Not detected
### Dev
- `task dev` — config_file: `Taskfile.yml`, working_directory: `.`
### Test
- `task test` — config_file: `Taskfile.yml`, working_directory: `.`
### Lint
- `task lint` — config_file: `Taskfile.yml`, working_directory: `.`
### Type Check
- `task typecheck` — config_file: `Taskfile.yml`, working_directory: `.`

## Dependency Guide
See [`dependencies_overview.md`](./dependencies_overview.md) for the full dependency catalog and usage notes.

## Business Domain
### Description

This service centers on code intelligence for repository ingestion, using Tree-sitter-based analysis to detect framework usage in Python and TypeScript. It extracts imports, call expressions, and class inheritance patterns to classify source files and emit metadata for downstream workflow processing.

### References

See [`business_domain_references.md`](./business_domain_references.md) for the supporting source references used to derive this domain summary.

## App Interfaces
See [`app_interfaces.md`](./app_interfaces.md) for the canonical interface and endpoint reference.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->
