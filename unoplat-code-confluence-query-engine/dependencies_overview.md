# Dependencies Overview

- **Package management**: Use `uv` with `pyproject.toml` for installing and syncing dependencies.
- **aiopath**: Async pathlib for Python: a complete reimplementation of Python's pathlib that is compatible with asyncio, trio, and async/await, with all I/O performed asynchronously and awaitably. Usage: use `AsyncPath`/`AsyncPurePath` with familiar pathlib APIs, and await I/O methods like read/write/open or async globbing that return async-friendly results.
- **qs-codec**: Query string encoding and decoding library for Python, ported from qs for JavaScript. Usage: encode/decode nested dict/list structures with list formats (indices, brackets, repeat, comma), dot-notation, charset options, hooks, and null/safety handling.
- **sqlalchemy**: SQL toolkit and ORM for Python providing comprehensive database tools. Usage: rely on Core for composable SQL expressions and the ORM for object mappings, unit-of-work persistence, and object-centric querying.
- **asyncpg**: Async PostgreSQL client designed for asyncio. Usage: use the native protocol API for connections, transactions, prepared statements, cursors, pooling, and rich PostgreSQL type conversions.
- **loguru**: Pre-instanced logger that simplifies Python logging. Usage: emit logs with the global `logger`, add sinks via `logger.add()`, and configure levels or formatting as needed.
- **sse-starlette**: Server-Sent Events implementation for Starlette/FastAPI following the W3C SSE spec. Usage: stream async event generators with `EventSourceResponse`, using helpers like `ServerSentEvent`/`JSONServerSentEvent` and disconnect handling.
- **ghapi**: Pythonic interface to GitHub's OpenAPI spec with always-updated coverage. Usage: call GitHub endpoints as standard Python methods with docs/autocomplete, or use the CLI for scripting.
- **sqlmodel**: SQLModel for relational database access with Python objects. Usage: define models with modern type annotations that serve as ORM mappings and Pydantic validation, while accessing underlying SQLAlchemy features.
- **fastapi**: High-performance API framework built on type hints. Usage: declare routes with automatic validation/OpenAPI docs and dependency injection for rapid API development.
- **logfire**: Observability platform built on OpenTelemetry with strong Python support. Usage: initialize with `logfire.configure()` and use instrumentation helpers like `logfire.instrument_<package>()` for traces, logs, and metrics.
- **pydantic-ai-slim**: Minimal core for Pydantic AI. Usage: install the slim core and add only the provider/tool extras you need to keep dependencies lightweight.
- **aiofiles**: Async file I/O library for asyncio. Usage: use async file APIs mirroring standard file objects while delegating blocking work to a thread pool.
- **pydantic-ai**: Python agent framework for production-grade generative AI workflows. Usage: build type-safe, model-agnostic agents with structured outputs, tool calls, and streaming/observability support.
