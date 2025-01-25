# Standard Library
from collections import defaultdict, deque
from typing import Deque, Dict, List, Set

# First Party
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_chapi_forge_function import UnoplatChapiForgeFunction


class SortFunctionDependencies:
    def sort_function_dependencies(self, functions: List[UnoplatChapiForgeFunction], node_type: str) -> List[UnoplatChapiForgeFunction]:
        if node_type and node_type == "CLASS":
            return self.__sort_function_dependencies_for_class(functions=functions)
        else:
            return self.__sort_function_dependencies_for_procedural(functions=functions)

    def __build_dependency_graph_for_class(self, functions: List[UnoplatChapiForgeFunction]) -> tuple[Dict[str, Set[str]], Dict[str, int]]:
        # Create adjacency list and in-degree count
        graph: Dict[str, Set[str]] = defaultdict(set)
        in_degree: Dict[str, int] = defaultdict(int)
        function_name_map = {func.name: func for func in functions if func.name is not None}

        # Initialize in-degree for all functions
        for func in functions:
            if func.name is not None:
                in_degree[func.name] = 0

        # Build the graph
        for func in functions:
            if not func.function_calls or func.name is None:
                continue

            for call in func.function_calls:
                # Skip self-dependencies
                if call.function_name == func.name:
                    continue  # Skip adding an edge from a function to itself

                # Check if it's an internal class method call
                if call.function_name is not None and (call.node_name in ("self", "cls") or not call.node_name) and call.function_name in function_name_map:
                    # Add edge from called function to calling function
                    # This means: called_function must be processed before calling_function
                    graph[call.function_name].add(func.name)
                    in_degree[func.name] += 1

        # Convert defaultdict to regular dict before returning
        return dict(graph), dict(in_degree)

    def __sort_function_dependencies_for_class(self, functions: List[UnoplatChapiForgeFunction]) -> List[UnoplatChapiForgeFunction]:
        if not functions:
            return []

        # Build dependency graph
        graph, in_degree = self.__build_dependency_graph_for_class(functions)

        # Initialize queue with functions that have no incoming edges (in-degree == 0)
        queue: Deque[str] = deque()
        for func_name, degree in in_degree.items():
            if degree == 0:
                queue.append(func_name)

        # Store function names in sorted order
        sorted_names: List[str] = []
        function_map = {func.name: func for func in functions if func.name is not None}

        # Process queue (Kahn's algorithm)
        while queue:
            current = queue.popleft()
            sorted_names.append(current)

            # Reduce in-degree for all functions that the current function depends on
            for neighbor in graph.get(current, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check for cycles
        if len(sorted_names) != len(function_map):
            # If there's a cycle, return original list as fallback
            return functions

        # Convert sorted names back to functions
        return [function_map[name] for name in sorted_names]

    def __build_dependency_graph_for_procedural(self, functions: List[UnoplatChapiForgeFunction]) -> tuple[Dict[str, Set[str]], Dict[str, int]]:
        # Create adjacency list and in-degree count
        graph: Dict[str, Set[str]] = defaultdict(set)
        in_degree: Dict[str, int] = defaultdict(int)
        function_name_map = {func.name: func for func in functions if func.name is not None}

        # Initialize in_degree for all functions
        for func in functions:
            if func.name is not None:
                in_degree[func.name] = 0

        # Build the graph
        for func in functions:
            if not func.function_calls or func.name is None:
                continue

            for call in func.function_calls:
                # Skip self-dependencies
                if call.function_name == func.name:
                    continue  # Skip adding an edge from a function to itself

                # Check if it's a call to another procedural function
                if call.function_name is not None and call.function_name in function_name_map:
                    # Add edge from current function to called function
                    graph[call.function_name].add(func.name)
                    in_degree[func.name] += 1

        # Convert defaultdict to regular dict before returning
        return dict(graph), dict(in_degree)

    def __sort_function_dependencies_for_procedural(self, functions: List[UnoplatChapiForgeFunction]) -> List[UnoplatChapiForgeFunction]:
        if not functions:
            return []

        # Build dependency graph
        graph, in_degree = self.__build_dependency_graph_for_procedural(functions)

        # Initialize queue with functions that have no incoming edges (in-degree == 0)
        queue: Deque[str] = deque()
        for func_name, degree in in_degree.items():
            if degree == 0:
                queue.append(func_name)

        # Store function names in sorted order
        sorted_names: List[str] = []
        function_map = {func.name: func for func in functions if func.name is not None}

        # Process queue (Kahn's algorithm)
        while queue:
            current = queue.popleft()
            sorted_names.append(current)

            # Reduce in-degree for all functions that the current function depends on
            for neighbor in graph.get(current, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check for cycles
        if len(sorted_names) != len(function_map):
            # If there's a cycle, return original list as fallback
            return functions

        # Convert sorted names back to functions
        return [function_map[name] for name in sorted_names]
