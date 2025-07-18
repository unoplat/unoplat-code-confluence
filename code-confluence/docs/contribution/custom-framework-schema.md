---
sidebar_position: 2
---

# Custom Framework/Library Schema

The Custom Framework/Library Schema enables contributors to define framework and library patterns for Code Confluence to detect and analyze across different programming languages. This schema provides a structured way to describe how frameworks and libraries should be identified in codebases.

## Schema Overview

The schema is located at `/static/schemas/custom-framework-lib-schema.json` and follows JSON Schema Draft 2020-12 specification. It organizes framework/library definitions by programming language, with each language containing multiple library definitions.

## Schema Structure

### Top Level Structure

```json
{
  "python": {
    "fastapi": { /* library definition */ },
    "django": { /* library definition */ }
  },
  "javascript": {
    "express": { /* library definition */ },
    "react": { /* library definition */ }
  }
}
```

### Supported Languages

The schema currently supports these programming languages:
- `python`
- `javascript` 
- `typescript`
- `java`
- `go`

## Library Definition Structure

Each library definition must include:

### Required Fields

#### `docs_url` (string, URI format)
The canonical documentation URL for the library.

```json
{
  "docs_url": "https://fastapi.tiangolo.com/"
}
```

#### `features` (object)
A collection of discoverable features keyed by contributor-chosen identifiers.

```json
{
  "features": {
    "api_endpoint": { /* feature definition */ },
    "dependency_injection": { /* feature definition */ }
  }
}
```

### Optional Fields

#### `version` (string)
Library version used to verify patterns.

```json
{
  "version": "0.104.1"
}
```

## Feature Definition Structure

Each feature within a library must include:

### Required Fields

#### `description` (string)
Human-readable explanation of the feature.

```json
{
  "description": "FastAPI route decorator for HTTP endpoints"
}
```

#### `absolute_paths` (array of strings)
Fully-qualified import paths identifying the constructor/base class/annotation provider.

```json
{
  "absolute_paths": [
    "fastapi.FastAPI",
    "fastapi.applications.FastAPI"
  ]
}
```

#### `target_level` (enum)
Granularity of the code element that owns the feature.
- `"function"` - Function-level features
- `"class"` - Class-level features

#### `concept` (enum)
Language-agnostic construct category:
- `"AnnotationLike"` - Decorators, annotations, attributes
- `"CallExpression"` - Function/method calls
- `"Inheritance"` - Class inheritance patterns

#### `locator_strategy` (enum)
How to locate the feature in code:
- `"VariableBound"` - Discover identifiers bound to a constructor/factory first
- `"Direct"` - Match the symbol verbatim

### Optional Fields

#### `docs_url` (string, URI format)
Feature-specific documentation URL.

#### `startpoint` (boolean, default: false)
Indicates if this feature represents an entry point (API endpoints, message consumers, etc.).

#### `notes` (string)
Contributor notes, caveats, or additional links.

#### `construct_query` (object)
Optional refinements to the auto-generated Tree-sitter query. Available keys depend on the feature's concept:
- `method_regex` - Regular expression for method names
- `annotation_name_regex` - Regular expression for annotation names
- `attribute_regex` - Regular expression for attribute names
- `callee_regex` - Regular expression for function call names
- `superclass_regex` - Regular expression for superclass names

## Real Framework Examples

Here are actual examples from the Code Confluence codebase:

### FastAPI Framework

```json
{
  "python": {
    "fastapi": {
      "docs_url": "https://fastapi.tiangolo.com",
      "features": {
        "http_endpoint": {
          "description": "HTTP verb decorator that registers a route handler",
          "absolute_paths": [
            "fastapi.FastAPI",
            "fastapi.applications.FastAPI"
          ],
          "target_level": "function",
          "concept": "AnnotationLike",
          "locator_strategy": "VariableBound",
          "construct_query": {
            "method_regex": "(get|post|put|delete|patch|head|options|trace)"
          },
          "startpoint": true
        },
        "background_tasks": {
          "description": "Background task execution using BackgroundTasks",
          "absolute_paths": [
            "fastapi.BackgroundTasks"
          ],
          "target_level": "function",
          "concept": "CallExpression",
          "locator_strategy": "Direct"
        },
        "api_router": {
          "description": "Route organization using APIRouter",
          "absolute_paths": [
            "fastapi.APIRouter"
          ],
          "target_level": "function",
          "concept": "AnnotationLike",
          "locator_strategy": "VariableBound",
          "construct_query": {
            "method_regex": "(get|post|put|delete|patch|head|options|trace|include_router)"
          },
          "startpoint": true
        }
      }
    }
  }
}
```

### Pydantic Framework

```json
{
  "python": {
    "pydantic": {
      "docs_url": "https://docs.pydantic.dev",
      "features": {
        "data_model": {
          "description": "Base class for Pydantic models with automatic validation",
          "absolute_paths": [
            "pydantic.BaseModel",
            "pydantic.main.BaseModel"
          ],
          "target_level": "class",
          "concept": "Inheritance",
          "locator_strategy": "Direct"
        }
      }
    }
  }
}
```

### SQLAlchemy Framework

```json
{
  "python": {
    "sqlalchemy": {
      "docs_url": "https://docs.sqlalchemy.org",
      "features": {
        "declarative_base": {
          "description": "Base class for SQLAlchemy declarative models",
          "absolute_paths": [
            "sqlalchemy.ext.declarative.declarative_base",
            "sqlalchemy.orm.declarative_base"
          ],
          "target_level": "class",
          "concept": "Inheritance",
          "locator_strategy": "VariableBound"
        },
        "mapped_column": {
          "description": "Column definition using mapped_column for modern SQLAlchemy",
          "absolute_paths": [
            "sqlalchemy.orm.mapped_column"
          ],
          "target_level": "function",
          "concept": "CallExpression",
          "locator_strategy": "Direct"
        },
        "relationship": {
          "description": "Relationship definition between models",
          "absolute_paths": [
            "sqlalchemy.orm.relationship"
          ],
          "target_level": "function",
          "concept": "CallExpression",
          "locator_strategy": "Direct"
        },
        "column": {
          "description": "Traditional column definition using Column",
          "absolute_paths": [
            "sqlalchemy.Column",
            "sqlalchemy.sql.schema.Column"
          ],
          "target_level": "function",
          "concept": "CallExpression",
          "locator_strategy": "Direct"
        }
      }
    }
  }
}
```

### SQLModel Framework

```json
{
  "python": {
    "sqlmodel": {
      "docs_url": "https://sqlmodel.tiangolo.com",
      "features": {
        "sqlmodel_base": {
          "description": "Base class for SQLModel models combining Pydantic and SQLAlchemy",
          "absolute_paths": [
            "sqlmodel.SQLModel"
          ],
          "target_level": "class",
          "concept": "Inheritance",
          "locator_strategy": "Direct"
        },
        "field_definition": {
          "description": "Field definition using Field() function with SQLModel extensions",
          "absolute_paths": [
            "sqlmodel.Field"
          ],
          "target_level": "function",
          "concept": "CallExpression",
          "locator_strategy": "Direct"
        },
        "relationship": {
          "description": "Relationship definition between SQLModel models",
          "absolute_paths": [
            "sqlmodel.Relationship"
          ],
          "target_level": "function",
          "concept": "CallExpression",
          "locator_strategy": "Direct"
        }
      }
    }
  }
}
```

### Complete Multi-Framework Example

Here's how multiple frameworks can be combined in a single schema file:

```json
{
  "python": {
    "fastapi": {
      "docs_url": "https://fastapi.tiangolo.com",
      "features": {
        "http_endpoint": {
          "description": "HTTP verb decorator that registers a route handler",
          "absolute_paths": ["fastapi.FastAPI"],
          "target_level": "function",
          "concept": "AnnotationLike",
          "locator_strategy": "VariableBound",
          "construct_query": {
            "method_regex": "(get|post|put|delete|patch|head|options|trace)"
          },
          "startpoint": true
        }
      }
    },
    "pydantic": {
      "docs_url": "https://docs.pydantic.dev",
      "features": {
        "data_model": {
          "description": "Base class for Pydantic models with automatic validation",
          "absolute_paths": ["pydantic.BaseModel"],
          "target_level": "class",
          "concept": "Inheritance",
          "locator_strategy": "Direct"
        }
      }
    },
    "sqlalchemy": {
      "docs_url": "https://docs.sqlalchemy.org",
      "features": {
        "mapped_column": {
          "description": "Column definition using mapped_column for modern SQLAlchemy",
          "absolute_paths": ["sqlalchemy.orm.mapped_column"],
          "target_level": "function",
          "concept": "CallExpression",
          "locator_strategy": "Direct"
        }
      }
    }
  }
}
```

## Validation Rules

The schema includes several validation rules:

### Concept-Target Level Constraints

1. **CallExpression** features must use `target_level: "function"`
2. **Inheritance** features must use `target_level: "class"`

### Pattern Validation

- **absolute_paths** must follow the pattern: `^[A-Za-z_][\\w]*(\\.[A-Za-z_][\\w]*)+$`
- **Language keys** must be lowercase and match the supported languages enum
- **Library names** can be any non-empty string

## Best Practices

### 1. Comprehensive Coverage
- Define all major features of a framework/library
- Include both common and advanced usage patterns
- Cover different ways the same concept might be expressed

### 2. Accurate Paths
- Use fully-qualified import paths
- Test paths against actual library documentation
- Include version information when patterns change between versions

### 3. Clear Descriptions
- Write human-readable descriptions
- Explain the purpose and context of each feature
- Include examples in notes when helpful

### 4. Proper Categorization
- Choose appropriate `concept` values based on how the feature is used
- Use `startpoint: true` for entry points like API endpoints
- Set correct `target_level` based on where the feature applies

### 5. Strategic Regex Usage
- Use `construct_query` regex patterns to refine matches
- Test regex patterns against real code examples
- Keep patterns specific enough to avoid false positives

## Contributing Schema Updates

To contribute new framework/library definitions:

1. **Fork the repository** and create a feature branch
2. **Update the schema file** at `/static/schemas/custom-framework-lib-schema.json`
3. **Add comprehensive definitions** following the structure above
4. **Test your definitions** against real codebases
5. **Submit a pull request** with detailed examples and test cases

### Testing Your Schema

Before submitting, verify your schema definitions:

1. **JSON Validation**: Ensure the file is valid JSON
2. **Schema Validation**: Validate against the JSON Schema specification
3. **Real-world Testing**: Test against actual codebases using the framework
4. **Documentation**: Ensure all referenced URLs are accessible

## Troubleshooting

### Common Issues

#### Invalid absolute_paths
```
Error: Pattern does not match required format
```
**Solution**: Ensure paths follow the format `module.submodule.symbol`

#### Missing Required Fields
```
Error: Missing required property 'target_level'
```
**Solution**: Include all required fields in feature definitions

#### Concept-Target Level Mismatch
```
Error: CallExpression requires target_level 'function'
```
**Solution**: Follow the concept-target level constraints outlined above


## Future Enhancements

The schema is designed to be extensible. Future versions may include:
- Additional programming languages
- More concept types for different framework/library constructs
- Enhanced query refinement options