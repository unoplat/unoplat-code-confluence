import argparse
import os
from loguru import logger
import datetime
from unoplat_code_confluence.codebaseparser.arc_guard_handler import ArchGuardHandler
import re
from unoplat_code_confluence.configuration.external_config import AppConfig
from unoplat_code_confluence.data_models.chapi_unoplat_codebase import UnoplatCodebase
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_codebase_summary import DspyUnoplatCodebaseSummary
from unoplat_code_confluence.downloader.downloader import Downloader
from unoplat_code_confluence.dspy_class_summary import CodeConfluenceClassModule
from unoplat_code_confluence.dspy_codebase_summary import CodeConfluenceCodebaseModule
from unoplat_code_confluence.dspy_function_summary import CodeConfluenceFunctionModule
from unoplat_code_confluence.dspy_package_summary import CodeConfluencePackageModule
from unoplat_code_confluence.loader import iload_json, iparse_json
from unoplat_code_confluence.loader.json_loader import JsonLoader
from unoplat_code_confluence.loader.parse_json import JsonParser
from unoplat_code_confluence.nodeparser.markdownsummariser import MarkdownSummariser

from unoplat_code_confluence.summary_parser.codebase_summary import CodebaseSummaryParser
import warnings

def start_pipeline():
    parser = argparse.ArgumentParser(description="Codebase Parser CLI")
    parser.add_argument("--config", help="Path to configuration file for unoplat utility", default=os.getcwd() + '/default_config.json', type=str)
    args = parser.parse_args()

    iload_json = JsonLoader()
    iparse_json = JsonParser()
    isummariser = MarkdownSummariser()
    #loading the config
    json_configuration_data = iload_json.load_json_from_file(args.config)
    
    #TODO: fix logging config
    # logging_config = iload_json.load_json_from_file("loguru.json")
    # logger.configure(handlers=logging_config["handlers"])


    get_codebase_metadata(json_configuration_data,iload_json,iparse_json,isummariser)
    

def get_codebase_metadata(json_configuration_data,iload_json,iparse_json,isummariser):
    # Collect necessary inputs from the user to set up the codebase indexing
    app_config = AppConfig(**json_configuration_data)
    

    # Button to submit the indexing
    start_parsing(
        app_config,
        iload_json,
        iparse_json,
        isummariser
    )

def download_and_continue(settings,manager):
    try:
        jar_path = Downloader.download_latest_jar(settings.download_url, settings.download_directory, settings.github_token)
        logger.info(f"Download completed: {jar_path}")
    except Exception as e:
        logger.error(f"Error during download: {e}")
    finally:
        manager.stop() 
        return jar_path

def ensure_jar_downloaded(github_token,arcguard_cli_repo,local_download_directory):
    # Compile the regex pattern for the JAR file
    jar_pattern = re.compile(r"scanner_cli-.*-all\.jar")

    # Check if any file matching the pattern exists in the download directory
    existing_jars = [f for f in os.listdir(local_download_directory) if jar_pattern.match(f)]

    if not existing_jars:
        logger.info("Downloading utility to parse codebase...")
        # No JAR matches, need to download
        jar_path = Downloader.download_latest_jar(arcguard_cli_repo, local_download_directory, github_token)
        logger.info("Download finished JAR file...")
    else:
        # Use the first matching JAR found
        jar_path = os.path.join(local_download_directory, existing_jars[0])
        logger.info("Using existing JAR:")
        logger.info(f"JAR Path: {jar_path}")
    
    return jar_path


def start_parsing(app_config: AppConfig, iload_json: JsonLoader, iparse_json: JsonParser, isummariser: MarkdownSummariser):

    # Log the start of the parsing process
    logger.info("Starting parsing process...")
    
    # Ensure the JAR is downloaded or use the existing one
    jar_path = ensure_jar_downloaded(app_config.api_tokens["github_token"],app_config.repo.download_url,app_config.repo.download_directory)

    logger.info(f"Local Workspace URL: {app_config.local_workspace_path}")
    logger.info(f"Programming Language: {app_config.programming_language}")
    logger.info(f"Output Path: {app_config.output_path}")
    logger.info(f"Codebase Name: {app_config.codebase_name}")

    # Initialize the ArchGuard handler with the collected parameters.
    archguard_handler = ArchGuardHandler(
        jar_path=jar_path,
        language=app_config.programming_language,
        codebase_path=app_config.local_workspace_path,
        codebase_name=app_config.codebase_name,
        output_path=app_config.output_path
    )
    
    chapi_metadata_path = archguard_handler.run_scan()

    chapi_metadata = iload_json.load_json_from_file(chapi_metadata_path)
    
   
    current_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    output_filename = f"{app_config.codebase_name}_{current_timestamp}.md"

    unoplat_codebase : UnoplatCodebase = iparse_json.parse_json_to_nodes(chapi_metadata)
    
    dspy_function_pipeline_summary : CodeConfluenceFunctionModule = CodeConfluenceFunctionModule()
    
    dspy_class_pipeline_summary : CodeConfluenceClassModule = CodeConfluenceClassModule()
    
    dspy_package_pipeline_summary : CodeConfluencePackageModule = CodeConfluencePackageModule()

    dspy_codebase_pipeline_summary: CodeConfluenceCodebaseModule = CodeConfluenceCodebaseModule()

    dspy_function_pipeline_summary : CodeConfluenceFunctionModule = CodeConfluenceFunctionModule()
    
    dspy_class_pipeline_summary : CodeConfluenceClassModule = CodeConfluenceClassModule()

    codebase_summary = CodebaseSummaryParser(unoplat_codebase,dspy_function_pipeline_summary, dspy_class_pipeline_summary,dspy_package_pipeline_summary,dspy_codebase_pipeline_summary,app_config.llm_provider_config)

    unoplat_codebase_summary: DspyUnoplatCodebaseSummary = codebase_summary.parse_codebase()

    # now write to a markdown dspy unoplat codebase summary
    
    markdown_output = isummariser.summarise_to_markdown(unoplat_codebase_summary)
    # write the markdown output to a file
    with open(os.path.join(app_config.output_path, output_filename), 'w') as md_file:
        md_file.write(markdown_output)
        
    logger.info("Parsing process completed.")

    
if __name__ == "__main__":
    
    warnings.filterwarnings("ignore", category=DeprecationWarning, module='pydantic.*')
   
    start_pipeline()
    
