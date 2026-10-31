from textual.app import ComposeResult
from textual.widgets import Label, ListItem, ListView


class DataManagerMenu(ListView):

    def compose(self) -> ComposeResult:
        yield ListItem(Label("Import file"), id="import_file")
        yield ListItem(Label("Create database"), id="create_database")
        yield ListItem(Label("View imported files"), id="view_imported_files")
        yield ListItem(Label("Delete database"), id="delete_database")
        yield ListItem(Label("Delete all", id="delete_all"))