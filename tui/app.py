from textual.app import App
from tui.screens.main_menu_screen import MainMenuScreen
from tui.theme import NIGHT_CIRCUIT

class MaraudeurApp(App):
    """A Textual app to manage wardriving data"""
    CSS_PATH = "styles.tcss"

    def __init__(self) -> None:
        super().__init__()
        self.register_theme(NIGHT_CIRCUIT)
        self.theme = NIGHT_CIRCUIT.name

    def on_mount(self) -> None:
        self.push_screen(MainMenuScreen())