import json
from os import get_terminal_size
import os
from pytermgui import tim
from loguru import logger
from codeagent.unoplat_agent import UnoplatAgent
from codebaseparser.ArchGuardHandler import ArchGuardHandler
from pytermgui import Toggle, WindowManager, Window, InputField, Label, Button, boxes
import re
from downloader.downloader import Downloader
from loader import iload_json, iparse_json
from loader.json_loader import JsonLoader
from loader.parse_json import JsonParser
from nodeparser.nodesummariser import NodeSummariser
from nodeparser.isummariser import ISummariser
from settings.appsettings import AppSettings

selected_language=None

# Load logging configuration from loguru.json
with open("loguru.json", "r") as config_file:
    config = json.load(config_file)
logger.configure(handlers=config["handlers"])

def main(iload_json, iparse_json,isummariser):
    global selected_language 


    settings = AppSettings()

    manager = WindowManager()
    
    # Create a window to hold the form
    window = Window(
        title="Choose an action:",
        box=boxes.SINGLE
    )
    
    # Add only the option to parse and summarise the codebase
    window += Label("Parse and summarise Codebase")

    # Button to submit the action directly without choice
    submit_button = Button("Submit", onclick=lambda _: get_codebase_metadata(manager,settings,iload_json,iparse_json,isummariser))
    window += submit_button

    # Set window position
    window.center()
    manager.add(window)
    manager.run()
    

def handle_toggle(value):
    global selected_language
    selected_language = value
    logger.info(f"Selected language: {value}")


def get_codebase_metadata(manager,settings,iload_json,iparse_json,isummariser):
    global selected_language
    # Clear previous windows
    for win in list(manager):
        manager.remove(win)
 

    # Create a larger window based on terminal size
    term_width, term_height = get_terminal_size()
    window_width = int(term_width * 0.4)  # 60% of terminal width
    window_height = int(term_height * 0.4)  # 60% of terminal height

    window = Window(
        title="Parse & Summarise Codebase Setup",
        box=boxes.SINGLE,
        width=window_width,
        height=window_height
    )

    # Collect necessary inputs from the user to set up the codebase indexing
    git_url_field = InputField(prompt="Enter the local workspace repository: ")
    programming_language_toggle = Toggle(
        states=["java","py"], 
        on_toggle=handle_toggle
    )
    #archguard_cli_path_field = InputField(prompt="Enter the full path to the ArchGuard CLI executable: ")
    output_path_field = InputField(prompt="Enter the output path for storing scan results: ")
    codebase_name_field = InputField(prompt="Enter the Repository name: ")

    # Add fields to the window using the += operator
    window += git_url_field
    #TODO: renable them
    #window += programming_language_toggle
    
    #window += archguard_cli_path_field
    window += output_path_field
    window += codebase_name_field

    # Button to submit the indexing
    submit_button = Button("Start Parsing", onclick=lambda _: start_parsing(
        git_url_field.value,
        # move this when expanding to new languages
        "java",
        output_path_field.value,
        codebase_name_field.value,
        settings,
        manager,
        iload_json,
        iparse_json,
        isummariser
    ))
    window += submit_button
    # Set window position
    window.center()
    manager.add(window)
    manager.run()

def download_and_continue(settings,manager):
    try:
        jar_path = Downloader.download_latest_jar(settings.download_url, settings.download_directory, settings.github_token)
        print(f"Download completed: {jar_path}")
    except Exception as e:
        print(f"Error during download: {e}")
    finally:
        manager.stop() 
        return jar_path

def ensure_jar_downloaded(settings):
    # Compile the regex pattern for the JAR file
    jar_pattern = re.compile(r"scanner_cli-.*-all\.jar")

    # Check if any file matching the pattern exists in the download directory
    existing_jars = [f for f in os.listdir(settings.download_directory) if jar_pattern.match(f)]

    if not existing_jars:
        tim.print("[bold lightblue]Downloading utility to parse codebase...[/]")
        # No JAR matches, need to download
        jar_path = Downloader.download_latest_jar(settings.download_url, settings.download_directory, settings.github_token)
        tim.print("[bold lightgreen]Download finished JAR file...[/]")
    else:
        # Use the first matching JAR found
        jar_path = os.path.join(settings.download_directory, existing_jars[0])
        tim.print("[bold lightgreen]Using existing JAR:[/]")
        tim.print(f"JAR Path: {jar_path}")
    
    return jar_path

def start_parsing(git_url, programming_language, output_path, codebase_name, settings, manager, iload_json, iparse_json,isummariser):
    # Log the start of the parsing process
    logger.info("Starting parsing process...")
    
    # TIM-based printing to indicate the start of parsing
    tim.print("[bold lightblue]Starting parsing process...[/]")
    
    # Ensure the JAR is downloaded or use the existing one
    jar_path = ensure_jar_downloaded(settings)

    logger.info(f"Repository URL: {git_url}")
    logger.info(f"Programming Language: {programming_language}")
    logger.info(f"Output Path: {output_path}")
    logger.info(f"Codebase Name: {codebase_name}")

    # Initialize the ArchGuard handler with the collected parameters.
    archguard_handler = ArchGuardHandler(
        jar_path=jar_path,
        language=programming_language,
        codebase_path=git_url,
        codebase_name=codebase_name,
        output_path=output_path
    )
    
    manager.stop()
    # Execute the scanning process.
    chapi_metadata_path = archguard_handler.run_scan()

    chapi_metadata = iload_json.load_json_from_file(chapi_metadata_path)

    codebase_metadata = [
        {"summary": node.summary} for node in iparse_json.parse_json_to_nodes(chapi_metadata, isummariser) if node.type == "CLASS"
    ]
    with open('codebase_summary.json', 'w') as file:
        json.dump(codebase_metadata, file)
    
    tim.print("[bold lightgreen]Parsing process completed.[/]")

    



if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning, module='pydantic.*')
    unoplat_agent_setup =UnoplatAgent()
    unoplat_agent_setup.run_crew()
    # iload_json = JsonLoader()
    # iparse_json = JsonParser()
    # isummariser = NodeSummariser()
    # main(iload_json, iparse_json, isummariser)

