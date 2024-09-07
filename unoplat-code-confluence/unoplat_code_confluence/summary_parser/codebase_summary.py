import asyncio
from collections import deque
import datetime
from itertools import cycle
import sys
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
        self.json_output = app_config.json_output
        self.codebase_name = app_config.codebase_name

    def init_dspy_lm(self,llm_config: dict,parallisation: int):
        #todo define a switch case
        llm_provider = next(iter(llm_config.keys()))
        self.provider_list: dspy.LM = []
        match llm_provider:
            case "openai":
                openai_provider = dspy.OpenAI(**llm_config["openai"])
                dspy.configure(lm=openai_provider, experimental=True)
                self.provider_list = [openai_provider]
                if parallisation and parallisation > 1:
                    self.provider_list.extend([dspy.OpenAI(**llm_config["openai"]) for _ in range(parallisation - 1)])
                
            case "together":
                together_provider = dspy.Together(**llm_config["together"])
                dspy.configure(lm=together_provider, experimental=True)
                self.provider_list = [together_provider]
                if parallisation and parallisation > 1:
                    self.provider_list.extend([dspy.Together(**llm_config["together"]) for _ in range(parallisation - 1)])
            
            case "anyscale":
                anyscale_provider = dspy.Anyscale(**llm_config["anyscale"])
                dspy.configure(lm=anyscale_provider, experimental=True)
                self.provider_list = [anyscale_provider]
                if parallisation and parallisation > 1:
                    self.provider_list.extend([dspy.Anyscale(**llm_config["anyscale"]) for _ in range(parallisation - 1)])
            
            case "awsanthropic":
                awsanthropic_provider = dspy.AWSAnthropic(**llm_config["awsanthropic"])
                dspy.configure(lm=awsanthropic_provider, experimental=True)
                self.provider_list = [awsanthropic_provider]
                if parallisation and parallisation > 1:
                    self.provider_list.extend([dspy.AWSAnthropic(**llm_config["awsanthropic"]) for _ in range(parallisation - 1)])
            
            case "ollama":
                ollama_provider = dspy.OllamaLocal(**llm_config["ollama"])
                dspy.configure(lm=ollama_provider, experimental=True) 
                self.provider_list = [ollama_provider]
                if parallisation and parallisation > 1:
                    self.provider_list.extend([dspy.OllamaLocal(**llm_config["ollama"]) for _ in range(parallisation - 1)])
            
            case "cohere":
                cohere_provider = dspy.Cohere(**llm_config["cohere"])
                dspy.configure(lm=cohere_provider, experimental=True)
                self.provider_list = [cohere_provider]
                if parallisation and parallisation > 1:
                    self.provider_list.extend([dspy.Cohere(**llm_config["cohere"]) for _ in range(parallisation - 1)])
            case _:
                raise ValueError(f"Invalid LLM provider: {llm_provider}")
        return self.provider_list
                
    async def parse_codebase(self) -> DspyUnoplatCodebaseSummary:
        
        unoplat_codebase_summary = DspyUnoplatCodebaseSummary()
        
        root_packages: Dict[str,UnoplatPackage] = self.codebase.packages

        root_package_summaries = await self.process_packages(root_packages)

        try:
            dspy_codebase_summary = self.dspy_pipeline_codebase(package_objective_dict=root_package_summaries)
        except Exception as e:
            logger.error(f"Error generating codebase summary: {e}")
            logger.exception("Traceback:")
            sys.exit(1)
            
        unoplat_codebase_summary.codebase_summary = dspy_codebase_summary.summary
        unoplat_codebase_summary.codebase_objective = dspy_codebase_summary.answer
        unoplat_codebase_summary.codebase_package = root_package_summaries

        # if json_output is true, then write to a json file
        if self.json_output:
            json_unoplat_codebase_summary = unoplat_codebase_summary.model_dump_json()
            # write to file
            current_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f"{self.codebase_name}_{current_timestamp}.json", "w") as f:
                f.write(json_unoplat_codebase_summary)

        # write to md file
        #todo: pydantic out to a file of unoplat codebase summary
        return unoplat_codebase_summary

    async def count_total_packages(self, packages: Dict[str, UnoplatPackage]) -> int:
        total = 0
        stack = list(packages.values())
        while stack:
            package = stack.pop()
            total += 1
            stack.extend(package.sub_packages.values())
        return total

    async def process_packages(self, packages: Dict[str,UnoplatPackage]) -> Dict[str,DspyUnoplatPackageSummary]:
        package_summaries: Dict[str, DspyUnoplatPackageSummary] = {}
        stack = deque([(name, package, True) for name, package in packages.items()])
        processed = set()
        memo = {}
        
        total_packages = await self.count_total_packages(packages)

        
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
                    class_summaries = await self.process_classes_async(package.node_subsets,package_name,pman=pman,provider_list=self.provider_list)
                    for sub_name in package.sub_packages:
                        if sub_name in memo:
                            logger.debug("Sub package {} already processed, adding to sub_package_summaries",sub_name)
                            sub_package_summaries[sub_name] = memo[sub_name]

                    try:
                        logger.debug("Generating package summary for {}",package_name)
                        package_summary =  self.dspy_pipeline_package(
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
        
    
    async def process_batch(self, batch: List[DspyUnoplatNodeSubset], package_name: str, pman: ProgressManager, lm_cycle: cycle) -> List[DspyUnoplatNodeSummary]:
        tasks = []
        async with asyncio.TaskGroup() as tg:
            for node in batch:
                
                try:
                    lm = next(lm_cycle)
                    task = tg.create_task(self.process_single_class_wrapper(node, package_name, pman, lm))
                    tasks.append(task)
                except Exception as e:
                    logger.error(f"Error creating task for {node.node_name}: {e}")
                    logger.exception("Traceback:")
        return await self.collect_batch_results(tasks)

    async def collect_batch_results(self, tasks: List[asyncio.Task]) -> List[DspyUnoplatNodeSummary]:
        batch_results = []
        for task in tasks:
            try:
                result = await task
                if result is not None:
                    batch_results.append(result)
            except Exception as e:
                logger.error(f"Error collecting batch result: {e}")
                logger.exception("Traceback:")
        return batch_results            

    

    async def process_classes_async(self, classes: List[DspyUnoplatNodeSubset],package_name: str,pman: ProgressManager,provider_list: List[dspy.LM]) -> List[DspyUnoplatNodeSummary]:
        class_summaries = []
        concurrency = len(provider_list)
        lm_cycle = cycle(provider_list)

        for i in range(0, len(classes), concurrency):
            batch = classes[i:i+concurrency]
            batch_summaries = await self.process_batch(batch, package_name, pman, lm_cycle)
            class_summaries.extend(batch_summaries)

        return class_summaries
    
    async def process_single_class_wrapper(self, node: DspyUnoplatNodeSubset, package_name: str, pman: ProgressManager, lm: dspy.LM) -> DspyUnoplatNodeSummary:
        return await asyncio.to_thread(self.process_single_class, node, package_name, pman, lm)

    
    def process_single_class(self, node: DspyUnoplatNodeSubset, package_name: str, pman: ProgressManager,  lm: dspy.LM) -> DspyUnoplatNodeSummary:
        try:
            with dspy.context(lm=lm):
                function_summaries =  self.process_functions(node.functions, node, pman)
                class_summary =  self.dspy_pipeline_class(class_metadata=node, function_objective_summary=function_summaries).answer
                return class_summary
        except Exception as e:
            logger.error(f"Error processing class {node.node_name}: {e}")
            logger.exception("Traceback:")
            return None


    def process_functions(self, functions: List[DspyUnoplatFunctionSubset], node: DspyUnoplatNodeSubset, pman: ProgressManager) -> List[DspyUnoplatFunctionSummary]:
        function_summaries = []
        for function in functions:
            if function.name:
                try:
                    function_summary =  self.dspy_pipeline_function(function_metadata=function, class_metadata=node).answer
                    function_summaries.append(DspyUnoplatFunctionSummary(FunctionName=function.name, FunctionSummary=function_summary))
                except Exception as e:
                    logger.error(f"Error generating function summary for {function.name}: {e}")
                    logger.exception("Traceback:")
        return function_summaries

 

      
           
                    

    