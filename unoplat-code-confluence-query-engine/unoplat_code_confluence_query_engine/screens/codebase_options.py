from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import Button, Label, DirectoryTree
from textual.containers import Container
from textual import on
import asyncio
import os
from widgets.json_directory_tree import JSONDirectoryTree
from screens.graph_load_progress_screen import LoadCodebaseGraphScreen
from processing.query_engine_process import QueryEngineProcess


class CodebaseOptionsModal(ModalScreen):
    
    def __init__(self, query_engine_process: QueryEngineProcess, **kwargs):
        super().__init__(**kwargs)
        self.query_engine_process = query_engine_process

    def compose(self) -> ComposeResult:
        home_dir = os.path.expanduser("~")
        with Container(id="codebase-options-modal-container"):
            yield Label("Select a File:", id="codebase-options-modal-title")
            yield JSONDirectoryTree(home_dir+"/Downloads", id="file-picker")  # Add a DirectoryTree widget
            

    @on(DirectoryTree.FileSelected, "#file-picker")
    async def handle_file_selected(self, event: DirectoryTree.FileSelected) -> None:
         await self.app.push_screen(LoadCodebaseGraphScreen(event.path,self.query_engine_process))
         self.app.pop_screen()
        