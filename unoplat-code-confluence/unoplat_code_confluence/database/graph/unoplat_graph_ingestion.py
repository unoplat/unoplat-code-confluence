from neo4j import GraphDatabase
from typing import Dict, Any
from unoplat_code_confluence.configuration.external_config import AppConfig
from neomodel import config,db

class UnoplatGraphIngestion:
    def __init__(self, app_config: AppConfig):
        uri = app_config.neo4j_uri
        username = app_config.neo4j_username
        password = app_config.neo4j_password
        config.DATABASE_URL = f'bolt://{username}:{password}@{uri.split("://")[-1]}'
        db.set_connection(config.DATABASE_URL)
        
    def close(self):
        db.close_connection()
    
    def create_schema(self):
        db.install_all_labels()

    def create_vector_index(self, label: str, property: str, dimension: int = None, similarity_function: str = 'cosine') -> None:
        query = f"CREATE VECTOR INDEX {property}_vector_index FOR (n:{label}) ON (n.{property})"
        if dimension is not None:
            query += f" OPTIONS {{indexConfig: {{`vector.dimensions`: {dimension}, `vector.similarity_function`: '{similarity_function}'}}}}"
        try:
            # Using neomodel's db object to execute the query
            db.cypher_query(query)
        except Exception as e:
            if "equivalent index already exists" in str(e):
                print(f"Vector index for {label}.{property} already exists. Skipping creation.")
            else:
                raise  # Re-raise the exception if it's not about existing index

    def create_text_index(self, label: str, property: str) -> None:
        index_name = f"{property.lower()}_text_index"
        query = f"CREATE TEXT INDEX {index_name} FOR (n:{label}) ON (n.{property})"
        # Using neomodel's db object to execute the query
        db.cypher_query(query)
