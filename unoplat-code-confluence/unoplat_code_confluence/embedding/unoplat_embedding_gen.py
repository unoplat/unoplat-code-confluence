# Standard Library
from typing import List

# Third Party
from sentence_transformers import SentenceTransformer

# First Party
from unoplat_code_confluence.configuration.external_config import AppConfig


class UnoplatEmbeddingGenerator:
    def __init__(self, config: AppConfig):
        self.model = SentenceTransformer(config.sentence_transformer_model, trust_remote_code=True)
        self.dimensions = self.model.get_sentence_embedding_dimension()

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        task = 'retrieval.query'
        return self.model.encode(texts, task=task).tolist()
   
    def generate_embeddings_for_single_text(self, text: str) -> List[float]:
        task = 'retrieval.query'
        return self.model.encode(text, task=task).tolist()
    
    def get_dimensions(self) -> int:
        return self.dimensions

