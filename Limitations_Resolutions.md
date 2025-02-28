# Limitations and Resolutions

This document tracks known limitations in code parsing capabilities and their resolution status across supported programming languages.

## Status Legend

| Status | Description |
|--------|-------------|
| ✅ RESOLVED | Issue has been fixed in our implementation and upstream |
| 🟡 PARTIAL | Issue has been partially resolved or has a workaround |
| 🔴 ACTIVE | Known limitation that is currently being addressed |
| 📅 PLANNED | Issue is scheduled to be resolved in an upcoming release |
| ⚪ UNPLANNED | Known limitation with no current plans for resolution |

## Python

### Active Limitations

| Feature | Status | Description | Impact | Workaround |
|---------|--------|-------------|--------|------------|
| Function Dependency Sorting | ⚪ UNPLANNED | Circular dependencies and recursive functions cannot be properly sorted as topological sort is used | May result in incomplete dependency graphs for codebases with circular references | Manual review may be required for circular dependencies |
| Function Return Type Parsing | 📅 PLANNED | Return types are not being properly captured in certain cases | May result in incomplete type information in the code grammar | Manual annotation of return types may be required |

### Resolved Limitations

| Feature | Status | Resolution Date | Description | Resolution Details |
|---------|--------|-----------------|-------------|-------------------|
| Function Call Parsing | ✅ RESOLVED | Q2 2023 | Method calls through class names were not being detected | Fixed in our implementation and in upstream [Issue #33](https://github.com/phodal/chapi/issues/33) |
| Class and Instance Variables | ✅ RESOLVED | Q3 2023 | Class variables and instance variables were only available per function, not per class/procedure | Fixed in our implementation and in upstream [Issue #32](https://github.com/phodal/chapi/issues/32). Previous POC using tree-sitter is no longer needed |

## Recent Improvements

Each release cycle, we actively work to resolve known limitations. Recent highlights include:

- Complete resolution of variable scope detection issues
- Enhanced method call detection through class names

## Reporting New Limitations

If you encounter a parsing issue not listed in this document, please report it through:
1. GitHub Issues: [Create a new issue](https://github.com/unoplat/unoplat-code-confluence/issues)
2. Community Discord: Join our [Discord channel](https://discord.com/channels/1131597983058755675/1169968780953260106)

Please include sample code that demonstrates the limitation and the expected parsing behavior.
