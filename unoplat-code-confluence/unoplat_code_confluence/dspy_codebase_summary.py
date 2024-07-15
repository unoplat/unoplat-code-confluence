from typing import Dict
import dspy
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_package_summary import DspyUnoplatPackageNodeSummary



#TODO: optimise using gpt4 judge and miprov2
class CodeConfluenceCodebaseSignature(dspy.Signature):
    """This signature takes in existing summary of a codebase and package summary of a package one at a time and refines codebase_existing_summary with new insights and returns final_codebase_summary as enhanced final summary of codebase."""
    codebase_existing_summary: str = dspy.InputField(alias="codebase_existing_summary",default="codebase existing summary:",desc="This will contain existing codebase summary")
    package_objective: str = dspy.InputField(alias="package_objective",desc="This will contain current package objective based on which final_codebase_summary has to be improved")
    final_codebase_summary: str = dspy.OutputField(alias="final_codebase_summary",desc="This will contain final improved concise codebase summary")
    

class CodeConfluenceCodebaseObjectiveSignature(dspy.Signature):
    """This signature takes in codebase summary and returns codebase_objective as concise objective of the codebase. Do not include your reasoning in codebase_objective."""
    final_codebase_summary: str = dspy.InputField(alias="final_codebase_summary",desc="This will contain concise detailed implementation summary of the codebase")
    codebase_objective: str = dspy.OutputField(alias="codebase_objective",desc="This will contain concise objective of the codebase based on detailed codebase summary")

class CodeConfluenceCodebaseModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_codebase_summary = dspy.ChainOfThoughtWithHint(CodeConfluenceCodebaseSignature)
        self.generate_codebase_objective = dspy.ChainOfThoughtWithHint(CodeConfluenceCodebaseObjectiveSignature)
        

    def forward(self, package_objective_dict: Dict[str, DspyUnoplatPackageNodeSummary]):

        codebase_summary = ""

        for _,package_metadata in package_objective_dict.items():
            signature_package_summary: CodeConfluenceCodebaseSignature = self.generate_codebase_summary(codebase_existing_summary=codebase_summary, package_objective=package_metadata.package_objective,hint="Generate the codebase summary for the codebase by being concise , factual and grounded")
            codebase_summary = signature_package_summary.final_codebase_summary
            
            
        codebase_objective_signature: CodeConfluenceCodebaseObjectiveSignature = self.generate_codebase_objective(final_codebase_summary=codebase_summary,hint="Generate the codebase objective for the codebase by being concise and dnt miss on any details")
        
        
        return dspy.Prediction(answer=codebase_objective_signature.codebase_objective,summary=signature_package_summary.final_codebase_summary)
 
        
        
        

    