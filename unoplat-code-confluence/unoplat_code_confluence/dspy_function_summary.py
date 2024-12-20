# Third Party
import dspy
from loguru import logger

# First Party
from unoplat_code_confluence.data_models.chapi_unoplat_function import \
    ChapiUnoplatFunction
from unoplat_code_confluence.data_models.chapi_unoplat_node import \
    ChapiUnoplatNode


#TODO: optimise using gpt4 judge and miprov2/textgrad
class CodeConfluenceFunctionSummary(dspy.Signature):
    """This signature takes in metadata about function in a class and returns unoplat_function_summary with all important details."""
    function_json_schema: str = dspy.InputField(desc="This will contain json schema of the function metadata")
    chapi_function_metadata: str = dspy.InputField(desc="This will contain relevant function metadata regarding the function")
    unoplat_function_summary: str = dspy.OutputField(desc="This will contain function summary based on function metadata.")

class CodeConfluenceFunctionCallSummary(dspy.Signature):
    """This signature takes in existing summary of function and function call metadata (one at a time) and returns enhanced unoplat_function_final_summary."""
    function_call_json_schema: str = dspy.InputField(desc="This will contain json schema of the function call metadata")
    unoplat_function_existing_summary: str = dspy.InputField(default="Function Summary:",desc="This will contain existing function summary which can be empty during first iteration.")
    chapi_function_call: str = dspy.InputField(desc="This will contain function call being made out of the function and its relevant metadata.")
    unoplat_function_final_summary: str = dspy.OutputField(desc="Refined and restructured final summary enhanced based on existing function summary, function metadata and function call metadata.")

class CodeConfluenceFunctionSummaryWithClassSignature(dspy.Signature):
    """This signature takes in chapi_class_metadata and unoplat_function_existing_summary and returns enhanced final summary unoplat_function_final_summary."""
    class_json_schema: str = dspy.InputField(desc="This will contain json schema of the class metadata")
    chapi_class_metadata: str = dspy.InputField(desc="This will contain relevant class metadata in json")
    unoplat_function_existing_summary: str = dspy.InputField(desc="This will contain existing function summary without class metadata")
    unoplat_function_final_summary: str = dspy.OutputField(desc="This will contain final function summary enhanced using class metadata covering all important details")

class CodeConfluenceFunctionObjectiveSignature(dspy.Signature):
    """This signature takes in function_implementation description and returns function_objective of the function in a concise and accurate manner."""
    function_implementation: str = dspy.InputField(desc="This will contain concise detailed implementation description of the function")
    function_objective: str = dspy.OutputField(desc="This will contain concise objective of the function based on implementation summary within 3 lines without missing on any details.")

class CodeConfluenceFunctionModule(dspy.Module):
    def __init__(self):
        super().__init__()
        # TODO: change to typed chain of thought post dspy signature optimisers and also improve the summarisation part
        self.generate_function_summary = dspy.TypedChainOfThought(CodeConfluenceFunctionSummary)
        self.generate_function_call_summary = dspy.TypedChainOfThought(CodeConfluenceFunctionCallSummary)
        self.generate_function_summary_with_class_metadata = dspy.TypedPredictor(CodeConfluenceFunctionSummaryWithClassSignature)
        self.generate_function_objective = dspy.TypedPredictor(CodeConfluenceFunctionObjectiveSignature)

    def forward(self, function_metadata: ChapiUnoplatFunction, class_metadata: ChapiUnoplatNode):
        logger.debug(f"Generating function summary for {function_metadata.name} present in class {class_metadata.node_name}")
        
        class_subset = str(class_metadata.model_dump_json(exclude_unset=True))
        function_subset = str(function_metadata.model_dump_json(exclude_unset=True)) 
        
        function_summary = self.generate_function_summary(function_json_schema=function_subset.model_json_schema(),chapi_function_metadata=function_subset).unoplat_function_summary
       
        for function_call in function_metadata.function_calls:
            current_function_call = str(function_call.model_dump_json())
            
            if function_call.node_name == function_metadata.name:
                continue
            else:
                function_summary = self.generate_function_call_summary(function_call_json_schema=current_function_call.model_json_schema(), unoplat_function_existing_summary=function_summary, chapi_function_call=current_function_call).unoplat_function_final_summary

        code_confluence_function_summary = self.generate_function_summary_with_class_metadata( class_json_schema=class_subset.model_json_schema(), chapi_class_metadata=class_subset, unoplat_function_existing_summary=function_summary).unoplat_function_final_summary

        code_confluence_function_objective = self.generate_function_objective(function_implementation=code_confluence_function_summary).function_objective       
     
        return dspy.Prediction(objective=code_confluence_function_objective, implementation_summary=code_confluence_function_summary)
    
