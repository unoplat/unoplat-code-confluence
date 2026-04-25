# Dependencies Overview

- **Package management**: Use `uv` as the package manager for this codebase.
- **pydantic**: Purpose: Python data validation library built around type annotations. It lets you define models to parse and validate input data, serialize outputs, and generate JSON Schema.
- **pytest**: Purpose: A Python testing framework for writing small, readable tests that also scales to complex functional testing for applications and libraries. It offers assertion introspection, automatic test discovery, fixtures, and a rich plugin ecosystem.
- **pytest-asyncio**: Purpose: A pytest plugin for testing asyncio code. It provides support for coroutine test functions and event-loop-aware async fixtures so you can await code inside your tests.
- **sqlalchemy**: Purpose: Python SQL toolkit and Object Relational Mapper for working with databases. Provides Core SQL expression/engine/connection services and ORM features for mapping Python objects to database schemas.
- **sqlmodel**: Purpose: SQLModel is a library for interacting with SQL databases from Python code using Python objects. It is built on Python type annotations and combines Pydantic and SQLAlchemy for a simple, type-friendly ORM experience.
