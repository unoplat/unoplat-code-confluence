from typing import List
from data_models.chapi_unoplat_codebase import UnoplatCodebase
from data_models.chapi_unoplat_package import UnoplatPackage
from data_models.dspy.dspy_unoplat_function_summary import DspyUnoplatFunctionSummary
from data_models.dspy.dspy_unoplat_node_summary import DspyUnoplatNodeSummary
from dspy_class_summary import CodeConfluenceClassModule
from dspy_function_summary import CodeConfluenceFunctionModule


class CodebaseSummaryParser:
    def __init__(self, codebase: UnoplatCodebase, dspy_pipeline_function: CodeConfluenceFunctionModule, dspy_pipeline_class: CodeConfluenceClassModule):
        self.codebase = codebase
        self.dspy_pipeline_function = dspy_pipeline_function
        self.dspy_pipeline_class = dspy_pipeline_class

    def parse_codebase(self):
        unoplat_packages :UnoplatPackage = self.codebase.packages
        for package_name, list_node_subset in unoplat_packages.package_dict.items():
            class_summaries: List[DspyUnoplatNodeSummary] = []
            for node in list_node_subset:
                function_summaries :List[DspyUnoplatFunctionSummary] = []
                for function in node.functions:
                    function_summary = self.dspy_pipeline_function(function_metadata=function,class_metadata=node)
                    dspyUnoplatFunctionSummary: DspyUnoplatFunctionSummary  = DspyUnoplatFunctionSummary(FunctionName=function.name,FunctionSummary=function_summary)
                    function_summaries.append(dspyUnoplatFunctionSummary)
                
                function_objectives = [summary.function_summary.objective for summary in function_summaries]
                class_summary: DspyUnoplatNodeSummary = self.dspy_pipeline_class(class_metadata=node, function_objective_summary_list=function_objectives)
                class_summary.functions_summary = function_summaries
                class_summary.node_name = node.node_name
                class_summaries.append(class_summary)


                  

                