from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label
from db.database import (
    connect,
    create_record_table,
    create_imported_file_table,
)


class CreateDatabaseScreen(ModalScreen):
    BINDINGS = [("escape", "app.pop_screen", "Cancel")]

    def on_input_submitted(self, event: Input.Submitted) -> None:
        city = event.value.strip()
        if not city:
            self.notify("Please enter a city name", severity="warning")
            return

        if Path(f"data/{city}.db").exists():
            self.notify(
                f"Database '{city}' already exists", severity="warning"
            )
            return

        connection = connect(city)
        create_record_table(connection)
        create_imported_file_table(connection)
        connection.commit()
        connection.close()

        self.notify(f"Database created: {city}")
        self.app.pop_screen()

    def compose(self) -> ComposeResult:
        with Vertical(classes="dialog") as dialog:
            dialog.border_title = "// CREATE DATABASE"
            yield Label("New database (city name):", classes="dialog-message")
            yield Input(placeholder="City name")