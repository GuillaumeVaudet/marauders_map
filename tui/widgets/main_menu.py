from textual.app import ComposeResult
from textual.widgets import ListView, ListItem, Label

class MainMenu(ListView):

    def compose(self) -> ComposeResult:
        yield ListItem(Label("View Networks"), id="view_networks")
        yield ListItem(Label("Statistics"), id="statistics")
        yield ListItem(Label("Data Manager"), id="data_manager")
        yield ListItem(Label("Settings"), id="settings")
        yield ListItem(Label("Quit"), id="quit")