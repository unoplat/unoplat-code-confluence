# App Interfaces

Format: `path: L<line>: <match_text>` where path is codebase-relative.

## Inbound Constructs

No inbound constructs detected.

## Outbound Constructs

### http_client (httpx)

- `src/unoplat_code_confluence_openmetadata/client.py`: L33: httpx.Client( base_url=config.normalized_query_engine_base_url, timeout=httpx.Timeout(config.timeout_seconds), )
- `src/unoplat_code_confluence_openmetadata/client.py`: L47: self._client.get( SNAPSHOT_ENDPOINT_PATH, params=params, )

## Bidirectional Constructs

No bidirectional constructs detected.

## Internal Constructs

No internal constructs detected.
