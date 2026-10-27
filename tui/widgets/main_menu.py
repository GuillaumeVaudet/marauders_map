from textual.app import ComposeResult
from textual.widgets import ListView, ListItem, Label

class MainMenu(ListView):

    def compose(self) -> ComposeResult:
        yield ListItem(Label("Option 1"))
        yield ListItem(Label("Option 2"))