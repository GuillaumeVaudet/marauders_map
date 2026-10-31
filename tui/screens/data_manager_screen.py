from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, ListView, Footer, DirectoryTree
from tui.widgets.data_manager_menu import DataManagerMenu
from tui.screens.file_browser_screen import FileBrowserScreen
from tui.screens.create_database_screen import CreateDatabaseScreen

class DataManagerScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def on_list_view_selected(self, event: ListView.Selected):
        selected_id = event.item.id

        if selected_id == "import_file":
            self.app.push_screen(FileBrowserScreen())
        elif selected_id == "create_database":
            self.app.push_screen(CreateDatabaseScreen())
        else:
            self.notify(f"Data Manager: {selected_id}")

    def compose(self) -> ComposeResult:
        yield DataManagerMenu()
        yield Footer()