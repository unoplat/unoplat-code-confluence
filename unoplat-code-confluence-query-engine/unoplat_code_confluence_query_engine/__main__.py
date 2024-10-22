import argparse
import os
from typing import Dict, List
import warnings
import click
from textual.app import App
from unoplat_code_confluence_query_engine.configuration.external_config import AppConfig
from unoplat_code_confluence_query_engine.processing.query_engine_process import QueryEngineProcess
from unoplat_code_confluence_query_engine.screens.chat_screen import ChatScreen



class ChatApp(App):
    TITLE = "Unoplat Code Confluence - Where Code Meets Clarity"
    CSS_PATH = "query_engine_style.tcss"
    
    def __init__(self, config: AppConfig):
        super().__init__()
        self.query_engine_process = QueryEngineProcess(config)


    async def on_mount(self) -> None:
        await self.push_screen(ChatScreen(query_engine_process=self.query_engine_process))



@click.command()
@click.option('--config', required=True, type=click.Path(exists=True), help='Path to the code confluence query engine configuration file.')
def main(config):
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    """A simple chat application."""
    if not os.path.isfile(config):
        click.echo(f"Error: The code confluence query engine configuration file '{config}' does not exist.", err=True)
        return
    app = ChatApp(config)
    app.run()

if __name__ == "__main__":
    main()