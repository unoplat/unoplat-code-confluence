## Engineering Workflow
- Install: `task install` (config: `Taskfile.yml`).
- Test: `task test` (config: `Taskfile.yml`).

## Dependency Guide
- **cryptography**: `cryptography` provides both high-level recipes and low-level interfaces to common cryptographic algorithms such as symmetric ciphers, message digests, and key derivation functions.
  - Usage: It offers high-level “recipes” (e.g., Fernet) for tasks like symmetric encryption that prioritize safe defaults and ease of use. It also exposes low-level, hazardous-materials interfaces for direct access to underlying primitives and bindings when you need fine-grained control.
- **pytest-asyncio**: pytest-asyncio is a pytest plugin that facilitates testing code using the asyncio library and supports coroutines as test functions so you can await code inside tests.
  - Usage: It enables async test functions by providing pytest markers that let coroutines run as test items. It supplies fixtures (including for event loops) to make testing asyncio-based code straightforward and compatible with pytest workflows.
- **sqlalchemy**: SQLAlchemy is the Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL. It provides a full suite of well-known enterprise-level persistence patterns for efficient, high-performing database access in a Pythonic domain language.
  - Usage: SQLAlchemy is organized into two major components: the Core (a SQL expression language and DBAPI integration layer) and the ORM, which builds on Core to map Python objects to database schemas and automate persistence. It supports constructing and executing SQL statements, managing connections/transactions, describing schemas, and using ORM querying and unit-of-work patterns for object-centric data access.
- **pytest**: The pytest framework makes it easy to write small, readable tests and can scale to support complex functional testing for applications and libraries.
  - Usage: Pytest provides detailed assertion introspection and uses plain assert statements to produce helpful failure information. It includes automatic test discovery along with fixtures and a plugin architecture to manage test resources and extend functionality.
- **sqlmodel**: SQLModel is a library for interacting with SQL databases from Python using Python objects, designed to be intuitive, easy to use, highly compatible, and robust. It is based on Python type annotations and powered by Pydantic and SQLAlchemy.
  - Usage: SQLModel lets you define models that combine Pydantic-style data validation/serialization with SQLAlchemy ORM table mapping so the same class can serve as both a data model and a database model. It provides an intuitive, type-annotated API with strong editor support and sensible defaults for working with relational databases in Python.
- **pydantic**: Pydantic is a widely used Python data validation library that lets you define data models in pure Python type hints and validates input against them.
  - Usage: It validates and parses data into Python types (including from JSON) with strict or lax modes and produces clear validation errors. Pydantic can generate JSON Schema and supports custom validators/serializers plus validation for dataclasses, TypedDicts, and other standard typing constructs.
## Business Logic Domain
- **Domain overview:** This codebase models a “code confluence” platform that ingests git repositories and codebases, stores structural signatures of source files, and detects framework-specific features using configurable queries and metadata. It also tracks workflow runs for repository and codebase processing, including statuses, errors, events, and agent output snapshots, alongside package manager and language metadata. Supporting models handle credentials, feature flags, and PR publication metadata for automated documentation or agent output updates.
- **Core model groups:**
  - Structural signatures and positioning primitives: `python_structural_signature.py`, `typescript_structural_signature.py`, `data_model_position.py`.
  - Framework feature definitions, imports, and query matching: `framework_models.py`.
  - Repository/codebase persistence, file inventories, and relational mappings: `relational_models/unoplat_code_confluence.py`, `repo_models.py`, `engine_models.py`.
  - Workflow execution tracking (runs, statuses, errors, snapshots): `workflow_models.py`, `workflow_envelopes.py`.
  - Configuration and operational metadata (credentials, flags, metadata, PR publication): `configuration_models.py`, `credentials.py`, `flags.py`, `programming_language_metadata.py`, `pr_metadata_model.py`.
- **References:** See `business_logic_references.md` for a file-by-file map of business logic models.

## App Interfaces
- **Overview:** No app interface constructs have been documented for this codebase yet.
- **Inbound interfaces:** None documented.
- **Outbound interfaces:** None documented.
- **Internal interfaces:** None documented.
- **References:** See `app_interfaces.md` for the tracked interface inventory.