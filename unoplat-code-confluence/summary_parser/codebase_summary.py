from typing import List
from data_models.chapi_unoplat_codebase import UnoplatCodebase
from data_models.chapi_unoplat_package import UnoplatPackage
from data_models.dspy.dspy_unoplat_function_summary import DspyUnoplatFunctionSummary
from dspy_function_summary import CodeConfluenceFunctionModule


class CodebaseSummaryParser:
    def __init__(self, codebase: UnoplatCodebase, dspy_pipeline_function: CodeConfluenceFunctionModule):
        self.codebase = codebase
        self.dspy_pipeline_function = dspy_pipeline_function

    def parse_codebase(self):
        unoplat_packages :UnoplatPackage = self.codebase.packages
        for node_name, node_subset in unoplat_packages.package_dict.items():
            for node in node_subset:
                function_summaries :List[DspyUnoplatFunctionSummary] = []
                for function in node.functions:
                    function_summary = self.dspy_pipeline_function(function_metadata=function,class_metadata=node)
                    dspyUnoplatFunctionSummary: DspyUnoplatFunctionSummary  = DspyUnoplatFunctionSummary(FunctionName=function.name,FunctionSummary=function_summary)
                    function_summaries.append(dspyUnoplatFunctionSummary)

                