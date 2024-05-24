# Unoplat-CodeConfluence - Where Code Meets Clarity


## Overall Flow Diagram
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








