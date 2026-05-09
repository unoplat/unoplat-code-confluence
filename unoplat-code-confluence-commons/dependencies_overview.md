# Dependencies Overview

- **Package management**: Use `uv` as the package manager for this codebase.
- **cryptography**: Purpose: Provides high-level cryptographic recipes and lower-level primitives for common algorithms such as symmetric ciphers, message digests, and key derivation functions. It also includes safer helpers like Fernet and X.509 support.
- **pydantic**: Purpose: Data validation using Python type annotations; it parses and validates complex data, generates JSON Schemas, and helps ensure data integrity.
- **pytest**: Purpose: pytest is a Python testing framework for writing small, readable tests that can scale to complex functional testing for applications and libraries. It provides assertion introspection, test auto-discovery, fixtures, and a rich plugin ecosystem.
- **pytest-asyncio**: Purpose: pytest-asyncio is a pytest plugin for testing code that uses Python’s asyncio library. It provides support for coroutine test functions so you can `await` inside tests.
- **sqlalchemy**: Purpose: Python SQL toolkit and Object Relational Mapper for working with SQL in a Pythonic way. It includes Core for SQL construction, schema/connection management, and an ORM for automated persistence of Python objects.
- **sqlmodel**: Purpose: SQLModel is a Python library for working with SQL databases using Python classes and type annotations. It combines Pydantic and SQLAlchemy to keep models concise and compatible with FastAPI.
