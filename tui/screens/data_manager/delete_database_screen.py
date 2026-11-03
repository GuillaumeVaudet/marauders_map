from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import ListView, ListItem, Label, Footer
from db.database import list_databases
from tui.screens.data_manager.confirm_delete_screen import ConfirmDeleteScreen
from tui.widgets.screen_header import ScreenHeader


class DeleteDatabaseScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        city = str(event.item.query_one(Label).content)
        self.app.push_screen(ConfirmDeleteScreen(city))

    def compose(self) -> ComposeResult:
        yield ScreenHeader("DELETE DATABASE", "SELECT DATABASE")
        yield ListView(
            *[ListItem(Label(city)) for city in list_databases()]
        )
        yield Footer()