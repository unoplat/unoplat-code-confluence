# Standard Library
import argparse
import asyncio
import datetime
import json
import os
import warnings

# Third Party
from loguru import logger

# First Party
from unoplat_code_confluence.codebaseparser.arc_guard_handler import \
    ArchGuardHandler
from unoplat_code_confluence.confluence_git.github_helper import GithubHelper
from unoplat_code_confluence.data_models.chapi_forge.unoplat_codebase import \
    UnoplatCodebase
from unoplat_code_confluence.data_models.chapi_forge.unoplat_git_repository import \
    UnoplatGitRepository
from unoplat_code_confluence.downloader.downloader import Downloader
from unoplat_code_confluence.loader.json_loader import JsonLoader
from unoplat_code_confluence.markdownparser.markdownsummariser import MarkdownSummariser
from unoplat_code_confluence.parser.codebase_parser import CodebaseParser
from unoplat_code_confluence.configuration.settings import AppSettings


async def start_pipeline():
    parser = argparse.ArgumentParser(description="Codebase Parser CLI")
    parser.add_argument(
        "--config", 
        help="Path to configuration file for unoplat utility", 
        default=None,
        type=str
    )
    args = parser.parse_args()

    # Load settings with optional config override
    settings = AppSettings.get_settings(args.config)
    
    # Configure logging from settings
    if settings.config.logging_handlers:
        logger.configure(handlers=settings.config.logging_handlers)

    # Initialize components
    iload_json = JsonLoader()
    codebase_parser = CodebaseParser()
    
    isummariser = MarkdownSummariser()

    # Process repositories
    
    await get_codebase_metadata(settings, iload_json, codebase_parser, isummariser)
    

async def get_codebase_metadata(settings: AppSettings, iload_json: JsonLoader, codebase_parser: CodebaseParser, isummariser: MarkdownSummariser):
    # Collect necessary inputs from the user to set up the codebase indexing
    
    #logger.configure(handlers=app_config.handlers)
    logger.configure(handlers=settings.config.logging_handlers)

    await start_parsing(
        settings,
        iload_json,
        codebase_parser,
        isummariser
    )


async def ensure_jar_downloaded( github_token: str, arcguard_cli_repo: str, local_download_directory: str):
    
    jar_path = Downloader.download_latest_jar(arcguard_cli_repo, local_download_directory, github_token)
    
    return jar_path

async def get_extension(programming_language: str):
    #TODO: convert this to enum based check
    if programming_language == "java":
        return "java"
    elif programming_language == "python":
        return "py"
    else:
        raise ValueError(f"Unsupported programming language: {programming_language}")

#TODO: do it in parallel for each repository and inside repository if it is a mono repo for each codebase. .Rightnow keep it simple  as we will move to temporal soon.
async def start_parsing(app_settings: AppSettings, iload_json: JsonLoader, codebase_parser: CodebaseParser, isummariser: MarkdownSummariser):
    """Start parsing process for repositories and codebases."""
    logger.info("Starting parsing process...")
    
    jar_path = await ensure_jar_downloaded(
        app_settings.secrets.github_token,
        app_settings.config.archguard.download_url, 
        app_settings.config.archguard.download_directory
    )
    
    github_helper = GithubHelper(app_settings=app_settings)
    # Process each repository
    for index, repository in enumerate(app_settings.config.repositories):
        logger.info(f"Processing repository: {repository.git_url}")
        github_repository: UnoplatGitRepository = github_helper.clone_repository(repository)
        markdown_output_path = repository.markdown_output_path
        
        # Process each codebase in the repository
        for codebase_index, codebase in enumerate(github_repository.codebases):
           
            logger.info(f"Processing codebase at path: {codebase.local_path}")
            
            programming_language = codebase.package_manager_metadata.programming_language #type: ignore
            
            logger.info(f"Programming Language: {programming_language}")
            logger.info(f"Output Path: {repository.markdown_output_path}")
            logger.info(f"Codebase Name: {codebase.name}")
            
            # Get file extension based on programming language
            extension = await get_extension(programming_language)

            # Initialize the ArchGuard handler
            archguard_handler = ArchGuardHandler(
                jar_path=jar_path,
                language=programming_language,
                codebase_path=codebase.local_path,
                codebase_name=codebase.name,
                output_path=markdown_output_path,
                extension=extension
            )
            
            chapi_metadata_path = archguard_handler.run_scan()
            chapi_metadata = iload_json.load_json_from_file(chapi_metadata_path)   
            
            current_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            output_filename = f"{os.path.basename(codebase.name)}_{current_timestamp}.json"

            unoplat_codebase: UnoplatCodebase = codebase_parser.parse_codebase(
                json_data = chapi_metadata, 
                local_workspace_path = codebase.local_path,
                programming_language_metadata = app_settings.repositories[index].codebases[codebase_index].programming_language_metadata,
                codebase_name=codebase.name
            )
            github_repository.codebases[codebase_index] = unoplat_codebase
                
                # Serialize repository to JSON string with proper formatting
        try:
            json_str = github_repository.model_dump_json(
                indent=2
            )
            
            # Write JSON output to file
            json_output_path = os.path.join(repository.markdown_output_path, output_filename)
            os.makedirs(os.path.dirname(json_output_path), exist_ok=True)
            
            with open(json_output_path, 'w', encoding='utf-8') as json_file:
                json_file.write(json_str)
                
            logger.info(f"Successfully wrote repository JSON schema to {json_output_path}")
                
        except Exception as e:
            logger.error(
                f"Error serializing/writing JSON output for repository {repository.git_url}\n"
                f"Codebase: {codebase.name}\n"
                f"Error: {str(e)}"
            )
            
                    
        

    logger.info("Parsing process completed for all repositories and codebases.")

    
def main():
    warnings.filterwarnings("ignore", category=DeprecationWarning, module='pydantic.*')
    asyncio.run(start_pipeline())
if __name__ == "__main__":
    main()
