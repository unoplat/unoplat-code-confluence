# Business Domain References

## Domain Summary
This codebase serves Code Confluence, a repository ingestion and code-intelligence platform for analyzing source code at the repository and codebase level. Its models center on Git repositories, workflow runs, credentials, agent event/progress tracking, and persisted structural signatures for Python and TypeScript files. It also stores framework feature definitions and detected source spans, supporting automated code-feature mapping and AGENTS.md publication workflows.

## Data Model References
### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/data_model_position.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/data_model_position.py#L8-L14`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py#L51-L76`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py#L99-L169`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py#L172-L214`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py#L217-L235`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py#L238-L264`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py#L267-L286`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/framework_models.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/framework_models.py#L32-L54`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/framework_models.py#L60-L217`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/framework_models.py#L223-L265`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/python_structural_signature.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/python_structural_signature.py#L11-L15`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/python_structural_signature.py#L18-L26`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/python_structural_signature.py#L29-L37`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/python_structural_signature.py#L40-L51`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L11-L25`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L28-L34`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L37-L54`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L71-L86`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L89-L95`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L98-L104`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L107-L126`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L129-L141`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L144-L169`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L172-L176`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L179-L195`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L198-L213`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L216-L223`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L226-L233`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L236-L276`

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
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py#L114-L146`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py#L149-L173`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py#L181-L236`

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
