from graph.neo4j_helper import Neo4jHelper
from embedding.unoplat_embedding_generator import UnoplatEmbeddingGenerator

from unoplat_dspy.intent_detection_module import CodeConfluenceIntentDetectionModule
from unoplat_dspy.user_query_final_response import CodeConfluenceUserQueryResponseModule
from unoplat_dspy.user_query_based_rererank_module import CodeConfluenceUserQueryReRankModule
from models.confluence_func_hiearchy import CodeConfluenceFunctionHiearchySub
from configuration.external_config import AppConfig
import dspy
import time
from typing import List
from helper.json_loader import JsonLoader
from textual import log


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
        embedding_start = time.time()
        user_query_embedding = self.embedding_generator.generate_embeddings_for_single_text(user_query)
        embedding_end = time.time()
        embedding_time = embedding_end - embedding_start
        log.debug(f"Embedding time: {embedding_time:.2f}s")

        user_intent_list: List[str] = self.intent_module(user_query=user_query).answer
        
        if "FUNCTIONAL_IMPLEMENTATION" in user_intent_list:
            # Search similar functions
            search_start = time.time()
            results = self.graph_helper.search_similar_nodes(vector_index="Method_objective_embedding_vector_index", query_embedding=user_query_embedding,top_k=5)
            function_objective_dict = {result["name"]:result["summary"] for result in results}
            log.debug(f"Function objective dict: {function_objective_dict}")
            rerank_results = self.rerank_module(user_query=user_query,possible_answers=function_objective_dict).answer.relevant_answers
            filtered_rerank_results = {k: v for k, v in rerank_results.items() if v > 7}
            context = {k: v for k, v in function_objective_dict.items() if k in filtered_rerank_results.keys()}
            search_end = time.time()
            search_time = search_end - search_start
            log.debug(f"Search time: {search_time:.2f}s")

            # Get hierarchy for all function names
            hierarchy_start = time.time()
            for function_name in context.keys():
                function_hierarchy = self.graph_helper.get_function_hierarchy_and_details(function_name=function_name)[0]
                function_hierarchy_object = CodeConfluenceFunctionHiearchySub(**function_hierarchy)
                function_hierarchy_object.relevance_score = filtered_rerank_results[function_name]
                context[function_name] = function_hierarchy_object
            hierarchy_end = time.time()
            hierarchy_time = hierarchy_end - hierarchy_start
            log.debug(f"Hierarchy time: {hierarchy_time:.2f}s")

            # Generate final response
            response_start = time.time()
            final_response = self.user_query_response_module(user_query=user_query, code_hierarchy_dict=context).answer
            response_end = time.time()
            response_time = response_end - response_start
            
            log.debug(f"Response time: {response_time:.2f}s")
            log.debug(f"Total time: {embedding_time + search_time + hierarchy_time + response_time:.2f}s")
            log.debug(f"Final response: {final_response}")

            return final_response
