from neo4j import GraphDatabase
import json

# Replace these credentials with your Neo4j database info
uri = "bolt://localhost:7687"
username = "neo4j"
password = "Ke7Rk7jB:Jn2Uz:"

driver = GraphDatabase.driver(uri, auth=(username, password))

def export_graph_to_json():
    with driver.session() as session:
        # Query for all nodes and their properties
        nodes_query = """
        MATCH (n)
        RETURN elementId(n) as id, labels(n) as labels, properties(n) as properties
        """
        nodes_result = session.run(nodes_query)

        # Query for all relationships and their properties
        relationships_query = """
        MATCH (start)-[r]->(end)
        RETURN id(r) as id, type(r) as type, properties(r) as properties, 
               elementId(start) as startNode, elementId(end) as endNode
        """
        relationships_result = session.run(relationships_query)

        # Build the JSON structure
        data = {"nodes": [], "relationships": []}

        # Process nodes
        for record in nodes_result:
            node = {
                "id": record["id"],
                "labels": record["labels"],
                "properties": record["properties"]
            }
            data["nodes"].append(node)

        # Process relationships
        for record in relationships_result:
            relationship = {
                "id": record["id"],
                "type": record["type"],
                "properties": record["properties"],
                "startNode": record["startNode"],
                "endNode": record["endNode"]
            }
            data["relationships"].append(relationship)

        # Output to JSON file
        with open("textgrad_graph_export.json", "w") as f:
            json.dump(data, f, indent=4)

        print("Export completed. JSON saved as textgrad_graph_export.json.")

# Run the export
export_graph_to_json()

# Close the driver connection
driver.close()