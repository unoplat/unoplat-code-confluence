# Unoplat-CodeConfluence - Where Code Meets Clarity


## Java Examples:

1. Spring Java Cassandra Starter
### Input:
Local workspace on your computer from:
```
 https://github.com/DataStax-Examples/spring-data-starter.git
```

### Output:

[JavaResult](https://github.com/unoplat/unoplat-code-confluence/blob/main/unoplat-code-confluence/examples/java/springstarterjava1_20240708115959.md)


## Python Example 

~~Note: Python support is alpha right now - check issue- [Python-Improvements](https://github.com/unoplat/unoplat-code-confluence/issues/77)~~ 

Python is stable and we tested on the most latest groundbreaking optimiser for prompts - textgrad through a model that has not seen beyond 2021. We have got amazing results. please check output below.

1. TextGrad
### Input:
Local workspace on your computer from:
```
https://github.com/zou-group/textgrad
```

### Output:

[TextGradPythonResult](https://github.com/unoplat/unoplat-code-confluence/blob/main/unoplat-code-confluence/examples/python/textgrad)

~~Refer - class and function level summaries for python as it is in alpha right now. Package and code are not up to the mark.~~

2. DSPY
### Input: 
Local workspace on your computer from:
```
https://github.com/stanfordnlp/dspy/tree/main/dspy
```
### Output:
[DspyPythonresult](https://github.com/unoplat/unoplat-code-confluence/tree/main/unoplat-code-confluence/examples/python/dspy)

#### Note: ~~Gpt3.5 turbo 16k is currently used for all examples.~~ You can use gpt-4o-mini as it is better and cheaper and the the utlity has been optimised for it.

## Current Stage

### Usage Instructions

1. Install [Pipx](https://pipx.pypa.io/stable/)
2. Install unoplat-code-confluence through :
```
   pipx install 'git+https://github.com/unoplat/unoplat-code-confluence.git@v0.11.1#subdirectory=unoplat-code-confluence'
```
3. Before you can run the unoplat code confluence tool on your local machine, you need to set up the necessary configuration file. This file tells tool where your codebase is located, where to output the analysis results, and other essential information. Below is a step-by-step guide to setting up your configuration.


```
{
    "local_workspace_path": "your path to codebase",
    "output_path": "directory path for markdown output",
    "output_file_name": "name of markdown output (example - xyz.md)",
    "codebase_name": "name of your codebase",
    "programming_language": "programming language type(example- java or python)",
    "repo": {
      "download_url": "archguard/archguard",
      "download_directory": "download directory for arcguard tool"
    },
    "api_tokens": {
      "github_token": "your github pat for downloading arcguard"
    },
    "llm_provider_config": {
      "openai": {
        "api_key": "YourApiKey",
        "model": "gpt-3.5-turbo-16k",
        "model_type" : "chat",
        "max_tokens": 1024,
        "temperature": 0.0
    }
},
    "logging_handlers": [
      {
          "sink": "~/Documents/unoplat/app.log",
          "format": "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
          "rotation": "10 MB",
          "retention": "10 days",
          "level": "INFO"
      }
    ],
   "parallisation": 3,
   "json_output": true
}
```
Configuration Note: Do not change the download_url and keep the programming_language to java or python (as right now only java & python are supported)

llm Provider Config: 
- Model Providers Supported: ["openai","together","anyscale","awsanthropic","cohere","ollama"] (cohere does not work right now. there is a issue already created. 
we will be addressing it soon)
 
- For config inside llm_provider_config refer - [Dspy Model Provider Doc](https://dspy-docs.vercel.app/docs/category/remote-language-model-clients)

- Parallisation creates multiple instances of model using your selected llm provider. Max parallelisation is limited by amount of max tokens per day/per sec from llm provider so experimentation is needed to arrive at optimimum parallelisation.

- Json Output of our pydantic schema is false by default. If you want to turn it on set it to true.

If you are looking for some credits sign up on Together AI and get 25$ to run code confluence on repository of your choice. You can even use Ollama

Together Example:
```
"llm_provider_config": {
      "together": {
        "api_key": "YourApiKey",
        "model": "zero-one-ai/Yi-34B-Chat"
    }

```

Ollama Example:
```
"llm_provider_config": {
      "ollama": {
        "model": "llama3"
    }

```

4. Run code confluence and check your output path. you will have a file name based on output file name. That file will carry precise summary of codebase at all levels - codebase,packages,classes and functions.
```
unoplat-code-confluence --config example_config.json
```

## Project Board

[GithubProjectBoard](https://github.com/orgs/unoplat/projects/6/views/2)

## Tech Stack 

1. [Chapi](https://chapi.phodal.com/)
2. [ArchGuard](https://github.com/archguard/archguard)
3. [DSPY](https://dspy-docs.vercel.app/)
4. [loguru](https://loguru.readthedocs.io/en/stable/api/logger.html)
5. [PyTest](https://pytest.org/)
6. [Pydantic](https://www.pydantic.dev)

