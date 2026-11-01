from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Label, Button
from db.database import delete_all_databases


class ConfirmDeleteAllScreen(ModalScreen):
    BINDINGS = [("escape", "app.pop_screen", "Cancel")]

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            count = delete_all_databases()
            self.notify(f"{count} database(s) deleted")
        self.app.pop_screen()

    def compose(self) -> ComposeResult:
        yield Label("Delete ALL databases? This cannot be undone.")
        yield Button("Yes, delete all", id="confirm", variant="error")
        yield Button("Cancel", id="cancel")