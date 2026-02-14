## Engineering Workflow
- Install: `uv sync` (config: `Taskfile.yml`). Docs: https://docs.astral.sh/uv/concepts/projects/sync/?utm_source=openai
- Test: `uv run pytest -v tests/` (config: `Taskfile.yml`). Docs: https://docs.astral.sh/uv/concepts/projects/run/?utm_source=openai

## Dependency Guide
- **sqlmodel**: SQLModel is a library for interacting with SQL databases from Python code, with Python objects, designed to be intuitive, easy to use, highly compatible, and robust.
  - Usage: SQLModel is based on standard Python type annotations and is powered by Pydantic and SQLAlchemy to define models that map to database tables. It is designed to be compatible with FastAPI, Pydantic, and SQLAlchemy while minimizing code duplication and providing strong editor support.
- **sqlalchemy**: SQLAlchemy is a SQL toolkit and Object Relational Mapper (ORM) that provides a comprehensive set of tools for working with databases and Python.
  - Usage: It provides the SQL Expression Language (Core) for schema-centric SQL construction, rendering, and DBAPI/transaction integration across database backends. It also includes an ORM that maps Python objects to database tables for domain-centric persistence and querying.
- **pydantic**: Pydantic is a data validation library for Python that uses type annotations to define how data should be in canonical Python and validates it at runtime. It provides user-friendly errors when data is invalid.
  - Usage: Pydantic models validate input data (Python objects, JSON, or strings) and can coerce or strictly enforce types depending on configuration. It also supports extensible customization such as custom validators/serializers and can emit JSON Schema for integration with other tools.
- **pytest-asyncio**: pytest-asyncio is a pytest plugin that facilitates testing of code that uses the asyncio library.
  - Usage: It provides support for coroutines as test functions so async tests can be awaited and executed by pytest. It integrates with pytest’s asyncio marker/fixtures to run async code within the event loop during tests.
- **cryptography**: `cryptography` provides high-level recipes and low-level interfaces to common cryptographic algorithms such as symmetric ciphers, message digests, and key derivation functions.
  - Usage: It offers a recipes layer with safe, easy-to-use primitives like Fernet symmetric encryption and X.509 tooling for common tasks. It also exposes a lower-level "hazmat" layer of cryptographic primitives for advanced or specialized use cases where fine-grained control is required.
- **pytest**: pytest is a framework that makes building small, readable tests easy and scales to support complex functional testing for applications and libraries.
  - Usage: It uses plain assert statements with detailed assertion introspection to produce clear failure reports. It auto-discovers tests and provides fixtures and a rich plugin system to manage test resources and extend functionality.
## Business Logic Domain
- **Domain overview:** Code Confluence ingests repositories and codebases, stores structural signatures of source files, and records detected framework features with their locations. The domain also captures language/package-manager metadata and framework feature specifications (definitions, import paths, construct queries), along with persistence models that link repositories, codebases, files, and framework mappings. Workflow execution tracking covers repository/codebase runs, statuses, error reports, and agent snapshots, supported by operational configuration such as credentials and feature flags.
- **Core model groups:**
  - Structural signatures and positioning primitives: `python_structural_signature.py`, `typescript_structural_signature.py`, `data_model_position.py`.
  - Framework feature specifications and detections: `framework_models.py`.
  - Repository/codebase/file persistence and relational mappings: `relational_models/unoplat_code_confluence.py`, `repo_models.py`, `engine_models.py`.
  - Workflow execution tracking (runs, statuses, snapshots): `workflow_models.py`, `workflow_envelopes.py`.
  - Configuration and operational metadata: `configuration_models.py`, `credentials.py`, `flags.py`, `programming_language_metadata.py`.
- **References:** See `business_logic_references.md` for a file-by-file map of business logic models.

## App Interfaces
- **Overview:** No app interface constructs have been documented for this codebase yet.
- **Inbound interfaces:** None documented.
- **Outbound interfaces:** None documented.
- **Internal interfaces:** None documented.
- **References:** See `app_interfaces.md` for the tracked interface inventory.