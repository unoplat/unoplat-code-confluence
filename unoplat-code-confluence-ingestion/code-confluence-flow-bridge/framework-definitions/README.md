# Framework Definitions

This directory contains JSON definitions for programming language frameworks and libraries that follow the custom grammar schema (v3).

## Directory Structure

```
framework-definitions/
├── schema.json (JSON Schema v3 for validation)
├── python/
│   ├── fastapi.json
│   ├── pydantic.json
│   ├── sqlalchemy.json
│   └── sqlmodel.json
├── typescript/
│   └── (future framework definitions)
└── README.md
```

## Schema Format (v3)

Each JSON file follows the `schema.json` schema with the structure:

```json
{
  "language": {
    "library": {
      "docs_url": "https://...",
      "features": {
        "feature_key": {
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
```

## Detection Heuristics (v3)

Detection is **import-gated** and **regex-based**:
- `absolute_paths` must be present in the file imports for a match to occur
- `construct_query` refines tree-sitter regex patterns for decorators, calls, inheritance, and exported function handlers
- `base_confidence` sets a default feature-level confidence (`0.0..1.0`, default `0.85`)
- `CallExpression` definitions are heuristic; low-confidence cases are validated downstream by the app-interfaces validator agent
- `FunctionDefinition` is used for exported handler declarations (for example Next.js route handlers such as `export async function GET(...)`)

When `base_confidence` is below `0.70`, include disambiguation guidance in feature `notes` so downstream validation can apply framework-specific checks consistently.

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
