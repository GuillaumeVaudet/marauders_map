from textual.app import ComposeResult
from textual.screen import Screen

from tui.widgets.main_menu import MainMenu, ListView

class MainMenuScreen(Screen):

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self.notify("Une option a été choisie")

    def compose(self) -> ComposeResult:
        yield MainMenu()