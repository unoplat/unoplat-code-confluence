import logging
from textual.screen import Screen
from textual.widgets import Header, Footer, Input, RichLog
from textual.binding import Binding
from textual.app import ComposeResult
from textual.containers import Horizontal
from widgets.chat_history import ChatHistory
from widgets.unoplat_chat import UnoplatChat
from processing.query_engine_process import QueryEngineProcess
from screens.codebase_options import CodebaseOptionsModal
class ChatScreen(Screen):
    AUTO_FOCUS = "#message-input"

    BINDINGS = [
        Binding("ctrl+q", "request_quit", "Quit"),
            ]
    
    def __init__(self, query_engine_process: QueryEngineProcess):
        super().__init__()
        self.query_engine_process = query_engine_process
        
 #TODO: Add citations and history to the chat screen 
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
           #yield ChatHistory(id="chat-history")
           yield UnoplatChat(id="chat", query_engine_process=self.query_engine_process)
        yield Footer()

    def action_request_quit(self) -> None:
        self.app.exit()