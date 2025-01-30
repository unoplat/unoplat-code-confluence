# Standard Library
from typing import Any, Dict

# Third Party
from neo4j import GraphDatabase


class Neo4jConnector:
    def __init__(self, uri: str, username: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()

    def create_node(self, label: str, properties: Dict[str, Any]) -> None:
        with self.driver.session() as session:
            session.run(f"MERGE (n:{label} $props)", props=properties)

    def create_relationship(self, start_node_label: str, start_node_property: str, 
                            end_node_label: str, end_node_property: str, 
                            relationship_type: str) -> None:
        query = f"""
        MATCH (a:{start_node_label}), (b:{end_node_label})
        WHERE a.{start_node_property} = $start_value AND b.{end_node_property} = $end_value
        CREATE (a)-[:{relationship_type}]->(b)
        """
        with self.driver.session() as session:
            session.run(query, start_value=start_node_property, end_value=end_node_property)
