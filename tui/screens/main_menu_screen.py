from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import ListView

from tui.screens.network.network_database_select_screen import NetworkDatabaseSelectScreen
from tui.screens.data_manager.data_manager_screen import DataManagerScreen
from tui.widgets.main_menu import MainMenu

class MainMenuScreen(Screen):

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        selected_id = event.item.id

        if selected_id == "quit":
            self.app.exit()
        elif selected_id == "view_networks":
            self.app.push_screen(NetworkDatabaseSelectScreen())
        elif selected_id == "data_manager":
            self.app.push_screen(DataManagerScreen())
        else:
            self.notify(f"Selected: {selected_id}")

    def compose(self) -> ComposeResult:
        yield MainMenu()