from typing import List
import dspy
from data_models.dspy.dspy_o_function_summary import DspyFunctionSummary
from data_models.dspy.dspy_unoplat_fs_function_subset import DspyUnoplatFunctionSubset
from data_models.dspy.dspy_unoplat_fs_node_subset import DspyUnoplatNodeSubset
from data_models.dspy.dspy_unoplat_node_summary import DspyUnoplatNodeSummary

# ollama_codestral = dspy.OllamaLocal(model='codestral:22b-v0.1-q8_0')
# dspy.configure(lm=ollama_codestral)

ollama_qwen2 = dspy.OllamaLocal(model='qwen2:7b-instruct-q8_0',model_type='text',max_tokens=1000)
dspy.configure(lm=ollama_qwen2)
# ollama_llama_70b = dspy.OllamaLocal(model='llama3:70b-instruct')
# dspy.configure(lm=ollama_llama_70b)


class CodeConfluenceFunctionClassSignature(dspy.Signature):
    """This signature takes in existing summary of a class and function summary of a class one at a time to keep improving final summary"""
    class_existing_summary: str = dspy.InputField(default="Summary:",desc="This will contain existing class summary")
    function_summary: str = dspy.InputField(desc="This will contain current function summary based on which existing class summary has to be improved")
    class_metadata: str = dspy.InputField(desc="This will contain current class metadata")
    final_class_summary: str = dspy.OutputField(desc="This will contain improved concise class summary")
    

class CodeConfluenceClassObjectiveSignature(dspy.Signature):
    """This signature takes in class summary and returns concise objective of the class"""
    final_class_summary: str = dspy.InputField(desc="This will contain concise detailed implementation summary of the class")
    class_objective: str = dspy.OutputField(desc="This will contain concise objective of the class based on implementation summary")

class CodeConfluenceClassModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_class_summary = dspy.ChainOfThought(CodeConfluenceFunctionClassSignature)
        self.generate_class_objective = dspy.ChainOfThought(CodeConfluenceClassObjectiveSignature)

    def forward(self, class_metadata: DspyUnoplatNodeSubset, function_objective_summary_list: List[str]):
        class_summary = ""
        for function_objective in function_objective_summary_list:
            signature_class_summary = self.generate_class_summary(class_existing_summary=class_summary, function_summary=function_objective, class_metadata=class_metadata)
            class_summary = signature_class_summary.final_class_summary
            
        class_objective_signature = self.generate_class_objective(final_class_summary=class_summary)
        dspy_class_summary = DspyUnoplatNodeSummary(NodeObjective=class_objective_signature.class_objective, NodeSummary=class_summary)
        return dspy_class_summary
 
        
        
        

    