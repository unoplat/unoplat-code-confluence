from unoplat_code_confluence.data_models.dspy.dspy_unoplat_function_summary import DspyUnoplatFunctionSummary
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_node_summary import DspyUnoplatNodeSummary
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_package_summary import DspyUnoplatPackageSummary
from unoplat_code_confluence.database.graph.unoplat_graph_ingestion import UnoplatGraphIngestion
from unoplat_code_confluence.embedding.unoplat_embedding_gen import UnoplatEmbeddingGenerator
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_codebase_summary import DspyUnoplatCodebaseSummary
from unoplat_code_confluence.configuration.external_config import AppConfig
from unoplat_code_confluence_commons.graph_models.confluence_codebase import ConfluenceCodebase
from unoplat_code_confluence_commons.graph_models.confluence_package import ConfluencePackage
from unoplat_code_confluence_commons.graph_models.confluence_class import ConfluenceClass
from unoplat_code_confluence_commons.graph_models.confluence_method import ConfluenceMethod
from neomodel import config, db
import logging

class UnoplatGraphProcessing:
    def __init__(self, app_config: AppConfig):
        self.unoplat_graph_ingestion = UnoplatGraphIngestion(app_config)
        self.embedding_generator = UnoplatEmbeddingGenerator(app_config)
        # Configure neomodel connection
        neo4j_url = f'bolt://{app_config.neo4j_username}:{app_config.neo4j_password}@{app_config.neo4j_uri.split("://")[-1]}'
        config.DATABASE_URL = neo4j_url
        db.set_connection(neo4j_url)
        self.unoplat_graph_ingestion.create_schema()

    def process_codebase_summary(self, codebase_summary: DspyUnoplatCodebaseSummary):
        try:
            # Generate embeddings
            objective_embedding = self.embedding_generator.generate_embeddings_for_single_text(
                codebase_summary.codebase_objective)
            implementation_embedding = self.embedding_generator.generate_embeddings_for_single_text(
                codebase_summary.codebase_summary)
            
            # Create or update codebase node
            
            codebase_node_dict =  [ 
            {
                    "qualified_name": codebase_summary.codebase_name,
                    "objective": codebase_summary.codebase_objective,
                    "codebase_objective_embedding": objective_embedding,
                    "implementation_summary": codebase_summary.codebase_summary,
                    "codebase_implementation_summary_embedding": implementation_embedding
            }
            ]
            
            ConfluenceCodebase.create_or_update(*codebase_node_dict)
            #TODO: handle none scenarios
            codebase_node: ConfluenceCodebase = ConfluenceCodebase.nodes.get_or_none(qualified_name=codebase_summary.codebase_name)

            # Process packages using DFS
            stack = [(codebase_node, package_name, package_summary) 
                    for package_name, package_summary in codebase_summary.codebase_package.items()]

            while stack:
                parent_node, package_name, package_summary = stack.pop()
                processed_package = self._process_package(parent_node, package_name, package_summary)
                
                # Add subpackages to stack
                for subpackage_name, subpackage_summary in package_summary.sub_package_summaries.items():
                    stack.append((processed_package, subpackage_name, subpackage_summary))
            
            self._create_vector_index_on_all_nodes(self.embedding_generator.get_dimensions())

        except Exception as e:
            logging.error(f"Error processing codebase: {str(e)}")
            raise
        finally:
            db.close_connection()

    def _process_package(self, parent_node, package_name: str, package_summary: DspyUnoplatPackageSummary):
        try:
            # Generate embeddings
            package_objective_embedding = self.embedding_generator.generate_embeddings_for_single_text(
                package_summary.package_objective)
            package_implementation_embedding = self.embedding_generator.generate_embeddings_for_single_text(
                package_summary.package_summary)
            
            # Create package node
            package_node_dict = [{
                "qualified_name": f"{parent_node.qualified_name}.{package_name}",
                "objective": package_summary.package_objective,
                "package_objective_embedding": package_objective_embedding,
                "implementation_summary": package_summary.package_summary,
                "package_implementation_summary_embedding": package_implementation_embedding
            }]
            
            ConfluencePackage.create_or_update(*package_node_dict)
            package_node: ConfluencePackage = ConfluencePackage.nodes.get_or_none(qualified_name=f"{parent_node.qualified_name}.{package_name}")
   
            # Connect to parent
            if isinstance(parent_node, ConfluenceCodebase):
                
                if not parent_node.packages.is_connected(package_node):
                    parent_node_relation_result = parent_node.packages.connect(package_node)
                    logging.debug(f"parent_node_relation_result: {parent_node_relation_result}")
                
                if not package_node.confluence_codebase.is_connected(parent_node):
                    package_node_relation_result = package_node.confluence_codebase.connect(parent_node)
                    logging.debug(f"package_node_relation_result: {package_node_relation_result}")
                    
            elif isinstance(parent_node, ConfluencePackage):
                
                if not parent_node.sub_packages.is_connected(package_node):
                    package_sub_package_relation_result = parent_node.sub_packages.connect(package_node)
                    logging.debug(f"package_sub_package_relation_result: {package_sub_package_relation_result}")
                
                if not package_node.sub_packages.is_connected(parent_node):
                    sub_package_package_relation_result = package_node.sub_packages.connect(parent_node)
                    logging.debug(f"sub_package_package_relation_result: {sub_package_package_relation_result}")
            # Process classes
            for class_summary in package_summary.class_summary:
                self._process_class(package_node, class_summary)

            return package_node

        except Exception as e:
            logging.error(f"Error processing package {package_name}: {str(e)}")
            raise

    def _process_class(self, package_node: ConfluencePackage, class_summary: DspyUnoplatNodeSummary):
        try:
            # Generate embeddings
            class_objective_embedding = self.embedding_generator.generate_embeddings_for_single_text(
                class_summary.node_objective)
            class_implementation_embedding = self.embedding_generator.generate_embeddings_for_single_text(
                class_summary.node_summary)
            
            # Create class node
            class_node_dict = [{
                "qualified_name": f"{package_node.qualified_name}.{class_summary.node_name}",
                "class_name": class_summary.node_name,
                "objective": class_summary.node_objective,
                "class_objective_embedding": class_objective_embedding,
                "implementation_summary": class_summary.node_summary,
                "class_implementation_summary_embedding": class_implementation_embedding
            }]
            
            ConfluenceClass.create_or_update(*class_node_dict)
            class_node: ConfluenceClass = ConfluenceClass.nodes.get_or_none(qualified_name=f"{package_node.qualified_name}.{class_summary.node_name}")

            # Connect to package
            if not package_node.classes.is_connected(class_node):
                package_node_class_relation_result = package_node.classes.connect(class_node)
                logging.debug(f"package_node_class_relation_result: {package_node_class_relation_result}")
                
            if not class_node.package.is_connected(package_node):
                class_node_package_relation_result = class_node.package.connect(package_node)
                logging.debug(f"class_node_package_relation_result: {class_node_package_relation_result}")

            # Process methods
            for method_summary in class_summary.functions_summary:
                self._process_method(class_node, method_summary)

        except Exception as e:
            logging.error(f"Error processing class {class_summary.node_name}: {str(e)}")
            raise

    def _process_method(self, class_node: ConfluenceClass, method_summary: DspyUnoplatFunctionSummary):
        try:
            # Generate embeddings
            method_objective_embedding = self.embedding_generator.generate_embeddings_for_single_text(
                method_summary.function_summary.objective)
            method_implementation_embedding = self.embedding_generator.generate_embeddings_for_single_text(
                method_summary.function_summary.implementation_summary)
            
            # Create method node
            method_node_dict = [{
                "qualified_name": f"{class_node.qualified_name}.{method_summary.function_name}",
                "function_name": method_summary.function_name,
                "objective": method_summary.objective,
                "function_objective_embedding": method_objective_embedding,
                "implementation_summary": method_summary.implementation_summary,
                "function_implementation_summary_embedding": method_implementation_embedding
            }]
            
            ConfluenceMethod.create_or_update(*method_node_dict)
            method_node: ConfluenceMethod = ConfluenceMethod.nodes.get_or_none(qualified_name=f"{class_node.qualified_name}.{method_summary.function_name}")

            # Connect to class
            if not class_node.methods.is_connected(method_node):
                class_node_method_relation_result = class_node.methods.connect(method_node)
                logging.debug(f"class_node_method_relation_result: {class_node_method_relation_result}")
                
            if not method_node.confluence_class.is_connected(class_node):
                method_node_class_relation_result = method_node.confluence_class.connect(class_node)
                logging.debug(f"method_node_class_relation_result: {method_node_class_relation_result}")

        except Exception as e:
            logging.error(f"Error processing method {method_summary.function_name}: {str(e)}")
            raise

    def _create_vector_index_on_all_nodes(self, dimensions: int):
            # Create vector indexes for all node types
            node_embedding_properties = {
                "ConfluenceCodebase": ["codebase_objective_embedding", "codebase_implementation_summary_embedding"],
                "ConfluencePackage": ["package_objective_embedding", "package_implementation_summary_embedding"],
                "ConfluenceClass": ["class_objective_embedding", "class_implementation_summary_embedding"],
                "ConfluenceMethod": ["function_objective_embedding", "function_implementation_summary_embedding"]
            }
            
            for node_type, embedding_properties in node_embedding_properties.items():
                for embedding_property in embedding_properties:
                    self._create_vector_index(node_label=node_type, embedding_property=embedding_property, dimensions=dimensions)

    def _create_vector_index(self, node_label: str, embedding_property: str, dimensions: int):
        self.unoplat_graph_ingestion.create_vector_index(label=node_label, dimension=dimensions,property=embedding_property)
