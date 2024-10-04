---
sidebar_position: 2
---

# How to Run

 Before you can run the unoplat code confluence tool on your local machine, you need to set up the necessary configuration file. This file tells tool where your codebase is located, where to output the analysis results, and other essential information. Below is a step-by-step guide to setting up your configuration.


```bash
{
    "local_workspace_path": "your path to codebase",
    "output_path": "directory path for markdown output",
    "output_file_name": "name of markdown output (example - xyz.md)",
    "codebase_name": "name of your codebase",
    "programming_language": "programming language type(example- java or python)",
    "repo": 
    {
      "download_url": "archguard/archguard",
      "download_directory": "download directory for arcguard tool"
    },
    "api_tokens": 
    {
      "github_token": "your github pat for downloading arcguard"
    },
    "llm_provider_config": 
    {
      "openai": 
      {
        "api_key": "YourApiKey",
        "model": "gpt-3.5-turbo-16k",
        "model_type" : "chat",
        "max_tokens": 1024,
        "temperature": 0.0
      }
    },
    "logging_handlers": 
    [
      {
          "sink": "~/Documents/unoplat/app.log",
          "format": "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
          "rotation": "10 MB",
          "retention": "10 days",
          "level": "INFO"
      }
    ]
}
```


**Configuration Note:** Do not change the download_url and keep the programming_language to java or python (as right now only java & python are supported)

**LLM Provider Config**

Model Providers Supported:
- OpenAI
- Together AI
- Anyscale
- AWS Anthropic
- Cohere (currently not working, issue already created and will be addressed soon)
- Ollama

For configuration inside `llm_provider_config`, refer to the [Dspy Model Provider Documentation](https://github.com/stanfordnlp/dspy/blob/main/docs/model_providers.md).

If you're looking for credits, sign up on [Together AI](https://www.together.ai/) and get $25 to run Code Confluence on a repository of your choice. You can also use Ollama as an alternative.


**Together Example:**

```bash
"llm_provider_config": 
{
      "together": 
      {
        "api_key": "YourApiKey",
        "model": "zero-one-ai/Yi-34B-Chat"
      }
}
```