from os import get_terminal_size
import os
from codebaseparser.ArchGuardHandler import ArchGuardHandler
from pytermgui import Toggle, WindowManager, Window, InputField, Label, Button, boxes, tim
import re
from downloader.downloader import Downloader
from settings.appsettings import AppSettings

selected_language=None

def main():
    global selected_language 


    settings = AppSettings()

    manager = WindowManager()

    # Create a window to hold the form
    window = Window(
        title="Choose an action:",
        box=boxes.SINGLE  # Corrected from has_border to box with a border style
    )
    
    # Add only the option to parse and summarise the codebase
    window += Label("Parse and summarise Codebase")

    # Button to submit the action directly without choice
    submit_button = Button("Submit", onclick=lambda _: parse_codebase(manager,settings))
    window += submit_button

    # Set window position
    window.center()
    manager.add(window)
    manager.run()
    

def handle_toggle(value):
    global selected_language
    selected_language = value
    print(f"Selected language: {value}")


def parse_codebase(manager,settings):
    global selected_language
    # Clear previous windows
    for win in list(manager):
        manager.remove(win)

    # Create a larger window based on terminal size
    term_width, term_height = get_terminal_size()
    window_width = int(term_width * 0.6)  # 60% of terminal width
    window_height = int(term_height * 0.6)  # 60% of terminal height

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
    window += programming_language_toggle
    
    #window += archguard_cli_path_field
    window += output_path_field
    window += codebase_name_field

    # Button to submit the indexing
    submit_button = Button("Start Parsing", onclick=lambda _: start_parsing(
        git_url_field.value,
        selected_language,
        output_path_field.value,
        codebase_name_field.value,
        settings
    ))
    window += submit_button
    # Set window position
    window.center()
    manager.add(window)
    manager.run()

def ensure_jar_downloaded(settings, manager):
    # Compile the regex pattern for the JAR file
    jar_pattern = re.compile(r"scanner_cli-.*-all\.jar")

    # Check if any file matching the pattern exists in the download directory
    existing_jars = [f for f in os.listdir(settings.download_directory) if jar_pattern.match(f)]
    
    # Create a window to show the status
    window = Window(title="JAR Management", box=boxes.DOUBLE)
    window.center()
    manager.add(window)
    

    if not existing_jars:
        # No JAR matches, need to download
        window += Label("[210 bold]No suitable JAR found, downloading...[/]")
        manager.run()
        
        jar_path = Downloader.download_latest_jar(settings.download_url, settings.download_directory, settings.github_token)
        
        # Update window after download
        window.clear()
        window += Label("[157 bold]Download complete![/]")
        window += Label(f"JAR Path: {jar_path}")
    else:
        # Use the first matching JAR found
        jar_path = os.path.join(settings.download_directory, existing_jars[0])
        window += Label("[157 bold]Using existing JAR:[/]")
        window += Label(f"JAR Path: {jar_path}")
    
    manager.run()  # Refresh the window to show final status
    return jar_path

def start_parsing(git_url, programming_language, output_path, codebase_name, settings):
    manager = WindowManager()

    # Ensure the JAR is downloaded or use the existing one
    jar_path = ensure_jar_downloaded(settings, manager)

    print(f"Repository URL: {git_url}")
    print(f"Programming Language: {programming_language}")
    print(f"Output Path: {output_path}")
    print(f"Codebase Name: {codebase_name}")

    # Initialize the ArchGuard handler with the collected parameters.
    archguard_handler = ArchGuardHandler(
        jar_path=jar_path,
        language=programming_language,
        codebase_path=git_url,
        output_path=output_path
    )
    # Display a progress bar to provide visual feedback during the scan.
    archguard_handler.show_progress()
    # Execute the scanning process.
    archguard_handler.run_scan()




if __name__ == "__main__":
    main()

