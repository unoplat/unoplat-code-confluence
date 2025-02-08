# Unoplat-CodeConfluence - The Universal Code Context Engine

## 🎯 Vision

Unoplat-CodeConfluence aims to be the definitive solution for extracting, understanding, and providing precise code context across repositories and domains. By combining deterministic code grammar with state-of-the-art LLM pipelines, we achieve human-like understanding of codebases in minutes rather than months. Our graph-based architecture ensures relationships and context are preserved at every level.

## 🌟 Why Unoplat-CodeConfluence?

- **Deterministic Understanding**: Built on ArchGuard and Tree-sitter for reliable, language-agnostic code parsing
- **Smart Summarization**: Bottom-up code analysis from functions to entire codebases, preserving context at every level
- **Graph based Embedding**: Embed codebases' functions using SOTA embeddings to enable semantic search and retrieval
- **Enhanced Onboarding**: Intuitive, interconnected documentation helps new team members understand complex codebases quickly
- **Graph-Based Intelligence**: Query and explore codebases through natural, graphical relationships between components
- **Deep Dependency Insights**: Comprehensive parsing of package managers as well as any other related metadata reveals true project structure and relationships.
- **Integration Ready**: Designed to work seamlessly with your existing development tools and workflows

## 🤝 For Knowledge Engine and AI Coding Assistants

Unoplat-CodeConfluence will provide:

- **Precise Context API**: Get reliable, deterministic code understanding through:
  - Bottom-up code summarization from functions to systems
  - Graph-based querying on SOTA embeddings with deterministic code grammar for natural code exploration.
  - Deep package and dependency analysis

## 🔍 OSS Atlas Initiative

Our [UnoplatOssAtlas](https://github.com/unoplat/unoplat-oss-atlas/tree/main) project is designed to dramatically accelerate contributor onboarding and productivity in open-source projects. By providing deep, contextual understanding of popular repositories, we will help developers in the following:

- **Accelerate Onboarding**: Understand complex codebases in minutes instead of months
- **Boost Contribution Velocity**: Make meaningful contributions faster with deep contextual insights
- **Navigate Complex Systems**: Easily understand dependencies, patterns, and architectural decisions
- **Learn Best Practices**: Study and adopt patterns from well-established open-source projects

This initiative demonstrates our commitment to:

- Empowering the open-source ecosystem by reducing barriers to contribution
- Showcasing practical applications of our context extraction capabilities
- Supporting sustainable open-source development through better understanding and reducing time to value for oss projects.

## 🚀 Getting Started

Ready to enhance your development workflow? 
Check out our [Quick Start Guide](https://unoplat.github.io/unoplat-code-confluence/docs/quickstart/how-to-run) 
We ran our code graph capability on [Onyx](https://github.com/onyx-dot-app/onyx) for its python backend and here is 
[result](https://github.com/unoplat/unoplat-oss-atlas/blob/main/danswer/onyx_code_grammar_graph.json) 

## Project Status

ALPHA

### Programming Language Support

| Language | In-POC | Alpha | Beta | Stable |
|----------|---------|-------|------|---------|
| Python   | ✓       | ✓     | ✓    |         |
| Java     | ✓       |       |      |         |
| TypeScript |       |       |      |         |
| Go       |       |       |      |         |

### Tasks Status

| Task                                  | Research | POC | Released |
|---------------------------------------|----------|-----|----------|
| Code Grammar                          | ✓        | ✓   | ✓        |
| Integration With Workflow Orchestrator | ✓        | ✓   | ✓        |
| Data Modelling for Code Grammar             | ✓        | ✓   | ✓         |
| Insertion into Graph Database         | ✓        | ✓   | ✓        |
| Data Modelling for Code Summarisation | ✓        | ✓   |          |
| SOTA LLM Pipelines For Code Grammar Summarisation/Reports | ✓        | ✓   |          |
| SOTA Embeddings on Codebase Functions | ✓        |     |          |
| Automatic Documentation              | ✓        |     |          |
| GraphRag based Query Module          |          |     |          |
| SDK for integration                  |          |     |          |


### Code Grammar

#### Python

| Feature                          | Beta | Stable | Limitations |
|----------------------------------|------|---------|-------------|
| Package Parsing                  | ✓    |        |             |
| Package Metadata Parsing - Poetry and PIP and UV | ✓    |        |             |
| Inheritance                      | ✓    |        |             |
| Function Parsing                 | ✓    |        |             |
| Class Parsing                    | ✓    |        |             |
| Procedural Code Parsing          | ✓    |        |             |
| Global Variable Parsing          | ✓    |        |             |
| Function Call Parsing            | ✓    |        | Certain function calls are not detected. |
| Class Variables/Instance Variables Parsing          | ✓    |        |Not available per class/procedure.  But available per function across functions.             |
| Function Local Variable Parsing  | ✓    |        |             |
| Function Return Type Parsing     | ✓    |        | Return type is not captured properly. |
| Figuring out dependent internal classes | ✓    |        |             |
| Import Segregation              | ✓    |        |             |
| Sorting functions within a class/procedure based on dependency | ✓    |        | Circular dependencies/recursion will not work as topological sort is used. |

Note: For detailed limitations and resolutions that we are working towards refer to [Limitations_Resolutions.md](Limitations_Resolutions.md)


## Credits/heroes/supporters/Inspirations

These are the people/entities because of which this work has been possible. Unoplat code confluence would not exist without them.
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
  
Book a call with us - [Cal Link](https://cal.com/jay-ghiya/15min)
  
## Community Channel

[UnoplatCodeConfluence Discord Channel](https://discord.com/channels/1131597983058755675/1169968780953260106) 
  
## X handle
[x](https://x.com/unoplatio)

