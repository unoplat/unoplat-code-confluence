from abc import ABC
from data_models.chapi_unoplat_node import Node
from data_models.dspy.dspy_unoplat_codebase_summary import DspyUnoplatCodebaseSummary
from nodeparser.isummariser import ISummariser
from litellm import completion
from loguru import logger

class MarkdownSummariser(ISummariser):    
    def summarise_to_markdown(self, unoplat_codebase_summary: DspyUnoplatCodebaseSummary) -> str:
        markdown_output = []

        # Codebase Summary
        markdown_output.append("# Codebase Summary\n")
        markdown_output.append(f"**Summary:** {unoplat_codebase_summary.codebase_summary}\n")
        markdown_output.append(f"**Objective:** {unoplat_codebase_summary.codebase_objective}\n")
        markdown_output.append(f"**Name:** {unoplat_codebase_summary.codebase_name or 'N/A'}\n")

        # Package Summaries
        markdown_output.append("## Package Summaries\n")
        for package_name,DspyUnoplatPackageNodeSummary in unoplat_codebase_summary.codebase_package.package_summary_dict.items():
            markdown_output.append(f"### {package_name}\n")
            markdown_output.append(f"**Objective:** {DspyUnoplatPackageNodeSummary.package_objective}\n")
            markdown_output.append(f"**Summary:** {DspyUnoplatPackageNodeSummary.package_summary}\n")

            markdown_output.append("##### Class Summaries\n")
            for class_detail in DspyUnoplatPackageNodeSummary.class_summary:
                markdown_output.append(f"###### {class_detail.node_name}\n")
                markdown_output.append(f"**Objective:** {class_detail.node_objective}\n")
                markdown_output.append(f"**Summary:** {class_detail.node_summary}\n")

                markdown_output.append("####### Function Summaries\n")
                for function in class_detail.functions_summary:
                    markdown_output.append(f"######## {function.function_name}\n")
                    markdown_output.append(f"**Objective:** {function.function_summary.objective}\n")
                    markdown_output.append(f"**Implementation:** {function.function_summary.implementation_summary}\n")
        return "\n".join(markdown_output)
