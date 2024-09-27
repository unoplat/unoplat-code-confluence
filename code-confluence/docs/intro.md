---
sidebar_position: 1
---

# Quickstart

Unoplat code confluence provide most deterministic and precise code context for any code repository and across multiple such code repositories tied through domain and then eventually become the unified code context provider which then can be integrated with projects like OpenDevin, Devon, Danswer, Continue Dev and other oss.

# Installation

**Usage Instructions :**

1. Install Pipx
2. Install unoplat-code-confluence through : 

```bash
pipx install 'git+https://github.com/unoplat/unoplat-code-confluence.git@v0.10.0#subdirectory=unoplat-code-confluence'
```

 
3. Before you can run the unoplat code confluence tool on your local machine, you need to set up the necessary configuration file. This file tells tool where your codebase is located, where to output the analysis results, and other essential information. Below is a step-by-step guide to setting up your configuration.


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

**llm Provider Config:**
  **Model Providers Supported:** ["openai","together","anyscale","awsanthropic","cohere","ollama"] (cohere does not work right now. there is a issue already created. we will be addressing it soon)
  For config inside llm_provider_config refer - Dspy Model Provider Doc
If you are looking for some credits sign up on Together AI and get 25$ to run code confluence on repository of your choice. You can even use Ollama


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
