"""Main Textual application for Porter."""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer


class PorterApp(App):
    """A Textual app for making HTTP requests."""

    TITLE = "Porter - HTTP Client"
    CSS = """
    Screen {
        background: $background;
    }
    """

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
