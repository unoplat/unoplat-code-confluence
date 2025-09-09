"""Centralized registry for agent-specific prompt templates.

This registry builds user prompts for agents. Where we previously embedded
JSON blobs directly into prompts, we now prefer XML via
`pydantic_ai.format_as_xml` since models often follow XML structure more
reliably in free-form text.
"""

from typing import Callable, Dict, Optional, Union

from pydantic import BaseModel
from pydantic_ai import format_as_xml

from unoplat_code_confluence_query_engine.models.agent_execution_request import (
    PromptProviderProtocol,
)


class AgentPromptRegistry(PromptProviderProtocol):
    """Registry providing agent-specific prompt templates."""
    
    def __init__(self) -> None:
        """Initialize registry with all agent prompt templates."""
        self._templates: Dict[str, Callable[..., str]] = {
            "framework_explorer": self._frameworks_prompt,
            "project_configuration_agent": self._directory_prompt,
            "development_workflow": self._development_workflow_prompt,
            "business_logic_domain": self._business_logic_domain_prompt,
        }
    
    def get_user_message(
        self,
        agent_name: str,
        repository_qualified_name: str,
        codebase_name: str,
        codebase_path: str,
        codebase_language: str,
        extra_prompt_context: Optional[Dict[str, Union[BaseModel, list[BaseModel], str]]] = None,
    ) -> str:
        """Generate user message prompt for the given agent and codebase context."""
        if agent_name not in self._templates:
            raise KeyError(f"No prompt template registered for agent '{agent_name}'")
        
        return self._templates[agent_name](
            repository_qualified_name,
            codebase_name,
            codebase_path,
            codebase_language,
            extra_prompt_context,
        )
    
    def _format_additional_context(self, extra_prompt_context: Optional[Dict[str, Union[BaseModel, list[BaseModel], str]]]) -> str:
        """Format additional context from extra_prompt_context into XML or string format."""
        additional_context = ""
        if extra_prompt_context:
            for key, value in extra_prompt_context.items():
                if isinstance(value, BaseModel):
                    root_tag = key.replace("_", "").capitalize()
                    xml_content = format_as_xml(value, root_tag=root_tag)
                    additional_context += f"{xml_content}\n\n"
                elif isinstance(value, list) and all(isinstance(item, BaseModel) for item in value):
                    root_tag = key.replace("_", "").capitalize()
                    for item in value:
                        xml_content = format_as_xml(item, root_tag=f"{root_tag}Item")
                        additional_context += f"{xml_content}\n\n"
                elif isinstance(value, str):
                    additional_context += f"{key.replace('_', ' ').title()}: {value}\n\n"
        return additional_context
    
    def _frameworks_prompt(
        self,
        repository_qualified_name: str,
        codebase_name: str,
        codebase_path: str,
        codebase_language: str,
        extra_prompt_context: Optional[Dict[str, Union[BaseModel, list[BaseModel], str]]] = None,
    ) -> str:
        """Generate prompt for framework_explorer_agent."""
        header = (
            f"Analyze the major frameworks and libraries for repository "
            f"{repository_qualified_name}. "
            f"Focus ONLY on the codebase '{codebase_name}' located at "
            f"{codebase_path} written in "
            f"{codebase_language}. "
        )
        
        additional_context = self._format_additional_context(extra_prompt_context)
        return header + additional_context
    
    def _directory_prompt(
        self,
        repository_qualified_name: str,
        codebase_name: str,
        codebase_path: str,
        codebase_language: str,
        extra_prompt_context: Optional[Dict[str, Union[BaseModel, list[BaseModel], str]]] = None,
    ) -> str:
        """Generate prompt for project_configuration_agent."""
        header = (
            f"Analyze the project configuration"
            f"Focus ONLY on the codebase '{codebase_name}' located at "
            f"{codebase_path} written in "
            f"{codebase_language}. "
        )
        
        additional_context = self._format_additional_context(extra_prompt_context)
        return header + additional_context
    
    def _development_workflow_prompt(
        self,
        repository_qualified_name: str,
        codebase_name: str,
        codebase_path: str,
        codebase_language: str,
        extra_prompt_context: Optional[Dict[str, Union[BaseModel, list[BaseModel], str]]] = None,
    ) -> str:
        """Generate prompt for development_workflow_agent."""
        header = (
            f"Analyze the development workflow for repository {repository_qualified_name}. "
            f"Focus ONLY on the codebase '{codebase_name}' located at {codebase_path} "
            f"written in {codebase_language}. Return only DevelopmentWorkflow JSON.\n\n"
        )
        
        additional_context = self._format_additional_context(extra_prompt_context)
        
        instructions = (
            "Workflow:\n"
            "1. Use the additional context provided above (if any) to identify config files and directories\n"
            "2. Read package manifests to find build/test/lint dependencies and scripts\n"
            "3. For unclear tools, use get_lib_data with queries like 'What are the commands for [tool] as a linter/test-runner/build-tool'\n"
            "4. Extract actual commands from scripts or apply language defaults\n"
            "5. Output strictly the DevelopmentWorkflow JSON with no prose\n\n"
            
            "Language-specific patterns:\n"
            "- JavaScript/TypeScript: package.json scripts.{build,test,lint}, config files like .eslintrc*, jest.config.*\n"
            "- Python: pyproject.toml [tool.*], Makefile, tox.ini, pytest.ini, common commands like 'ruff check', 'pytest'\n"
            "- Go: go.mod, 'go build ./...', 'go test ./...', 'golangci-lint run'\n"
            "- Java: pom.xml/build.gradle, 'mvn test', 'gradle build', checkstyle/spotbugs configs\n\n"
            
            "Output format: Only the JSON for DevelopmentWorkflow with a single field 'commands' as a list of CommandSpec entries.\n"
            "Each CommandSpec must include: kind (one of build, dev, test, lint, type_check), command (string). Optional fields: \n"
            "description, tool, runner, config_files (list of strings), working_directory."
        )
        
        return header + additional_context + instructions

    def _business_logic_domain_prompt(
        self,
        repository_qualified_name: str,
        codebase_name: str,
        codebase_path: str,
        codebase_language: str,
        extra_prompt_context: Optional[Dict[str, Union[BaseModel, list[BaseModel], str]]] = None,
    ) -> str:
        """Generate prompt for business_logic_domain_agent."""
        header = (
            f"Identify the single critical business logic domain for repository {repository_qualified_name}. "
            f"Focus ONLY on the codebase '{codebase_name}' located at {codebase_path} written in {codebase_language}. "
            f"Return only JSON for BusinessLogicDomain with fields: domain (optional), description, core_files[]."
        )
        
        additional_context = self._format_additional_context(extra_prompt_context)
        return header + additional_context
