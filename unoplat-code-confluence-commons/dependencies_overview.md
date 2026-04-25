# Dependencies Overview

- **Package management**: Use `uv` as the package manager for this codebase.
- **cryptography**: Purpose: Python library that provides high-level cryptographic recipes and low-level interfaces for common algorithms such as symmetric ciphers, message digests, and key derivation functions. The docs recommend using the safe recipes layer when possible and only using the hazmat layer when necessary.
- **pydantic**: Purpose: Pydantic is a Python library for data parsing, validation, and serialization driven by type hints. It also supports generating JSON Schema from models defined with `BaseModel`.
- **pytest**: Purpose: The `pytest` framework makes it easy to write small, readable tests, and can scale to support complex functional testing for applications and libraries. It provides detailed assertion introspection, auto-discovers tests, and supports fixtures and plugins.
- **pytest-asyncio**: Purpose: A pytest plugin for testing asyncio-based code. It adds support for async test functions and event-loop handling so tests can await async operations.
- **sqlalchemy**: Purpose: The SQLAlchemy SQL Toolkit and Object Relational Mapper is a comprehensive set of tools for working with databases and Python. It provides the SQL expression language, Core database integration, ORM, and dialect support.
- **sqlmodel**: Purpose: SQLModel is a Python library for interacting with SQL databases using Python objects. It is based on Python type annotations and powered by Pydantic and SQLAlchemy, with compatibility for FastAPI.
