# Business Domain References

## Domain Summary
The dominant domain is a CLI for operating the Unoplat Code Confluence local stack, delivered as Docker Compose services. Its core data models revolve around release manifests/state, repository ingestion payloads/results, and browser setup actions, showing it manages pinned GitHub releases and the app’s runtime lifecycle. It also kicks off repository ingestion and AGENTS.md generation/update workflows against the Flow Bridge and Query Engine services.

## Data Model References
### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-cli/src/unoplat_code_confluence_cli/agent_md_runtime.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-cli/src/unoplat_code_confluence_cli/agent_md_runtime.py#L13-L21`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-cli/src/unoplat_code_confluence_cli/agent_md_runtime.py#L24-L30`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-cli/src/unoplat_code_confluence_cli/app_runtime.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-cli/src/unoplat_code_confluence_cli/app_runtime.py#L28-L33`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-cli/src/unoplat_code_confluence_cli/app_runtime.py#L36-L41`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-cli/src/unoplat_code_confluence_cli/app_runtime.py#L44-L47`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-cli/src/unoplat_code_confluence_cli/app_runtime.py#L50-L54`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-cli/src/unoplat_code_confluence_cli/app_runtime.py#L57-L62`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-cli/src/unoplat_code_confluence_cli/app_runtime.py#L65-L71`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-cli/src/unoplat_code_confluence_cli/app_runtime.py#L74-L81`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-cli/src/unoplat_code_confluence_cli/app_runtime.py#L84-L98`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-cli/src/unoplat_code_confluence_cli/app_runtime.py#L101-L115`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-cli/src/unoplat_code_confluence_cli/app_runtime.py#L118-L124`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-cli/src/unoplat_code_confluence_cli/app_runtime.py#L127-L130`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-cli/src/unoplat_code_confluence_cli/ingestion_runtime.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-cli/src/unoplat_code_confluence_cli/ingestion_runtime.py#L16-L20`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-cli/src/unoplat_code_confluence_cli/ingestion_runtime.py#L23-L29`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-cli/src/unoplat_code_confluence_cli/setup_runtime.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-cli/src/unoplat_code_confluence_cli/setup_runtime.py#L11-L18`
