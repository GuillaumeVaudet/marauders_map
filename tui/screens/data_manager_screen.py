from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Footer

class DataManagerScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def compose(self) -> ComposeResult:
        yield Label("Data manager screen")
        yield Footer()