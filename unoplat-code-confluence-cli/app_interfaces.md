# App Interfaces

Format: `path: L<line>: <match_text>` where path is codebase-relative.

## Inbound Constructs

### cli_command (click)

- `src/unoplat_code_confluence_cli/cli_app/repo_commands.py`: L15: @repo_group.command(name="add")
- `src/unoplat_code_confluence_cli/cli_app/repo_commands.py`: L27: @click.command(name="add-repository")
- `src/unoplat_code_confluence_cli/cli_app/repo_commands.py`: L42: @click.command(name="agent-md")
- `src/unoplat_code_confluence_cli/cli_app/service_commands.py`: L20: @service_group.command(name="run")
- `src/unoplat_code_confluence_cli/cli_app/service_commands.py`: L28: @service_group.command(name="status")
- `src/unoplat_code_confluence_cli/cli_app/service_commands.py`: L47: @service_group.command(name="update")
- `src/unoplat_code_confluence_cli/cli_app/service_commands.py`: L55: @service_group.command(name="stop")
- `src/unoplat_code_confluence_cli/cli_app/service_commands.py`: L63: @service_group.command(name="destroy")
- `src/unoplat_code_confluence_cli/cli_app/setup_commands.py`: L16: @setup_group.command(name="token-repo-provider")
- `src/unoplat_code_confluence_cli/cli_app/setup_commands.py`: L28: @setup_group.command(name="model-provider")

## Outbound Constructs

### http_client (httpx2)

- `src/unoplat_code_confluence_cli/adapters/httpx2_client.py`: L37: httpx2.get( f"{candidate_base_url}{path}", params=params, headers=headers, follow_redirects=follow_redirects, timeout=timeout, )
- `src/unoplat_code_confluence_cli/adapters/httpx2_client.py`: L73: httpx2.post( f"{candidate_base_url}{path}", json=json, timeout=timeout, )

## Bidirectional Constructs

No bidirectional constructs detected.

## Internal Constructs

No internal constructs detected.
