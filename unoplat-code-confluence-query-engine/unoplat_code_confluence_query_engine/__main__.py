import os
import dspy
from dspy.retrieve.neo4j_rm import Neo4jRM


qwen_dspy = dspy.OllamaLocal(model='qwen2.5:72b-instruct-fp16',base_url='http://206.1.58.174:11434')
os.environ["NEO4J_URI"] = 'bolt://localhost:7687'
os.environ["NEO4J_USERNAME"] = 'neo4j'
os.environ["NEO4J_PASSWORD"] = 'Ke7Rk7jB:Jn2Uz:'


retriever_model = Neo4jRM(
    index_name="vector",
    text_node_property="text"
)

results = retriever_model("Explore the significance of quantum computing", k=3)

for passage in results:
    print("Document:", passage, "\n")