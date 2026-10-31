from pathlib import Path

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, Label
from db.database import import_file


class CityInputScreen(ModalScreen):
    BINDINGS = [("escape", "app.pop_screen", "Cancel")]

    def __init__(self, file_path: Path) -> None:
        super().__init__()
        self.file_path = file_path

    def on_input_submitted(self, event: Input.Submitted) -> None:
        city = event.value.strip()
        if not city:
            self.notify("Please enter a city name", severity="warning")
            return

        imported = import_file(self.file_path, city)
        if imported:
            self.notify(f"Imported: {self.file_path.name} into {city}")
        else:
            self.notify(f"Already imported: {self.file_path.name}")
        self.app.pop_screen()

    def compose(self) -> ComposeResult:
        yield Label("Enter city name:")
        yield Input(placeholder="City name (database)")