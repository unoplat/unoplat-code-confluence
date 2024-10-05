
from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import Button, Label, DirectoryTree
from textual.containers import Container
from processing.query_engine_process import QueryEngineProcess
import os
from widgets.json_directory_tree import JSONDirectoryTree
from textual.widgets import ListView, ListItem
from textual.binding import Binding
class ExistingCodebaseList(ModalScreen):
    
    BINDINGS = [
        Binding("ctrl+q", "request_quit", "Quit",show=True,priority=True),
            ]
    
    def action_request_quit(self) -> None:
        self.app.pop_screen()

    def __init__(self, query_engine_process: QueryEngineProcess, **kwargs):
        super().__init__(**kwargs)
        self.query_engine_process = query_engine_process

    def compose(self) -> ComposeResult:
            yield Container(
                ListView(id="async-list"),
                id="list-container"
            )

    async def on_mount(self) -> None:
        await self.load_data()

    async def load_data(self) -> None:
        list_view = self.query_one("#async-list", ListView)
        codebases_list: list = await self.query_engine_process.load_existing_codebases()
        list_items = [ListItem(Label(codebase)) for codebase in codebases_list]
        list_view.extend(list_items)
        
        
