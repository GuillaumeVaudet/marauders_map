from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Label


class ScreenHeader(Horizontal):
    """Shared top bar: current section on the left, context on the right."""

    def __init__(self, section: str, context: str = "") -> None:
        super().__init__()
        self.section = section
        self.context = context

    def compose(self) -> ComposeResult:
        yield Label(
            f"MARAUDERS // {self.section}",
            classes="header-section",
            markup=False,
        )
        yield Label(self.context, classes="header-context", markup=False)
