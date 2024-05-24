# Unoplat-CodeConfluence - Where Code Meets Clarity


## Current Problem with AI Tooling (Codium,Codedium,TabNine etc)

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
5. Compliance and Security Issues: Storing and processing entire codebases can lead to compliance issues, especially with code that contains sensitive or proprietary information.
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
3. Enhancing Metadata: The semi-structured JSON is then used to enhance the metadata around the codebase. This enhanced metadata includes detailed information about code functions, variables, classes, and other relevant details that are crucial for understanding and navigating the codebase efficiently.
4. Integration with Open Source LLMs: Leveraging open-source large language models (LLMs), Unoplat combines the enriched metadata with multi-agentic workflows. This integration aims to produce a more sophisticated and useful "Code Atlas," which developers can use to navigate and understand large and complex codebases more effectively.
5. Output: The output is a highly detailed, easily navigable representation of the codebase, allowing developers to understand and modify code with much higher accuracy and speed than traditional AI-based tools.

#### Benefits:
1. Deterministic and Transparent: The deterministic nature of the process ensures transparency and reliability in how code is analyzed and understood.
2. Cost-Effective: Reduces the dependency on expensive AI models and the associated computational and maintenance costs.
3. Compliance and Security: By not relying on AI models trained on external data, Unoplat minimizes potential compliance and security issues.
4. Scalability: The approach is highly scalable, as it can handle any programming language or framework without needing specific model training.
##### Mermaid Diagram of the Process:
Here’s a visual representation using a Mermaid diagram to illustrate the Unoplat process:

```mermaid
graph TD
    A[Start] --> B[Language-Agnostic Parsing]
    B --> C[Generate Semi-Structured JSON]
    C --> D[Enhance Metadata]
    D --> E[Integrate with Open Source LLMs]
    E --> F[Generate Enhanced Code Atlas]
    F --> G[End]
```
This diagram outlines the Unoplat process from the initial parsing of the codebase to the generation of an enhanced Code Atlas, highlighting the deterministic and structured approach to managing and understanding codebases.

## Unoplat Solution to this
```mermaid
flowchart TD
    Start(Unoplat GUI/Terminal Experience)
    Parse[Parse Java Codebase]
    CHAP[Common Hierarchical Abstract Parser]
    IC[Information Converter]
    Archguard[Archguard]
    Output[Semi-structured JSON - Class Metadata]
    Litellm[litellm using sota oss llm for reasoning- phi3-14b-instruct]
    Finer_Summary[Finer Summary per Class]
    CrewAI_Manager_Agent[Manager_Crewai]
    Data_Engineer_Agent[Data Engineer - Job is to provide per class unoplat markdown spec]
    Unoplat_Custom_Tool[Custom Tool - Fetch Finer summary one at a time until end of items using long term memory]
    Software_Engineer_Agent[Software_Engineer_CrewAi - Clean up markdown]
    Senior_Software_Engineer_Agent[Senior Software Engineer- Adjust/Modify overall summary based on current summary]
    Senior_Markdown_Technical_Documentation_Specialist[Unoplat Markdown tech doc specialist- Analyze the evolving summary for accuracy and insights based on all available classes' metadata and include flow/interactions within the codebases between classes.]
    MarkdDownOutput[MarkdDownOutput]

    Start --> Parse
    Parse --> CHAP & IC & Archguard
    CHAP & IC & Archguard --> Output
    Output --> Litellm
    Litellm --> Finer_Summary
    Finer_Summary  --> CrewAI_Manager_Agent
    CrewAI_Manager_Agent --> Data_Engineer_Agent
    Data_Engineer_Agent --> Unoplat_Custom_Tool
    Unoplat_Custom_Tool --> Software_Engineer_Agent
    Software_Engineer_Agent --> Senior_Software_Engineer_Agent
    Senior_Software_Engineer_Agent --> Senior_Markdown_Technical_Documentation_Specialist
    Senior_Markdown_Technical_Documentation_Specialist --> MarkdDownOutput
```

## Tech Stack 

1. [Chapi](https://chapi.phodal.com/)
2. [PyTermGui](https://ptg.bczsalba.com/)
3. [Litellm](https://docs.litellm.ai/docs/)
4. [ArchGuard](https://github.com/archguard/archguard)
5. [CrewAi](https://www.crewai.com/)
6. [loguru](https://loguru.readthedocs.io/en/stable/api/logger.html)
7. [PyTest](https://pytest.org/)


## Techniques Used
1. Markdown Spec based Filler prompt for extreme precision
2. Chain of Thought
3. Self Reflection for Autocorrection
4. Collaboration among crewi agents with long/short term memory with precise roles


## Credits/heroes

These are the people because of which this work has been possible. Unoplat code confluence would not exist without them.
1. [Phodal from Chapi and ArcGuard](https://github.com/phodal)
2. [Ishaan & Krrish from Litellm](ishaan@berri.ai / krrish@berri.ai)
3. [Joao Moura from crewai](https://github.com/joaomdmoura)
4. [Vipin Shreyas Kumar](https://github.com/vipinshreyaskumar)
5. [Apeksha](https://github.com/apekshamehta)








