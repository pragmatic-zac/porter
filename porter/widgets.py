"""Custom widgets for Porter."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Label, Select, Static, TabPane, TabbedContent, TextArea


class HeaderRow(Horizontal):
    """A single header key-value pair row."""

    def __init__(self, key: str = "", value: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self.header_key = key
        self.header_value = value

    def compose(self) -> ComposeResult:
        """Create key and value inputs."""
        yield Input(placeholder="Header name", value=self.header_key, classes="header-key")
        yield Input(placeholder="Header value", value=self.header_value, classes="header-value")


class HeadersEditor(Vertical):
    """Widget for editing HTTP headers as key-value pairs."""

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Label("Headers")
        # Container for header rows
        with VerticalScroll(id="headers-container"):
            yield HeaderRow(id="header-row-0")
        with Horizontal(id="headers-buttons"):
            yield Button("Add Header", id="add-header-button", variant="success")
            yield Button("Remove Last", id="remove-header-button", variant="error")


class BodyEditor(Vertical):
    """Widget for editing HTTP request body."""

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Label("Body")
        yield TextArea(
            id="body-text",
            language="json",
            theme="monokai",
        )


class ResponseViewer(Vertical):
    """Widget for displaying HTTP response with tabs."""

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Label("Response", id="response-label")
        with TabbedContent(id="response-tabs"):
            with TabPane("Body", id="body-tab"):
                yield TextArea(
                    id="response-body",
                    language="json",
                    theme="monokai",
                    read_only=True,
                )
            with TabPane("Headers", id="headers-tab"):
                yield TextArea(
                    id="response-headers",
                    read_only=True,
                )
            with TabPane("Raw", id="raw-tab"):
                yield TextArea(
                    id="response-raw",
                    read_only=True,
                )


class RequestEditor(Vertical):
    """Widget for editing HTTP request details."""

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        # Method selector and URL input in one row
        with Horizontal(id="request-line"):
            yield Select(
                options=[
                    ("GET", "GET"),
                    ("POST", "POST"),
                    ("PUT", "PUT"),
                    ("PATCH", "PATCH"),
                    ("DELETE", "DELETE"),
                    ("HEAD", "HEAD"),
                    ("OPTIONS", "OPTIONS"),
                ],
                value="GET",
                id="method-select",
            )
            yield Input(
                placeholder="Enter URL (e.g., https://api.example.com/users)",
                id="url-input",
            )
            yield Button("Send", variant="primary", id="send-button")

        # Headers editor
        yield HeadersEditor()

        # Body editor
        yield BodyEditor()
