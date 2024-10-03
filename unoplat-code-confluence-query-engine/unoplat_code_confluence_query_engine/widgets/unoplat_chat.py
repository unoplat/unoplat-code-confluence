import logging
from textual import work
from textual.widgets import  RichLog, Input, Static
from textual.app import ComposeResult
from processing.query_engine_process import QueryEngineProcess
from textual.containers import Vertical

class UnoplatChat(Vertical):
    
    def __init__(self, query_engine_process: QueryEngineProcess,name: str | None = None, id: str | None = None, classes: str | None = None):
        super().__init__(name=name, id=id, classes=classes)
        self.query_engine_process = query_engine_process
        self.logger = logging.getLogger(__name__)

    def compose(self) -> ComposeResult:
        yield RichLog(id="message-log", wrap=True, markup=True)
        yield Input(id="message-input", placeholder="Type a message...")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        message_input = self.query_one("#message-input", Input)
        message_log = self.query_one("#message-log", RichLog)
        message = event.value

        if message:
            message_log.write(f"[bold blue]You:[/bold blue] {message}")
            message_input.value = ""
            self.send_message_to_api(message, message_log)
     
    @work(thread=True,group="query_engine") # This decorator runs the method in a worker thread
    async def send_message_to_api(self, message: str, message_log: RichLog) -> None:
        response = await self.get_api_response(message)
        self.app.call_from_thread(
            message_log.write, f"[bold green]Bot:[/bold green] {response}"
        )

    async def get_api_response(self, message: str) -> str:
        # Placeholder for API call
        # Replace this with actual API interaction code
        final_response: str = await self.query_engine_process.process_query(message)
        return {final_response}