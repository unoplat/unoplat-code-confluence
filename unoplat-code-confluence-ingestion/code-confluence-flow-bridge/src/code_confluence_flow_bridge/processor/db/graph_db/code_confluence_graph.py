# Standard Library
import os

# Third Party
from neomodel import config, db

from src.code_confluence_flow_bridge.models.configuration.settings import EnvironmentSettings


class CodeConfluenceGraph:
    def __init__(self,code_confluence_env: EnvironmentSettings):
        host = code_confluence_env.neo4j_host
        port = code_confluence_env.neo4j_port
        username = code_confluence_env.neo4j_username
        password = code_confluence_env.neo4j_password.get_secret_value()
        if not all([host, port, username, password]):
            raise ValueError("Required environment variables NEO4J_HOST, NEO4J_PORT, NEO4J_USERNAME, NEO4J_PASSWORD must be set")
        config.DATABASE_URL = f'bolt://{username}:{password}@{host}:{port}'
        db.set_connection(config.DATABASE_URL)
        
    def close(self):
        db.close_connection()
    
    def create_schema(self):
        db.install_all_labels()

    