# Business Domain References

## Domain Summary
This codebase is a GitHub repository ingestion and code-intelligence platform. It analyzes Python and TypeScript codebases by parsing imports, structural signatures, package manifests, and workspace/package-manager metadata, then packages that information into repository and codebase models. It also orchestrates workflow execution and status tracking, supports GitHub App onboarding, and captures issue/feedback flows around the ingestion pipeline.

## Data Model References
### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/python/python_source_context.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/python/python_source_context.py#L149-L176`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/python/python_tree_sitter_framework_detector.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/python/python_tree_sitter_framework_detector.py#L72-L86`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/typescript_source_context.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/typescript_source_context.py#L153-L189`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/typescript_tree_sitter_framework_detector.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/typescript_tree_sitter_framework_detector.py#L72-L85`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/github_app/models.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/github_app/models.py#L18-L38`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/github_app/models.py#L41-L81`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/github_app/models.py#L84-L105`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/github_app/models.py#L108-L122`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/file_processing_data.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/file_processing_data.py#L8-L19`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/import_info.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/import_info.py#L8-L13`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/position.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/position.py#L8-L12`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/processing_batch.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/processing_batch.py#L12-L18`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_codebase.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_codebase.py#L15-L35`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_file.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/code_confluence_parsing_models/unoplat_file.py#L14-L41`

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
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L15-L25`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L28-L35`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L38-L84`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L87-L94`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L97-L103`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L111-L126`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L129-L148`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L151-L157`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L160-L164`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L167-L170`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L173-L185`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L188-L199`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L202-L209`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L212-L230`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L233-L262`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L265-L296`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L299-L304`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L312-L326`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L329-L334`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L337-L342`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L345-L351`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L354-L362`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L365-L372`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/github/github_repo.py#L375-L380`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/parent_child_clone_metadata.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/parent_child_clone_metadata.py#L4-L6`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py#L36-L44`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py#L47-L55`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py#L58-L65`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py#L68-L81`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py#L84-L92`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py#L95-L103`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/models/workflow/repo_workflow_base.py#L106-L118`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/language_processors/language_processor_context.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/language_processors/language_processor_context.py#L18-L30`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/typescript/manifests/package_json_loader.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/package_manager/typescript/manifests/package_json_loader.py#L28-L135`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/tree_sitter_config.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/tree_sitter_config.py#L13-L102`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/routers/github_issues/models.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/routers/github_issues/models.py#L19-L24`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/routers/github_issues/models.py#L27-L42`
