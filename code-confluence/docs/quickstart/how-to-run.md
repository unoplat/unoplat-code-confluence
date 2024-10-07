---
sidebar_position: 2
---

# # Quick Start Guide

Welcome to **Unoplat Code Confluence**! This guide will help you quickly set up and start using our platform to enhance your codebase management and collaboration.

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [1. Graph Database Setup](#1-graph-database-setup)
   - [Installation](#installation)
4. [2. Generate Summary and Ingest Codebase](#2-generate-summary-and-ingest-codebase)
   - [Ingestion Configuration](#ingestion-configuration)
   - [Running the Unoplat Code Confluence Ingestion Utility](#running-the-unoplat-code-confluence-ingestion-utility)
5. [3. Setup Chat Interface](#3-setup-chat-interface)
   - [Query Engine Configuration](#query-engine-configuration)
   - [Launch Query Engine](#launch-query-engine)
6. [Troubleshooting](#troubleshooting)



---

## Introduction

**Unoplat Code Confluence** empowers developers to effortlessly navigate and understand complex codebases. By leveraging a graph database and an intuitive chat interface, our platform enhances collaboration and accelerates onboarding.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- [Docker](https://www.docker.com/get-started) 
- [Pipx](https://github.com/pypa/pipx) 
- [Poetry](https://python-poetry.org/) 

```bash
pipx install poetry
```

## 1. Graph Database Setup

### Installation

1. **Run the Neo4j Container**

  ```bash
   docker run \
   --name neo4j-container \
   --restart always \
   --publish 7474:7474 \
   --publish 7687:7687 \
   --env NEO4J_AUTH=neo4j/Ke7Rk7jB:Jn2Uz: \
   --volume /Users/jayghiya/Documents/unoplat/neo4j-data:/data \
   --volume /Users/jayghiya/Documents/unoplat/neo4j-plugins/:/plugins \
   neo4j:5.23.0
```


## 2. Generate Summary and Ingest Codebase

### Ingestion Configuration

```json
{
  "local_workspace_path": "/Users/jayghiya/Documents/unoplat/textgrad/textgrad",
  "output_path": "/Users/jayghiya/Documents/unoplat",
  "output_file_name": "unoplat_textgrad.md",
  "codebase_name": "textgrad",
  "programming_language": "python",
  "repo": {
    "download_url": "archguard/archguard",
    "download_directory": "/Users/jayghiya/Documents/unoplat"
  },
  "api_tokens": {
    "github_token": "Your github pat token"
  },
  "llm_provider_config": {
    "openai": {
      "api_key": "Your openai api key",
      "model": "gpt-4o-mini",
      "model_type": "chat",
      "max_tokens": 512,
      "temperature": 0.0
    }
  },
  "logging_handlers": [
    {
      "sink": "~/Documents/unoplat/app.log",
      "format": "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <magenta>{thread.name}</magenta> - <level>{message}</level>",
      "rotation": "10 MB",
      "retention": "10 days",
      "level": "DEBUG"
    }
  ],
  "parallisation": 3,
  "sentence_transformer_model": "jinaai/jina-embeddings-v3",
  "neo4j_uri": "bolt://localhost:7687",
  "neo4j_username": "neo4j",
  "neo4j_password": "Ke7Rk7jB:Jn2Uz:"

}```

### Running the Unoplat Code Confluence Ingestion Utility

1.**Installation**

```bash
pipx install 'git+https://github.com/unoplat/unoplat-code-confluence.git@main#subdirectory=unoplat-code-confluence'
```

2.**Run the Ingestion Utility**

```bash
unoplat-code-confluence --config /path/to/your/config.json
```


## 3. Setup Chat Interface

### Query Engine Configuration

```json
{
    "sentence_transformer_model": "jinaai/jina-embeddings-v3",
    "neo4j_uri": "bolt://localhost:7687",
    "neo4j_username": "neo4j",
    "neo4j_password": "your neo4j password",
    "provider_model_dict": {
        "model_provider" : "openai/gpt-4o-mini",
        "model_provider_args": {
            "api_key": "your openai api key",
            "max_tokens": 500,
            "temperature": 0.0
        }
    }
}
```

### Launch Query Engine

1. **Installation**

```bash
pipx install 'git+https://github.com/unoplat/unoplat-code-confluence.git@main#subdirectory=unoplat-code-confluence-query-engine'
```

2. **Run the Query Engine**

```bash
unoplat-code-confluence-query-engine --config /path/to/your/config.json
```