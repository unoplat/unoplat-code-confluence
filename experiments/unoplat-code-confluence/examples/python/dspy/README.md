# llm provider config used


```

"llm_provider_config": {
        "openai": {
            "api_key": "Your Key",
            "model": "gpt-3.5-turbo-16k",
            "model_type" : "chat",
            "temperature": 0.0,
            "max_tokens": 1024
          }
```

Note: max token right now affect codebase level objective/summary as we use uncompiled dspy pipelines right now. So be mindful of this while setting max tokens. Only if codebase is larger than 60-70 files use more than 512 tokens. Otherwise use less than that.
