# # Standard Library
# from typing import Dict, List

# # Third Party
# import dspy
# from loguru import logger

# # First Party
# from unoplat_code_confluence.data_models.chapi_unoplat_node import \
#     ChapiUnoplatNode
# from unoplat_code_confluence.data_models.forge_summary.forge_unoplat_function_summary import \
#     DspyUnoplatFunctionSummary
# from unoplat_code_confluence.data_models.forge_summary.forge_unoplat_node_summary import \
#     DspyUnoplatNodeSummary

# #TODO: optimise using gpt4 judge and miprov2

# class CodeConfluenceClassSummarySignature(dspy.Signature):
#     """This signature takes in existing summary of a class and function summary of a class one at a time and returns enhanced final_class_summary."""
#     class_existing_summary: str = dspy.InputField(default="Summary:",desc="This will contain existing class summary")
#     function_summary: str = dspy.InputField(desc="This will contain current function summary based on which existing class summary has to be improved")
#     class_json_schema: str = dspy.InputField(desc="This will contain json schema of the class metadata")
#     class_metadata: str = dspy.InputField(desc="This will contain relevant current class metadata")
#     final_class_summary: str = dspy.OutputField(desc="This will contain improved concise class summary")
    

# class CodeConfluenceClassObjectiveSignature(dspy.Signature):
#     """This signature takes in class summary and returns concise class_objective of the class. Do not include your reasoning in class_objective."""
#     final_class_summary: str = dspy.InputField(desc="This should contain concise detailed implementation summary of the class or in some cases direct content of the class if it is just a data model object.")
#     class_objective: str = dspy.OutputField(desc="This should contain concise objective of the class based on implementation summary in under 2 lines without loosing on any details")

   
# class CodeConfluenceClassModule(dspy.Module):
#     def __init__(self):
#         super().__init__()
#         self.generate_class_summary = dspy.ChainOfThoughtWithHint(CodeConfluenceClassSummarySignature)
#         self.generate_class_objective = dspy.ChainOfThoughtWithHint(CodeConfluenceClassObjectiveSignature)

#     def forward(self, class_metadata: ChapiUnoplatNode, function_objective_summary: List[DspyUnoplatFunctionSummary]):
#         logger.debug(f"Generating class summary for {class_metadata.node_name}")
#         class_summary = ""
    
#         for function_objective in function_objective_summary:
#             signature_class_summary = self.generate_class_summary(class_existing_summary=class_summary, function_summary=function_objective.objective, class_json_schema=class_metadata.model_json_schema(), class_metadata=str(class_metadata.model_dump_json()),hint="Generate the class detailed summary for the class by being concise , factual and grounded.:"+class_metadata.node_name)
#             class_summary = signature_class_summary.final_class_summary
    
#         if class_metadata.node_name is not None:
#             hint="Generate the class objective for the class by being concise and dnt miss on any details.:"+class_metadata.node_name
#         else:
#             hint="Generate the class objective for the class by being concise and dnt miss on any details."
        
#         if len(function_objective_summary) > 0:
#             class_objective_signature = self.generate_class_objective(final_class_summary = class_summary,hint=hint)
#         else:
#             class_objective_signature = self.generate_class_objective(final_class_summary = class_metadata.content,hint=hint)

#         dspy_class_summary = DspyUnoplatNodeSummary(NodeName=class_metadata.node_name,NodeObjective=class_objective_signature.class_objective, NodeSummary=class_summary,FunctionsSummary=function_objective_summary)
        
#         return dspy.Prediction(answer=dspy_class_summary)
 
        
        
        

    