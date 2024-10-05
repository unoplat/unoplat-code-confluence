from enum import Enum
from typing import Any, Dict, List
from pydantic import BaseModel, ValidationInfo, field_validator, Field

    

class AppConfig(BaseModel):
    sentence_transformer_model: str = Field(default="jinaai/jina-embeddings-v3", description="Name or path of the sentence transformer model")
    neo4j_uri: str = Field(default="bolt://localhost:7687", description="URI of the Neo4j database")
    neo4j_username: str = Field(default="neo4j", description="Username for the Neo4j database")
    neo4j_password: str = Field(default="Ke7Rk7jB:Jn2Uz:", description="Password for the Neo4j database")
    provider_model_dict: Dict[str, Any] = Field(description="Dictionary containing provider and model information"
    )
 