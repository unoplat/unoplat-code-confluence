


from sentence_transformers import SentenceTransformer
from typing import List
from loguru import logger as log

#todo: change to oss with permissive license rerankers based on hugging face mteb 
class UnoplatRerankEmbedding:
    def __init__(self, sentence_transformer_model: str):
        self.sentence_rerank_model = SentenceTransformer(sentence_transformer_model, trust_remote_code=True).cuda()
        self.query_prompt_name = "s2p_query"  # Change to "s2s_query" for sentence-to-sentence tasks

    def generate_rerank_embedding(self, query: List[str], documents: List[str]):
        # Encode the queries with the s2p query prompt
        query_embeddings = self.sentence_rerank_model.encode(query, prompt_name=self.query_prompt_name)
        # Encode the documents (no prompt needed)
        doc_embeddings = self.sentence_rerank_model.encode(documents)
        similarities = self.sentence_rerank_model.similarity(query_embeddings, doc_embeddings)
        log.info(f"Similarity Matrix: {similarities}")
        return similarities

