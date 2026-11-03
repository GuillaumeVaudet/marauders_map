from rich.text import Text
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Footer
from db.database import connect, get_networks
from tui.screens.network.network_detail_screen import NetworkDetailScreen
from tui.widgets.screen_header import ScreenHeader


class NetworkListScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def __init__(self, city: str) -> None:
        super().__init__()
        self.city = city

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("BSSID", "SSID", "Encryption")
        connection = connect(self.city)
        rows = get_networks(connection)
        connection.close()
        for row in rows:
            bssid = row[0]
            table.add_row(*(Text(str(cell)) for cell in row), key=bssid)

    def on_data_table_row_selected(
        self, event: DataTable.RowSelected
    ) -> None:
        bssid = event.row_key.value
        self.app.push_screen(NetworkDetailScreen(self.city, bssid))

    def compose(self) -> ComposeResult:
        yield ScreenHeader("NETWORKS", self.city)
        yield DataTable(cursor_type="row", zebra_stripes=True)
        yield Footer()