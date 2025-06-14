# from src.code_confluence_flow_bridge.logging.trace_utils import seed_and_bind_logger_from_trace_id
# from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package import UnoplatPackage
# from src.code_confluence_flow_bridge.models.workflow.repo_workflow_base import CodebaseProcessingActivityEnvelope
# from src.code_confluence_flow_bridge.parser.codebase_parser import CodebaseParser
# from src.code_confluence_flow_bridge.parser.linters.linter_parser import LinterParser
# from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph_ingestion import CodeConfluenceGraphIngestion

# import os
# import json
# import traceback
# from typing import List

# from temporalio import activity
# from temporalio.exceptions import ApplicationError


# class CodebaseProcessingActivity:
#     """Activity for processing codebase through linting, AST generation and parsing."""
   
#     def __init__(self, code_confluence_graph_ingestion: CodeConfluenceGraphIngestion):
#         self.code_confluence_graph_ingestion = code_confluence_graph_ingestion

#     @activity.defn
#     async def process_codebase(
#         self,
#         envelope: CodebaseProcessingActivityEnvelope,
#     ) -> None:
#         """
#         Process codebase through linting, AST generation, and parsing.

#         Args:
#             envelope: CodebaseProcessingActivityEnvelope containing parameters

#         Returns:
#             UnoplatCodebase: Parsed codebase data
#         """
#         # Extract parameters from envelope
#         codebase_path = envelope.codebase_path
#         root_packages = envelope.root_packages
#         codebase_qualified_name = envelope.codebase_qualified_name
#         programming_language_metadata = envelope.programming_language_metadata
#         trace_id = envelope.trace_id
        
#         info : activity.Info = activity.info()
#         workflow_id = info.workflow_id
#         workflow_run_id = info.workflow_run_id
#         activity_id = info.activity_id
#         activity_name = info.activity_type
#         log = seed_and_bind_logger_from_trace_id(trace_id, workflow_id, workflow_run_id, activity_id, activity_name)
#         log.info("Starting codebase processing")
#         log.info("Programming language metadata: {}", programming_language_metadata.language.value)
#         linter_parser = LinterParser()
#         #TODO: review this post mvp in terms of how to do it better when codebases do not follow standard practices
#         lint_result = linter_parser.lint_codebase(
#             local_workspace_path=codebase_path,
#             dependencies=[],
#             programming_language_metadata=programming_language_metadata
#         )
        
#         if not lint_result:
#             log.warning("Linting completed with warnings")
#         else:
#             log.info("Linting completed successfully")

#         parser = CodebaseParser()
#         list_packages: List[UnoplatPackage] = parser.parse_codebase(
#             codebase_name=codebase_qualified_name,
#             json_data=json_data,
#             local_workspace_path=local_workspace_path,
#             source_directory=source_directory,
#             programming_language_metadata=programming_language_metadata
#         )
        
#         log.debug("Parsed {} packages from codebase", len(list_packages))
        
#         await self.code_confluence_graph_ingestion.insert_code_confluence_package(codebase_qualified_name=codebase_qualified_name, packages=list_packages)

#         log.debug("Inserted {} packages into graph DB", len(list_packages))

#         log.success("Completed codebase processing successfully")
        
#         return None
        
#     @activity.defn
#     async def process_codebase_with_error_handling(
#         self,
#         envelope: CodebaseProcessingActivityEnvelope,
#     ) -> None:
#         """
#         Process codebase with proper error handling.
        
#         Args:
#             envelope: CodebaseProcessingActivityEnvelope containing parameters
#         """
#         # Extract parameters from envelope
#         local_workspace_path = envelope.local_workspace_path
#         codebase_qualified_name = envelope.codebase_qualified_name
#         trace_id = envelope.trace_id
        
#         info : activity.Info = activity.info()
#         workflow_id = info.workflow_id
#         workflow_run_id = info.workflow_run_id
#         activity_id = info.activity_id
#         activity_name = info.activity_type
#         log = seed_and_bind_logger_from_trace_id(trace_id, workflow_id, workflow_run_id, activity_id, activity_name)
        
#         try:
#             await self.process_codebase(envelope)
#         except Exception as e:
#             if isinstance(e, ApplicationError):
#                 # Re-raise ApplicationError as is since it already contains detailed error info
#                 raise
                
#             log.error(
#                 "Failed to process codebase | codebase_name={} | error_type={} | error_details={} | status=error",
#                 codebase_qualified_name, type(e).__name__, str(e)
#             )
            
#             # Capture the traceback string
#             tb_str = traceback.format_exc()
            
#             raise ApplicationError(
#                 f"Failed to process codebase {codebase_qualified_name}",
#                 {"codebase": codebase_qualified_name},
#                 {"local_path": local_workspace_path},
#                 {"error": str(e)},
#                 {"error_type": type(e).__name__},
#                 {"traceback": tb_str},
#                 {"workflow_id": info.workflow_id},
#                 {"workflow_run_id": info.workflow_run_id},
#                 {"activity_name": info.activity_type},
#                 {"activity_id": info.activity_id},
#                 type="CODEBASE_PROCESSING_ERROR"
#             )
