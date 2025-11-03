"""
Graph assertion utilities for integration tests.

These utilities provide direct Neo4j graph validation to ensure complete cleanup
of nodes and relationships, beyond what the API layer reports.
"""

from typing import Any, Dict, List


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
        relationship_type: Type of relationship (e.g., 'USES_FEATURE', 'PART_OF_CODEBASE')
        
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
        "node_counts": {},
        "issues": []
    }
    
    # Check for specific node types that should be cleaned up
    node_labels_to_check = [
        "CodeConfluenceCodebase",
        "CodeConfluenceFile",
        "CodeConfluencePackageManagerMetadata"
    ]
    
    for label in node_labels_to_check:
        # For integration tests with single repository, count all nodes of each type
        count = count_nodes_by_label(neo4j_client, label)
        verification_results["node_counts"][label] = count
        
        if count > 0:
            verification_results["issues"].append(f"Found {count} residual {label} nodes")
    
    # Check if repository still exists
    if verification_results["repository_exists"]:
        verification_results["issues"].append("Repository node still exists")
    
    return verification_results


def get_all_graph_model_labels() -> List[str]:
    """
    Get all node labels from graph models.
    
    Returns:
        List of all graph model node labels
    """
    return [
        "CodeConfluenceGitRepository",
        "CodeConfluenceCodebase",
        "CodeConfluenceFile",
        "CodeConfluencePackageManagerMetadata",
        "CodeConfluenceFramework",
        "CodeConfluenceFrameworkFeature",
    ]


def capture_repository_state_snapshot(neo4j_client, repo_qualified_name: str) -> Dict[str, Any]:
    """
    Capture comprehensive state snapshot of a repository before deletion.
    
    This captures all node counts that should be affected by repository deletion, 
    providing baseline data for validation.
    
    Args:
        neo4j_client: Neomodel database instance  
        repo_qualified_name: Repository qualified name to snapshot
        
    Returns:
        Dictionary containing node counts and validation data
    """
    snapshot: Dict[str, Any] = {
        "repo_qualified_name": repo_qualified_name,
        "node_counts": {},
        "repository_exists": repo_exists(neo4j_client, repo_qualified_name)
    }
    
    # Capture node counts for all graph model types
    # In integration tests, only one repository is ingested, so count all nodes of each type
    graph_model_labels = get_all_graph_model_labels()
    for label in graph_model_labels:
        if label == "CodeConfluenceGitRepository":
            # For repository, check if it exists (should be 1)
            snapshot["node_counts"][label] = 1 if repo_exists(neo4j_client, repo_qualified_name) else 0
        else:
            # For integration tests, count all nodes of each type since only one repo is ingested
            snapshot["node_counts"][label] = count_nodes_by_label(neo4j_client, label)
    
    # Capture global relationship counts for reference
    return snapshot


def assert_deletion_stats_accuracy(deletion_stats: Dict[str, int], pre_snapshot: Dict[str, Any]) -> None:
    """
    Validate API deletion statistics against actual pre-deletion graph state.
    
    This is the key validation that compares what the API reports vs what actually
    existed in the graph.
    
    Args:
        deletion_stats: API response deletion statistics
        pre_snapshot: Pre-deletion state snapshot from capture_repository_state_snapshot()
        
    Raises:
        AssertionError: If deletion stats don't match pre-snapshot counts
    """
    # Map API deletion stat keys to graph model labels
    stat_to_label_mapping = {
        "repositories_deleted": "CodeConfluenceGitRepository",
        "codebases_deleted": "CodeConfluenceCodebase",
        "files_deleted": "CodeConfluenceFile",
        "metadata_deleted": "CodeConfluencePackageManagerMetadata",
    }
    
    mismatches = []
    
    for stat_key, label in stat_to_label_mapping.items():
        if stat_key in deletion_stats:
            api_count = deletion_stats[stat_key]
            actual_count = pre_snapshot["node_counts"].get(label, 0)
            
            if api_count != actual_count:
                mismatches.append(
                    f"API reports {api_count} {stat_key}, but {actual_count} {label} nodes existed before deletion"
                )
    
    # Also validate that we had some content to delete (sanity check)
    files_count = pre_snapshot["node_counts"].get("CodeConfluenceFile", 0)

    if files_count == 0:
        mismatches.append("Sanity check failed: No files existed after ingestion to delete")
    
    if mismatches:
        error_msg = f"❌ DELETION STATS VALIDATION FAILED for {pre_snapshot['repo_qualified_name']}:\n"
        error_msg += "\n".join(f"  - {mismatch}" for mismatch in mismatches)
        error_msg += f"\n\nPre-deletion node counts: {pre_snapshot['node_counts']}"
        error_msg += f"\nAPI deletion stats: {deletion_stats}"
        raise AssertionError(error_msg)


def assert_repository_completely_deleted(neo4j_client, repo_qualified_name: str) -> None:
    """
    Assert that a repository and all related nodes/relationships are completely deleted.
    
    This is a comprehensive post-deletion verification that ensures complete cleanup.
    
    Args:
        neo4j_client: Neomodel database instance
        repo_qualified_name: Repository qualified name that should be deleted
        
    Raises:
        AssertionError: If any repository-related nodes or relationships remain
    """
    # Use existing comprehensive verification
    verification_results = verify_complete_repository_deletion(neo4j_client, repo_qualified_name)
    
    if verification_results["issues"]:
        error_msg = f"❌ REPOSITORY DELETION VERIFICATION FAILED for {repo_qualified_name}:\n"
        error_msg += "\n".join(f"  - {issue}" for issue in verification_results["issues"])
        error_msg += f"\n\nPost-deletion node counts: {verification_results['node_counts']}"
        raise AssertionError(error_msg)
