from typing import List
import dspy
from data_models.dspy.dspy_o_function_summary import DspyFunctionSummary
from data_models.dspy.dspy_unoplat_fs_function_subset import DspyUnoplatFunctionSubset
from data_models.dspy.dspy_unoplat_fs_node_subset import DspyUnoplatNodeSubset
from data_models.dspy.dspy_unoplat_function_summary import DspyUnoplatFunctionSummary
from data_models.dspy.dspy_unoplat_node_summary import DspyUnoplatNodeSummary


class CodeConfluenceClassSummarySignature(dspy.Signature):
    """This signature takes in existing summary of a class and function summary of a class one at a time and returns enhanced final summary."""
    class_existing_summary: str = dspy.InputField(default="Summary:",desc="This will contain existing class summary")
    function_summary: str = dspy.InputField(desc="This will contain current function summary based on which existing class summary has to be improved")
    class_metadata: str = dspy.InputField(desc="This will contain current class metadata")
    final_class_summary: str = dspy.OutputField(desc="This will contain improved concise class summary")
    

class CodeConfluenceClassObjectiveSignature(dspy.Signature):
    """This signature takes in class summary and returns concise objective of the class"""
    final_class_summary: str = dspy.InputField(desc="This should contain concise detailed implementation summary of the class or in some cases direct content of the class if it is just a data model object")
    class_objective: str = dspy.OutputField(desc="This should contain concise objective of the class based on implementation summary in under 2 lines without loosing on any details")

   
class CodeConfluenceClassModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_class_summary = dspy.ChainOfThought(CodeConfluenceClassSummarySignature)
        self.generate_class_objective = dspy.ChainOfThought(CodeConfluenceClassObjectiveSignature)

    def forward(self, class_metadata: DspyUnoplatNodeSubset, function_objective_summary: List[DspyUnoplatFunctionSummary]):
        class_summary = ""
        
        for function_objective in function_objective_summary:
            signature_class_summary = self.generate_class_summary(class_existing_summary=class_summary, function_summary=function_objective.function_summary.objective, class_metadata=str(class_metadata.model_dump_json()))
            class_summary = signature_class_summary.final_class_summary
        
        print("class summary",class_summary)
        
        if len(function_objective_summary) > 0:
            class_objective_signature = self.generate_class_objective(final_class_summary = class_summary)
        else:
            class_objective_signature = self.generate_class_objective(final_class_summary = class_metadata.content)
        print("class objective",class_objective_signature.class_objective) 
        dspy_class_summary = DspyUnoplatNodeSummary(NodeName=class_metadata.node_name,NodeObjective=class_objective_signature.class_objective, NodeSummary=class_summary,FunctionsSummary=function_objective_summary)
        
        return dspy.Prediction(answer=dspy_class_summary)
 
        
        
        

    