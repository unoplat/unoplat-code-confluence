from sentence_transformers import SentenceTransformer
from typing import List

class UnoplatEmbeddingGenerator:
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name, trust_remote_code=True)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        task = 'retrieval.query'
        return self.model.encode(texts, task=task).tolist()
   
    def generate_embeddings_for_single_text(self, text: str) -> List[float]:
        task = 'retrieval.query'
        return self.model.encode(text, task=task, convert_to_tensor=False)