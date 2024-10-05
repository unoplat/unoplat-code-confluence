from textual.widgets import Label, LoadingIndicator
from textual.containers import Container
from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual import on, work
import asyncio
from processing.query_engine_process import QueryEngineProcess
from textual.binding import Binding

class LoadCodebaseGraphScreen(ModalScreen):

    
    def __init__(self, file_path, query_engine_process: QueryEngineProcess):
        super().__init__()
        self.file_path = file_path
        self.query_engine_process = query_engine_process

    def compose(self) -> ComposeResult:
        with Container(id="progress-container"):
            yield Label("Loading Textual Codebase into Database...")
            yield LoadingIndicator()

    async def on_mount(self) -> None:
        await self.process_file()
    
    
    async def process_file(self):
        # Simulate file processing
        result = await self.query_engine_process.load_codebase_graph(str(self.file_path))
        self.app.notify(result, severity="success")
        self.app.pop_screen()
        
        