---
sidebar_position: 2
---

# Quick Start Guide

Welcome to **Unoplat Code Confluence**

:::info Current Status
Unoplat Code Confluence currently supports Python codebases and is in alpha stage. We're actively working on expanding language support and features.
:::

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Troubleshooting](#troubleshooting)

## Introduction

The current version supports parsing codebases and exporting a JSON representation of code graph. For more details, check out:
- [📘 Vision](/docs/deep-dive/vision)
- [🗺️ Roadmap](/docs/deep-dive/roadmap)
- [⚙️ How It Works](/docs/deep-dive/how-it-works)

## Prerequisites

### Codebase Requirements

:::caution Version Limitation
Currently supports Python codebases up to 3.11 (due to dependency on isort)
:::

Code Confluence relies on two powerful tools for import segregation and dependency analysis:
- [🔍 Ruff](https://docs.astral.sh/ruff/) - For code analysis
- [🔄 isort](https://pycqa.github.io/isort/) - For import organization

### Required Configurations

#### 1. Ruff Configuration

Create a `ruff.toml` file in your project root:

```toml title="ruff.toml"
target-version = "py311"

exclude = [
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "build",
    "dist",
]

src = ["unoplat_code_confluence"]  # Adjust this to your project's source directory
line-length = 320

[lint]
# Enable only flake8-tidy-imports
select = ["I","E402","INP001","TID","F401","F841"]

[lint.per-file-ignores]
"__init__.py" = ["E402","F401"]

[lint.flake8-tidy-imports]
ban-relative-imports = "all"

[lint.isort]
combine-as-imports = true
force-to-top = ["os","sys"]
```

:::note
This configuration is temporary for the alpha version and will be automated in future releases.
:::

Run Ruff with:

```bash
ruff check --fix . --unsafe-fixes
```

#### 2. isort Configuration

Create an `.isort.cfg` file:

```ini title=".isort.cfg"
[settings]
known_third_party = "Include third party dependencies here"
import_heading_stdlib = Standard Library
import_heading_thirdparty = Third Party
import_heading_firstparty = First Party
import_heading_localfolder = Local 
py_version = 311
line_length = 500
```

Run isort with:

```bash
isort . --python-version 311
```

### Installation Requirements

Before starting, install these tools:

- [🐍 PyEnv](https://github.com/pyenv/pyenv) - Python version manager
- [📦 Pipx](https://github.com/pypa/pipx) - Python app installer
- [🎭 Poetry](https://python-poetry.org/) - Dependency manager

```bash
pipx install poetry
```

## Installation

### 1. Python Setup

```bash
pyenv install 3.12.1
pyenv global 3.12.1
```

### 2. Install Code Confluence

```bash title="Install latest version"
pipx install --python $(pyenv which python) 'git+https://github.com/unoplat/unoplat-code-confluence.git@unoplat-code-confluence-v0.17.0#subdirectory=unoplat-code-confluence'
```

## Configuration

### JSON Configuration

:::tip
All configuration fields support environment variable overrides using the `UNOPLAT_` prefix.
:::

#### Required Fields

<details>
<summary><b>repositories</b>: Array of repositories to analyze</summary>

- `git_url`: Repository URL
- `output_path`: Analysis output directory
- `codebases`: Array of codebase configurations
  - `codebase_folder_name`: Codebase directory name
  - `root_package_name`: Root package name
  - `programming_language_metadata`: Language config
    - `language`: Programming language
    - `package_manager`: Package manager type
    - `language_version`: Language version
</details>

<details>
<summary><b>archguard</b>: ArchGuard tool configuration</summary>

- `download_url`: ArchGuard download URL
- `download_directory`: Local storage directory
</details>

<details>
<summary><b>logging_handlers</b>: Logging configuration</summary>

- `sink`: Log file path
- `format`: Log message format
- `rotation`: Log rotation size
- `retention`: Log retention period
- `level`: Logging level
</details>

#### Example Configuration

```json title="config.json"
{
  "repositories": [
    {
      "git_url": "https://github.com/unoplat/unoplat-code-confluence",
      "output_path": "/Users/jayghiya/Documents/unoplat",
      "codebases": [
        {
          "codebase_folder_name": "unoplat-code-confluence",
          "root_package_name": "unoplat_code_confluence",
          "programming_language_metadata": {
            "language": "python",
            "package_manager": "poetry",
            "language_version": "3.12.0"
          }        
        }
      ]
    }
  ],
  "archguard": {
    "download_url": "archguard/archguard",
    "download_directory": "/Users/jayghiya/Documents/unoplat"
  },
  "logging_handlers": [
    {
      "sink": "~/Documents/unoplat/app.log",
      "format": "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <magenta>{thread.name}</magenta> - <level>{message}</level>",
      "rotation": "10 MB",
      "retention": "10 days",
      "level": "DEBUG"
    }
  ]
}
```

### Environment Variables

Create a `.env.dev` file:

```env title=".env.dev"
UNOPLAT_ENV=dev
UNOPLAT_DEBUG=true 
UNOPLAT_GITHUB_TOKEN=Your_Github_Pat_Token
```

### Running the Application

```bash
unoplat-code-confluence --config /path/to/your/config.json
```

## Troubleshooting

:::danger Common Issues
If you encounter any issues, please check:
1. Python version compatibility
2. Environment variable configuration
3. JSON configuration syntax
:::

For more help, visit our [GitHub Issues](https://github.com/unoplat/unoplat-code-confluence/issues) page.

