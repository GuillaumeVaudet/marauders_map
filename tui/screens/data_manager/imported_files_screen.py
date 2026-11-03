from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Footer
from db.database import connect, get_imported_files
from tui.widgets.screen_header import ScreenHeader


class ImportedFilesScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def __init__(self, city: str) -> None:
        super().__init__()
        self.city = city

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("File", "Imported at")
        connection = connect(self.city)
        rows = get_imported_files(connection)
        connection.close()
        table.add_rows(rows)

    def compose(self) -> ComposeResult:
        yield ScreenHeader("IMPORTED FILES", self.city)
        yield DataTable(cursor_type="row", zebra_stripes=True)
        yield Footer()