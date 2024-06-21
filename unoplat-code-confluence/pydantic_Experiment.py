import json

from data_models.chapi_unoplat_node import Node
from data_models.dspy.dspy_unoplat_fs_annotation_subset import DspyUnoplatAnnotationSubset
from data_models.dspy.dspy_unoplat_fs_node_subset import DspyUnoplatNodeSubset

def process_node_data():
    try:
        with open('springstarterjava1_codes.json', 'r') as file:
            springstarterjava1_codes = json.load(file)
    except FileNotFoundError:
        print("Error: File 'springstarterjava1_codes.json' not found.")
        springstarterjava1_codes = []
    except json.JSONDecodeError:
        print("Error: File 'springstarterjava1_codes.json' contains invalid JSON.")
        springstarterjava1_codes = []

    node_subsets = []
    function_subsets = []

    for item in springstarterjava1_codes:
        try:
            node = Node(**item)
            node_subset = DspyUnoplatNodeSubset(
                node_name=node.node_name,
                imports=node.imports,
                extend=node.extend,
                multiple_extend=node.multiple_extend,
                fields=node.fields,
                annotations=[DspyUnoplatAnnotationSubset(**annotation.model_dump()) for annotation in node.annotations]
            )
            node_subsets.append(node_subset)
            print(node_subset.node_name)
            print(node.model_dump(mode='json'))
            print("node subset", node_subset.model_dump(mode='json'))
            break
            
            # for func in node.functions:
            #     function_subset = DspyUnoplatFunctionSubset(
            #         name=func.name,
            #         return_type=func.return_type,
            #         annotations=func.annotations,
            #         position=func.position,
            #         local_variables=func.local_variables,
            #         content=func.content,
            #         function_calls=[DspyUnoplatFunctionCallSubset(node_name=call.node_name, function_name=call.function_name, parameters=call.parameters, position=call.position) for call in func.function_calls]
            #     )
            #     function_subsets.append(function_subset)
        except AttributeError as e:
            print(f"Error processing node data: {e}")

    # Optionally, print or process the subsets
    print(node_subsets)
    print(function_subsets)



if __name__ == 'main' :
    process_node_data()