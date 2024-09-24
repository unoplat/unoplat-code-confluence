from unoplat_code_confluence.data_models.dspy.dspy_unoplat_function_summary import DspyUnoplatFunctionSummary
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_node_summary import DspyUnoplatNodeSummary
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_package_summary import DspyUnoplatPackageSummary
from unoplat_code_confluence.database.graph.unoplat_graph_ingestion import UnoplatGraphIngestion
from unoplat_code_confluence.embedding.unoplat_embedding_gen import UnoplatEmbeddingGenerator
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_codebase_summary import DspyUnoplatCodebaseSummary
from unoplat_code_confluence.configuration.external_config import AppConfig

class UnoplatGraphProcessing:
    def __init__(self, config: AppConfig):
        self.graph_ingestion = UnoplatGraphIngestion(config)
        self.embedding_generator = UnoplatEmbeddingGenerator(config)

    def process_codebase_summary(self, codebase_summary: DspyUnoplatCodebaseSummary):
        # Generate embeddings for codebase objective and implementation summary
        objective_embedding = self.embedding_generator.generate_embeddings_for_single_text(codebase_summary.codebase_objective)
        implementation_embedding = self.embedding_generator.generate_embeddings_for_single_text(codebase_summary.codebase_summary)

        # Create a node for the codebase summary
        self.graph_ingestion.merge_node(
            label="Codebase",
            properties={
                "qualified_name": codebase_summary.codebase_name,
                "objective": codebase_summary.codebase_objective,
                "objective_embedding": objective_embedding,
                "implementation_summary": codebase_summary.codebase_summary,
                "implementation_embedding": implementation_embedding
            }
        )

        # Initialize stack for DFS
        stack = [("Codebase", codebase_summary.codebase_name, package_name, package_summary) 
                 for package_name, package_summary in codebase_summary.codebase_package.items()]

        while stack:
            parent_label, parent_name, package_name, package_summary = stack.pop()
            self._process_package(parent_label, parent_name, package_name, package_summary, stack)

        # Create index on all nodes
        self._create_vector_index_on_all_nodes()

        # Close the connection to the graph database
        self.graph_ingestion.close()

    def _process_package(self, parent_label: str, parent_name: str, package_name: str, package_summary: DspyUnoplatPackageSummary, stack):
        # Generate embeddings for package objective and implementation summary
        package_objective_embedding = self.embedding_generator.generate_embeddings_for_single_text(package_summary.package_objective)
        package_implementation_embedding = self.embedding_generator.generate_embeddings_for_single_text(package_summary.package_summary)
        
        # Create a node for the package
        self.graph_ingestion.merge_node(
            label="Package",
            properties={
                "qualified_name": package_name,
                "objective": package_summary.package_objective,
                "objective_embedding": package_objective_embedding,
                "implementation_summary": package_summary.package_summary,
                "implementation_embedding": package_implementation_embedding
            }
        )

        # Create a relationship between parent and package
        self.graph_ingestion.merge_relationship(
            start_node_label=parent_label,
            start_node_property=parent_name,
            end_node_label="Package",
            end_node_property=package_name,
            relationship_type="CONTAINS"
        )

        # Process each class in the package
        for class_summary in package_summary.class_summary:
            self._process_class(package_name, class_summary.node_name, class_summary)

        # Add subpackages to the stack for DFS
        for subpackage_name, subpackage_summary in package_summary.sub_package_summaries.items():
            stack.append(("Package", package_name, subpackage_name, subpackage_summary))

    def _process_class(self, package_name: str, class_name: str, class_summary: DspyUnoplatNodeSummary):
        # Generate embeddings for class objective and implementation summary
        class_objective_embedding = self.embedding_generator.generate_embeddings_for_single_text(class_summary.node_objective)
        class_implementation_embedding = self.embedding_generator.generate_embeddings_for_single_text(class_summary.node_summary)
        
        # Create a node for the class
        self.graph_ingestion.merge_node(
            label="Class",
            properties={
                "qualified_name": f"{package_name}.{class_name}",
                "objective": class_summary.node_objective,
                "objective_embedding": class_objective_embedding,
                "implementation_summary": class_summary.node_summary,
                "implementation_embedding": class_implementation_embedding
            }
        ) 

        # Create a relationship between package and class
        self.graph_ingestion.merge_relationship(
            start_node_label="Package",
            start_node_property=package_name,
            end_node_label="Class",
            end_node_property=f"{package_name}.{class_name}",
            relationship_type="CONTAINS"
        )

        # Process each method in the class
        for method_summary in class_summary.functions_summary:
            self._process_method(f"{package_name}.{class_name}",method_summary.function_name, method_summary)

    def _process_method(self, class_name: str, method_name: str, method_summary: DspyUnoplatFunctionSummary):
        # Generate embeddings for method objective and implementation summary
        method_objective_embedding = self.embedding_generator.generate_embeddings_for_single_text(method_summary.function_summary.objective)
        method_implementation_embedding = self.embedding_generator.generate_embeddings_for_single_text(method_summary.function_summary.implementation_summary)
        
        # Create a node for the method
        self.graph_ingestion.merge_node(
            label="Method",
            properties={
                "qualified_name": f"{class_name}.{method_name}",
                "objective": method_summary.function_summary.objective,
                "objective_embedding": method_objective_embedding,
                "implementation_summary": method_summary.function_summary.implementation_summary,
                "implementation_embedding": method_implementation_embedding
            }
        )

        # Create a relationship between class and method
        self.graph_ingestion.merge_relationship(
            start_node_label="Class",
            start_node_property=class_name,
            end_node_label="Method",
            end_node_property=f"{class_name}.{method_name}",
            relationship_type="CONTAINS"
        )

    def _create_vector_index_on_all_nodes(self):
        # Create vector indexes for all node types
        node_types = ["Package","Class","Method"]
        embedding_types = ["objective_embedding", "implementation_embedding"]
        
        for node_type in node_types:
            for embedding_type in embedding_types:
                self._create_vector_index(node_type, embedding_type)

    def _create_vector_index(self, node_label: str, embedding_property: str):
        self.graph_ingestion.create_vector_index(node_label, embedding_property)
