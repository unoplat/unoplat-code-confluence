from typing import List
from data_models.chapi_unoplat_codebase import UnoplatCodebase
from data_models.chapi_unoplat_package import UnoplatPackage
from data_models.dspy.dspy_unoplat_codebase_summary import DspyUnoplatCodebaseSummary
from data_models.dspy.dspy_unoplat_function_summary import DspyUnoplatFunctionSummary
from data_models.dspy.dspy_unoplat_node_summary import DspyUnoplatNodeSummary
from data_models.dspy.dspy_unoplat_package_summary import DspyUnoplatPackageNodeSummary, DspyUnoplatPackageSummary
from dspy_class_summary import CodeConfluenceClassModule
from dspy_codebase_summary import CodeConfluenceCodebaseModule, CodeConfluenceCodebaseObjectiveSignature
from dspy_function_summary import CodeConfluenceFunctionModule
from dspy_package_summary import CodeConfluencePackageModule
from settings.appsettings import AppSettings
import dspy


class CodebaseSummaryParser:
    
    def __init__(self, codebase: UnoplatCodebase, dspy_pipeline_function: CodeConfluenceFunctionModule, dspy_pipeline_class: CodeConfluenceClassModule,dspy_pipeline_package: CodeConfluencePackageModule,dspy_pipeline_codebase: CodeConfluenceCodebaseModule,settings: AppSettings):
        self.codebase = codebase
        self.dspy_pipeline_function = dspy_pipeline_function
        self.dspy_pipeline_class = dspy_pipeline_class
        self.dspy_pipeline_package = dspy_pipeline_package
        self.dspy_pipeline_codebase = dspy_pipeline_codebase
        self.settings: AppSettings = settings
        #TODO: we will be externalise the different llms that can be used at all dspy pipelines and within dspy pipelines once dspy switches to litellm
        self.config = {
            "llm_to_func_questions": dspy.Together(api_key=self.settings.togetherai_api_key,model="zero-one-ai/Yi-34B-Chat",max_tokens=1024),
            "llm_to_class_questions": dspy.Together(api_key=self.settings.togetherai_api_key,model="zero-one-ai/Yi-34B-Chat",max_tokens=1024),
            "llm_to_package_questions": dspy.Together(api_key=self.settings.togetherai_api_key,model="zero-one-ai/Yi-34B-Chat",max_tokens=1024),
            "llm_to_codebase_questions": dspy.Together(api_key=self.settings.togetherai_api_key,model="zero-one-ai/Yi-34B-Chat",max_tokens=1024),
            "llm_to_codebase_summary": dspy.OpenAI(model='gpt-3.5-turbo-16k',api_key=self.settings.openai_api_key)
        }
        self.init_dspy_lm()
    
    def init_dspy_lm(self):
        dspy.configure(lm=self.config["llm_to_codebase_summary"])


    def parse_codebase(self) -> DspyUnoplatCodebaseSummary:
        unoplat_codebase_summary: DspyUnoplatCodebaseSummary = DspyUnoplatCodebaseSummary()
        unoplat_packages :UnoplatPackage = self.codebase.packages
        unoplat_package_summary: DspyUnoplatPackageSummary = DspyUnoplatPackageSummary()
        
        for package_name, list_node_subset in unoplat_packages.package_dict.items():
            class_summaries: List[DspyUnoplatNodeSummary] = []
            for node in list_node_subset:
                function_summaries :List[DspyUnoplatFunctionSummary] = []
                
                for function in node.functions:
                    function_summary = self.dspy_pipeline_function(function_metadata=function,class_metadata=node,llm_config=self.config).answer
                    dspyUnoplatFunctionSummary: DspyUnoplatFunctionSummary  = DspyUnoplatFunctionSummary(FunctionName=function.name,FunctionSummary=function_summary)
                    function_summaries.append(dspyUnoplatFunctionSummary)
                
                class_summary: DspyUnoplatNodeSummary = self.dspy_pipeline_class(class_metadata=node, function_objective_summary=function_summaries,llm_config=self.config).answer
                class_summaries.append(class_summary)
        
            dspy_pipeline_package_node_summary: DspyUnoplatPackageNodeSummary = self.dspy_pipeline_package(class_summaries,llm_config=self.config).answer
            unoplat_package_summary.package_summary_dict[package_name] = dspy_pipeline_package_node_summary
        
        # Extract list of DspyUnoplatPackageNodeSummary from unoplat_package_summary
        # Pass the list of DspyUnoplatPackageNodeSummary to dspy_pipeline_codebase
        dspy_codebase_summary = self.dspy_pipeline_codebase(package_objective_dict=unoplat_package_summary.package_summary_dict,llm_config=self.config)

        unoplat_codebase_summary.codebase_summary = dspy_codebase_summary.summary
        unoplat_codebase_summary.codebase_objective = dspy_codebase_summary.answer
        unoplat_codebase_summary.codebase_package = unoplat_package_summary

        #todo: pydantic out to a file of unoplat codebase summary
        return unoplat_codebase_summary