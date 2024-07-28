import dspy
from unoplat_code_confluence.data_models.dspy.dspy_o_function_summary import DspyFunctionSummary
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_fs_function_subset import DspyUnoplatFunctionSubset
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_fs_node_subset import DspyUnoplatNodeSubset
from loguru import logger

#TODO: optimise using gpt4 judge and miprov2/textgrad
class CodeConfluenceFunctionSummary(dspy.Signature):
    """This signature takes in metadata about function in a class and returns unoplat_function_summary with all important details."""
    chapi_function_metadata: str = dspy.InputField(desc="This will contain function metadata regarding the function")
    unoplat_function_summary: str = dspy.OutputField(desc="This will contain function summary based on function metadata.")

class CodeConfluenceFunctionCallSummary(dspy.Signature):
    """This signature takes in existing summary of function and function call metadata (one at a time) and returns enhanced unoplat_function_final_summary."""
    unoplat_function_existing_summary: str = dspy.InputField(default="Function Summary:",desc="This will contain existing function summary which can be empty during first iteration.")
    chapi_function_call: str = dspy.InputField(desc="This will contain function call being made out of the function and its metadata.")
    unoplat_function_final_summary: str = dspy.OutputField(desc="Refined and restructured final summary enhanced based on existing function summary, function metadata and function call metadata.")

class CodeConfluenceFunctionSummaryWithClassSignature(dspy.Signature):
    """This signature takes in chapi_class_metadata and unoplat_function_existing_summary and returns enhanced final summary unoplat_function_final_summary."""
    chapi_class_metadata: str = dspy.InputField(desc="This will contain class metadata in json")
    unoplat_function_existing_summary: str = dspy.InputField(desc="This will contain existing function summary without class metadata")
    unoplat_function_final_summary: str = dspy.OutputField(desc="This will contain final function summary enhanced using class metadata covering all important details")

class CodeConfluenceFunctionObjectiveSignature(dspy.Signature):
    """This signature takes in function_implementation description and returns function_objective of the function in a concise and accurate manner."""
    function_implementation: str = dspy.InputField(desc="This will contain concise detailed implementation description of the function")
    function_objective: str = dspy.OutputField(desc="This will contain concise objective of the function based on implementation summary within 3 lines without missing on any details.")

class CodeConfluenceFunctionModule(dspy.Module):
    def __init__(self):
        super().__init__()
        # TODO: change to typed chain of thought post dspy signature optimisers
        self.generate_function_summary = dspy.TypedChainOfThought(CodeConfluenceFunctionSummary)
        self.generate_function_call_summary = dspy.TypedChainOfThought(CodeConfluenceFunctionCallSummary)
        self.generate_function_summary_with_class_metadata = dspy.TypedPredictor(CodeConfluenceFunctionSummaryWithClassSignature)
        self.generate_function_objective = dspy.TypedPredictor(CodeConfluenceFunctionObjectiveSignature)

    def forward(self, function_metadata: DspyUnoplatFunctionSubset, class_metadata: DspyUnoplatNodeSubset):
        logger.debug(f"Generating function summary for {function_metadata.name}")
        
        class_subset = str(class_metadata.model_dump_json())
        function_subset = str(function_metadata.model_dump_json()) 
        
        function_summary = self.generate_function_summary(chapi_function_metadata=function_subset).unoplat_function_summary
       
        for function_call in function_metadata.function_calls:
            current_function_call = str(function_call.model_dump_json())
            
            if function_call.node_name == function_metadata.name:
                continue
            else:
                function_summary = self.generate_function_call_summary(unoplat_function_existing_summary=function_summary, chapi_function_call=current_function_call).unoplat_function_final_summary

        code_confluence_function_summary = self.generate_function_summary_with_class_metadata( chapi_class_metadata=class_subset, unoplat_function_existing_summary=function_summary).unoplat_function_final_summary

        code_confluence_function_objective = self.generate_function_objective(function_implementation=code_confluence_function_summary)        

        dspy_function_summary = DspyFunctionSummary(Objective=code_confluence_function_objective.function_objective, ImplementationSummary=code_confluence_function_summary)

        return dspy.Prediction(answer=dspy_function_summary)
    
