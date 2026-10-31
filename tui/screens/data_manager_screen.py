from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Footer, DirectoryTree
from tui.widgets.data_manager_menu import DataManagerMenu


class DataManagerScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def compose(self) -> ComposeResult:
        yield DataManagerMenu()
        yield Footer()