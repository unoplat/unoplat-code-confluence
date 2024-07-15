# Description

Versions depict the progress in codebase understanding. Latest is better.


v1-v4 were all generated using gpt3.5 turbo.
More tests coming soon with yi01-34b and llama3-70b

# llm provider config used


```

"llm_provider_config": {
        "openai": {
            "api_key": "Your Key",
            "model": "gpt-3.5-turbo-16k",
            "model_type" : "chat",
            "temperature": 0.0,
            "max_tokens": 150
          }
```

Note: max token right now affect codebase level objective/summary as we use uncompiled dspy pipelines right now. So be mindful of this while setting max tokens.
