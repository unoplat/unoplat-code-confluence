<a name="top"></a>

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
    Always keep your agents ready with all the context required per repository.
    <br />
    <a href="https://docs.unoplat.io"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://docs.unoplat.io/docs/quickstart/how-to-run">Quick Start</a>
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

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#demo-agentsmd-first-context">Demo</a></li>
    <li><a href="#%EF%B8%8F-the-problem">The Problem</a></li>
    <li><a href="#-the-solution">The Solution</a></li>
    <li><a href="#-core-principles">Core Principles</a></li>
    <li><a href="#-getting-started">Getting Started</a></li>
    <li><a href="#-project-status">Project Status</a></li>
    <li><a href="#maintainers">Maintainers</a></li>
    <li><a href="#-product-feedback--alpha-disclaimer">Product Feedback</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>

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

**What's in the demo:** automatic `AGENTS.md` generation per repo and an org index that gives any coding agent a precise source of truth.

<!-- THE PROBLEM SECTION -->
## ⚠️ The Problem

<p align="center">
  <img src="images/problem-statement.png" alt="Greenfield vs Brownfield Project comparison showing AI agent challenges" width="800">
</p>

AI coding agents excel at **greenfield projects** (new codebases built from scratch) but struggle with **brownfield codebases** (mature, production systems with existing code).

**Why?** They burn most of their context window on exploration—searching files, tracing flows, connecting dots—leaving little capacity for actual implementation. By the time they're ready to code, they've hit the "dumb zone" where performance degrades sharply. And since they lack long-term memory, this cycle repeats with every conversation.

**Multi-repo complexity** makes it worse. When code is split across connected repositories, the agent exhausts its context just mapping dependencies between codebases—often before writing a single line.

**Internal dependencies** present another failure mode. The agent has no onboarding to proprietary systems, so it hallucinates usage patterns. Worse, when internal documentation has drifted from actual implementation, the agent trusts those "lies" and produces code that doesn't work.

The end result: **slop code** requiring heavy rework.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- SOLUTION SECTION -->
## 🎯 The Solution

Unoplat Code Confluence is the **context engine** for application development, organizing precise, up-to-date knowledge of your data models, entry points, endpoints, and more—so coding agents can deliver and maintain features **2–3x faster** with higher quality.

### AGENTS.md-first Context

Auto-generates machine-readable `AGENTS.md` files per repo to give coding agents a **precise source of truth**:

- **Project Configuration** — Key config files and their responsibilities
- **Development Workflow** — Dev/build/test commands, infra, and third-party dependencies
- **Business Logic** — Core application logic, domain entities, and database entities
- **Entry Points & Interfaces** — Main entry points, API endpoints, and external interfaces
- **External Dependencies** — Roles and responsibilities of external libraries

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CORE PRINCIPLES SECTION -->
## 🌟 Core Principles

### 1. **Precision First**
- **[Extensible Language Support](https://github.com/unoplat/unoplat-code-confluence/tree/main/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/queries)**: Modular Tree-sitter based grammar extraction delivers consistent, accurate code context across all programming languages
- **[Extensible Framework-Aware Parsing](https://docs.unoplat.io/contribution/custom-framework-schema)**: Specialized grammar engines recognize framework and library-specific patterns based on project dependencies

### 2. **Context Engineering**
- All important metadata about application—dependencies, inbound/outbound interfaces, domain models, and data store models—are identified and their relationships preserved

### 3. **Enterprise-Grade Scalability, Reliability and Auditability**
- Scalable, auditable and reliable processing powered by workflow orchestrator

### 4. **Performance Optimization**
- Optimized algorithms across all aspects of discovery, detection, ingestion and AI-based insights

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- GETTING STARTED SECTION -->
## 🚀 Getting Started

Ready to enhance your development workflow?

Check out our [Quick Start Guide](https://docs.unoplat.io/docs/quickstart/how-to-run).

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- PROJECT STATUS SECTION -->
## 📊 Project Status

<div align="center">
  <h3>ALPHA</h3>
  <p>We're actively developing Unoplat Code Confluence. Currently supports <b>Python</b> and <b>TypeScript</b> codebases.</p>
</div>

For detailed roadmap, language support status, and planned features, see our **[Product Roadmap](https://docs.unoplat.io/docs/introduction/roadmap)**.

<p align="right">(<a href="#top">back to top</a>)</p>

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
