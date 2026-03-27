# Business Logic References

Catalog of domain models supporting repository ingestion, parsing metadata, workflow/run tracking, GitHub App onboarding, and issue feedback.

## Ingestion + Parsing Pipeline
- `src/code_confluence_flow_bridge/engine/programming_language/python/python_source_context.py`: Python parsing context and extracted module metadata.
- `src/code_confluence_flow_bridge/parser/language_processors/language_processor_context.py`: Shared context passed through language processors during parsing.
- `src/code_confluence_flow_bridge/parser/tree_sitter_config.py`: Tree-sitter language bindings/configuration used for parsing.
- `src/code_confluence_flow_bridge/parser/package_manager/typescript/manifests/package_json_loader.py`: Loads and normalizes TypeScript package.json metadata.

## Codebase Parsing Models
- `src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_git_repository.py`: Repository identity and clone metadata captured during ingestion.
- `src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_codebase.py`: Codebase-level metadata derived from repository scans.
- `src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_file.py`: File-level metadata extracted during parsing.
- `src/code_confluence_flow_bridge/models/code_confluence_parsing_models/file_processing_data.py`: Per-file processing state and extracted payloads.
- `src/code_confluence_flow_bridge/models/code_confluence_parsing_models/import_info.py`: Import/source reference records captured from parsed files.
- `src/code_confluence_flow_bridge/models/code_confluence_parsing_models/position.py`: Source position metadata used by parsing records.
- `src/code_confluence_flow_bridge/models/code_confluence_parsing_models/processing_batch.py`: Batch tracking for grouped parsing runs.
- `src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_package.py`: Discovered package records within a codebase.
- `src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_version.py`: Version metadata for packages/components.
- `src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_project_dependency.py`: Dependency relationships between packages/projects.
- `src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_package_manager_metadata.py`: Package manager metadata and manifest-derived dependency context.

## Workflow + Monitoring Models
- `src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py`: Base workflow model for repository processing runs.
- `src/code_confluence_flow_bridge/models/workflow/parent_child_clone_metadata.py`: Metadata linking parent/child clone workflows.
- `src/code_confluence_flow_bridge/routers/github_issues/models.py`: Issue/feedback payloads used for reporting parsing problems.

## GitHub Integration + Configuration
- `src/code_confluence_flow_bridge/github_app/models.py`: GitHub App manifest/installation models used for authorization.
- `src/code_confluence_flow_bridge/models/github/github_repo.py`: GitHub repository metadata schema.
- `src/code_confluence_flow_bridge/models/configuration/settings.py`: Runtime configuration settings supporting ingestion workflows.

## Test Fixture Coverage
- `tests/test_data/framework_samples/code_confluence_flow_bridge/github_app/models.py`
- `tests/test_data/framework_samples/code_confluence_flow_bridge/models/github/github_repo.py`
- `tests/test_data/framework_samples/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py`
- `tests/test_data/framework_samples/unoplat_code_confluence_commons/repo_models.py`
- `tests/test_data/unoplat-code-confluence-cli/unoplat_code_confluence_cli/config/settings.py`
- `tests/test_data/unoplat-code-confluence-cli/unoplat_code_confluence_cli/models/user_model.py`
