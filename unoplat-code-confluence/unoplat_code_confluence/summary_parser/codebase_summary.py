from typing import List
from unoplat_code_confluence.data_models.chapi_unoplat_codebase import UnoplatCodebase
from unoplat_code_confluence.data_models.chapi_unoplat_package import UnoplatPackage
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_codebase_summary import DspyUnoplatCodebaseSummary
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_function_summary import DspyUnoplatFunctionSummary
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_node_summary import DspyUnoplatNodeSummary
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_package_summary import DspyUnoplatPackageNodeSummary, DspyUnoplatPackageSummary
from unoplat_code_confluence.dspy_class_summary import CodeConfluenceClassModule
from unoplat_code_confluence.dspy_codebase_summary import CodeConfluenceCodebaseModule, CodeConfluenceCodebaseObjectiveSignature
from unoplat_code_confluence.dspy_function_summary import CodeConfluenceFunctionModule
from unoplat_code_confluence.dspy_package_summary import CodeConfluencePackageModule
import dspy
from loguru import logger


class CodebaseSummaryParser:
    
    def __init__(self, codebase: UnoplatCodebase, dspy_pipeline_function: CodeConfluenceFunctionModule, dspy_pipeline_class: CodeConfluenceClassModule,dspy_pipeline_package: CodeConfluencePackageModule,dspy_pipeline_codebase: CodeConfluenceCodebaseModule,llm_config: dict):
        self.codebase = codebase
        self.dspy_pipeline_function = dspy_pipeline_function
        self.dspy_pipeline_class = dspy_pipeline_class
        self.dspy_pipeline_package = dspy_pipeline_package
        self.dspy_pipeline_codebase = dspy_pipeline_codebase
        #TODO: we will be externalise the different llms that can be used at all dspy pipelines and within dspy pipelines once dspy switches to litellm
        self.init_dspy_lm(llm_config)
    
    def init_dspy_lm(self,llm_config: dict):
        #todo define a switch case
        llm_provider = next(iter(llm_config.keys()))
        match llm_provider:
            case "openai":
                dspy.configure(lm=dspy.OpenAI(**llm_config["openai"]),experimental=True)
            case "together":
                dspy.configure(lm=dspy.Together(**llm_config["together"]),experimental=True)
            case "anyscale":
                dspy.configure(lm=dspy.Anyscale(**llm_config["anyscale"]),experimental=True)
            case "anthropic":
                dspy.configure(lm=dspy.Anthropic(**llm_config["anthropic"]),experimental=True)
            


    def parse_codebase(self) -> DspyUnoplatCodebaseSummary:

        unoplat_codebase_summary: DspyUnoplatCodebaseSummary = DspyUnoplatCodebaseSummary()
        unoplat_packages :UnoplatPackage = self.codebase.packages
        unoplat_package_summary: DspyUnoplatPackageSummary = DspyUnoplatPackageSummary()
        
        for package_name, list_node_subset in unoplat_packages.package_dict.items():
            class_summaries: List[DspyUnoplatNodeSummary] = []
            for node in list_node_subset:
                function_summaries :List[DspyUnoplatFunctionSummary] = []
                
                for function in node.functions:
                    function_summary = self.dspy_pipeline_function(function_metadata=function,class_metadata=node).answer
                    dspyUnoplatFunctionSummary: DspyUnoplatFunctionSummary  = DspyUnoplatFunctionSummary(FunctionName=function.name,FunctionSummary=function_summary)
                    function_summaries.append(dspyUnoplatFunctionSummary)
                
                class_summary: DspyUnoplatNodeSummary = self.dspy_pipeline_class(class_metadata=node, function_objective_summary=function_summaries).answer
                class_summaries.append(class_summary)
        
            dspy_pipeline_package_node_summary: DspyUnoplatPackageNodeSummary = self.dspy_pipeline_package(class_summaries).answer
            logger.info(f"Generating package summary for {package_name}")
            unoplat_package_summary.package_summary_dict[package_name] = dspy_pipeline_package_node_summary
        
        # Extract list of DspyUnoplatPackageNodeSummary from unoplat_package_summary
        # Pass the list of DspyUnoplatPackageNodeSummary to dspy_pipeline_codebase

        dspy_codebase_summary = self.dspy_pipeline_codebase(package_objective_dict=unoplat_package_summary.package_summary_dict)

        unoplat_codebase_summary.codebase_summary = dspy_codebase_summary.summary
        unoplat_codebase_summary.codebase_objective = dspy_codebase_summary.answer
        unoplat_codebase_summary.codebase_package = unoplat_package_summary

        #todo: pydantic out to a file of unoplat codebase summary
        return unoplat_codebase_summary

