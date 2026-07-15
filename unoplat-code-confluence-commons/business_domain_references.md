# Business Domain References

## Domain Summary
This package supports Code Confluence, a repository-ingestion and code-intelligence platform. It models Git repositories, codebases, source files, package metadata, framework feature definitions, and detected source-code spans, using configurable queries to identify library capabilities. It also orchestrates and audits repository/codebase workflows through run statuses, errors, progress events, agent output snapshots, credentials, and AGENTS.md publication metadata.

## Data Model References
### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/data_model_position.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/data_model_position.py#L8-L14`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py#L58-L99`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py#L135-L206`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py#L209-L256`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py#L259-L277`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py#L280-L306`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py#L309-L328`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/framework_models.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/framework_models.py#L32-L54`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/framework_models.py#L60-L217`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/framework_models.py#L223-L265`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/configuration_models.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/configuration_models.py#L10-L19`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/configuration_models.py#L22-L26`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/credentials.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/credentials.py#L20-L48`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/flags.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/flags.py#L8-L15`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/pr_metadata_model.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/pr_metadata_model.py#L7-L27`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/programming_language_metadata.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/programming_language_metadata.py#L32-L41`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py#L13-L36`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py#L39-L81`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py#L84-L111`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py#L114-L143`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py#L146-L170`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py#L178-L233`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/repo_models.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/repo_models.py#L42-L76`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/repo_models.py#L79-L115`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/repo_models.py#L118-L194`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/repo_models.py#L197-L277`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/repo_models.py#L280-L373`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/repo_models.py#L376-L488`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/repo_models.py#L491-L570`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/workflow_envelopes.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/workflow_envelopes.py#L13-L47`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/workflow_envelopes.py#L50-L75`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/workflow_models.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/workflow_models.py#L22-L31`
