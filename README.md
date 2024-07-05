# Unoplat-CodeConfluence - Where Code Meets Clarity


## The Ultimate Goal

Goal of the project is to be the most deterministic and precise code context provider for any code repository and across multiple such code repositories tied through domain and then eventually become the unified code context provider which then can be integrated with projects like OpenDevin, Devon, Danswer,
Continue Dev and other oss , thereby complimenting the precision of these frameworks with minimal opex.

### Short term goals 

| Task                                                      | Status     |
|-----------------------------------------------------------|------------|
| Launch autodoc for Java                                    | Done       |
| Launch autodoc for Python                                  | In Progress|
| Launch autodoc for all programming languages               | Planned    |
| Launch Graph based ingestion and query                     | Planned    |
| Solve cross cutting concerns and make it possible to self host | Planned    |
| Plug it in.                                                | Planned    |

note: for detailed issues please refer roadmap mentioned below.

## Current Problem with doing Repository level Documentation using AI Tooling 

### Process Overview:

1. Indexing Code Files: All code files are indexed into a vector database using embeddings that capture the semantic meaning of the code.
2. Query Processing: The system uses fine-tuned language models to interpret the user's query about the codebase.
3. Retrieval-Augmented Generation: The language model performs RAG to fetch relevant code snippets or documentation based on the query.
4. Reranking: Retrieved results are reranked to present the most relevant information first based on the context and specifics of the query.

###  Challenges:

1. Limited Context Windows: Most AI tools suffer from limited context windows of large language models, which can hinder their ability to process large blocks of code or extended documentation effectively.
2. Lack of Long-term Memory: These tools generally do not incorporate long-term memory, which affects their ability to remember past interactions or understand extensive codebases deeply.
3. Inefficiency: This process can be computationally expensive and slow, particularly for large codebases, due to the extensive indexing and complex querying mechanisms.
4. Cost: The operational costs can be significant because of the resources required for maintaining up-to-date embeddings and processing queries with advanced AI models.
5. Compliance and Security Issues: Storing and processing entire codebases through cloud based commercial vendors can lead to lot of time lost in compliance issues/processes, especially with code that contains sensitive or proprietary information. 
6. First Principles Concern: The approach may not align with first principles of software engineering, which emphasize simplicity and minimizing complexity across programming languages constructs and frameworks.

### Mermaid Diagram of the Process:
Here's a visual representation of the process using a Mermaid diagram:

```mermaid
graph LR
    A[Start] --> B[Index Code Files]
    B --> C[Process Query]
    C --> D[Retrieve Relevant Data]
    D --> E[Rerank Results]
    E --> F[Present Results]
    F --> G[End]
```
This diagram helps visualize the workflow from the start of the query to the presentation of results, illustrating the steps where inefficiencies and complexities arise.

### Unoplat Solution to all of these problems

#### Unoplat Solution: Deterministic Information Ingestion for Enhanced Code Understanding
The Unoplat approach offers a significant shift from the conventional AI-powered tools by opting for a deterministic method to manage and understand codebases. Here’s an overview of how Unoplat proposes to resolve the inefficiencies of current AI-powered code assistance tools:

#### Process Overview:

1. Language-Agnostic Parsing: Unoplat uses a language-agnostic parser, similar to generic compilers, to analyze and interpret any programming language or framework. This step involves no AI, focusing solely on deterministic parsing methods.
2. Generating Semi-Structured JSON: From the parsing step, Unoplat generates semi-structured JSON data. This JSON captures essential constructs and elements of the programming languages being analyzed, providing a clear, structured view of the codebase without reliance on AI for code understanding.
3. Enhancing Metadata: The semi-structured JSON is transformed to optimised data model to represent codebase in most optimal fashion.
4. LLM Pipelines: There are tailored dspy pipelines (uncompiled as of now) for function, class, package and codebase summary capture. The goal is to externalise the config of preferred llms(oss/commercial) across dspy pipelines.
5. Output: The output is a highly detailed, easily navigable representation of the codebase, allowing developers to understand and modify code with much higher accuracy and speed than traditional AI-based tools.


##### Mermaid Diagram of the Process:
Here’s a visual representation using a Mermaid diagram to illustrate the Unoplat process:

```mermaid
graph TD
    A[Start] --> B[Language-Agnostic Parsing]
    B --> C[Generate Semi-Structured JSON]
    C --> D[Enhance Metadata]
    D --> E[Integrate with Dspy Pipelines]
    E --> F[Generate Enhanced Code Atlas]
    F --> G[End]
```
This diagram outlines the Unoplat process from the initial parsing of the codebase to the generation of an enhanced Code Atlas, highlighting the deterministic and structured approach to managing and understanding codebases.


## Example:

### Input:
```
Local workspace on your computer from https://github.com/DataStax-Examples/spring-data-starter.git
```

### Output:
```
springstarterjava1_20240701111627.md (the file is present in unoplat-code-confluence folder - it has formatting issues which will get resolved soon but the results are good)
```


## Current Stage

### Usage Instructions

1. Install Pipx.
2. Install unoplat-code-confluence through :
```
   pipx install git+https://github.com/unoplat/unoplat-code-confluence.git@v0.2.3#subdirectory=unoplat-code-confluence
```
3. Before you can run the unoplat code confluence tool on your local machine, you need to set up the necessary configuration file. This file tells tool where your codebase is located, where to output the analysis results, and other essential information. Below is a step-by-step guide to setting up your configuration.


```
{
    "local_workspace_path": "your path to codebase",
    "output_path": "directory path for markdown output",
    "output_file_name": "name of markdown output (example - xyz.md)",
    "codebase_name": "name of your codebase",
    "programming_language": "programming language type(example- java(right now only java is supported)",
    "repo": {
      "download_url": "archguard/archguard",
      "download_directory": "download directory for arcguard tool"
    },
    "api_tokens": {
      "github_token": "your github pat for downloading arcguard"
    },
    "ai_tokens": {
      "openai_api_key": "your openai api key"
    }
}
```
Configuration Note: Do not change the download_url and keep the programming_language to java (as right now only java is supported)

Note: we have tried gpt3.5 turbo and it works well as data is precise for code understanding. Our experience with https://huggingface.co/01-ai/Yi-1.5-34B-Chat also has been great apart from hiccups with last level when codebase understand is being formed. Also this will get much better as currently all the dspy modules are uncompiled.We will be rolling out evaluated models and results post optimisation soon. Until then users can use 3.5turbo for decent results.

4. Run code confluence and check your output path. you will have a file name based on output file name. That file will carry precise summary of codebase at all levels - codebase,packages,classes and functions.
```
unoplat-code-confluence --config example_config.json
```


### Status: Alpha

### Programming Language Support

1. Java  - Supported
2. Python - In Progress
3. Go - Planned
4. Ts/Js - Planned

Note: support is based on https://chapi.phodal.com/ and contributions are required on chapi upstream to improve parsing metadata. 

### Roadmap:
1. Generate training data for optimisation of summary generated at function ,class , package and codebase (use argilla for that)
2. Enable oss llms and induce llm routing for cost and effective optimisation for oss and commercial llms
3. Enable Python Language Support (extend current pydantic data models based on chapi for python)
4. Enable Graph based ingestion as well as retrieval - baleen/tree-summary
using multi hop ingestion/dspy pipelines. (basically baleen)
5. Encapsulate the offering in a rest fashion through fastapi
6. Integrate with Unoplat core to make it possible to self host with all cross cutting concerns for both unoplat code confluence and any embeddable graph db. (https://github.com/unoplat/unoplat)
5. Launch custom context provider with help of continue dev.
6. Launch custom context provider with llama index as llama code parser as a lib.
7. Make the context pluggable to danswer.
8. Make the context pluggable to opendevin and devon.
9. Now the most important Get all heroes/inspirations on board.


## Tech Stack 

1. [Chapi](https://chapi.phodal.com/)
2. [Litellm](https://docs.litellm.ai/docs/)
3. [ArchGuard](https://github.com/archguard/archguard)
4. [DSPY](https://dspy-docs.vercel.app/)
5. [loguru](https://loguru.readthedocs.io/en/stable/api/logger.html)
6. [PyTest](https://pytest.org/)
7. [Pydantic](https://www.pydantic.dev)


## Credits/heroes/supporters/Inspirations

These are the people because of which this work has been possible. Unoplat code confluence would not exist without them.
1. [Phodal from Chapi and ArcGuard](https://github.com/phodal)
2. [Ishaan & Krrish from Litellm](ishaan@berri.ai / krrish@berri.ai)
3. [Omar Khattab](https://omarkhattab.com/)
3. [Joao Moura from crewai](https://github.com/joaomdmoura)
4. [Vipin Shreyas Kumar](https://github.com/vipinshreyaskumar)
5. [Danswer](https://www.danswer.ai/)
6. [Continue](https://www.continue.dev/)
7. [OpenDevin](https://github.com/OpenDevin/OpenDevin)
8. [Devon](https://github.com/entropy-research/Devon)
7. [Apeksha](https://github.com/apekshamehta)
8. [Argilla](https://argilla.io/)
9. [Jeremy Howard](https://www.linkedin.com/in/howardjeremy)

## Maintainers

1. [Jay Ghiya](https://github.com/JayGhiya)
    - Contact: jayghiya@unoplat.co.in  
2. [Vipin Shreyas Kumar](https://github.com/vipinshreyaskumar)
    - Contact: vipinshreyaskumar@unoplat.co.in
  
## Community Channel
[UnoplatCodeConfluence Discord Channel](https://discord.com/channels/1131597983058755675/1169968780953260106) 
  
