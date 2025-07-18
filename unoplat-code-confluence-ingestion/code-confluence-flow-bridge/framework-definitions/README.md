# Framework Definitions

This directory contains JSON definitions for programming language frameworks and libraries that follow the custom grammar schema.

## Directory Structure

```
framework-definitions/
├── schema.json (JSON Schema for validation)
├── python/
│   ├── fastapi.json
│   ├── pydantic.json
│   ├── sqlalchemy.json
│   └── sqlmodel.json
├── javascript/
│   └── (future framework definitions)
└── README.md
```

## Schema Format

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
          "concept": "AnnotationLike|CallExpression|Inheritance",
          "locator_strategy": "VariableBound|Direct",
          "construct_query": {
            "method_regex": "pattern"
          }
        }
      }
    }
  }
}
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
uv run --group dev check-jsonschema --schemafile framework-definitions/schema.json framework-definitions/python/*.json
```

## Contributing

1. Create a new JSON file for your framework in the appropriate language directory
2. Follow the schema structure and validation rules in `schema.json`
3. **Validate your changes** using the validation commands above
4. Include comprehensive absolute_paths for all import variations
5. Use appropriate concepts and locator strategies
6. Test with actual code examples from your codebase

## Concepts

- **AnnotationLike**: Decorators, annotations (@app.get, @field_validator)
- **CallExpression**: Function calls (Field(), Depends(), Column())
- **Inheritance**: Class inheritance (BaseModel, SQLModel, declarative_base)

## Locator Strategies

- **VariableBound**: Find variables bound to constructors first (app = FastAPI(); @app.get)
- **Direct**: Match symbols as written (@field_validator, Field())