# Standard Library
import os
from typing import List

# Third Party
from git import Repo
from github import Auth, Github

# First Party
from unoplat_code_confluence.configuration.settings import AppSettings, ProgrammingLanguageMetadata, RepositorySettings
from unoplat_code_confluence.data_models.chapi_forge.unoplat_codebase import UnoplatCodebase
from unoplat_code_confluence.data_models.chapi_forge.unoplat_git_repository import UnoplatGitRepository
from unoplat_code_confluence.data_models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata


class GithubHelper:
    def __init__(self,app_settings: AppSettings):
        self.settings = app_settings
        
    # works with - vhttps://github.com/organization/repository,https://github.com/organization/repository.git,git@github.com:organization/repository.git
    def clone_repository(self,repository_config: RepositorySettings) -> UnoplatGitRepository:
        """
        Clone the repository and return repository details
        Works with URL formats:
        - https://github.com/organization/repository
        - https://github.com/organization/repository.git
        - git@github.com:organization/repository.git
        """
        
        # Initialize Github client with personal access token
        auth = Auth.Token(self.settings.secrets.github_token)
        github_client = Github(auth=auth)
    
        # Get repository from URL
        repo_url = repository_config.git_url
        
        # Extract owner and repo name from different URL formats
        if repo_url.startswith('git@'):
            # Handle SSH format: git@github.com:org/repo.git
            repo_path = repo_url.split('github.com:')[-1]
        else:
            # Handle HTTPS format: https://github.com/org/repo[.git]
            repo_path = repo_url.split('github.com/')[-1]
        
        # Remove .git suffix if present
        repo_path = repo_path.replace('.git', '')
        repo_name = repo_path.split('/')[-1]
        
        try:
            # Get repository object from Github using owner/repo format
            github_repo = github_client.get_repo(repo_path)
            
            # Create local directory if it doesn't exist
            local_path = os.path.join(os.path.expanduser("~"), ".unoplat", "repositories")
            os.makedirs(local_path, exist_ok=True)
            repo_path = os.path.join(local_path, repo_name)
            
            # Clone repository if not already cloned
            if not os.path.exists(repo_path):
                repo_metadata: Repo = Repo.clone_from(repo_url, repo_path)
            
            # Get repository metadata
            repo_metadata = {
                "stars": github_repo.stargazers_count,
                "forks": github_repo.forks_count,
                "default_branch": github_repo.default_branch,
                "created_at": str(github_repo.created_at),
                "updated_at": str(github_repo.updated_at),
                "language": github_repo.language,
            }
            
            # Get README content
            try:
                readme_content = github_repo.get_readme().decoded_content.decode('utf-8')
            except:
                readme_content = None
                
            # Create UnoplatCodebase objects for each codebase config
            codebases: List[UnoplatCodebase] = []
            for codebase_config in repository_config.codebases:
                # Split the path and join each component properly
                path_components = codebase_config.codebase_folder_name.split('/')
                local_path = repo_path
                for component in path_components:
                    local_path = os.path.join(local_path, component)
                
                programming_language_metadata: ProgrammingLanguageMetadata = codebase_config.programming_language_metadata
                # Verify the path exists
                if not os.path.exists(local_path):
                    raise Exception(f"Codebase path not found: {local_path}")
                
                codebase = UnoplatCodebase(
                    name=codebase_config.root_package_name, #type: ignore
                    local_path=local_path,
                    package_manager_metadata=UnoplatPackageManagerMetadata(
                        programming_language=programming_language_metadata.language.value,
                        package_manager=programming_language_metadata.package_manager,
                        programming_language_version={'version': programming_language_metadata.language_version} if programming_language_metadata.language_version else None
                    )
                )
                codebases.append(codebase)
            
            # Create and return UnoplatGitRepository
            return UnoplatGitRepository(
                repository_url=repo_url,
                repository_name=repo_name,
                repository_metadata=repo_metadata,
                codebases=codebases,
                readme=readme_content,
                github_organization=github_repo.organization.login if github_repo.organization else None
            )
            
        except Exception as e:
            raise Exception(f"Failed to clone repository: {str(e)}")
        
    def close(self):
        """
        Close the Github client connection
        """
        self.github_client.close()
        
        
         
        
        
        