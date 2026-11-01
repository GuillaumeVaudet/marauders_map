from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, ListView, Footer, DirectoryTree
from tui.widgets.data_manager_menu import DataManagerMenu
from tui.screens.file_browser_screen import FileBrowserScreen
from tui.screens.create_database_screen import CreateDatabaseScreen
from tui.screens.database_select_screen import DatabaseSelectScreen
from tui.screens.delete_database_screen import DeleteDatabaseScreen
from tui.screens.confirm_delete_all_screen import ConfirmDeleteAllScreen


class DataManagerScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def on_list_view_selected(self, event: ListView.Selected):
        selected_id = event.item.id

        if selected_id == "import_file":
            self.app.push_screen(FileBrowserScreen())
        elif selected_id == "create_database":
            self.app.push_screen(CreateDatabaseScreen())
        elif selected_id == "view_imported_files":
            self.app.push_screen(DatabaseSelectScreen())
        elif selected_id == "delete_database":
            self.app.push_screen(DeleteDatabaseScreen())
        elif selected_id == "delete_all":
            self.app.push_screen(ConfirmDeleteAllScreen())
        else:
            self.notify(f"Data Manager: {selected_id}")

    def compose(self) -> ComposeResult:
        yield DataManagerMenu()
        yield Footer()