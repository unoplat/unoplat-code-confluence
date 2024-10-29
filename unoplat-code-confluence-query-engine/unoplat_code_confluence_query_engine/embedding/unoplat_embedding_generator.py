from sentence_transformers import SentenceTransformer
from typing import List

#TODO: this code is duplicated across ingestion and query engine. We will not refactor
 # as we move the embedding part to infrastructure such as vespa/marqo
class UnoplatEmbeddingGenerator:
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name, trust_remote_code=True)
        self.dimensions = self.model.get_sentence_embedding_dimension()
        
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        task = 'retrieval.query'
        return self.model.encode(texts, task=task).tolist()
   
    def generate_embeddings_for_single_text(self, text: str) -> List[float]:
        task = 'retrieval.query'
        return self.model.encode(text, task=task, convert_to_tensor=False)
    
    def get_dimensions(self) -> int:
        return self.dimensions
