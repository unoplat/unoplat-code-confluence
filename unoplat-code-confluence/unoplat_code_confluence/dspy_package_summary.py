from typing import Dict, List
import dspy
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_node_summary import DspyUnoplatNodeSummary
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_package_summary import DspyUnoplatPackageNodeSummary
from loguru import logger

#TODO: optimise using gpt4 judge and miprov2s
class CodeConfluencePackageSignature(dspy.Signature):
    """This signature takes in existing summary of a class and function summary of a class one at a time and refines package_existing_summary with new insights and returns final_package_summary. """
    package_existing_summary: str = dspy.InputField(default="package existing summary:",desc="This will contain existing package summary")
    class_objective: str = dspy.InputField(desc="This will contain current class objective based on which existing package summary has to be improved")
    package_name: str = dspy.InputField(desc="This will contain name of the package")
    final_package_summary: str = dspy.OutputField(desc="This will contain improved concise package summary")
    

class CodeConfluencePackageObjectiveSignature(dspy.Signature):
    """This signature takes in package summary and returns concise package_objective of the package."""
    final_package_summary: str = dspy.InputField(desc="This will contain concise detailed implementation summary of the package")
    package_name: str = dspy.InputField(desc="This will contain name of the package")
    package_objective: str = dspy.OutputField(desc="This will contain concise objective of the package based on package summary")

class CodeConfluencePackageModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_package_summary = dspy.ChainOfThoughtWithHint(CodeConfluencePackageSignature)
        self.generate_package_objective = dspy.ChainOfThoughtWithHint(CodeConfluencePackageObjectiveSignature)
        

    def forward(self, class_objective_list: List[DspyUnoplatNodeSummary],package_name: str):
        
        package_summary_hint="Enhance the package summary +:"+package_name+" based on class objective. Do not extrapolate or make up anything. Strictly be factual and grounded.While enhancing the package summary do not loose any existing important details by being overly concise."
        package_summary = ""
        for class_objective in class_objective_list:
            signature_package_summary: CodeConfluencePackageSignature = self.generate_package_summary(package_existing_summary=package_summary, package_name=package_name,class_objective=class_objective.node_objective,hint=package_summary_hint)
            package_summary = signature_package_summary.final_package_summary
        
        package_objective_hint = "First capture all highlights from summary and based on highlights generate the package objective for the package by being concise and dnt miss on any details for:"+package_name+". Do not extrapolate or make up anything. Strictly be factual and grounded."
        class_objective_signature: CodeConfluencePackageObjectiveSignature = self.generate_package_objective(final_package_summary=package_summary,package_name=package_name,hint=package_objective_hint)
        dspy_package_summary = DspyUnoplatPackageNodeSummary(package_objective=class_objective_signature.package_objective,package_summary=package_summary,class_summary=class_objective_list)
        return dspy.Prediction(answer=dspy_package_summary)
 
        
        
        

    