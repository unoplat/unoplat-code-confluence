from typing import List
import dspy
from data_models.dspy.dspy_unoplat_package_summary import DspyUnoplatPackageSummary



class CodeConfluenceCodebaseSignature(dspy.Signature):
    """This signature takes in existing summary of a codebase and package summary of a package one at a time and returns final_codebase_summary as enhanced final summary of codebase"""
    codebase_existing_summary: str = dspy.InputField(default="codebase existing summary:",desc="This will contain existing codebase summary")
    package_objective: str = dspy.InputField(desc="This will contain current package objective based on which existing codebase summary has to be improved")
    final_codebase_summary: str = dspy.OutputField(desc="This will contain final improved concise codebase summary")
    

class CodeConfluenceCodebaseObjectiveSignature(dspy.Signature):
    """This signature takes in codebase summary and returns codebase_objective as concise objective of the codebase"""
    final_codebase_summary: str = dspy.InputField(desc="This will contain concise detailed implementation summary of the codebase")
    codebase_objective: str = dspy.OutputField(desc="This will contain concise objective of the codebase based on detailed codebase summary")

class CodeConfluenceCodebaseModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_codebase_summary = dspy.ChainOfThought(CodeConfluenceCodebaseSignature)
        self.generate_codebase_objective = dspy.ChainOfThought(CodeConfluenceCodebaseObjectiveSignature)
        

    def forward(self, package_objective_list: List[DspyUnoplatPackageSummary]):
        codebase_summary = ""
        for package_objective in package_objective_list:
            signature_package_summary: CodeConfluenceCodebaseSignature = self.generate_codebase_summary(codebase_existing_summary=codebase_summary, package_objective=package_objective.package_objective)
            codebase_summary = signature_package_summary.final_codebase_summary
            print(codebase_summary)
            
        codebase_objective_signature: CodeConfluenceCodebaseObjectiveSignature = self.generate_codebase_objective(final_codebase_summary=codebase_summary)
        
        
        return dspy.Prediction(answer=codebase_objective_signature.codebase_objective,summary=signature_package_summary.final_codebase_summary)
 
        
        
        

    