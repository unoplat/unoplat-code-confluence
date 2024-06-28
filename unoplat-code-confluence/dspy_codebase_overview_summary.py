from typing import List
import dspy
from data_models.dspy.dspy_o_function_summary import DspyFunctionSummary
from data_models.dspy.dspy_unoplat_fs_function_subset import DspyUnoplatFunctionSubset
from data_models.dspy.dspy_unoplat_fs_node_subset import DspyUnoplatNodeSubset
from data_models.dspy.dspy_unoplat_node_summary import DspyUnoplatNodeSummary
from data_models.dspy.dspy_unoplat_package_summary import DspyUnoplatPackageNodeSummary, DspyUnoplatPackageSummary

# ollama_codestral = dspy.OllamaLocal(model='codestral:22b-v0.1-f16')
# dspy.configure(lm=ollama_codestral)

# ollama_codestral = dspy.OllamaLocal(model='phi3:14b-medium-4k-instruct-f16')
# dspy.configure(lm=ollama_codestral)


ollama_qwen2 = dspy.OllamaLocal(model='qwen2:7b-text-q8_0',model_type='text',max_tokens=1000)
dspy.configure(lm=ollama_qwen2)

# ollama_qwen2 = dspy.OllamaLocal(model='qwen2:7b-instruct-q8_0',model_type='text',max_tokens=1000)
# dspy.configure(lm=ollama_qwen2)
# ollama_llama_70b = dspy.OllamaLocal(model='llama3:70b-instruct')
# dspy.configure(lm=ollama_llama_70b)


class CodeConfluenceCodebaseSignature(dspy.Signature):
    """This signature takes in existing summary of a codebase and package summary of a package one at a time and returns enhanced final summary of codebase"""
    codebase_existing_summary: str = dspy.InputField(default="package existing summary:",desc="This will contain existing package summary")
    package_objective: str = dspy.InputField(desc="This will contain current package objective based on which existing package summary has to be improved")
    final_codebase_summary: str = dspy.OutputField(desc="This will contain final improved concise codebase summary")
    

class CodeConfluenceCodebaseObjectiveSignature(dspy.Signature):
    """This signature takes in codebase summary and returns concise objective of the codebase"""
    final_codebase_summary: str = dspy.InputField(desc="This will contain concise detailed implementation summary of the codebase")
    codebase_objective: str = dspy.OutputField(desc="This will contain concise objective of the codebase based on detailed codebase summary")

class CodeConfluencePackageModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_codebase_summary = dspy.ChainOfThought(CodeConfluenceCodebaseSignature)
        self.generate_codebase_objective = dspy.ChainOfThought(CodeConfluenceCodebaseObjectiveSignature)
        

    def forward(self, class_objective_list: List[DspyUnoplatPackageSummary]):
        package_summary = ""
        for class_objective in class_objective_list:
            signature_package_summary: CodeConfluencePackageSignature = self.generate_codebase_summary(package_existing_summary=package_summary, class_objective=class_objective.node_objective)
            package_summary = signature_package_summary.final_package_summary
            
        class_objective_signature: CodeConfluencePackageObjectiveSignature = self.generate_package_objective(final_package_summary=package_summary)
        dspy_package_summary = DspyUnoplatPackageNodeSummary(package_objective=class_objective_signature.package_objective,package_summary=package_summary,class_summary=class_objective_list)
        return dspy.Prediction(answer=dspy_package_summary)
 
        
        
        

    