from textual.widgets import Label, Placeholder
from textual.app import ComposeResult
from textual.containers import Vertical

class ChatHistory(Vertical):

    def compose(self) -> ComposeResult:
        yield Label("Chat History", id="history-title")
        yield Placeholder("Chat history will be implemented soon", id="history-placeholder")

