import logging
from textual.screen import Screen
from textual.widgets import Header, Footer, Input, RichLog
from textual.binding import Binding
from textual.app import ComposeResult
from textual.containers import Horizontal
from unoplat_code_confluence_query_engine.widgets.chat_history import ChatHistory
from unoplat_code_confluence_query_engine.widgets.unoplat_chat import UnoplatChat
from unoplat_code_confluence_query_engine.processing.query_engine_process import QueryEngineProcess
from unoplat_code_confluence_query_engine.screens.codebase_options import CodebaseOptionsModal
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