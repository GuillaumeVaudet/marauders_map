from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Footer
from textual.containers import Vertical
from textual.widgets import ListView
from tui.widgets.main_menu import MainMenu
from tui.screens.network.network_database_select_screen import NetworkDatabaseSelectScreen
from tui.screens.data_manager.data_manager_screen import DataManagerScreen
from tui.screens.statistics_database_select_screen import StatisticsDatabaseSelectScreen

LOGO = r"""
███╗   ███╗ █████╗ ██████╗  █████╗ ██╗   ██╗██████╗ ███████╗██████╗ ███████╗
████╗ ████║██╔══██╗██╔══██╗██╔══██╗██║   ██║██╔══██╗██╔════╝██╔══██╗██╔════╝
██╔████╔██║███████║██████╔╝███████║██║   ██║██║  ██║█████╗  ██████╔╝███████╗
██║╚██╔╝██║██╔══██║██╔══██╗██╔══██║██║   ██║██║  ██║██╔══╝  ██╔══██╗╚════██║
██║ ╚═╝ ██║██║  ██║██║  ██║██║  ██║╚██████╔╝██████╔╝███████╗██║  ██║███████║
╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝
"""


class MainMenuScreen(Screen):

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        selected_id = event.item.id
        if selected_id == "quit":
            self.app.exit()
        elif selected_id == "view_networks":
            self.app.push_screen(NetworkDatabaseSelectScreen())
        elif selected_id == "data_manager":
            self.app.push_screen(DataManagerScreen())
        elif selected_id == "statistics":
            self.app.push_screen(StatisticsDatabaseSelectScreen())
        else:
            self.notify(f"Selected: {selected_id}")

    def compose(self) -> ComposeResult:
        with Vertical(id="menu-box"):
            yield Static(LOGO, id="logo")
            yield Static("M A P  //  WARDRIVING CONTROL DECK", id="subtitle")
            yield MainMenu()
        yield Footer()