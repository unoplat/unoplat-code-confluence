import dspy
from data_models.dspy.dspy_o_function_summary import DspyFunctionSummary
from data_models.dspy.dspy_unoplat_fs_function_subset import DspyUnoplatFunctionSubset
from data_models.dspy.dspy_unoplat_fs_node_subset import DspyUnoplatNodeSubset

# ollama_codestral = dspy.OllamaLocal(model='codestral:22b-v0.1-q8_0')
# dspy.configure(lm=ollama_codestral)

ollama_qwen2 = dspy.OllamaLocal(model='qwen2:7b-instruct-q8_0',model_type='text',max_tokens=1000)
dspy.configure(lm=ollama_qwen2)
# ollama_llama_70b = dspy.OllamaLocal(model='llama3:70b-instruct')
# dspy.configure(lm=ollama_llama_70b)


class CodeConfluenceFunctionSummarySignature(dspy.Signature):
    """This signature contains class metadata and function metadata with function content and returns objective and descriptive function summaries."""
    dspy_class_subset: str = dspy.InputField(desc="This will contain class metadata in json")
    dspy_function_subset: str = dspy.InputField(desc="This will contain function metadata with function content in json")
    function_implementation: str = dspy.OutputField(desc="This will contain concise detailed implementation summary of the function")


class CodeConfluenceFunctionObjectiveSignature(dspy.Signature):
    function_implementation: str = dspy.InputField(desc="This will contain concise detailed implementation summary of the function")
    function_objective: str = dspy.OutputField(desc="This will contain concise objective of the function based on implementation summary")

class CodeConfluenceFunctionModule(dspy.Module):
    def __init__(self):
        super().__init__()
        # TODO: change to typed chain of thought post dspy signature optimisers
        self.generate_function_summary = dspy.ChainOfThought(CodeConfluenceFunctionSummarySignature)
        self.generate_function_objective = dspy.ChainOfThought(CodeConfluenceFunctionObjectiveSignature)

    def forward(self, function_metadata: DspyUnoplatFunctionSubset, class_metadata: DspyUnoplatNodeSubset):
        class_subset = str(class_metadata.model_dump_json())
        function_subset = str(function_metadata.model_dump_json())
        code_confluence_function_summary = self.generate_function_summary( dspy_class_subset = class_subset, dspy_function_subset= function_subset)
        dspy_function_summary = DspyFunctionSummary(Objective=code_confluence_function_summary.function_objective, ImplementationSummary=code_confluence_function_summary.function_implementation)
        return dspy_function_summary

    