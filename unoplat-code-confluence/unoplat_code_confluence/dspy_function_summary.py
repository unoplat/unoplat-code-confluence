from typing import Dict
import dspy
from unoplat_code_confluence.data_models.dspy.dspy_o_function_summary import DspyFunctionSummary
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_fs_function_subset import DspyUnoplatFunctionSubset
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_fs_node_subset import DspyUnoplatNodeSubset
from loguru import logger

#TODO: optimise using gpt4 judge and miprov2/textgrad

class CodeConfluenceFunctionSummarySignature(dspy.Signature):
    """This signature takes in class metadata and function metadata with function content and returns objective and descriptive function summaries."""
    dspy_class_subset: str = dspy.InputField(desc="This will contain class metadata in json")
    dspy_function_subset: str = dspy.InputField(desc="This will contain function metadata with function content in json")
    function_implementation: str = dspy.OutputField(desc="This will contain concise detailed implementation summary of the function")


class CodeConfluenceFunctionObjectiveSignature(dspy.Signature):
    """This signature takes in function implementation description and returns objective of the function in a concise and accurate manner."""
    function_implementation: str = dspy.InputField(desc="This will contain concise detailed implementation description of the function")
    function_objective: str = dspy.OutputField(desc="This will contain concise objective of the function based on implementation summary within 3 lines without missing on any details.")

class CodeConfluenceFunctionModule(dspy.Module):
    def __init__(self):
        super().__init__()
        # TODO: change to typed chain of thought post dspy signature optimisers
        self.generate_function_summary = dspy.ChainOfThought(CodeConfluenceFunctionSummarySignature)
        self.generate_function_objective = dspy.ChainOfThought(CodeConfluenceFunctionObjectiveSignature)

    def forward(self, function_metadata: DspyUnoplatFunctionSubset, class_metadata: DspyUnoplatNodeSubset,llm_config: Dict):
        logger.info(f"Generating function summary for {function_metadata.name}")
        class_subset = str(class_metadata.model_dump_json())

        function_subset = str(function_metadata.model_dump_json())

        code_confluence_function_summary = self.generate_function_summary( dspy_class_subset = class_subset, dspy_function_subset= function_subset)

        code_confluence_function_objective = self.generate_function_objective(function_implementation=code_confluence_function_summary.function_implementation)        

        dspy_function_summary = DspyFunctionSummary(Objective=code_confluence_function_objective.function_objective, ImplementationSummary=code_confluence_function_summary.function_implementation)

        return dspy.Prediction(answer=dspy_function_summary)

    