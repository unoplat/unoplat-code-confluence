# Limitations and Resolutions

This document provides detailed information about known limitations in code parsing and their possible resolutions for each supported programming language.

## Python

### Function Call Parsing
**Limitation:**
- Certain function calls are not detected, particularly:
  - Method calls through class names.

Upstream Issue Tracking: [Issue](https://github.com/phodal/chapi/issues/33)

### Function Return Type Parsing
**Limitation:**
- Return type is not captured properly in cases such as:

Upstream Issue Tracking: [Issue](https://github.com/phodal/chapi/issues/34)

### Function Dependency Sorting
**Limitation:**
- Circular dependencies/recursion will not work as topological sort is used

### ClassVariables and Instance Variables 
**Limitation:**
- Currently class variables and instance variables are not available per class/procedure. They are available per function.

Upstream Issue Tracking: [Issue](https://github.com/phodal/chapi/issues/32)

- We have a poc which uses tree sitter to capture this at node level which can be released post [issue](https://github.com/archguard/archguard/issues/159). 
