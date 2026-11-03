from rich.text import Text
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Footer
from db.database import connect, get_observations
from tui.widgets.screen_header import ScreenHeader


class NetworkDetailScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def __init__(self, city: str, bssid: str) -> None:
        super().__init__()
        self.city = city
        self.bssid = bssid

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Timestamp", "Latitude", "Longitude", "RSSI")
        connection = connect(self.city)
        rows = get_observations(connection, self.bssid)
        connection.close()
        for row in rows:
            table.add_row(*(Text(str(cell)) for cell in row))

    def compose(self) -> ComposeResult:
        yield ScreenHeader("OBSERVATIONS", f"{self.city} / {self.bssid}")
        yield DataTable(cursor_type="row", zebra_stripes=True)
        yield Footer()