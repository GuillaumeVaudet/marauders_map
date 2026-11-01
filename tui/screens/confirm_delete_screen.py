from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Label, Button
from db.database import delete_database


class ConfirmDeleteScreen(ModalScreen):
    BINDINGS = [("escape", "app.pop_screen", "Cancel")]

    def __init__(self, city: str) -> None:
        super().__init__()
        self.city = city

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            deleted = delete_database(self.city)
            if deleted:
                self.notify(f"Database deleted: {self.city}")
            else:
                self.notify(
                    f"Database not found: {self.city}",
                    severity="warning",
                )
        self.app.pop_screen()

    def compose(self) -> ComposeResult:
        yield Label(f"Delete database '{self.city}' ?")
        yield Button("Yes, delete", id="confirm", variant="error")
        yield Button("Cancel", id="cancel")