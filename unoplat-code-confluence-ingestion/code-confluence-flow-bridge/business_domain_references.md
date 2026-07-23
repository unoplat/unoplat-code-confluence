# Business Domain References

## Domain Summary
This service is a GitHub repository-ingestion and code-intelligence platform. It inventories repositories and codebases, parses Python and TypeScript source structure and imports, detects package managers and workspace layouts, and collects project metadata for downstream processing. It also manages GitHub App onboarding plus Temporal workflow status, error issues, and user feedback for the ingestion lifecycle.

## Data Model References
### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/common/language_service.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/common/language_service.py#L15-L33`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/common/source_context.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/common/source_context.py#L21-L30`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/common/source_context.py#L42-L75`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/common/source_context.py#L78-L99`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/python/python_tree_sitter_framework_detector.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/python/python_tree_sitter_framework_detector.py#L75-L89`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/typescript_tree_sitter_framework_detector.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/typescript_tree_sitter_framework_detector.py#L75-L88`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/github_app/models.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/github_app/models.py#L18-L38`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/github_app/models.py#L41-L81`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/github_app/models.py#L84-L105`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/github_app/models.py#L108-L122`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/file_processing_data.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/file_processing_data.py#L8-L18`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/import_info.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/import_info.py#L8-L13`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/position.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/position.py#L8-L12`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/processing_batch.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/processing_batch.py#L12-L18`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_codebase.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_codebase.py#L15-L35`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_file.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_file.py#L12-L33`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_git_repository.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_git_repository.py#L12-L37`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_package.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_package.py#L12-L22`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_package_manager_metadata.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_package_manager_metadata.py#L12-L100`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_project_dependency.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_project_dependency.py#L12-L36`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_version.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_version.py#L8-L22`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/configuration/settings.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/configuration/settings.py#L13-L15`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/python/rules.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/python/rules.py#L6-L12`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/python/rules.py#L15-L21`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/python/rules.py#L24-L28`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/python/rules.py#L31-L34`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/shared/evidence.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/shared/evidence.py#L6-L13`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/shared/inventory.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/shared/inventory.py#L10-L15`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/shared/results.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/shared/results.py#L10-L33`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/shared/rules.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/shared/rules.py#L10-L21`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/shared/rules.py#L24-L32`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/shared/rules.py#L35-L39`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript/discovery.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript/discovery.py#L11-L21`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript/discovery.py#L24-L42`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript/discovery.py#L45-L69`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript/rules.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript/rules.py#L6-L12`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript/rules.py#L15-L21`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript/rules.py#L24-L28`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript/rules.py#L31-L34`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript/rules.py#L37-L40`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/detection/typescript/rules.py#L43-L46`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L19-L29`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L32-L39`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L42-L88`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L91-L98`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L101-L107`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L115-L130`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L133-L152`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L155-L161`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L164-L168`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L171-L174`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L177-L219`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L222-L229`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L232-L242`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L245-L256`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L259-L266`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L269-L287`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L290-L319`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L322-L353`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L356-L361`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L369-L383`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L386-L391`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L394-L399`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L402-L408`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L411-L419`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L422-L429`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L432-L437`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/repository_git_url.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/repository_git_url.py#L10-L19`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/parent_child_clone_metadata.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/parent_child_clone_metadata.py#L4-L6`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py#L19-L27`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py#L30-L38`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py#L41-L49`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py#L52-L59`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py#L62-L75`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py#L78-L86`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py#L89-L97`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py#L100-L112`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/language_processors/language_processor_context.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/language_processors/language_processor_context.py#L18-L30`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/typescript/manifests/package_json_loader.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/typescript/manifests/package_json_loader.py#L28-L135`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/routers/github_issues/models.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/routers/github_issues/models.py#L19-L24`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/routers/github_issues/models.py#L27-L42`
