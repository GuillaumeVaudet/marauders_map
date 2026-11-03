from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import ListView, ListItem, Label, Footer
from db.database import list_databases
from tui.screens.data_manager.imported_files_screen import ImportedFilesScreen
from tui.widgets.screen_header import ScreenHeader


class DatabaseSelectScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        city = str(event.item.query_one(Label).content)
        self.app.push_screen(ImportedFilesScreen(city))

    def compose(self) -> ComposeResult:
        yield ScreenHeader("IMPORTED FILES", "SELECT DATABASE")
        yield ListView(
            *[ListItem(Label(city)) for city in list_databases()]
        )
        yield Footer()