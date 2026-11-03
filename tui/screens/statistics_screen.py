from rich.text import Text
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Label
from tui.widgets.screen_header import ScreenHeader
from db.database import (
    connect,
    get_network_count,
    get_observation_count,
    get_hidden_count,
    get_encryption_breakdown,
)


class StatisticsScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def __init__(self, city: str) -> None:
        super().__init__()
        self.city = city

    def on_mount(self) -> None:
        connection = connect(self.city)
        networks = get_network_count(connection)
        observations = get_observation_count(connection)
        hidden = get_hidden_count(connection)
        breakdown = get_encryption_breakdown(connection)
        connection.close()

        self.query_one("#totals", Label).update(
            f"NETWORKS [$secondary b]{networks}[/]    "
            f"OBSERVATIONS [$secondary b]{observations}[/]    "
            f"HIDDEN [$secondary b]{hidden}[/]"
        )
        table = self.query_one(DataTable)
        table.add_columns("Encryption", "Count")
        for encryption, count in breakdown:
            table.add_row(Text(str(encryption)), Text(str(count)))

    def compose(self) -> ComposeResult:
        yield ScreenHeader("STATISTICS", self.city)
        yield Label("", id="totals")
        yield DataTable(cursor_type="row", zebra_stripes=True)
        yield Footer()