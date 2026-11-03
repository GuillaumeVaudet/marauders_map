from textual.app import ComposeResult
from textual.widgets import Label, ListItem, ListView


class DataManagerMenu(ListView):
    BORDER_TITLE = "// DATA MANAGER"

    def compose(self) -> ComposeResult:
        yield ListItem(Label("IMPORT FILE"), id="import_file")
        yield ListItem(Label("CREATE DATABASE"), id="create_database")
        yield ListItem(Label("VIEW IMPORTED FILES"), id="view_imported_files")
        yield ListItem(Label("DELETE DATABASE"), id="delete_database")
        yield ListItem(Label("DELETE ALL"),  id="delete_all")