import argparse
import os
from typing import Dict, List
import warnings
import click
from textual.logging import TextualHandler
import logging

from textual.app import App
from configuration.external_config import AppConfig
from processing.query_engine_process import QueryEngineProcess

from screens.chat_screen import ChatScreen



class ChatApp(App):
    CSS = """
    
    #chat-history {
        border: solid green;
        height: 100%;
        width: 20%;
    }
    #chat {
        border: solid blue;
        height: 100%;
        width: 80%;
    }
    #message-log {
        height: 1fr;  /* Allow message log to take up available vertical space */
    }
    #message-input {
        dock: bottom;
        height: 3;  /* Fix height of input field */
    }
    #history-title {
        content-align: center middle;
        height: 3;
    }
    #history-placeholder {
        height: 1fr;  /* Make sure the placeholder fills remaining space */
    }
    """
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

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        handlers=[TextualHandler()],
        format="%(message)s",
    )

    app = ChatApp(config)
    app.run()

if __name__ == "__main__":
    main()