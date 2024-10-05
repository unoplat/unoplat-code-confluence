# UNOPLAT CODE CONFLUENCE QUERY ENGINE

## How to Run?

```bash
poetry run python -m unoplat_code_confluence_query_engine --config ./unoplat_code_confluence_query_engine/configuration/config.yaml
```

## Configuration Example

```yaml
{
    "sentence_transformer_model": "jinaai/jina-embeddings-v3",
    "neo4j_uri": "bolt://localhost:7687",
    "neo4j_username": "neo4j",
    "neo4j_password": "your neo4j password",
    "provider_model_dict": {
        "model_provider" : "openai/gpt-4o-mini",
        "model_provider_args": {
            "api_key": "your api key",
            "max_tokens": 500,
            "temperature": 0.0
        }
    }
}
```