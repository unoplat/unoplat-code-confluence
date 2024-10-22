from unoplat_code_confluence_query_engine.graph.neo4j_helper import Neo4jHelper
from unoplat_code_confluence_query_engine.embedding.unoplat_embedding_generator import UnoplatEmbeddingGenerator
from unoplat_code_confluence_query_engine.models.confluence_class import CodeConfluenceClass
from unoplat_code_confluence_query_engine.unoplat_dspy.intent_detection_module import CodeConfluenceIntentDetectionModule
from unoplat_code_confluence_query_engine.unoplat_dspy.user_query_final_response import CodeConfluenceUserQueryResponseModule
from unoplat_code_confluence_query_engine.unoplat_dspy.user_query_based_rererank_module import CodeConfluenceUserQueryReRankModule
from unoplat_code_confluence_query_engine.models.confluence_func_hiearchy import CodeConfluenceFunctionHiearchySub
from unoplat_code_confluence_query_engine.configuration.external_config import AppConfig
import dspy
import time
from typing import List
from unoplat_code_confluence_query_engine.helper.json_loader import JsonLoader
from textual import log
from unoplat_code_confluence_query_engine.models.confluence_codebase import CodeConfluenceCodebase
from unoplat_code_confluence_query_engine.models.confluence_package import CodeConfluencePackage
from unoplat_code_confluence_query_engine.models.confluence_user_intent import ConfluenceUserIntent

class QueryEngineProcess:
    def __init__(self, appConfigPath:str):
        
        json_loader = JsonLoader()
        
        json_configuration_data = json_loader.load_json_from_file(appConfigPath)
        
        self.app_config = AppConfig(**json_configuration_data)
        
        self.embedding_generator = UnoplatEmbeddingGenerator(self.app_config.sentence_transformer_model)
        
        openai_provider = dspy.LM(model=self.app_config.provider_model_dict["model_provider"],**self.app_config.provider_model_dict["model_provider_args"])
        
        dspy.configure(lm=openai_provider)
        
        self.rerank_module = CodeConfluenceUserQueryReRankModule()
        
        self.intent_module = CodeConfluenceIntentDetectionModule()
        
        self.user_query_response_module = CodeConfluenceUserQueryResponseModule()
        
        self.graph_helper = Neo4jHelper(self.app_config.neo4j_uri, self.app_config.neo4j_username, self.app_config.neo4j_password)
       
    

    async def process_query(self, user_query: str) -> str:
        
        user_query_embedding = self.embedding_generator.generate_embeddings_for_single_text(user_query)
        user_intent_list: List[int] = self.intent_module(user_query=user_query).answer
        final_response = ""

        if int(ConfluenceUserIntent.FUNCTIONAL_IMPLEMENTATION.value) in user_intent_list:
            # Search similar functions
            results = self.graph_helper.search_similar_nodes(vector_index="Method_implementation_embedding_vector_index", query_embedding=user_query_embedding, top_k=5)
            context = {result["name"]: result["summary"] for result in results}
            
            if len(context) > 1:
                rerank_results = self.rerank_module(user_query=user_query, possible_answers=context).answer.relevant_answers
                filtered_rerank_results = {k: v for k, v in rerank_results.items() if v > 7}
                context = {k: v for k, v in context.items() if k in filtered_rerank_results.keys()}
            else:
                # If there's only one or no context, we don't need to rerank
                filtered_rerank_results = {list(context.keys())[0]: 10} if context else {}
            
            for function_name in list(context.keys()):
                function_hierarchy = self.graph_helper.get_function_hierarchy_and_details(function_name=function_name)[0]
                function_hierarchy_object = CodeConfluenceFunctionHiearchySub(**function_hierarchy)
                function_hierarchy_object.relevance_score = filtered_rerank_results.get(function_name, 10)  # Default to 10 if not ranked
                context[function_name] = function_hierarchy_object.model_dump_json()
            
            final_response = self.user_query_response_module(user_query=user_query, code_metadata=context).answer
            
        elif int(ConfluenceUserIntent.CODE_SUMMARIZATION.value) in user_intent_list:
            
            results = self.graph_helper.search_similar_nodes(vector_index="Codebase_implementation_embedding_vector_index", query_embedding=user_query_embedding,top_k=5)
            context = {result["name"]: result["summary"] for result in results}
            
            if len(context) > 1:
                rerank_results = self.rerank_module(user_query=user_query, possible_answers=context).answer.relevant_answers
                filtered_rerank_results = {k: v for k, v in rerank_results.items() if v > 7}
                context = {k: v for k, v in context.items() if k in filtered_rerank_results.keys()}
            else:
                # If there's only one or no context, we don't need to rerank
                filtered_rerank_results = {list(context.keys())[0]: 10} if context else {}

            # Get hierarchy for all codebase names
            for codebase_name in context.keys():
                codebase_hierarchy = self.graph_helper.get_codebase_details(codebase_name=codebase_name)[0]
                codebase_hierarchy_object = CodeConfluenceCodebase(**codebase_hierarchy)
                codebase_hierarchy_object.relevance_score = filtered_rerank_results.get(codebase_name, 10)  # Default to 10 if not ranked
                context[codebase_name] = codebase_hierarchy_object.model_dump_json()
            # Generate final response
            final_response = final_response + self.user_query_response_module(user_query=user_query, code_metadata=context).answer
        
        elif int(ConfluenceUserIntent.PACKAGE_OVERVIEW.value) in user_intent_list:
            results = self.graph_helper.search_similar_nodes(vector_index="Package_implementation_embedding_vector_index", query_embedding=user_query_embedding,top_k=5)
            context = {result["name"]: result["summary"] for result in results}
            
            if len(context) > 1:
                rerank_results = self.rerank_module(user_query=user_query, possible_answers=context).answer.relevant_answers
                filtered_rerank_results = {k: v for k, v in rerank_results.items() if v > 7}
                context = {k: v for k, v in context.items() if k in filtered_rerank_results.keys()}
            else:
                # If there's only one or no context, we don't need to rerank
                filtered_rerank_results = {list(context.keys())[0]: 10} if context else {}

            # Get hierarchy for all package names
            for package_name in context.keys():
                package_hierarchy = self.graph_helper.get_package_details(package_name=package_name)[0]
                package_hierarchy_object = CodeConfluencePackage(**package_hierarchy)
                package_hierarchy_object.relevance_score = filtered_rerank_results.get(package_name, 10)  # Default to 10 if not ranked
                context[package_name] = package_hierarchy_object.model_dump_json()
            # Generate final response
            final_response = final_response + self.user_query_response_module(user_query=user_query, code_metadata=context).answer
        
        elif int(ConfluenceUserIntent.CLASS_DETAILS.value) in user_intent_list:
            results = self.graph_helper.search_similar_nodes(vector_index="Class_implementation_embedding_vector_index", query_embedding=user_query_embedding, top_k=5)
            context = {result["name"]: result["summary"] for result in results}
            
            if len(context) > 1:
                rerank_results = self.rerank_module(user_query=user_query, possible_answers=context).answer.relevant_answers
                filtered_rerank_results = {k: v for k, v in rerank_results.items() if v > 7}
                context = {k: v for k, v in context.items() if k in filtered_rerank_results.keys()}
            else:
                # If there's only one or no context, we don't need to rerank
                filtered_rerank_results = {list(context.keys())[0]: 10} if context else {}

            # Get details for all class names
            for class_name in context.keys():
                class_details = self.graph_helper.get_class_details(class_name=class_name)[0]
                class_details_object = CodeConfluenceClass(**class_details)
                class_details_object.relevance_score = filtered_rerank_results.get(class_name, 10)  # Default to 10 if not ranked
                context[class_name] = class_details_object.model_dump_json()
            
            # Generate final response
            final_response = final_response + self.user_query_response_module(user_query=user_query, code_metadata=context).answer

        else:
            return "Could not understand your intent. Please be more specific in terms of whether you want to understand at codebase level, feature level, or implementation level."
        
        
        return final_response    

 # TODO: proper exception handling at all levels
    async def load_codebase_graph(self, file_path: str) -> None:
         result = self.graph_helper.import_json_file(file_path=file_path)
         await self._create_vector_index_on_all_nodes()
         return result
    
    async def _create_vector_index_on_all_nodes(self):
        # Create vector indexes for all node types
        
        node_types = ["Codebase","Package","Class","Method"]
        embedding_types = ["objective_embedding", "implementation_embedding"]
        
        for node_type in node_types:
            for embedding_type in embedding_types:
                await self._create_vector_index(node_type, embedding_type)

    async def _create_vector_index(self, node_label: str, embedding_property: str):
        self.graph_helper.create_vector_index(node_label, embedding_property)

    async def load_existing_codebases(self):
        return self.graph_helper.get_existing_codebases()
        

