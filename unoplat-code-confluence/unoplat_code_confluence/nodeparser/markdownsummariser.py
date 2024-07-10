from abc import ABC
from unoplat_code_confluence.data_models.chapi_unoplat_node import Node
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_codebase_summary import DspyUnoplatCodebaseSummary
from unoplat_code_confluence.nodeparser.isummariser import ISummariser
from litellm import completion
from loguru import logger

class MarkdownSummariser(ISummariser):    
    def summarise_to_markdown(self, unoplat_codebase_summary: DspyUnoplatCodebaseSummary) -> str:
        markdown_output = []

        # Codebase Summary
        markdown_output.append("# Codebase Summary\n")
        markdown_output.append(f"**Objective:** <p>{unoplat_codebase_summary.codebase_objective}</p>\n")
        markdown_output.append(f"**Summary:** <p>{unoplat_codebase_summary.codebase_summary}</p>\n")
        markdown_output.append(f"**Name:** {unoplat_codebase_summary.codebase_name or 'N/A'}\n")

        # Package Summaries
        markdown_output.append("## Package Summaries\n")
        for package_name, DspyUnoplatPackageNodeSummary in unoplat_codebase_summary.codebase_package.package_summary_dict.items():
            markdown_output.append(f"- **Package:** {package_name}\n")
            markdown_output.append(f"  - **Objective:** <p>{DspyUnoplatPackageNodeSummary.package_objective}</p>\n")
            markdown_output.append(f"  - **Summary:** <p>{DspyUnoplatPackageNodeSummary.package_summary}</p>\n")

            markdown_output.append("### Class Summaries\n")
            
            for class_detail in DspyUnoplatPackageNodeSummary.class_summary:
                
                markdown_output.append(f"- **{class_detail.node_name}**\n")
                markdown_output.append(f"  - **Objective:** <p>{class_detail.node_objective}</p>\n")

                if class_detail.node_summary:
                    markdown_output.append(f"  - **Summary:** <p>{class_detail.node_summary}</p>\n")
 
                if len(class_detail.functions_summary) > 0:
                    markdown_output.append("#### Function Summaries\n")
                    for function in class_detail.functions_summary:
                        markdown_output.append(f"- **{function.function_name}**\n")
                        markdown_output.append(f"  - **Objective:** <p>{function.function_summary.objective}</p>\n")
                        markdown_output.append(f"  - **Implementation:** <p>{function.function_summary.implementation_summary.strip().replace('\n', ' ')}</p>\n")
        return "\n".join(markdown_output)
