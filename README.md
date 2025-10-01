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
    Extract, understand, and provide precise code context and related metadata across repositories tied through domains
    <br />
    <a href="https://docs.unoplat.io"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://docs.unoplat.io/docs/category/quickstart">Quick Start</a>
    ·
    <a href="https://github.com/unoplat/unoplat-code-confluence/issues">Report Bug</a>
    ·
    <a href="https://github.com/unoplat/unoplat-code-confluence/issues">Request Feature</a>
  </p>
  
  <!-- PROJECT SHIELDS -->
  <p align="center">
    <img src="https://img.shields.io/badge/Status-ALPHA-orange" alt="Status" />
    <img src="https://img.shields.io/badge/License-AGPL%203.0-blue" alt="License" />
    <a href="https://github.com/unoplat/unoplat-code-confluence/stargazers">
      <img src="https://img.shields.io/github/stars/unoplat/unoplat-code-confluence?style=social" alt="Star on GitHub" />
    </a>
    <a href="https://youtu.be/fRBV_f9fDKc?si=XYKkDv4IBGoFBS9u">
      <img src="https://img.shields.io/badge/Watch%20demo-YouTube?logo=youtube" alt="Watch the demo" />
    </a>
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

<!-- DEMO SECTION -->
<a id="demo-agentsmd-first-context"></a>
## 🎥 Demo: Agents.md-first Context

<p align="center">
  <a href="https://youtu.be/fRBV_f9fDKc?si=XYKkDv4IBGoFBS9u" target="_blank">
    <img src="https://img.youtube.com/vi/fRBV_f9fDKc/maxresdefault.jpg" alt="Agents.md demo video" width="900">
  </a>
  <br />
  <a href="https://github.com/unoplat/unoplat-code-confluence/stargazers"><b>Like this? Star the repo</b> ⭐</a>
  ·
  <a href="https://youtu.be/fRBV_f9fDKc?si=XYKkDv4IBGoFBS9u">Watch on YouTube</a>
</p>

**What’s in the demo:** automatic `AGENTS.md` generation per repo and an org index that gives any coding agent a precise source of truth.

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#-vision">Vision</a></li>
    <li><a href="#-why-unoplat-codeconfluence">Why Unoplat-CodeConfluence?</a></li>
    <li><a href="#-for-knowledge-engine-and-ai-coding-assistants">For Knowledge Engine and AI Coding Assistants</a></li>
    <li><a href="#-getting-started">Getting Started</a></li>
    <li><a href="#demo-agentsmd-first-context">Demo</a></li>
    <li><a href="#project-status">Project Status</a>
      <ul>
        <li><a href="#programming-language-support">Programming Language Support</a></li>
        <li><a href="#tasks-status">Tasks Status</a></li>
        <li><a href="#code-grammar">Code Grammar</a></li>
      </ul>
    </li>
    <li><a href="#creditsheeroessupportersinspirations">Credits/Heroes/Supporters/Inspirations</a></li>
    <li><a href="#maintainers">Maintainers</a></li>
    <li><a href="#-product-feedback">Product Feedback</a></li>
    <li><a href="#community-channel">Community Channel</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>

<!-- VISION SECTION -->
## 🎯 Vision

Unoplat Code Confluence aims to be the definitive solution for discovering, extracting, ingesting, understanding, and providing precise code context across repositories. By combining deterministic code grammar with state-of-the-art LLM pipelines, we unlock a wide range of use cases around code understanding, maintainability, and collaboration.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- WHY SECTION -->
## 🌟 Core Principles

### 1. **Precision First**
- **[Extensible Language Support](https://github.com/unoplat/unoplat-code-confluence/tree/main/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/queries)**: Modular Tree-sitter based grammar extraction delivers consistent, accurate code context across all programming languages
- **[Extensible Framework-Aware Parsing](https://docs.unoplat.io/contribution/custom-framework-schema)**: Specialized grammar engines recognize framework and library-specific patterns based on project dependencies

### 2. **Context Engineering**
- **Complete Context Graph**: All essential context—internal/external dependencies, inbound/outbound interfaces, domain models, data stores will be preserved.
- **Selective Context Routing & Hierarchical Decomposition**: Route only what matters to boost accuracy and efficiency across tasks. For example our structural signature focuses on declarations and important bits of function such as function calls instead of passing the entire content of function.

### 3. **Enterprise-Grade Reliability**
- Scalable and reliable processing powered by workflow orchestrator

### 4. **Performance Optimization**
- Optimized algorithms across all aspects of discovery, detection, ingestion and AI-based insights

## 🚀 Use Cases

### In Progress
- **AGENTS.md-first Context**: Auto-generate machine-readable AGENTS.md per repo and an org index, giving any coding agent a precise source of truth

### Planned
- **Application Overview**: Comprehensive understanding of application architecture, dependencies, and relationships through graph-based exploration

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

| Task                       | Done | In Progress | Planned |
|----------------------------|:----:|:-----------:|:-------:|
| Repository Discovery       |  ✓   |             |         |
| Auto Codebase Detection    |  ✓   |             |         |
| GitHub Ingestion           |  ✓   |             |         |
| GitHub Manual Sync         |  ✓   |             |         |
| Local Ingestion            |  ✓   |             |         |
| Local Manual Sync          |  ✓   |             |         |
| AGENTS.md-first Context    |      |       ✓     |         |
| Application Overview       |      |             |    ✓    |

<!-- MAINTAINERS SECTION -->
## Maintainers

<table>
  <tr>
    <td>
      <a href="https://github.com/JayGhiya">
        <strong>Jay Ghiya</strong>
        <br>
        Contact: jayghiya@unoplat.io
      </a>
    </td>
  </tr>
</table>
<p>Book a call with me - <a href="https://cal.com/jay-ghiya/15min">Cal Link</a></p>

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- PRODUCT FEEDBACK SECTION -->
## 💬 Product Feedback & Alpha Disclaimer

Unoplat Code Confluence is in alpha. We’re building for our own daily use first, prioritizing stability and bug fixes. We’re collecting feedback now and will act on it once the core is solid. Early adopters welcome. Expect rapid changes and rough edges.

- **Discord**: Join our [community channel](https://discord.com/channels/1131597983058755675/1169968780953260106)
- **GitHub Issues**: [Create an issue](https://github.com/unoplat/unoplat-code-confluence/issues) for bug reports or feature requests
- **GitHub Discussions**: [Start a discussion](https://github.com/unoplat/unoplat-code-confluence/discussions) for broader conversations

Your feedback is invaluable as we work toward production readiness and helps us prioritize our roadmap to better serve the developer community.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- LICENSE SECTION -->
## License

Unoplat-CodeConfluence is licensed under the [GNU Affero General Public License v3.0 (AGPL-3.0) + COMMONS CLAUSE](LICENSE).

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- ANCHOR FOR BACK TO TOP LINKS -->
<a name="top"></a>
