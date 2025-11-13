---
sidebar_position: 2
slug: /
---

# Quick Start Guide

Welcome to **Unoplat Code Confluence** - Your Gateway to Code Understanding!

:::info Current Status
🔄 Unoplat Code Confluence currently supports Python and typescript codebases and is in alpha stage. We're actively working on expanding language support and features.
While in alpha stage, it's best suited for developers and tech enthusiasts who enjoy exploring new tools, don't mind a few rough edges, and are willing to provide feedback as we work towards establishing a complete end-to-end workflow!
:::

## Introduction

Unoplat Code Confluence is an open source dev tooling platform that maintains a live, pluggable context layer per repo that renders and updates Agents.md.

- 📘 [**Vision »**](/deep-dive/vision)

## Prerequisites

Before you begin, ensure you have the following tool installed:

| Tool | Purpose |
|------|---------|
| [**🐳 Docker & Docker Compose »**](https://www.portainer.io/) | For running services |

## Setting Up Code Confluence

Follow these steps to set up Code Confluence:

1. **Create Project Directory and Download Configuration:**
   ```bash
   mkdir -p code-confluence && cd code-confluence

   # Download Docker Compose file
   curl -O https://raw.githubusercontent.com/unoplat/unoplat-code-confluence/refs/heads/main/prod-docker-compose.yml
   ```

2. **Launch Services:**
   ```bash
   docker compose -f prod-docker-compose.yml up -d
   ```

3. **Verify Deployment:**
   ```bash
   docker compose -f prod-docker-compose.yml ps
   ```

## Running the Application

### 1. Access the Web Interface
- Open your browser and go to [http://localhost:3000](http://localhost:3000)

### 2. Enter Your GitHub Personal Access Token (PAT)
- When prompted, enter a GitHub PAT with read access to the repositories you want to ingest.
- This is required for Code Confluence to clone and analyze your repositories.

![Enter GitHub PAT Token](../../static/new_github_token.png)

:::tip Getting a GitHub PAT
If you don't have a GitHub PAT:
1. Click "Generate new token on github (classic)"
2. Click "Generate token" and copy it in the dialog box.

:::

### 3. Search for GitHub Repositories
- Press **`s`** or **`S`** (Shift + s) to open the search dialog.
- You can search through your personal, public, and open source repositories.

![Search for Repository](../../static/repository_search.png)

### 4. Ingest Repository
- In the **Actions** column, click on **Ingest Repo** for the repository you want to analyze.
- Code Confluence will automatically detect Python and Typescript codebases as part of repository along with corresponding package manager metadata.

![Ingest Repo Action](../../static/repository_ingest_action.jpeg)

:::warning Codebase Detection - Beta Feature
Automatic codebase detection is currently in beta and may have bugs. After ingestion completes:

1. Navigate to **Ingestion Management** to review your repository ingestion results
2. Verify that all expected codebases were detected correctly
3. Check for any errors or missing codebases

![Ingestion Management - Codebases Ingested](../../static/codebases-ingested.png)

If you encounter any issues, such as codebases not being detected or errors during ingestion, please [**report them on our GitHub Issues**](https://github.com/unoplat/unoplat-code-confluence/issues).
:::

### 5. Configure Model Provider

After ingestion completes, configure your AI model provider to enable code intelligence features.

- Navigate to **Settings > Model Providers** in the application
- Code Confluence supports multiple AI model providers for code analysis and understanding

#### Recommended Configuration: OpenRouter with Grok

We recommend using **OpenRouter** with the **x-ai/grok-code-fast-1** model, which we've tested extensively for optimal performance and efficiency.

**Setup Steps**:
1. Select **OpenRouter** from the Provider dropdown
2. Enter your OpenRouter API key in the **API key** field
3. Set the **Model name** to `x-ai/grok-code-fast-1`
4. Click **Save Configuration**

![Model Provider Configuration - OpenRouter](../../static/model-provider.png)

:::tip Getting an OpenRouter API Key
If you don't have an OpenRouter API key:
1. Visit [OpenRouter](https://openrouter.ai/) and create an account
2. Navigate to your API Keys section
3. Generate a new API key and copy it

OpenRouter provides access to multiple AI models including Grok with competitive pricing.
:::

:::info Other Model Providers
While we recommend OpenRouter with Grok for the best experience, Code Confluence supports other model providers as well. You can experiment with different providers and models based on your preferences and requirements.
:::

:::warning Known Limitations
**Testing Status**: We have not thoroughly tested all model providers. OpenRouter with Grok has been tested extensively and is our recommended configuration.

**Streaming Bug**: There is a known issue with model providers that do not support streaming - agents may fail when using these providers. For details, see [GitHub Issue #727](https://github.com/unoplat/unoplat-code-confluence/issues/727).

If you encounter issues with a specific provider, please report them on our [GitHub Issues](https://github.com/unoplat/unoplat-code-confluence/issues) page.
:::

### 6. Repository Operations

After successfully ingesting your repository, you can perform various operations to manage your codebase. Navigate to **Ingestion Management** to access these operations.

![Repository Operations](../../static/repository-operations.png)

Code Confluence provides three key repository operations:

- **Generate Agents.md** - Automatically generates comprehensive documentation for AI agents to understand your codebase
- **Refresh Repository** - Updates your ingested codebase to reflect the latest changes from the source repository
- **Delete Repository** - Removes the ingested repository and all associated data from Code Confluence

#### AGENTS.md

When you trigger the **Generate Agents.md** operation, you can monitor the progress in real-time. The workflow shows progress for each codebase individually, as well as overall progress when your repository contains multiple codebases. You can view agent events in real-time as actions are performed.

![AGENTS.md Workflow Progress](../../static/agents-md-workflow.png)

You can continue ingesting and generating AGENTS.md for multiple repositories in parallel until you reach the maximum tokens per second limit of your model provider.

The generated AGENTS.md provides structured documentation covering:
- **Project Structure** - Overview of your codebase organization
- **Development Workflow** - Development practices and patterns
- **Business Logic** - Core functionality and domain logic

![AGENTS.md Preview Result](../../static/agents-md-preview-result.png)

:::info Coming Soon
We're continuously expanding the AGENTS.md sections to provide even more comprehensive codebase documentation for AI agents.
:::

### 7. Monitor Ingestion & Enable Developer Mode
- Navigate to **Settings > Developer Mode**, and toggle the switch on to unlock infrastructure tooling.
- Once enabled, you will see two new tools:

![Developer Mode](../../static/developer_mode.png)

#### Workflow Orchestrator
- Access and manage automated workflows
- View execution logs and debug orchestration issues.
- Monitor real-time workflow performance
- **Click the "Workflow Orchestrator" button** to open the temporal workflow orchestrator dashboard.

#### Knowledge Graph
- Explore the knowledge graph, inspect entities and relationships, and debug data connections
- **Click the "Knowledge Graph" button** to open the Neo4j Browser directly
- When Neo4j Browser opens, you'll be prompted to log in with:
  ```
  Username: neo4j
  Password: password
  ```
- Once logged in, try this query to explore your code graph:
  ```cypher
  MATCH (n)
  RETURN n
  LIMIT 25
  ```

:::tip
The above query displays the first 25 nodes in your code graph, perfect for a quick overview!
:::

## Troubleshooting

Need assistance? We're here to help!

### Support Options

1. **GitHub Issues**
   - 📝 Visit [**GitHub Issues »**](https://github.com/unoplat/unoplat-code-confluence/issues) to:
     - Report bugs or request features
     - Browse existing solutions
     - Get developer support

2. **Community Support**
   - 💬 Join our [**Discord Community »**](https://discord.com/channels/1131597983058755675/1169968780953260106) to:
     - Connect with other users
     - Get real-time assistance

:::note
Remember to check existing issues before creating a new one!
:::

---

<div className="docusaurus-powered">
  <p>This documentation is powered by <a href="https://docusaurus.io" target="_blank">Docusaurus</a>, making it easy to maintain and extend.</p>
</div>
