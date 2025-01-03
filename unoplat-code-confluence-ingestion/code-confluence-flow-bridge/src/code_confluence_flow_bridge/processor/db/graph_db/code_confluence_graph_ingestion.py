# Standard Library

# Third Party

from unoplat_code_confluence_commons.graph_models.code_confluence_git_repository import CodeConfluenceGitRepository

from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_git_repository import UnoplatGitRepository
from src.code_confluence_flow_bridge.models.configuration.settings import EnvironmentSettings
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph import CodeConfluenceGraph


class CodeConfluenceGraphIngestion:
    def __init__(self,code_confluence_env: EnvironmentSettings):
        self.code_confluence_graph = CodeConfluenceGraph(code_confluence_env=code_confluence_env)

    def insert_code_confluence_git_repo(self,git_repo: UnoplatGitRepository) -> None:
        CodeConfluenceGitRepository.create_or_update(git_repo.model_dump(mode='json'))
        