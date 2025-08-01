"""
Graph assertion utilities for integration tests.

These utilities provide direct Neo4j graph validation to ensure complete cleanup
of nodes and relationships, beyond what the API layer reports.
"""

from typing import Dict, List, Any


def count_nodes_by_label(neo4j_client, label: str) -> int:
    """
    Count all nodes with a specific label.
    
    Args:
        neo4j_client: Neomodel database instance
        label: Node label to count (e.g., 'CodeConfluenceFile')
        
    Returns:
        Number of nodes with the specified label
    """
    results, _ = neo4j_client.cypher_query(f"MATCH (n:{label}) RETURN count(n) AS c")
    return results[0][0] if results else 0


def count_nodes_by_label_and_qualifier(neo4j_client, label: str, qualifier_prefix: str) -> int:
    """
    Count nodes with a specific label that match a qualified_name prefix.
    
    Useful for scoped deletion validation when multiple repositories exist.
    
    Args:
        neo4j_client: Neomodel database instance
        label: Node label to count
        qualifier_prefix: Prefix to match against qualified_name property
        
    Returns:
        Number of matching nodes
    """
    results, _ = neo4j_client.cypher_query(
        f"MATCH (n:{label}) WHERE n.qualified_name STARTS WITH $prefix RETURN count(n) AS c",
        {"prefix": qualifier_prefix}
    )
    return results[0][0] if results else 0


def repo_exists(neo4j_client, qualified_name: str) -> bool:
    """
    Check if a repository node exists by qualified name.
    
    Args:
        neo4j_client: Neomodel database instance
        qualified_name: Repository qualified name (format: owner_repo)
        
    Returns:
        True if repository exists, False otherwise
    """
    results, _ = neo4j_client.cypher_query(
        "MATCH (r:CodeConfluenceGitRepository {qualified_name: $qn}) RETURN count(r) AS c",
        {"qn": qualified_name}
    )
    return (results[0][0] if results else 0) > 0


def count_all_relationships(neo4j_client) -> int:
    """
    Count all relationships in the graph.
    
    Useful for detecting dangling relationships after deletion.
    
    Args:
        neo4j_client: Neomodel database instance
        
    Returns:
        Total number of relationships in the graph
    """
    results, _ = neo4j_client.cypher_query("MATCH ()-[r]-() RETURN count(r) AS c")
    return results[0][0] if results else 0


def count_relationships_by_type(neo4j_client, relationship_type: str) -> int:
    """
    Count relationships of a specific type.
    
    Args:
        neo4j_client: Neomodel database instance
        relationship_type: Type of relationship (e.g., 'USES_FEATURE', 'PART_OF_PACKAGE')
        
    Returns:
        Number of relationships of the specified type
    """
    results, _ = neo4j_client.cypher_query(f"MATCH ()-[r:{relationship_type}]-() RETURN count(r) AS c")
    return results[0][0] if results else 0


def get_relationship_type_counts(neo4j_client) -> Dict[str, int]:
    """
    Get counts of all relationship types in the graph.
    
    Useful for comprehensive relationship cleanup validation.
    
    Args:
        neo4j_client: Neomodel database instance
        
    Returns:
        Dictionary mapping relationship type to count
    """
    results, _ = neo4j_client.cypher_query("MATCH ()-[r]-() RETURN type(r) AS rel_type, count(r) AS c")
    counts: Dict[str, int] = {}
    for row in results:
        counts[row[0]] = row[1]  # rel_type, count
    return counts


def find_nodes_related_to_repository(neo4j_client, repo_qualified_name: str) -> Dict[str, List[str]]:
    """
    Find all nodes that are still connected to a repository (should be empty after deletion).
    
    Args:
        neo4j_client: Neomodel database instance
        repo_qualified_name: Repository qualified name to check
        
    Returns:
        Dictionary mapping node labels to lists of qualified names that are still connected
    """
    # This query finds any nodes that have a path to the repository
    results, _ = neo4j_client.cypher_query("""
        MATCH (repo:CodeConfluenceGitRepository {qualified_name: $repo_qn})
        MATCH (repo)-[*]-(connected_node)
        WHERE connected_node <> repo
        RETURN labels(connected_node) AS labels, 
               connected_node.qualified_name AS qn,
               connected_node.file_path AS file_path
    """, {"repo_qn": repo_qualified_name})
    
    connected: Dict[str, List[str]] = {}
    for row in results:
        node_labels = row[0]  # labels
        qn = row[1]  # qualified_name
        file_path = row[2]  # file_path
        identifier = qn or file_path or "unknown"
        
        for label in node_labels:
            if label not in connected:
                connected[label] = []
            connected[label].append(identifier)
    
    return connected


def rel_count_by_type(neo4j_client, rel_type: str, repo_qualified_name: str) -> int:
    """
    Count relationships of a specific type connected to a repository.
    
    This function finds any relationships of the specified type that are connected
    to nodes belonging to the given repository.
    
    Args:
        neo4j_client: Neomodel database instance
        rel_type: Type of relationship to count (e.g., 'USES_FEATURE', 'CONTAINS_CODEBASE')
        repo_qualified_name: Repository qualified name to scope the search
        
    Returns:
        Number of relationships of the specified type connected to the repository
    """
    query = f"""
    MATCH (repo:CodeConfluenceGitRepository {{qualified_name: $repo_qn}})
    MATCH (repo)-[*0..]-()-[rel:{rel_type}]-()
    RETURN count(rel) AS c
    """
    results, _ = neo4j_client.cypher_query(query, {"repo_qn": repo_qualified_name})
    return results[0][0] if results else 0


def verify_complete_repository_deletion(neo4j_client, repo_qualified_name: str) -> Dict[str, Any]:
    """
    Comprehensive verification that a repository and all related nodes/relationships are deleted.
    
    Args:
        neo4j_client: Neomodel database instance
        repo_qualified_name: Repository qualified name that should be deleted
        
    Returns:
        Dictionary with verification results and any issues found
    """
    verification_results: Dict[str, Any] = {
        "repository_exists": repo_exists(neo4j_client, repo_qualified_name),
        "connected_nodes": find_nodes_related_to_repository(neo4j_client, repo_qualified_name),
        "node_counts": {},
        "relationship_counts": get_relationship_type_counts(neo4j_client),
        "issues": []
    }
    
    # Check for specific node types that should be cleaned up
    node_labels_to_check = [
        "CodeConfluenceCodebase",
        "CodeConfluencePackage", 
        "CodeConfluenceFile",
        "CodeConfluencePackageManagerMetadata"
    ]
    
    for label in node_labels_to_check:
        count = count_nodes_by_label_and_qualifier(neo4j_client, label, repo_qualified_name)
        verification_results["node_counts"][label] = count
        
        if count > 0:
            verification_results["issues"].append(f"Found {count} residual {label} nodes")
    
    # Check if repository still exists
    if verification_results["repository_exists"]:
        verification_results["issues"].append("Repository node still exists")
    
    # Check for connected nodes
    if verification_results["connected_nodes"]:
        for label, nodes in verification_results["connected_nodes"].items():
            verification_results["issues"].append(f"Found {len(nodes)} connected {label} nodes: {nodes[:5]}...")  # Show first 5
    
    # Check for specific relationship types that should be completely gone
    relationship_types_to_check = [
        "CONTAINS_CODEBASE", "PART_OF_GIT_REPOSITORY", "USES_FRAMEWORK", "USED_BY",
        "CONTAINS_PACKAGE", "PART_OF_PACKAGE", "PART_OF_CODEBASE", "CONTAINS_FILE", 
        "USES_FEATURE", "HAS_PACKAGE_MANAGER_METADATA"
    ]
    
    verification_results["repository_relationship_counts"] = {}
    for rel_type in relationship_types_to_check:
        count = rel_count_by_type(neo4j_client, rel_type, repo_qualified_name)
        verification_results["repository_relationship_counts"][rel_type] = count
        
        if count > 0:
            verification_results["issues"].append(f"Found {count} residual {rel_type} relationships")
    
    return verification_results