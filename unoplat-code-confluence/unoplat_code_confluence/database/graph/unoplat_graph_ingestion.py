from neo4j import GraphDatabase
from typing import Dict, Any

from unoplat_code_confluence.configuration.external_config import AppConfig

class UnoplatGraphIngestion:
    def __init__(self, config: AppConfig):
        uri = config.neo4j_uri
        username = config.neo4j_username
        password = config.neo4j_password
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()

    def merge_node(self, label: str, properties: Dict[str, Any]) -> None:
        with self.driver.session() as session:
            # Construct the MERGE clause with explicit properties
            merge_clause = f"MERGE (n:{label} {{"
            merge_clause += ", ".join([f"{key}: $props.{key}" for key in properties.keys()])
            merge_clause += "})"
            
            # Construct the SET clause to update the properties
            set_clause = "SET " + ", ".join([f"n.{key} = $props.{key}" for key in properties.keys()])
        
            # Combine the MERGE and SET clauses
            query = f"{merge_clause} {set_clause}"
        
            session.run(query, props=properties)

    def merge_relationship(self, start_node_label: str, start_node_property: str, 
                           end_node_label: str, end_node_property: str, 
                           relationship_type: str) -> None:
        query = f"""
        MATCH (a:{start_node_label} {{qualified_name: $start_value}}), (b:{end_node_label} {{qualified_name: $end_value}})
        MERGE (a)-[:{relationship_type}]->(b)
        """
        with self.driver.session() as session:
            session.run(query, start_value=start_node_property, end_value=end_node_property)

    def create_vector_index(self, label: str, property: str, dimension: int = None, similarity_function: str = 'cosine') -> None:
        with self.driver.session() as session:
            query = f"CREATE VECTOR INDEX {label}_{property}_vector_index FOR (n:{label}) ON (n.{property})"
            if dimension is not None:
                query += f" OPTIONS {{indexConfig: {{`vector.dimensions`: {dimension}, `vector.similarity_function`: '{similarity_function}'}}}}"
            session.run(query)

    def create_text_index(self, label: str, property: str) -> None:
        with self.driver.session() as session:
            index_name = f"{label.lower()}_{property.lower()}_text_index"
            query = f"CREATE TEXT INDEX {index_name} FOR (n:{label}) ON (n.{property})"
            session.run(query)

