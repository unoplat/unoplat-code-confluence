<!-- PROJECT LOGO -->
<br />
<div align="center">
  <!-- If you have a logo, uncomment and use this
  <a href="https://github.com/unoplat/unoplat-code-confluence">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>
  -->

  <h1 align="center">Unoplat-CodeConfluence</h1>
  <h3 align="center">The Universal Code Context Engine</h3>

  <p align="center">
    Extract, understand, and provide precise code context across repositories and domains
    <br />
    <a href="https://unoplat.github.io/unoplat-code-confluence/docs/"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://docs.unoplat.io/">Quick Start</a>
    ·
    <a href="https://github.com/unoplat/unoplat-code-confluence/issues">Report Bug</a>
    ·
    <a href="https://github.com/unoplat/unoplat-code-confluence/issues">Request Feature</a>
  </p>
  
  <!-- PROJECT SHIELDS -->
  <p align="center">
    <img src="https://img.shields.io/badge/Status-ALPHA-orange" alt="Status" />
    <img src="https://img.shields.io/badge/Python-Beta-blue" alt="Python" />
    <img src="https://img.shields.io/badge/License-AGPL%203.0-blue" alt="License" />
  </p>
  
  <!-- SOCIAL SHIELDS -->
  <p align="center">
    <a href="https://discord.com/channels/1131597983058755675/1169968780953260106">
      <img src="https://img.shields.io/badge/Discord-Join_Us-7289DA?style=flat&logo=discord&logoColor=white" alt="Discord" />
    </a>
    <a href="https://x.com/unoplatio">
      <img src="https://img.shields.io/badge/Twitter-Follow_Us-1DA1F2?style=flat&logo=twitter&logoColor=white" alt="Twitter" />
    </a>
    <a href="https://www.linkedin.com/company/unoplat/">
      <img src="https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat&logo=linkedin&logoColor=white" alt="LinkedIn" />
    </a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#-vision">Vision</a></li>
    <li><a href="#-why-unoplat-codeconfluence">Why Unoplat-CodeConfluence?</a></li>
    <li><a href="#-for-knowledge-engine-and-ai-coding-assistants">For Knowledge Engine and AI Coding Assistants</a></li>
    <li><a href="#-oss-atlas-initiative">OSS Atlas Initiative</a></li>
    <li><a href="#-getting-started">Getting Started</a></li>
    <li><a href="#project-status">Project Status</a>
      <ul>
        <li><a href="#programming-language-support">Programming Language Support</a></li>
        <li><a href="#tasks-status">Tasks Status</a></li>
        <li><a href="#code-grammar">Code Grammar</a></li>
      </ul>
    </li>
    <li><a href="#creditsheeroessupportersinspirations">Credits/Heroes/Supporters/Inspirations</a></li>
    <li><a href="#maintainers">Maintainers</a></li>
    <li><a href="#community-channel">Community Channel</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>

<!-- VISION SECTION -->
## 🎯 Vision

Unoplat-CodeConfluence aims to be the definitive solution for extracting, understanding, and providing precise code context across repositories and domains. By combining deterministic code grammar with state-of-the-art LLM pipelines, we achieve human-like understanding of codebases in minutes rather than months. Our graph-based architecture ensures relationships and context are preserved at every level.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- WHY SECTION -->
## 🌟 Why Unoplat-CodeConfluence?

- **Deterministic Understanding**: Built on ArchGuard and Tree-sitter for reliable, language-agnostic code parsing
- **Smart Summarization**: Bottom-up code analysis from functions to entire codebases, preserving context at every level
- **Graph based Embedding**: Embed codebases' functions using SOTA embeddings to enable semantic search and retrieval
- **Enhanced Onboarding**: Intuitive, interconnected documentation helps new team members understand complex codebases quickly
- **Graph-Based Intelligence**: Query and explore codebases through natural, graphical relationships between components
- **Deep Dependency Insights**: Comprehensive parsing of package managers as well as any other related metadata reveals true project structure and relationships
- **Integration Ready**: Designed to work seamlessly with your existing development tools and workflows

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- FOR KNOWLEDGE ENGINE SECTION -->
## 🤝 For Knowledge Engine and AI Coding Assistants

Unoplat-CodeConfluence will provide:

- **Precise Context API**: Get reliable, deterministic code understanding through:
  - Bottom-up code summarization from functions to systems
  - Graph-based querying on SOTA embeddings with deterministic code grammar for natural code exploration
  - Deep package and dependency analysis

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- OSS ATLAS INITIATIVE SECTION -->
## 🔍 OSS Atlas Initiative

Our [UnoplatOssAtlas](https://github.com/unoplat/unoplat-oss-atlas/tree/main) project is designed to dramatically accelerate contributor onboarding and productivity in open-source projects. By providing deep, contextual understanding of popular repositories, we will help developers in the following:

- **Accelerate Onboarding**: Understand complex codebases in minutes instead of months
- **Boost Contribution Velocity**: Make meaningful contributions faster with deep contextual insights
- **Navigate Complex Systems**: Easily understand dependencies, patterns, and architectural decisions
- **Learn Best Practices**: Study and adopt patterns from well-established open-source projects

This initiative demonstrates our commitment to:

- Empowering the open-source ecosystem by reducing barriers to contribution
- Showcasing practical applications of our context extraction capabilities
- Supporting sustainable open-source development through better understanding and reducing time to value for oss projects

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- GETTING STARTED SECTION -->
## 🚀 Getting Started

Ready to enhance your development workflow?

Check out our [Quick Start Guide](https://docs.unoplat.io/).

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- PROJECT STATUS SECTION -->
## Project Status

<div align="center">
  <h3>ALPHA</h3>
</div>

### Programming Language Support

| Language   | In-POC | Alpha | Beta | Stable |
|------------|--------|-------|------|--------|
| Python     | ✓      | ✓     | ✓    |        |
| Java       | ✓      |       |      |        |
| TypeScript |        |       |      |        |
| Go         |        |       |      |        |

### Tasks Status

| Task                                                     | Research | POC | Released |
|----------------------------------------------------------|----------|-----|----------|
| Code Grammar                                             | ✓        | ✓   | ✓        |
| Integration With Workflow Orchestrator                   | ✓        | ✓   | ✓        |
| Data Modelling for Code Grammar                          | ✓        | ✓   | ✓        |
| Insertion into Graph Database                            | ✓        | ✓   | ✓        |
| Data Modelling for Code Summarisation                    | ✓        | ✓   |          |
| SOTA LLM Pipelines For Code Grammar Summarisation/Reports| ✓        | ✓   |          |
| SOTA Embeddings on Codebase Functions                    | ✓        |     |          |
| Automatic Documentation                                  | ✓        |     |          |
| GraphRag based Query Module                              |          |     |          |
| SDK for integration                                      |          |     |          |

### Code Grammar

#### Python

| Feature                                               | Beta | Stable | Limitations                                                                                                                                      |
|-------------------------------------------------------|------|--------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| Package Parsing                                       | ✓    |        |                                                                                                                                                  |
| Package Metadata Parsing - Poetry and PIP and UV      | ✓    |        |                                                                                                                                                  |
| Inheritance                                           | ✓    |        |                                                                                                                                                  |
| Function Parsing                                      | ✓    |        |                                                                                                                                                  |
| Class Parsing                                         | ✓    |        |                                                                                                                                                  |
| Procedural Code Parsing                               | ✓    |        |                                                                                                                                                  |
| Global Variable Parsing                               | ✓    |        |                                                                                                                                                  |
| Function Call Parsing                                 | ✓    |        | ~~Certain function calls are not detected.~~                                                                                                     |
| Class Variables/Instance Variables Parsing            | ✓    |        | ~~Not available per class/procedure. But available per function across functions.~~                                                              |
| Function Local Variable Parsing                       | ✓    |        |                                                                                                                                                  |
| Function Return Type Parsing                          | ✓    |        | Return type is not captured properly.                                                                                                            |
| Figuring out dependent internal classes               | ✓    |        |                                                                                                                                                  |
| Import Segregation                                    | ✓    |        | Currently only identifies internal procedures, classes, and others as unknown. External imports with links to dependencies in package manager metadata coming soon. |
| Sorting functions within a class/procedure based on dependency | ✓    |        | Circular dependencies/recursion will not work as topological sort is used.                                                              |
| Nested Functions                                      |      |        |                                                                                                                                                  |

> **Note**: For detailed limitations and resolutions that we are working towards refer to [Limitations_Resolutions.md](Limitations_Resolutions.md)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CREDITS SECTION -->
## Credits/heroes/supporters/Inspirations

<div align="center">
  <h4>These are the people/entities because of which this work has been possible.<br>Unoplat code confluence would not exist without them.</h4>
</div>

1. [Phodal from Chapi and ArcGuard](https://github.com/phodal)
2. [Ishaan & Krrish from Litellm](ishaan@berri.ai / krrish@berri.ai)
3. [Omar Khattab](https://omarkhattab.com/)
4. [Joao Moura from crewai](https://github.com/joaomdmoura)
5. [Vipin Shreyas Kumar](https://github.com/vipinshreyaskumar)
6. [Danswer](https://www.danswer.ai/)
7. [Continue](https://www.continue.dev/)
8. [OpenDevin](https://github.com/OpenDevin/OpenDevin)
9. [Devon](https://github.com/entropy-research/Devon)
10. [Apeksha](https://github.com/apekshamehta)
11. [Argilla](https://argilla.io/)
12. [Jeremy Howard](https://www.linkedin.com/in/howardjeremy)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- MAINTAINERS SECTION -->
## Maintainers

<div align="center">
  <table>
    <tr>
      <td align="center">
        <a href="https://github.com/JayGhiya">
          <strong>Jay Ghiya</strong>
          <br>
          Contact: jayghiya@unoplat.co.in
        </a>
      </td>
      <td align="center">
        <a href="https://github.com/vipinshreyaskumar">
          <strong>Vipin Shreyas Kumar</strong>
          <br>
          Contact: vipinshreyaskumar@unoplat.co.in
        </a>
      </td>
    </tr>
  </table>
  <p>Book a call with us - <a href="https://cal.com/jay-ghiya/15min">Cal Link</a></p>
</div>

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- COMMUNITY SECTION -->
## Community Channel

<div align="center">
  <a href="https://discord.com/channels/1131597983058755675/1169968780953260106">
    <img src="https://img.shields.io/badge/Discord-Join%20our%20community-7289DA?style=for-the-badge&logo=discord&logoColor=white" alt="Discord" />
  </a>
  <br>
  <a href="https://x.com/unoplatio">
    <img src="https://img.shields.io/badge/Twitter-Follow%20us-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white" alt="Twitter" />
  </a>
</div>

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- LICENSE SECTION -->
## License

Unoplat-CodeConfluence is licensed under the [GNU Affero General Public License v3.0 (AGPL-3.0)](https://www.gnu.org/licenses/agpl-3.0.en.html). This strong copyleft license ensures that derivatives of this software remain open source and under the same license.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- ANCHOR FOR BACK TO TOP LINKS -->
<a name="top"></a>

