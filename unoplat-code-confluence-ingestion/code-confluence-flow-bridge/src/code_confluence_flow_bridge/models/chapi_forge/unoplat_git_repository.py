# # Standard Library
# # First Party
# from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_codebase import UnoplatCodebase
# 
# from typing import Any, List, Optional
# 
# # Third Party
# from pydantic import BaseModel, Field
# 
# 
# # TODO: Currently this is the root. Moving forward , root should be a Organisation and then it should have multiple Domains. And then each domain should have multiple repositories.
# class UnoplatGitRepository(BaseModel):
#     repository_url: str = Field(description="The URL of the repository")
#     repository_name: str = Field(description="The name of the repository")
#     repository_metadata: dict[str, Any] = Field(description="The metadata of the repository")
#     codebases: List[UnoplatCodebase] = Field(default_factory=list, description="The codebases of the repository")
#     readme: Optional[str] = Field(default=None, description="The readme of the repository")
#     domain: Optional[str] = Field(default=None, description="The domain of the repository")
#     github_organization: Optional[str] = Field(default=None, description="The github organization of the repository")
