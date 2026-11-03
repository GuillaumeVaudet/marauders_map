from textual.app import ComposeResult
from textual.widgets import ListView, ListItem, Label


class MainMenu(ListView):
    BORDER_TITLE = "// MAIN MENU"

    def compose(self) -> ComposeResult:
        yield ListItem(Label("VIEW NETWORKS"), id="view_networks")
        yield ListItem(Label("STATISTICS"), id="statistics")
        yield ListItem(Label("DATA MANAGER"), id="data_manager")
        yield ListItem(Label("SETTINGS"), id="settings")
        yield ListItem(Label("QUIT"), id="quit")