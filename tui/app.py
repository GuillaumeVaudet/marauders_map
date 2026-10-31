from textual.app import App
from tui.screens.main_menu_screen import MainMenuScreen

class MaraudeurApp(App):
    """A Textual app to manage wardriving data"""

    def on_mount(self) -> None:
        self.push_screen(MainMenuScreen())