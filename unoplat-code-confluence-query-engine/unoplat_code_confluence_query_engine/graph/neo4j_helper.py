
from neo4j import GraphDatabase
import json
from neo4j import Transaction

#TOOD: change to python async driver to make the end-end operation async
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

    def get_existing_codebases(self):
        query = """
        MATCH (cb:Codebase)
        RETURN cb.qualified_name AS codebase_name
        """
        result =  self.run_query(query)
        records: list = []
        for record in result:
            records.append(str(record["codebase_name"]))
        return records

    def get_package_details(self,package_name):
        query = """
        MATCH (p:Package {qualified_name: $package_name})
        RETURN 
            p.qualified_name AS package_name,
            p.objective AS package_objective,
            p.implementation_summary AS package_summary
        """
        return self.run_query(query, package_name=package_name)
    
    def get_class_details(self,class_name):
        query = """
        MATCH (c:Class {qualified_name: $class_name})
        RETURN 
            c.qualified_name AS class_name,
            c.objective AS class_objective,
            c.implementation_summary AS class_summary
        """
        return self.run_query(query, class_name=class_name)
    
    def get_codebase_details(self,codebase_name):   
        query = """
        MATCH (cb:Codebase {qualified_name: $codebase_name})
        RETURN 
            cb.qualified_name AS codebase_name,
            cb.objective AS codebase_objective,
            cb.implementation_summary AS codebase_summary
        """
        return self.run_query(query, codebase_name=codebase_name)

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
    
   #TODO: make the process async 
    def import_json_file(self, file_path, batch_size=100):
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        with self.driver.session() as session:
            # Import nodes
            for i in range(0, len(data["nodes"]), batch_size):
                batch = data["nodes"][i:i+batch_size]
                session.execute_write(self._create_nodes, batch)

            # Import relationships
            for i in range(0, len(data["relationships"]), batch_size):
                batch = data["relationships"][i:i+batch_size]
                session.execute_write(self._create_relationships, batch)
        

        return f"Import completed. Data from {file_path} has been imported to the database."

    def _create_nodes(self, tx: Transaction, nodes):
        for node in nodes:
            labels = ":".join(node["labels"])
            properties = ", ".join([f"{k}: ${k}" for k in node["properties"].keys()])
            query = f"CREATE (n:{labels} {{id: $id, {properties}}})"
            tx.run(query, id=node["id"], **node["properties"])

    def _create_relationships(self, tx: Transaction, relationships):
        for rel in relationships:
            query = f"""
            MATCH (start {{id: $start_id}})
            MATCH (end {{id: $end_id}})
            CREATE (start)-[r:{rel['type']} {{id: $id}}]->(end)
            SET r += $properties
            """
            tx.run(query, 
                   start_id=rel["startNode"], 
                   end_id=rel["endNode"], 
                   id=rel["id"], 
                   properties=rel["properties"])
    
  
    def create_vector_index(self, label: str, property: str, dimension: int = None, similarity_function: str = 'cosine') -> None:
        with self.driver.session() as session:
            query = f"CREATE VECTOR INDEX {label}_{property}_vector_index FOR (n:{label}) ON (n.{property})"
            if dimension is not None:
                query += f" OPTIONS {{indexConfig: {{`vector.dimensions`: {dimension}, `vector.similarity_function`: '{similarity_function}'}}}}"
            try:
                session.run(query)
            except Exception as e:
                if "equivalent index already exists" in str(e):
                    print(f"Vector index for {label}.{property} already exists. Skipping creation.")
                else:
                    raise  # Re-raise the exception if it's not about existing index

    def create_text_index(self, label: str, property: str) -> None:
        with self.driver.session() as session:
            index_name = f"{label.lower()}_{property.lower()}_text_index"
            query = f"CREATE TEXT INDEX {index_name} FOR (n:{label}) ON (n.{property})"
            session.run(query)