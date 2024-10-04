# UNOPLAT CODE CONFLUENCE QUERY ENGINE

## How to Run?

```bash
poetry run python -m unoplat_code_confluence_query_engine --config ./unoplat_code_confluence_query_engine/configuration/config.yaml
```

## Configuration Example

```yaml
{
    "sentence_transformer_model": "jinaai/jina-embeddings-v3",
    "neo4j_uri": "YOUR_NEO4J_URI",
    "neo4j_username": "neo4j",
    "neo4j_password": "YOUR_NEO4J_PASSWORD",
    "provider_model_dict": {
        "model_provider" : "openai/gpt-4o-mini",
        "model_provider_args": {
            "api_key": "YOUR_OPENAI_API_KEY",
            "max_tokens": 500,
            "temperature": 0.0
        }
    }
}
```