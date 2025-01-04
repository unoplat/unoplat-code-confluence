# Standard Library

# Third Party
from loguru import logger
from unoplat_code_confluence_commons.graph_models.code_confluence_codebase import CodeConfluenceCodebase
from unoplat_code_confluence_commons.graph_models.code_confluence_git_repository import CodeConfluenceGitRepository

from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_git_repository import UnoplatGitRepository
from src.code_confluence_flow_bridge.models.configuration.settings import EnvironmentSettings
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph import CodeConfluenceGraph


class CodeConfluenceGraphIngestion:
    def __init__(self,code_confluence_env: EnvironmentSettings):
        self.code_confluence_graph = CodeConfluenceGraph(code_confluence_env=code_confluence_env)
        self.code_confluence_graph.create_schema()

    def insert_code_confluence_git_repo(self,git_repo: UnoplatGitRepository) -> None:
        git_repo_dict = [
            {
                "qualified_name": f"{git_repo.github_organization}_{git_repo.repository_name}",
                "repository_url": git_repo.repository_url,
                "repository_name": git_repo.repository_name,
                "repository_metadata": git_repo.repository_metadata,
                "readme": git_repo.readme,
                "github_organization": git_repo.github_organization
            }
        ]
        try:
            code_confluence_git_repo_node = CodeConfluenceGitRepository.create_or_update(*git_repo_dict)
            logger.success(f"Git repo node created: {code_confluence_git_repo_node}")
            
            git_repo_node: CodeConfluenceGitRepository = code_confluence_git_repo_node[0]
            
            # Create codebase node
            for codebase in git_repo.codebases:
                codebase_dict = [
                    {
                        "qualified_name": f"{git_repo.github_organization}_{git_repo.repository_name}_{codebase.name}",
                        "name": codebase.name,
                        "readme": codebase.readme
                    }
                ]
                code_confluence_codebase_node = CodeConfluenceCodebase.create_or_update(*codebase_dict)
                codebase_node: CodeConfluenceCodebase = code_confluence_codebase_node[0]
                logger.success(f"Codebase node created: {codebase_node}")
                git_repo_node.codebases.connect(codebase_node)
                codebase_node.git_repository.connect(git_repo_node)
                
        except Exception as e:
            logger.error(f"Error creating nodes: {str(e)}")
            raise