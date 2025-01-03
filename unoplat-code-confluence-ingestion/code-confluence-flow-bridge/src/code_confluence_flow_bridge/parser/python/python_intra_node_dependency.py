# import re
# from typing import Dict, List, Set

# from unoplat_code_confluence.data_models.chapi_forge.unoplat_chapi_forge_node import UnoplatChapiForgeNode


# class PythonIntraNodeDependency:
    
    
#     def process_related_nodes(
#         self, unsorted_nodes: List[UnoplatChapiForgeNode]
#     ) -> List[UnoplatChapiForgeNode]:
#         """
#         Processes a list of nodes and orders them based on their dependencies.

#         Args:
#             unsorted_nodes: List of UnoplatChapiForgeNode instances to be ordered.

#         Returns:
#             List of UnoplatChapiForgeNode instances ordered based on dependencies.
#         """
#         # Step 1: Build mappings
#         function_to_node: Dict[str, UnoplatChapiForgeNode] = {}
#         class_name_to_node: Dict[str, UnoplatChapiForgeNode] = {}
#         node_name_map: Dict[str, UnoplatChapiForgeNode] = {}

#         for node in unsorted_nodes:
#             if node.node_name is None:
#                 continue
#             node_name_map[node.node_name] = node
#             if node.type == "CLASS":
#                 class_name_to_node[node.node_name] = node
#             for function in node.functions or []:
#                 if node.type == "CLASS":
#                     function_name = f"{node.node_name}.{function.name}"
#                 else:
#                     function_name = function.name
#                 if function_name:
#                     function_to_node[function_name] = node

#         # Step 2: Determine dependencies
#         node_dependencies: Dict[UnoplatChapiForgeNode, Set[UnoplatChapiForgeNode]] = {
#             node: set() for node in unsorted_nodes
#         }

#         for node in unsorted_nodes:
#             for function in node.functions or []:
#                 # Function call dependencies
#                 if function.function_calls:
#                     for call in function.function_calls:
#                         called_function_name = call.function_name
#                         if called_function_name is None:
#                             continue
#                         if call.node_name:
#                             called_function_full_name = f"{call.node_name}.{called_function_name}"
#                         else:
#                             called_function_full_name = called_function_name
#                         called_node = function_to_node.get(called_function_full_name)
#                         if called_node and called_node != node:
#                             node_dependencies[node].add(called_node)

#                 # Local variable type dependencies
#                 if function.local_variables:
#                     for var in function.local_variables:
#                         var_type = var.type_type
#                         if var_type:
#                             var_type = self.extract_type(var_type)
#                             dependent_node = class_name_to_node.get(var_type)
#                             if dependent_node and dependent_node != node:
#                                 node_dependencies[node].add(dependent_node)

#             # Class field dependencies
#             if node.type == "CLASS":
#                 if node.fields:
#                     for field in node.fields:
#                         field_type = field.type
#                         if field_type:
#                             field_type = self.extract_type(field_type)
#                             dependent_node = class_name_to_node.get(field_type)
#                             if dependent_node and dependent_node != node:
#                                 node_dependencies[node].add(dependent_node)

#         # Step 3: Topological sort
#         sorted_nodes = self.topological_sort(unsorted_nodes, node_dependencies)

#         return sorted_nodes

#     @staticmethod
#     def extract_type(type_str: str) -> str:
#         """
#         Extracts the main type from a type string, handling generic types.

#         Args:
#             type_str: The type string to extract from.

#         Returns:
#             The extracted type name.
#         """
#         # Remove generic type annotations like List[Type]
#         match = re.match(r"[\w\.]+", type_str)
#         if match:
#             return match.group(0)
#         return type_str

#     @staticmethod
#     def topological_sort(
#         nodes: List[UnoplatChapiForgeNode],
#         node_dependencies: Dict[UnoplatChapiForgeNode, Set[UnoplatChapiForgeNode]],
#     ) -> List[UnoplatChapiForgeNode]:
#         """
#         Performs a topological sort on the nodes based on their dependencies.

#         Args:
#             nodes: List of nodes to sort.
#             node_dependencies: Dictionary mapping nodes to their dependent nodes.

#         Returns:
#             List of nodes sorted based on dependencies.

#         Raises:
#             Exception: If a cycle is detected in the dependencies.
#         """
#         in_degree: Dict[UnoplatChapiForgeNode, int] = {node: 0 for node in nodes}
#         for node, deps in node_dependencies.items():
#             for dep in deps:
#                 in_degree[dep] += 1

#         queue = deque([node for node in nodes if in_degree[node] == 0])
#         sorted_nodes: List[UnoplatChapiForgeNode] = []

#         while queue:
#             current_node = queue.popleft()
#             sorted_nodes.append(current_node)
#             for dependent_node in node_dependencies[current_node]:
#                 in_degree[dependent_node] -= 1
#                 if in_degree[dependent_node] == 0:
#                     queue.append(dependent_node)

#         if len(sorted_nodes) != len(nodes):
#             logger.warning("Cycle detected in node dependencies. Processing remaining nodes arbitrarily.")
#             # Optionally, you can process the remaining nodes in any order
#             remaining_nodes = set(nodes) - set(sorted_nodes)
#             sorted_nodes.extend(remaining_nodes)

#         return sorted_nodes
        