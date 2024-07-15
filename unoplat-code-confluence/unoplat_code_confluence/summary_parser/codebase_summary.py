from typing import List
from unoplat_code_confluence.configuration.external_config import AppConfig
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
    
    def __init__(self, codebase: UnoplatCodebase, dspy_pipeline_function: CodeConfluenceFunctionModule, dspy_pipeline_class: CodeConfluenceClassModule,dspy_pipeline_package: CodeConfluencePackageModule,dspy_pipeline_codebase: CodeConfluenceCodebaseModule,app_config: AppConfig):
        self.codebase = codebase
        self.dspy_pipeline_function = dspy_pipeline_function
        self.dspy_pipeline_class = dspy_pipeline_class
        self.dspy_pipeline_package = dspy_pipeline_package
        self.dspy_pipeline_codebase = dspy_pipeline_codebase
        #TODO: we will be externalise the different llms that can be used at all dspy pipelines and within dspy pipelines once dspy switches to litellm
        self.init_dspy_lm(app_config.llm_provider_config)
        
    
    def init_dspy_lm(self,llm_config: dict):
        #todo define a switch case
        llm_provider = next(iter(llm_config.keys()))
        match llm_provider:
            case "openai":
                openai_provider = dspy.OpenAI(**llm_config["openai"])
                dspy.configure(lm=openai_provider,experimental=True)
            case "together":
                together_provider = dspy.Together(**llm_config["together"])
                dspy.configure(lm=together_provider,experimental=True)
            case "anyscale":
                anyscale_provider = dspy.Anyscale(**llm_config["anyscale"])
                dspy.configure(lm=anyscale_provider,experimental=True)
            case "awsanthropic":
                awsanthropic_provider = dspy.AWSAnthropic(**llm_config["awsanthropic"])
                dspy.configure(lm=awsanthropic_provider,experimental=True)
            case "ollama":
                ollama_provider = dspy.OllamaLocal(**llm_config["ollama"])
                dspy.configure(lm=ollama_provider,experimental=True) 
            case "cohere":
                cohere_provider = dspy.Cohere(**llm_config["cohere"])
                dspy.configure(lm=cohere_provider,experimental=True)
                       
                


    def parse_codebase(self) -> DspyUnoplatCodebaseSummary:

        unoplat_codebase_summary: DspyUnoplatCodebaseSummary = DspyUnoplatCodebaseSummary()
        unoplat_packages :UnoplatPackage = self.codebase.packages
        unoplat_package_summary: DspyUnoplatPackageSummary = DspyUnoplatPackageSummary()
        
        for package_name, list_node_subset in unoplat_packages.package_dict.items():
            class_summaries: List[DspyUnoplatNodeSummary] = []
            for node in list_node_subset:
                function_summaries :List[DspyUnoplatFunctionSummary] = []
                
                for function in node.functions:
                    if function.name is not None:
                        function_summary = self.dspy_pipeline_function(function_metadata=function,class_metadata=node).answer
                        dspyUnoplatFunctionSummary: DspyUnoplatFunctionSummary  = DspyUnoplatFunctionSummary(FunctionName=function.name,FunctionSummary=function_summary)
                        function_summaries.append(dspyUnoplatFunctionSummary)
                
                class_summary: DspyUnoplatNodeSummary = self.dspy_pipeline_class(class_metadata=node, function_objective_summary=function_summaries).answer
                class_summaries.append(class_summary)
        
            dspy_pipeline_package_node_summary: DspyUnoplatPackageNodeSummary = self.dspy_pipeline_package(class_summaries,package_name).answer
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

