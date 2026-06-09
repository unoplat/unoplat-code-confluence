# Dependencies Overview

- **Package management**: Use `uv` as the package manager for this codebase.
- **click**: Purpose: A Python package for building composable command-line interfaces with minimal code. It provides automatic help-page generation, nested commands, and support for lazy-loaded subcommands.
- **httpx2**: Purpose: A next-generation HTTP client for Python. It provides synchronous and asynchronous APIs, with support for both HTTP/1.1 and HTTP/2. Official docs: https://httpx2.pydantic.dev/ ; PyPI: https://pypi.org/project/httpx2/
- **platformdirs**: Purpose: A Python library for determining platform-specific system directories, such as user data, configuration, cache, and log locations. It resolves the correct paths for macOS, Windows, Linux/Unix, and Android, with `_dir` and `_path` variants for each directory.
- **pydantic**: Purpose: Python data validation and settings management library built around type hints. It validates, parses, and serializes structured data using Python models and can generate JSON Schema.
- **pydantic-settings**: Purpose: Provides Pydantic’s settings management via `BaseSettings`, letting you load configuration from environment variables, dotenv files, and secrets files. It also supports custom settings sources and priority control for how values are resolved.
- **python-on-whales**: Purpose: A Docker client for Python with a 1:1 mapping to the Docker CLI. It provides a typed, object-oriented API for common Docker operations like run, build, compose, and swarm management.
