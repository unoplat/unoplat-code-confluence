from loguru import logger as log
from neo4j import GraphDatabase

class Neo4jHelper:
    def __init__(self, uri="bolt://localhost:7687", username="neo4j", password="Ke7Rk7jB:Jn2Uz:"):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        

    def close(self):
        self.driver.close()

    def run_query(self, query, **params):
        with self.driver.session() as session:
            result = session.run(query, **params)
            return list(result)

    def search_similar_nodes(self, vector_index, query_embedding, top_k=5):
        query = f"""
        CALL db.index.vector.queryNodes('{vector_index}', $top_k, $embedding)
        YIELD node, score
        RETURN node.qualified_name AS name, node.objective AS objective, node.implementation_summary AS summary, score
        ORDER BY score DESC
        """
        result = self.run_query(query, embedding=query_embedding, top_k=top_k)
        # Fetch all records before consuming the result
        records = []
        for record in result:
            records.append({
                'name': record['name'],
                'objective': record['objective'],
                'summary': record['summary'],
                'score': record['score']
            })

        
        
        return records
        

       

    def get_function_hierarchy_and_details(self, function_name):
        query = """
        MATCH (f:Method {qualified_name: $function_name})
        OPTIONAL MATCH (f)<-[:CONTAINS]-(c:Class)<-[:CONTAINS]-(p:Package)<-[:CONTAINS]-(cb:Codebase)
        RETURN 
            cb.qualified_name AS codebase_name,
            cb.objective AS codebase_objective,
            cb.implementation_summary AS codebase_summary,
            p.qualified_name AS package_name,
            p.objective AS package_objective,
            p.implementation_summary AS package_summary,
            c.qualified_name AS class_name,
            c.objective AS class_objective,
            c.implementation_summary AS class_summary,
            f.qualified_name AS function_name,
            f.objective AS function_objective,
            f.implementation_summary AS function_summary
        """
        return self.run_query(query, function_name=function_name)
