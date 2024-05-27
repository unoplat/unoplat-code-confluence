import json


from litellm import completion

def generate_summary_with_ollama(content):
    # Initialize the LLM client
    # in messages pass example_content as content 
    # append in below content query - summarise the content 

    response = completion(
        model="ollama_chat/llama3:8b-instruct-q8_0", 
        messages=[
            {"role": "system", "content": "User will be passing functions and classes .Your job is to provide only summary and it should not be more than 2 lines. Do not mention anything apart from summary."},
            { "content": content,"role": "user"}], 
    )
    
    return str(response.choices[0].message['content']) 



# Function to safely get a value from a dictionary with a default if the key is not present
def safe_get(data, key, default=''):
    return data.get(key, default)


def add_summaries(data):
    nodes = json.loads(data)
    for node in nodes:
        # Safely retrieve values from each node
        node_name = safe_get(node, 'NodeName', 'Unnamed Node')
        file_path = safe_get(node, 'FilePath', 'Unknown Path')
        
        # Check if the node has 'Content', and generate a summary from it
        if 'Content' in node:
            node_content = node['Content']
            node_summary = generate_summary_with_ollama(node_content)
        else:
            node_summary = f"Node '{node_name}' at path '{file_path}' handles complex schema manipulations without detailed content."
        
        # Add or override the summary at the node level
        node['Summary'] = node_summary
        
        # Iterate through functions if they exist
        for function in node.get('Functions', []):
            # Check if the function has 'Content' and generate a summary from it
            if 'Content' in function:
                function_content = function['Content']
                function_summary = generate_summary_with_ollama(function_content)
            else:
                # If no content, create a basic summary based on what information is available
                function_name = safe_get(function, 'Name', 'Unnamed Function')
                function_summary = f"The function '{function_name}' performs operations without detailed content."

            # Add or override the summary for each function
            function['Summary'] = function_summary
    
    return json.dumps(nodes, indent=4)

# Example usage with error handling and file I/O
try:
    with open("0_codes.json", "r") as file:
        json_data = file.read()
        updated_json = add_summaries(json_data)
        with open("1_codes.json", "w") as outfile:
            outfile.write(updated_json)
except Exception as e:
    print(f"An error occurred: {e}")
