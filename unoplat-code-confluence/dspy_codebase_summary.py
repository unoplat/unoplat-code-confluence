
import dspy

class CodeConfluenceCodebaseSignature(dspy.Signature):
    """This signature takes in existing summary of a codebase and package objective of a package one at a time to keep improving final package summary"""
    codebase_existing_summary: str = dspy.InputField(default="package existing summary:",desc="This will contain existing package summary")
    package_objective: str = dspy.InputField(desc="This will contain current package objective based on which existing codebase summary has to be improved")
    final_codebase_summary: str = dspy.OutputField(desc="This will contain improved concise codebase summary")
    

class CodeConfluenceCodebaseObjectiveSignature(dspy.Signature):
    """This signature takes in package summary and returns concise objective of the package"""
    final_package_summary: str = dspy.InputField(desc="This will contain concise detailed implementation summary of the package")
    package_objective: str = dspy.OutputField(desc="This will contain concise objective of the package based on package summary")

class CodeConfluencePackageModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_package_summary = dspy.ChainOfThought(CodeConfluenceCodebaseSignature)
        self.generate_package_objective = dspy.ChainOfThought(CodeConfluenceCodebaseObjectiveSignature)

    def forward(self, class_objective_list: List[DspyUnoplatNodeSummary]):
        package_summary = ""
        for class_objective in class_objective_list:
            signature_package_summary: CodeConfluencePackageSignature = self.generate_package_summary(package_existing_summary=package_summary, class_objective=class_objective.node_objective)
            package_summary = signature_package_summary.final_package_summary
            
        class_objective_signature: CodeConfluencePackageObjectiveSignature = self.generate_package_objective(final_package_summary=package_summary)
        dspy_package_summary = DspyUnoplatPackageNodeSummary(package_objective=class_objective_signature.package_objective,package_summary=package_summary,class_summary=class_objective_list)
        return dspy_package_summary
