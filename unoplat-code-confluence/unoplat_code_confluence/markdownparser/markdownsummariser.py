from abc import ABC
from unoplat_code_confluence.data_models.chapi_unoplat_node import Node
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_codebase_summary import DspyUnoplatCodebaseSummary
from unoplat_code_confluence.markdownparser.isummariser import ISummariser
from litellm import completion
from loguru import logger

class MarkdownSummariser(ISummariser):    
    def summarise_to_markdown(self, unoplat_codebase_summary: DspyUnoplatCodebaseSummary) -> str:
        markdown_output = []

        # Codebase Summary
        markdown_output.append("# Codebase Summary\n")
        markdown_output.append(f"**Name:** {unoplat_codebase_summary.codebase_name or 'N/A'}\n")
        markdown_output.append(f"**Objective:** {unoplat_codebase_summary.codebase_objective}\n")
        markdown_output.append(f"**Summary:** {unoplat_codebase_summary.codebase_summary}\n\n")

        # Package Summaries
        markdown_output.append("## Package Summaries\n")
        for package_name, package_summary in unoplat_codebase_summary.codebase_package.items():
            markdown_output.append(f"### {package_name}\n")
            markdown_output.append(f"**Objective:** {package_summary.package_objective}\n")
            markdown_output.append(f"**Summary:** {package_summary.package_summary}\n")
            
            if package_summary.class_summary:
                markdown_output.append("#### Classes\n")
                for class_detail in package_summary.class_summary:
                    markdown_output.append(f"##### {class_detail.node_name}\n")
                    markdown_output.append(f"**Objective:** {class_detail.node_objective}\n")
                    if class_detail.node_summary:
                        markdown_output.append(f"**Summary:** {class_detail.node_summary}\n")
    
                    if class_detail.functions_summary:
                        markdown_output.append("**Functions:**\n")
                        for function in class_detail.functions_summary:
                            markdown_output.append(f"- `{function.function_name}`\n")
                            markdown_output.append(f"  - Objective: {function.function_summary.objective}\n")
                            markdown_output.append(f"  - Implementation: {function.function_summary.implementation_summary.strip().replace('\n', ' ')}\n")
                    markdown_output.append("\n")

            if package_summary.sub_package_summaries:
                markdown_output.append("#### Sub-packages\n")
                for sub_package_name,sub_package in package_summary.sub_package_summaries.items():
                    markdown_output.append(f"##### {sub_package_name}\n")
                    markdown_output.append(f"**Objective:** {sub_package.package_objective}\n")
                    markdown_output.append(f"**Summary:** {sub_package.package_summary}\n")

                    if sub_package.class_summary:
                        markdown_output.append("**Classes:**\n")
                        for class_detail in sub_package.class_summary:
                            markdown_output.append(f"- {class_detail.node_name}\n")
                            markdown_output.append(f"  - Objective: {class_detail.node_objective}\n")
                            if class_detail.functions_summary:
                                markdown_output.append("  - Functions:\n")
                                for function in class_detail.functions_summary:
                                    markdown_output.append(f"    - `{function.function_name}`\n")
                                    markdown_output.append(f"      - Objective: {function.function_summary.objective}\n")
                                    markdown_output.append(f"      - Implementation: {function.function_summary.implementation_summary.strip().replace('\n', ' ')}\n")
                    markdown_output.append("\n")

            markdown_output.append("\n")

        return "\n".join(markdown_output)