from typing import Dict, List
import dspy
from data_models.dspy.dspy_unoplat_node_summary import DspyUnoplatNodeSummary
from data_models.dspy.dspy_unoplat_package_summary import DspyUnoplatPackageNodeSummary



#TODO: optimise using gpt4 judge and miprov2s
class CodeConfluencePackageSignature(dspy.Signature):
    """This signature takes in existing summary of a class and function summary of a class one at a time and returns final enhanced summary"""
    package_existing_summary: str = dspy.InputField(default="package existing summary:",desc="This will contain existing package summary")
    class_objective: str = dspy.InputField(desc="This will contain current class objective based on which existing package summary has to be improved")
    final_package_summary: str = dspy.OutputField(desc="This will contain improved concise package summary")
    

class CodeConfluencePackageObjectiveSignature(dspy.Signature):
    """This signature takes in package summary and returns concise objective of the package"""
    final_package_summary: str = dspy.InputField(desc="This will contain concise detailed implementation summary of the package")
    package_objective: str = dspy.OutputField(desc="This will contain concise objective of the package based on package summary")

class CodeConfluencePackageModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_package_summary = dspy.ChainOfThought(CodeConfluencePackageSignature)
        self.generate_package_objective = dspy.ChainOfThought(CodeConfluencePackageObjectiveSignature)
        

    def forward(self, class_objective_list: List[DspyUnoplatNodeSummary],llm_config: Dict):
        package_summary = ""
        for class_objective in class_objective_list:
            signature_package_summary: CodeConfluencePackageSignature = self.generate_package_summary(package_existing_summary=package_summary, class_objective=class_objective.node_objective)
            package_summary = signature_package_summary.final_package_summary
        
            
        class_objective_signature: CodeConfluencePackageObjectiveSignature = self.generate_package_objective(final_package_summary=package_summary)
        dspy_package_summary = DspyUnoplatPackageNodeSummary(package_objective=class_objective_signature.package_objective,package_summary=package_summary,class_summary=class_objective_list)
        return dspy.Prediction(answer=dspy_package_summary)
 
        
        
        

    