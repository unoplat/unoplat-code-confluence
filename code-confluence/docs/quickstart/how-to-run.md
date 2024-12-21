---
sidebar_position: 2
---

# Quick Start Guide

Welcome to **Unoplat Code Confluence**

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Troubleshooting](#troubleshooting)

## Introduction

**Unoplat Code Confluence** currently supports python codebases. It is currently in alpha stage and we are working on adding support for more codebases and features. The current version supports parsing codebases and exporting a json representation of code graph. For more details on upcoming features, vision, deep dive please check out [vision](/docs/deep-dive/vision), [roadmap](/docs/deep-dive/roadmap) and [How-It-Works](/docs/deep-dive/how-it-works) respectively.

## Prerequisites

### Codebase Requirements

Currently unoplat code confluence supports python codebases till 3.11 (due to dependency on isort). To support features like segregating imports and figuring out internal dependencies code confluence relies on [ruff](https://docs.astral.sh/ruff/) and [isort](https://pycqa.github.io/isort/) ecosystem.

Here are the configurations that are required to be set in codebase:

#### 1. ruff.toml

```toml
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

Then run ruff on cli with:

```bash
ruff check --fix . --unsafe-fixes
```

#### 2. Isort Configuration (.isort.cfg)

```ini
[settings]
known_third_party = "Include third party dependencies here"
import_heading_stdlib = Standard Library
import_heading_thirdparty = Third Party
import_heading_firstparty = First Party
import_heading_localfolder = Local 
py_version = 311  # For Python 3.12
line_length = 500
```

Then run isort on cli with:

```bash
isort . --python-version 311
```

### Installation Requirements

Before you begin, ensure you have the following installed on your system:

- [PyEnv](https://github.com/pyenv/pyenv)
- [Pipx](https://github.com/pypa/pipx) 
- [Poetry](https://python-poetry.org/) 

```bash
pipx install poetry
```

## Installation

### 1. Python Setup

```bash
pyenv install 3.12.1
pyenv global 3.12.1
```

### 2. Install Unoplat Code Confluence

```bash
pipx install --python $(pyenv which python) 'git+https://github.com/unoplat/unoplat-code-confluence.git@unoplat-code-confluence-v0.17.0#subdirectory=unoplat-code-confluence'
```

## Configuration

### JSON Configuration

#### Configuration Fields

1. **repositories** (Required): Array of repositories to analyze
   - `git_url`: URL of the Git repository
   - `output_path`: Local directory where analysis results will be stored
   - `codebases`: Array of codebases within the repository
     - `codebase_folder_name`: Name of the folder containing the codebase
     - `root_package_name`: Root package name (optional for some languages)
     - `programming_language_metadata`: Language-specific configuration
       - `language`: Programming language (currently supports "python")
       - `package_manager`: Package manager type ("poetry" or "pip")
       - `language_version`: Version of the programming language

2. **archguard** (Required): Configuration for ArchGuard tool
   - `download_url`: URL to download ArchGuard from
   - `download_directory`: Local directory to store ArchGuard

3. **logging_handlers** (Required): Array of logging configurations
   - `sink`: Log file path
   - `format`: Log message format
   - `rotation`: Log file rotation size
   - `retention`: Log retention period
   - `level`: Logging level

#### Example Configuration

```json
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

Create a `.env.dev` file where you intend to run the project:

```env
UNOPLAT_ENV=dev
UNOPLAT_DEBUG=true 
UNOPLAT_GITHUB_TOKEN=Your_Github_Pat_Token
```

### Running the Application

```bash
unoplat-code-confluence --config /path/to/your/config.json
```

## Troubleshooting

