# Business Domain References

## Domain Summary
This repository is centered on code intelligence for repository ingestion, using Tree-sitter-based analysis to detect framework usage and structural patterns in Python and TypeScript. The key data models capture call-match evidence, annotation-like decorators, function/call detections, and inheritance matches so the system can recognize framework features from imports, calls, and base classes. Overall, it looks like a code analysis bridge that feeds downstream workflow processing and metadata storage for source-code understanding.

## Data Model References
### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/python/python_tree_sitter_framework_detector.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/python/python_tree_sitter_framework_detector.py#L72-L86`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/typescript_tree_sitter_framework_detector.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/engine/programming_language/typescript/typescript_tree_sitter_framework_detector.py#L72-L85`
