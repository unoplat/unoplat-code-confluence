# Framework Definitions

This directory contains JSON definitions for programming language frameworks and libraries that follow the custom grammar schema (v4).

## Directory Structure

```
framework-definitions/
├── schema.json (JSON Schema v4 for validation)
├── python/
│   ├── celery.json
│   ├── fastapi.json
│   ├── fastmcp.json
│   ├── litellm.json
│   ├── pydantic.json
│   ├── sqlalchemy.json
│   └── sqlmodel.json
├── typescript/
│   ├── litellm.json
│   ├── nextjs.json
│   ├── swr.json
│   └── zustand.json
└── README.md
```

## Schema Format (v4)

Each JSON file follows the `schema.json` schema with a capability-operation hierarchy:

```json
{
  "language": {
    "library": {
      "docs_url": "https://...",
      "capabilities": {
        "capability_key": {
          "description": "Capability description",
          "operations": {
            "operation_key": {
              "description": "Human-readable description",
              "absolute_paths": ["fully.qualified.symbol"],
              "target_level": "function|class",
              "concept": "AnnotationLike|CallExpression|Inheritance|FunctionDefinition",
              "base_confidence": 0.85,
              "construct_query": {
                "method_regex": "pattern",
                "function_name_regex": "pattern",
                "export_name_regex": "pattern"
              }
            }
          }
        }
      }
    }
  }
}
```

### Key v4 Concepts

- **Capability families**: The `capability_key` is constrained by the `CapabilityFamily` enum (e.g. `http_endpoint`, `relational_database`, `llm_inference`, `data_validation`, `background_worker`). Each capability groups related operations under one logical family.
- **Composite feature keys**: At persistence time the loader produces a composite key `capability_key.operation_key` (e.g. `http_endpoint.define_route`) that uniquely identifies each feature row.
- **Operations as runtime contracts**: Each operation inside a capability represents one executable runtime contract -- a single decorator, call-expression, inheritance relationship, or function definition that the detection engine can match.

## Detection Heuristics (v4)

Detection is **import-gated** and **regex-based**:
- `absolute_paths` must be present in the file imports for a match to occur
- `construct_query` refines tree-sitter regex patterns for decorators, calls, inheritance, and exported function handlers
- `base_confidence` is a contributor-authored confidence field used only for `CallExpression` definitions
- `Inheritance` matching is import-bound (symbol alias or module alias + symbol) and does not use suffix fallback
- `CallExpression` matching is import-bound (symbol alias, module alias + symbol, or default-import alias) and does not use suffix/member fallback matching
- `CallExpression` detections emit deterministic metadata for downstream validation: `match_confidence`, `call_match_kind`, `matched_absolute_path`, optional `matched_alias`, and `call_match_policy_version`
- `FunctionDefinition` is used for exported handler declarations (for example Next.js route handlers such as `export async function GET(...)`)

Under current query-engine gating, only `CallExpression` rows with `base_confidence < 0.70` are routed to the validator agent. When a `CallExpression` definition uses a value below `0.70`, include disambiguation guidance in feature `notes` so downstream validation can apply framework-specific checks consistently.

For `CallExpression` contributors:
- Set explicit `base_confidence`; schema validation requires it for `CallExpression` and rejects it for other concepts.
- For low-confidence features (`< 0.70`), include concrete `notes` describing import/object provenance checks the validator should confirm.
- Prefer specific API symbol paths in `absolute_paths` over generic verb-like entries to reduce ambiguous matches.

## Import Style For Detection Accuracy

Framework matching depends on imports. Use explicit import style to improve recall and reduce false positives.

- Python (enforced with Ruff):
  - Prefer explicit imports (`from package import Symbol`) over wildcard imports.
  - Keep absolute imports only (no relative imports).
  - Relevant Ruff rules in this repo: `F403`, `F405`, `F406`, `TID`, `I`.

- TypeScript/JavaScript (recommended with ESLint):
  - Prefer named imports for framework entry modules (for example `next/server`).
  - Avoid namespace imports for detection-critical modules.
  - Avoid `require(...)` in ESM-first TypeScript codebases.
  - Suggested rules: `import/no-namespace`, `@typescript-eslint/no-require-imports`, `import/no-commonjs`.

Examples:

```python
# preferred
from fastapi import APIRouter, FastAPI

# avoid
from fastapi import *
```

```typescript
// preferred
import { NextRequest, NextResponse } from "next/server"

// avoid for detection-critical imports
import * as nextServer from "next/server"
```

## Validation

### Validate All Framework Definitions
```bash
task validate-framework-definitions
```

### Validate Specific File
```bash
task validate-single-framework FILE=framework-definitions/python/fastapi.json
```

### Run All Quality Checks (includes validation)
```bash
task code-quality
```

### Direct uv Command
```bash
uv run --group dev check-jsonschema --schemafile framework-definitions/schema.json framework-definitions/*/*.json
```

## Contributing

1. Create a new JSON file for your framework in the appropriate language directory
2. Follow the schema structure and validation rules in `schema.json`
3. **Validate your changes** using the validation commands above
4. Include comprehensive absolute_paths for all import variations
5. Use appropriate concepts for matching patterns
6. Test with actual code examples from your codebase

## Concepts

- **AnnotationLike**: Decorators, annotations (@app.get, @field_validator)
- **CallExpression**: Function calls (Field(), Depends(), Column())
- **Inheritance**: Class inheritance (BaseModel, SQLModel, declarative_base)
- **FunctionDefinition**: Exported function declarations (`export async function GET(...)`)
