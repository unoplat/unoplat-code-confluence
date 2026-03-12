# App Interfaces

## FastAPI HTTP Endpoints

| Area | Endpoints | Module | Notes |
| --- | --- | --- | --- |
| Model config + providers | `GET /model-config`, `PUT /model-config`, `DELETE /model-config`, `GET /providers`, `GET /providers/{provider_key}` | `src/unoplat_code_confluence_query_engine/api/v1/endpoints/ai_model_config.py` | Manage provider model configuration and provider catalog exposure. |
| Codex OpenAI OAuth | `POST /model-config/codex-openai/oauth/authorize`, `GET /model-config/codex-openai/oauth/flows/{flow_id}`, `GET /model-config/codex-openai/oauth/callback`, `GET /model-config/codex-openai/oauth/status`, `DELETE /model-config/codex-openai/oauth`, `GET /auth/callback` | `src/unoplat_code_confluence_query_engine/api/v1/endpoints/ai_model_config.py` | OAuth flow lifecycle + callback handlers for Codex OpenAI provider configuration. |
| Feature flags | `GET /flags`, `GET /flags/{flag_name}`, `PUT /flags/{flag_name}`, `DELETE /flags/{flag_name}` | `src/unoplat_code_confluence_query_engine/api/v1/endpoints/flags.py` | Runtime flag configuration and lookup. |
| Repository agent rules | `GET /codebase-agent-rules`, `POST /repository-agent-run/cancel`, `GET /repository-agent-snapshot`, `POST /repository-agent-md-pr`, `GET /repository-agent-md-pr` | `src/unoplat_code_confluence_query_engine/api/v1/endpoints/codebase_agent_rules.py` | Rules metadata, run cancellation, snapshot payloads, and markdown PR workflows for repository agents. |
| Tool configuration | `GET /{provider}`, `PUT /{provider}`, `DELETE /{provider}`, `GET /` | `src/unoplat_code_confluence_query_engine/api/v1/endpoints/tool_config.py` | Provider-specific tool config CRUD and listing. |
