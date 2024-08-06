import asyncio
from collections import deque
from typing import Dict, List
from unoplat_code_confluence.configuration.external_config import AppConfig
from unoplat_code_confluence.data_models.chapi_unoplat_codebase import UnoplatCodebase
from unoplat_code_confluence.data_models.chapi_unoplat_package import UnoplatPackage
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_codebase_summary import DspyUnoplatCodebaseSummary
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_fs_function_subset import DspyUnoplatFunctionSubset
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_fs_node_subset import DspyUnoplatNodeSubset
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_function_summary import DspyUnoplatFunctionSummary
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_node_summary import DspyUnoplatNodeSummary
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_package_summary import DspyUnoplatPackageSummary
from unoplat_code_confluence.dspy_class_summary import CodeConfluenceClassModule
from unoplat_code_confluence.dspy_codebase_summary import CodeConfluenceCodebaseModule, CodeConfluenceCodebaseObjectiveSignature
from unoplat_code_confluence.dspy_function_summary import CodeConfluenceFunctionModule
from unoplat_code_confluence.dspy_package_summary import CodeConfluencePackageModule
import dspy
from loguru import logger
from progiter import ProgIter
from progiter.manager import ProgressManager



class CodebaseSummaryParser:
    
    def __init__(self, codebase: UnoplatCodebase, dspy_pipeline_function: CodeConfluenceFunctionModule, dspy_pipeline_class: CodeConfluenceClassModule,dspy_pipeline_package: CodeConfluencePackageModule,dspy_pipeline_codebase: CodeConfluenceCodebaseModule,app_config: AppConfig):
        self.codebase = codebase
        self.dspy_pipeline_function: CodeConfluenceFunctionModule = dspy_pipeline_function
        self.dspy_pipeline_class: CodeConfluenceClassModule = dspy_pipeline_class
        self.dspy_pipeline_package: CodeConfluencePackageModule = dspy_pipeline_package
        self.dspy_pipeline_codebase: CodeConfluenceCodebaseModule = dspy_pipeline_codebase
        #TODO: we will be externalise the different llms that can be used at all dspy pipelines and within dspy pipelines once dspy switches to litellm
        self.provider_list =self.init_dspy_lm(app_config.llm_provider_config,app_config.parallisation)
        
    
    def init_dspy_lm(self,llm_config: dict,parallisation: int):
        #todo define a switch case
        llm_provider = next(iter(llm_config.keys()))
        self.provider_list: dspy.LM = []
        match llm_provider:
            case "openai":
                openai_provider = dspy.OpenAI(**llm_config["openai"])
                dspy.configure(lm=openai_provider,experimental=True)
                if parallisation > 1:
                    self.provider_list = [dspy.OpenAI(**llm_config["openai"]) for _ in range(parallisation)]
                
            case "together":
                together_provider = dspy.Together(**llm_config["together"])
                dspy.configure(lm=together_provider,experimental=True)
                if parallisation > 1:
                    self.provider_list = [dspy.Together(**llm_config["together"]) for _ in range(parallisation)]
            case "anyscale":
                anyscale_provider = dspy.Anyscale(**llm_config["anyscale"])
                dspy.configure(lm=anyscale_provider,experimental=True)
                if parallisation > 1:
                    self.provider_list = [dspy.Anyscale(**llm_config["anyscale"]) for _ in range(parallisation)]
            case "awsanthropic":
                awsanthropic_provider = dspy.AWSAnthropic(**llm_config["awsanthropic"])
                dspy.configure(lm=awsanthropic_provider,experimental=True)
                if parallisation > 1:
                    self.provider_list = [dspy.AWSAnthropic(**llm_config["awsanthropic"]) for _ in range(parallisation)]
            case "ollama":
                ollama_provider = dspy.OllamaLocal(**llm_config["ollama"])
                dspy.configure(lm=ollama_provider,experimental=True) 
                if parallisation > 1:
                    self.provider_list = [dspy.OllamaLocal(**llm_config["ollama"]) for _ in range(parallisation)]
            case "cohere":
                cohere_provider = dspy.Cohere(**llm_config["cohere"])
                dspy.configure(lm=cohere_provider,experimental=True)
                if parallisation > 1:
                    self.provider_list = [dspy.Cohere(**llm_config["cohere"]) for _ in range(parallisation)]
            case _:
                raise ValueError(f"Invalid LLM provider: {llm_provider}")
        return self.provider_list
                
    def parse_codebase(self) -> DspyUnoplatCodebaseSummary:
        
        

        unoplat_codebase_summary = DspyUnoplatCodebaseSummary()
        
        root_packages: Dict[str,UnoplatPackage] = self.codebase.packages

        root_package_summaries = self.process_packages(root_packages,self.provider_list)
        

        try:
            dspy_codebase_summary = self.dspy_pipeline_codebase(package_objective_dict=root_package_summaries)
        except Exception as e:
            logger.error(f"Error generating codebase summary: {e}")
            logger.exception("Traceback:")

        unoplat_codebase_summary.codebase_summary = dspy_codebase_summary.summary
        unoplat_codebase_summary.codebase_objective = dspy_codebase_summary.answer
        unoplat_codebase_summary.codebase_package = root_package_summaries

        #todo: pydantic out to a file of unoplat codebase summary
        return unoplat_codebase_summary

    def count_total_packages(self, packages: Dict[str, UnoplatPackage],provider_list: List[dspy.LM]) -> int:
        total = 0
        stack = list(packages.values())
        while stack:
            package = stack.pop()
            total += 1
            stack.extend(package.sub_packages.values())
        return total

    def process_packages(self, packages: Dict[str,UnoplatPackage]) -> Dict[str,DspyUnoplatPackageSummary]:
        package_summaries: Dict[str, DspyUnoplatPackageSummary] = {}
        stack = deque([(name, package, True) for name, package in packages.items()])
        processed = set()
        memo = {}
        
        total_packages = self.count_total_packages(packages)

        
        pman = ProgressManager(backend='rich')
        
        with pman:
            outer_prog = pman.progiter(range(total_packages), desc='Processing packages', verbose=2)
            outer_prog.begin()

            while stack:
                package_name, package, is_root = stack.pop()
                logger.debug("Current package popped from stack: {}",package_name)

                if package_name in processed:
                    continue
                
                sub_package_summaries: Dict[str, DspyUnoplatPackageSummary] = {}
                all_sub_packages_processed = True

                for sub_name, sub_package in package.sub_packages.items():
                    

                    if sub_name not in processed:
                        stack.append((package_name, package, is_root))
                        logger.debug("Adding current package {} to stack",package_name)
                        stack.append((sub_name, sub_package, False))
                        logger.debug("Adding sub package {} to stack",sub_name)
                        all_sub_packages_processed = False
                        break

                if not all_sub_packages_processed:
                    continue

                # Process current package
                if package_name in memo:
                    package_summary = memo[package_name]
                else:
                    class_summaries = self.process_classes(package.node_subsets,package_name,pman=pman,provider_list=self.provider_list)
                    for sub_name in package.sub_packages:
                        if sub_name in memo:
                            logger.debug("Sub package {} already processed, adding to sub_package_summaries",sub_name)
                            sub_package_summaries[sub_name] = memo[sub_name]

                    try:
                        logger.debug("Generating package summary for {}",package_name)
                        package_summary = self.dspy_pipeline_package(
                            package_name=package_name,
                            class_objective_list=class_summaries,
                            sub_package_summaries=sub_package_summaries
                        ).answer

                        package_summary_object = DspyUnoplatPackageSummary(
                            package_objective=package_summary.package_objective,
                            package_summary=package_summary.package_summary,
                            class_summary=class_summaries,
                            sub_package_summaries=sub_package_summaries
                        )
                        memo[package_name] = package_summary_object
                    except Exception as e:
                        logger.error(f"Error generating package summary for {package_name}: {e}")
                        logger.exception("Traceback:")
                        continue

                if is_root:
                    logger.debug("Adding root package {} to package_summaries",package_name)
                    package_summaries[package_name] = package_summary_object
                
                processed.add(package_name)
                outer_prog.update(1)
            
            return package_summaries
        
    
    async def process_classes_async(self, classes: List[DspyUnoplatNodeSubset],package_name: str,pman: ProgressManager,provider_list: List[dspy.LM]) -> List[DspyUnoplatNodeSummary]:
          class_summaries = []
          
          async with asyncio.TaskGroup() as tg:
              for node,lm in zip(classes,provider_list):
                  task = tg.create_task(self.process_single_class(node, package_name, pman, lm))
                  
          for task in tg.tasks:
          return class_summaries
    
    
    async def process_single_class(self, node: DspyUnoplatNodeSubset, package_name: str, pman: ProgressManager, provider_list: List[dspy.LM]) -> DspyUnoplatNodeSummary:
        try:
            function_summaries = await self.process_functions(node.functions, node, pman)
            class_summary = await self.dspy_pipeline_class(class_metadata=node, function_objective_summary=function_summaries).answer
            return class_summary
        except Exception as e:
            logger.error(f"Error generating class summary for {node}: {e}")
            logger.exception("Traceback:")
            return None

    async def process_functions(self, functions: List[DspyUnoplatFunctionSubset], node: DspyUnoplatNodeSubset, pman: ProgressManager) -> List[DspyUnoplatFunctionSummary]:
        function_summaries = []
        for function in functions:
            try:
                function_summary = await self.dspy_pipeline_function(function_metadata=function, class_metadata=node).answer
                function_summaries.append(DspyUnoplatFunctionSummary(FunctionName=function.name, FunctionSummary=function_summary))
            except Exception as e:
                logger.error(f"Error generating function summary for {function.name}: {e}")
                logger.exception("Traceback:")
        return function_summaries

    def process_classes(self, classes: List[DspyUnoplatNodeSubset],package_name: str,pman: ProgressManager,provider_list: List[dspy.LM]) -> List[DspyUnoplatNodeSummary]:
        class_summaries: List[DspyUnoplatNodeSummary] = []
        
        class_prog  = pman.progiter(iterable = classes, desc=f"Processing classes of {package_name}", verbose=2,total=len(classes))
        
        for node in class_prog:
            function_summaries = self.process_functions(node.functions,node,pman=pman)
            
            try:
                class_summary = self.dspy_pipeline_class(class_metadata=node, function_objective_summary=function_summaries).answer
                class_summaries.append(class_summary)
            except Exception as e:
                logger.error(f"Error generating class summary for {node}: {e}")
                logger.exception("Traceback:")
        
            
        return class_summaries        


    def process_functions(self,functions: List[DspyUnoplatFunctionSubset],node: DspyUnoplatNodeSubset,pman: ProgressManager) -> List[DspyUnoplatFunctionSummary]:
        function_summaries: List[DspyUnoplatFunctionSummary] = []
        
        
        
        function_prog = pman.progiter(iterable =functions, desc=f"Processing functions of {node.node_name}", verbose=2,total=len(functions))
        
            
        for function in function_prog:
            if function.name is not None:
                try:
                    function_summary = self.dspy_pipeline_function(function_metadata=function,class_metadata=node).answer
                    dspyUnoplatFunctionSummary: DspyUnoplatFunctionSummary  = DspyUnoplatFunctionSummary(FunctionName=function.name,FunctionSummary=function_summary)
                    function_summaries.append(dspyUnoplatFunctionSummary)
                    function_prog.update(1)
                except Exception as e:
                    logger.error(f"Error generating function summary for {function.name}: {e}")
                    logger.exception("Traceback:")
        
        

        return function_summaries             
           
                    


