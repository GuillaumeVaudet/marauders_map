from textual.app import App, ComposeResult
from tui.widgets.main_menu import MainMenu

class MaraudeurApp(App):
    """A Textual app to manage wardriving data"""

    def compose(self) -> ComposeResult:
        yield MainMenu()