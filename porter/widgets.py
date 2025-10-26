"""Custom widgets for Porter."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.events import Key
from textual.widgets import Button, Input, Label, Select, Static, TabPane, TabbedContent, TextArea


def get_navigable_widgets(screen):
    """Get all navigable widgets in DOM order."""
    request_editor = screen.query_one("RequestEditor")

    # Walk through all descendant widgets in DOM order and filter to navigable types
    navigable = [
        widget for widget in request_editor.walk_children()
        if isinstance(widget, (Select, NavigableInput, NavigableButton, NavigableTextArea))
    ]

    return navigable


class NavigableInput(Input):
    """Input widget that supports arrow keys for focus navigation."""

    def on_key(self, event: Key) -> None:
        """Handle arrow keys for focus navigation."""
        if event.key == "up":
            event.prevent_default()
            self._focus_previous()
        elif event.key == "down":
            event.prevent_default()
            self._focus_next()
        elif event.key == "left":
            # Only navigate if cursor is at the start
            if self.cursor_position == 0:
                event.prevent_default()
                self._focus_previous()
        elif event.key == "right":
            # Only navigate if cursor is at the end
            if self.cursor_position == len(self.value):
                event.prevent_default()
                self._focus_next()

    def _focus_previous(self) -> None:
        """Focus the previous navigable widget."""
        focusable = get_navigable_widgets(self.screen)
        if not focusable:
            return

        try:
            current_index = focusable.index(self)
            if current_index > 0:
                focusable[current_index - 1].focus()
        except (ValueError, IndexError):
            pass

    def _focus_next(self) -> None:
        """Focus the next navigable widget."""
        focusable = get_navigable_widgets(self.screen)
        if not focusable:
            return

        try:
            current_index = focusable.index(self)
            if current_index < len(focusable) - 1:
                focusable[current_index + 1].focus()
        except (ValueError, IndexError):
            pass


class NavigableTextArea(TextArea):
    """TextArea widget that supports arrow key navigation at boundaries."""

    def on_key(self, event: Key) -> None:
        """Handle arrow keys for focus navigation at boundaries."""
        if event.key == "up":
            # Only navigate if cursor is on the first line
            if self.cursor_location[0] == 0:
                event.prevent_default()
                self._focus_previous()
        elif event.key == "left":
            # Only navigate if cursor is at the very start
            if self.cursor_location == (0, 0):
                event.prevent_default()
                self._focus_previous()

    def _focus_previous(self) -> None:
        """Focus the previous navigable widget."""
        focusable = get_navigable_widgets(self.screen)
        if not focusable:
            return

        try:
            current_index = focusable.index(self)
            if current_index > 0:
                focusable[current_index - 1].focus()
        except (ValueError, IndexError):
            pass


class NavigableButton(Button):
    """Button widget that supports all arrow keys for focus navigation."""

    def on_key(self, event: Key) -> None:
        """Handle arrow keys for focus navigation."""
        if event.key in ("up", "down", "left", "right"):
            event.prevent_default()
            if event.key == "up":
                self._focus_previous()
            elif event.key == "down":
                self._focus_next()
            elif event.key == "left":
                self._focus_previous()
            elif event.key == "right":
                self._focus_next()

    def _focus_previous(self) -> None:
        """Focus the previous navigable widget."""
        focusable = get_navigable_widgets(self.screen)
        if not focusable:
            return

        try:
            current_index = focusable.index(self)
            if current_index > 0:
                focusable[current_index - 1].focus()
        except (ValueError, IndexError):
            pass

    def _focus_next(self) -> None:
        """Focus the next navigable widget."""
        focusable = get_navigable_widgets(self.screen)
        if not focusable:
            return

        try:
            current_index = focusable.index(self)
            if current_index < len(focusable) - 1:
                focusable[current_index + 1].focus()
        except (ValueError, IndexError):
            pass


class HeaderRow(Horizontal):
    """A single header key-value pair row."""

    def __init__(self, key: str = "", value: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self.header_key = key
        self.header_value = value

    def compose(self) -> ComposeResult:
        """Create key and value inputs."""
        yield NavigableInput(placeholder="Header name", value=self.header_key, classes="header-key")
        yield NavigableInput(placeholder="Header value", value=self.header_value, classes="header-value")


class HeadersEditor(Vertical):
    """Widget for editing HTTP headers as key-value pairs."""

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Label("Headers")
        # Container for header rows
        with VerticalScroll(id="headers-container"):
            yield HeaderRow()
        with Horizontal(id="headers-buttons"):
            yield NavigableButton("Add Header", id="add-header-button", variant="success")
            yield NavigableButton("Remove Last", id="remove-header-button", variant="error")


class BodyEditor(Vertical):
    """Widget for editing HTTP request body."""

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Label("Body")
        yield NavigableTextArea(
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
            yield NavigableInput(
                placeholder="Enter URL (e.g., https://api.example.com/users)",
                id="url-input",
            )
            yield NavigableButton("Send", variant="primary", id="send-button")

        # Headers editor
        yield HeadersEditor()

        # Body editor
        yield BodyEditor()
