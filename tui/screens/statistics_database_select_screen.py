from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import ListView, ListItem, Label, Footer
from db.database import list_databases
from tui.screens.statistics_screen import StatisticsScreen
from tui.widgets.screen_header import ScreenHeader


class StatisticsDatabaseSelectScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        city = str(event.item.query_one(Label).content)
        self.app.push_screen(StatisticsScreen(city))

    def compose(self) -> ComposeResult:
        yield ScreenHeader("STATISTICS", "SELECT DATABASE")
        yield ListView(
            *[ListItem(Label(city)) for city in list_databases()]
        )
        yield Footer()