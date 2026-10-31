from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DirectoryTree, Footer
from tui.screens.city_input_screen import CityInputScreen


class FileBrowserScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        self.app.push_screen(CityInputScreen(event.path))

    def compose(self) -> ComposeResult:
        yield DirectoryTree(".")
        yield Footer()