from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import Button, Label, ListView, ListItem, Header, Footer
from textual.containers import Container
from unoplat_code_confluence_query_engine.processing.query_engine_process import QueryEngineProcess
from textual.binding import Binding

class ExistingCodebaseList(ModalScreen):
    
    BINDINGS = [
        Binding("ctrl+q", "request_quit", "Quit", show=True, priority=True),
    ]
    
    def __init__(self, query_engine_process: QueryEngineProcess, **kwargs):
        super().__init__(**kwargs)
        self.query_engine_process = query_engine_process

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Label("Existing Codebases", id="existing-codebases-title"),
            ListView(id="async-list"),
            id="list-container"
        )
        yield Footer()

    def action_request_quit(self) -> None:
        self.app.pop_screen()

    async def on_mount(self) -> None:
        await self.load_data()

    async def load_data(self) -> None:
        list_view = self.query_one("#async-list", ListView)
        codebases_list: list = await self.query_engine_process.load_existing_codebases()
        list_items = [ListItem(Label(codebase)) for codebase in codebases_list]
        list_view.extend(list_items)

