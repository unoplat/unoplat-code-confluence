import pytest
import json
from . import NodeSummariser
from data_models.chapi_unoplat_node import Node
from loguru import logger

# Function to load mock data from JSON file
def load_mock_data():
    with open('mock_node.json', 'r') as file:
        return json.load(file)

@pytest.fixture
def node_summariser():
    # Ensure that settings are correctly configured for live API calls
    return NodeSummariser()

def test_summarise_node(node_summariser):
    # Load mock data
    mock_node_data = load_mock_data()
    
    # Create a mock Node object
    mock_node = Node(**mock_node_data)
    
    # Call the method under test
    summarized_node = node_summariser.summarise_node(mock_node)
    #todo: output summary to a external file
    with open('summarised_node.txt', 'w') as file:
         file.write(summarized_node.summary)

    # Assertions to check if the node summary is updated
    # Note: This assertion needs to be adjusted based on expected output from the live API call
    
    assert summarized_node.summary is not None and len(summarized_node.summary) > 0
    

# Run the test
if __name__ == "__main__":
    pytest.main()

