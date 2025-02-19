---
sidebar_position: 2
---

# 🚀 Quick Start Guide

Welcome to **Unoplat Code Confluence** - Your Gateway to Code Understanding!

:::info Current Status
🔄 Unoplat Code Confluence currently supports Python codebases and is in alpha stage. We're actively working on expanding language support and features.
While in alpha stage, it's best suited for developers and tech enthusiasts who enjoy exploring new tools, don't mind a few rough edges, and are willing to provide feedback as we work towards establishing a complete end-to-end workflow!
:::

## 📑 Table of Contents

- [🚀 Quick Start Guide](#-quick-start-guide)
  - [📑 Table of Contents](#-table-of-contents)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Setting Up Code Confluence](#setting-up-code-confluence)
  - [Repository Configuration](#repository-configuration)
    - [📝 Creating Your Configuration](#-creating-your-configuration)
    - [Configuration Fields](#configuration-fields)
    - [💡 Example Configuration](#-example-configuration)
  - [CLI Installation](#cli-installation)
  - [Running the Application](#running-the-application)
  - [Troubleshooting](#troubleshooting)
    - [🔍 Support Options](#-support-options)

## Introduction

The current version supports parsing codebases and exporting a JSON representation of code graph. For more details, check out:
- 📘 [**Vision »**](/docs/deep-dive/vision)

## Prerequisites

Before you begin, ensure you have the following tools installed:

| Tool | Purpose |
|------|---------|
| [**🚀 uv »**](https://docs.astral.sh/uv/getting-started/installation/) | Fast Python package installer and resolver |
| [**🐳 Docker & Docker Compose »**](https://www.portainer.io/) | For running services |

## Setting Up Code Confluence

Follow these steps to set up the ingestion engine:

1. **Create Project Directory and Download Configuration:**
   ```bash
   mkdir -p code-confluence && cd code-confluence
   
   # Download Docker Compose file
   curl -O https://raw.githubusercontent.com/unoplat/unoplat-code-confluence/main/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/prod-docker-compose.yml
   ```

2. **Launch Services:**
   ```bash
   docker compose -f prod-docker-compose.yml up -d
   ```

3. **Verify Deployment:**
   ```bash
   docker compose -f prod-docker-compose.yml ps
   ```

## Repository Configuration

### 📝 Creating Your Configuration

Create a `config.json` file with your repository details:

<details>
<summary>Basic Configuration Template</summary>

```json
{
  "repositories": [
    {
      "git_url": "https://github.com/your-org/your-repo",
      "output_path": "/path/to/output/directory",
      "codebases": [
        {
          "codebase_folder": "path/to/codebase",
          "root_package": "src/package_name",
          "programming_language_metadata": {
            "language": "python",
            "package_manager": "uv"
          }
        }
      ]
    }
  ]
}
```
</details>

:::tip
You can configure multiple repositories by including additional objects in the "repositories" array, and within each repository, you can specify multiple codebases in the "codebases" array. All of these will be processed in parallel.
:::

:::note
Currently, the only supported language is Python.
:::

### Configuration Fields

| Field                             | Description                                 |
|-----------------------------------|---------------------------------------------|
| `repositories`                    | Array of repositories to analyze            |
| `git_url`                         | Repository URL (HTTPS)                      |
| `output_path`                     | Local directory for analysis output         |
| `codebases`                       | Array of codebase configurations            |
| `codebase_folder`                 | Path to codebase within repository          |
| `root_package`                    | Path to root package/module                 |
| `programming_language_metadata`   | Language configuration details              |

### 💡 Example Configuration

<details>
<summary>Real-world Configuration Example</summary>

```json
{
  "repositories": [
    {
      "git_url": "https://github.com/unoplat/unoplat-code-confluence",
      "output_path": "/Users/username/Documents/unoplat",
      "codebases": [
        {
          "codebase_folder": "unoplat-code-confluence-ingestion/code-confluence-flow-bridge",
          "root_package": "src/code_confluence_flow_bridge",
          "programming_language_metadata": {
            "language": "python",
            "package_manager": "uv"
          }
        }
      ]
    }
  ]
}
```
</details>

## CLI Installation

1. **Create Virtual Environment:**
   ```bash
   uv venv
   ```

2. **Install Code Confluence CLI:**
   ```bash
   uv pip install "git+https://github.com/unoplat/unoplat-code-confluence.git#subdirectory=unoplat-code-confluence-cli" 
   ```

## Running the Application

1. **Execute Analysis:**
   ```bash
   code-confluence --config /path/to/your/config.json
   ```

   When you run this command, you'll be prompted to enter a GitHub Personal Access Token (PAT). This token is needed to  clone the repositories specified in your config file.

   :::tip Getting a GitHub PAT
   If you don't have a GitHub PAT:
   1. Go to GitHub Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
   2. Click "Generate new token (classic)"
   3. Give it a name like "CodeConfluence"
   4. Select only the `repo` scope (this gives read access to repositories)
   5. Click "Generate token" and copy it
   
   You only need read access since we'll just be cloning repositories!
   :::

2. **Access Neo4j Browser:**
   - 🌐 Open: `http://localhost:7474/browser/`
   - 🔑 Login with:
     ```
     Username: neo4j
     Password: password
     ```

3. **Explore Your Code Graph:**
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

### 🔍 Support Options

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

