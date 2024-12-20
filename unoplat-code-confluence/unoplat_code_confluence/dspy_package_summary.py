# Standard Library
from typing import Dict, List

# Third Party
import dspy
from loguru import logger

# First Party
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_node_summary import \
    DspyUnoplatNodeSummary
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_package_summary import \
    DspyUnoplatPackageSummary

#TODO: optimise using gpt4 judge and miprov2s

class CodeConfluenceSubPackageSignature(dspy.Signature):
    """This signature takes in existing summary of a root package and sub package summary and refines root_package_existing_summary with new insights without loosing on existing insights and returns root_package_final_summary. """
    root_package_existing_summary: str = dspy.InputField(default="package existing summary:",desc="This will contain existing package summary")
    sub_package_summary: str = dspy.InputField(desc="This will contain summary of the sub package")
    sub_package_name: str = dspy.InputField(desc="This will contain name of the sub package")
    root_package_final_summary: str = dspy.OutputField(desc="This will contain improved concise package summary without loosing on existing details")


class CodeConfluencePackageSignature(dspy.Signature):
    """This signature takes in existing summary of root package and based on class summary of that package one at a time refines root_package_existing_summary with new insights without loosing on any existing details and returns root_package_final_summary. """
    root_package_existing_summary: str = dspy.InputField(default="package existing summary:",desc="This will contain existing package summary")
    root_class_objective: str = dspy.InputField(desc="This will contain current class objective based on which existing package summary has to be enhanced")
    root_package_name: str = dspy.InputField(desc="This will contain name of the package")
    root_package_final_summary: str = dspy.OutputField(desc="This will contain improved concise package summary")
    

class CodeConfluencePackageObjectiveSignature(dspy.Signature):
    """This signature takes in package summary and returns concise package_objective of the package."""
    root_package_summary: str = dspy.InputField(desc="This will contain concise detailed implementation summary of the package")
    root_package_name: str = dspy.InputField(desc="This will contain name of the package")
    root_package_objective: str = dspy.OutputField(desc="This will contain concise objective of the package based on package summary")

class CodeConfluencePackageModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_sub_package_summary = dspy.ChainOfThought(CodeConfluenceSubPackageSignature)
        self.generate_package_summary = dspy.ChainOfThoughtWithHint(CodeConfluencePackageSignature)
        self.generate_package_objective = dspy.ChainOfThoughtWithHint(CodeConfluencePackageObjectiveSignature)
        

    def forward(self, class_objective_list: List[DspyUnoplatNodeSummary],package_name: str,sub_package_summaries: Dict[str,DspyUnoplatPackageSummary]):
        
        package_summary_hint="Enhance the package summary +:"+package_name+" based on class objective. Do not extrapolate or make up anything. Strictly be factual and grounded.While enhancing the package summary do not loose any existing important details by being overly concise."
        package_summary = ""
        
        for sub_package_name,sub_package_summary in sub_package_summaries.items():
            package_summary = self.generate_sub_package_summary(root_package_existing_summary=package_summary,sub_package_summary=sub_package_summary.package_summary,sub_package_name=sub_package_name).root_package_final_summary

        for class_objective in class_objective_list:
            signature_package_summary: CodeConfluencePackageSignature = self.generate_package_summary(root_package_existing_summary=package_summary, root_class_objective=class_objective.node_objective,root_package_name=package_name,hint=package_summary_hint)
            package_summary = signature_package_summary.root_package_final_summary
        
        package_objective_hint = "First capture all highlights from summary and based on highlights generate the package objective for the package by being concise and dnt miss on any details for:"+package_name+". Do not extrapolate or make up anything. Strictly be factual and grounded."
        package_objective_signature: CodeConfluencePackageObjectiveSignature = self.generate_package_objective(root_package_summary=package_summary,root_package_name=package_name,hint=package_objective_hint)
        dspy_package_summary = DspyUnoplatPackageSummary(package_objective=package_objective_signature.root_package_objective,package_summary=package_summary,class_summary=class_objective_list)
        return dspy.Prediction(answer=dspy_package_summary)
 
        
        
        

    
