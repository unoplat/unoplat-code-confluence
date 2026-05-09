# Dependencies Overview

- **Package management**: Use `uv` as the package manager for this codebase.
- **cachetools**: Purpose: This module provides various memoizing collections and decorators, including variants of Python’s standard-library `@lru_cache` decorator. It offers multiple cache implementations and decorators for memoizing function and method calls.
- **httpx**: Purpose: A fully featured HTTP client for Python 3, with both synchronous and asynchronous APIs. Supports HTTP/1.1 and HTTP/2, with a requests-compatible interface.
- **openmetadata-ingestion**: Purpose: Python module that wraps the OpenMetadata API and builds workflows and utilities on top of it. It is used to bring metadata into OpenMetadata for workflows like metadata, lineage, usage, profiler, and data quality.
- **pydantic**: Purpose: Python data validation and settings management library. It defines models with type hints, then parses, validates, serializes, and generates JSON Schema from those models.
