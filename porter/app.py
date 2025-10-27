"""Main Textual application for Porter."""

import json

from textual.app import App, ComposeResult
from textual.containers import Horizontal as HorizontalContainer
from textual.widgets import Button, Header, Footer, Input, Label, Select, TextArea

from porter import collections
from porter.http_client import send_request, validate_url
from porter.widgets import HeaderRow, RequestEditor, ResponseViewer


class PorterApp(App):
    """A Textual app for making HTTP requests."""

    TITLE = "Porter - HTTP Client"
    SUB_TITLE = "Untitled Request"
    CSS = """
    Screen {
        background: $background;
    }

    #main-container {
        height: 100%;
    }

    RequestEditor {
        width: 1fr;
        height: 100%;
        padding: 1;
    }

    ResponseViewer {
        width: 1fr;
        height: 100%;
        padding: 1;
        border-left: solid $primary;
    }

    #request-name {
        width: 100%;
        height: 3;
        margin-bottom: 1;
        border: solid $primary;
    }

    #request-line {
        height: 3;
        width: 100%;
    }

    #method-select {
        width: 15;
    }

    #url-input {
        width: 1fr;
    }

    #send-button {
        width: 12;
    }

    HeadersEditor {
        height: 15;
        margin-top: 1;
    }

    #headers-container {
        height: 1fr;
        border: solid $primary;
    }

    HeaderRow {
        height: 3;
        width: 100%;
    }

    .header-key {
        width: 1fr;
    }

    .header-value {
        width: 2fr;
    }

    #headers-buttons {
        height: 3;
        width: 100%;
    }

    #add-header-button, #remove-header-button {
        width: 1fr;
    }

    BodyEditor {
        height: 1fr;
        margin-top: 1;
    }

    #body-text {
        height: 1fr;
    }

    #response-tabs {
        height: 1fr;
    }

    #response-body, #response-headers, #response-raw {
        height: 1fr;
    }

    Label {
        margin-bottom: 1;
        text-style: bold;
    }
    """

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+enter", "send_request", "Send"),
        ("ctrl+shift+f", "format_json", "Format JSON"),
        ("ctrl+k", "clear_body", "Clear Body"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with HorizontalContainer(id="main-container"):
            yield RequestEditor()
            yield ResponseViewer()
        yield Footer()

    def on_mount(self) -> None:
        """Load saved request on app startup."""
        saved_request = collections.load_request()
        if saved_request:
            self._load_request_into_ui(saved_request)

    def _load_request_into_ui(self, request: collections.Request) -> None:
        """Populate the UI with a saved request."""
        # Set name
        name_input = self.query_one("#request-name", Input)
        name_input.value = request.name
        self.sub_title = request.name

        # Set method
        method_select = self.query_one("#method-select", Select)
        method_select.value = request.method

        # Set URL
        url_input = self.query_one("#url-input", Input)
        url_input.value = request.url

        # Set body
        body_area = self.query_one("#body-text", TextArea)
        body_area.text = request.body

        # Set headers - clear existing rows first, then add new ones
        container = self.query_one("#headers-container")
        # Remove all existing header rows
        for row in container.query(HeaderRow):
            row.remove()

        # Add header rows for saved headers
        if request.headers:
            for key, value in request.headers.items():
                row = HeaderRow(key=key, value=value)
                container.mount(row)
        else:
            # Add one empty row if no headers
            container.mount(HeaderRow())

    def _get_current_request(self) -> collections.Request:
        """Get the current request state from the UI."""
        name = self.query_one("#request-name", Input).value
        method = self.query_one("#method-select", Select).value
        url = self.query_one("#url-input", Input).value
        headers = self._get_headers_from_ui()
        body = self.query_one("#body-text", TextArea).text

        return collections.Request(
            name=name,
            method=method,
            url=url,
            headers=headers,
            body=body,
        )

    def action_quit(self) -> None:
        """Save current request and quit the application."""
        # Save current request before exiting
        current_request = self._get_current_request()
        collections.save_request(current_request)
        self.exit()

    async def action_send_request(self) -> None:
        """Send the HTTP request."""
        # Gather request data from UI
        method = self.query_one("#method-select", Select).value
        url_input = self.query_one("#url-input", Input)
        url = url_input.value.strip()

        # Validate URL
        is_valid, error_msg = validate_url(url)
        if not is_valid:
            self._display_error(error_msg)
            url_input.focus()
            return

        # Gather headers
        headers = self._get_headers_from_ui()

        # Get body
        body_text = self.query_one("#body-text", TextArea).text.strip()
        body = body_text if body_text else None

        # Update response label to show loading
        response_label = self.query_one("#response-label", Label)
        response_label.update("Response - Loading...")

        # Send the request
        response = await send_request(
            method=method,
            url=url,
            headers=headers,
            body=body,
            verify_ssl=True,  # TODO: Add UI toggle for this
            timeout=30.0,
        )

        # Display the response
        self._display_response(response)

    def action_format_json(self) -> None:
        """Format the JSON in the request body editor."""
        body_area = self.query_one("#body-text", TextArea)
        body_text = body_area.text.strip()

        if not body_text:
            self.notify("Body is empty", severity="warning")
            return

        try:
            # Parse and re-format the JSON
            parsed = json.loads(body_text)
            formatted = json.dumps(parsed, indent=2)
            body_area.text = formatted
            self.notify("JSON formatted successfully", severity="information")
        except json.JSONDecodeError as e:
            self.notify(f"Invalid JSON: {str(e)}", severity="error")

    def action_clear_body(self) -> None:
        """Clear the request body editor."""
        body_area = self.query_one("#body-text", TextArea)
        body_area.text = ""
        body_area.focus()
        self.notify("Body cleared", severity="information")

    def _get_headers_from_ui(self) -> dict[str, str]:
        """Extract headers from the UI."""
        headers = {}
        container = self.query_one("#headers-container")
        for row in container.query(HeaderRow):
            inputs = row.query(Input)
            if len(inputs) == 2:
                key_input, value_input = inputs
                key = key_input.value.strip()
                value = value_input.value.strip()
                if key:  # Only add non-empty keys
                    headers[key] = value
        return headers

    def _display_response(self, response) -> None:
        """Display the HTTP response in the response viewer."""
        # Update response label with status and time
        response_label = self.query_one("#response-label", Label)
        if response.error:
            response_label.update(f"Response - Error ({response.duration_ms}ms)")
        else:
            response_label.update(f"Response - {response.status_text} ({response.duration_ms}ms)")

        # Display body
        body_area = self.query_one("#response-body", TextArea)
        if response.error:
            body_area.text = response.error
        else:
            # Try to pretty-print JSON
            try:
                parsed = json.loads(response.body)
                body_area.text = json.dumps(parsed, indent=2)
            except (json.JSONDecodeError, ValueError):
                # Not JSON, display as-is
                body_area.text = response.body

        # Display headers
        headers_area = self.query_one("#response-headers", TextArea)
        if response.error:
            headers_area.text = ""
        else:
            headers_text = "\n".join(
                f"{key}: {value}" for key, value in response.headers.items()
            )
            headers_area.text = headers_text

        # Display raw response
        raw_area = self.query_one("#response-raw", TextArea)
        if response.error:
            raw_area.text = f"Error: {response.error}\nDuration: {response.duration_ms}ms"
        else:
            raw_text = f"{response.status_text}\n"
            raw_text += f"Duration: {response.duration_ms}ms\n\n"
            raw_text += "Headers:\n"
            raw_text += "\n".join(
                f"{key}: {value}" for key, value in response.headers.items()
            )
            raw_text += "\n\nBody:\n"
            raw_text += response.body
            raw_area.text = raw_text

    def _display_error(self, error: str) -> None:
        """Display an error message in the response viewer."""
        response_label = self.query_one("#response-label", Label)
        response_label.update(f"Response - Error")

        # Show error in all tabs
        for area_id in ["#response-body", "#response-headers", "#response-raw"]:
            area = self.query_one(area_id, TextArea)
            area.text = error

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "add-header-button":
            self._add_header_row()
        elif event.button.id == "remove-header-button":
            self._remove_header_row()
        elif event.button.id == "send-button":
            self.action_send_request()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes."""
        if event.input.id == "request-name":
            # Update subtitle to show the request name
            name = event.value.strip()
            self.sub_title = name if name else "Untitled Request"

    def _add_header_row(self) -> None:
        """Add a new header row to the headers container."""
        container = self.query_one("#headers-container")
        new_row = HeaderRow()
        container.mount(new_row)

    def _remove_header_row(self) -> None:
        """Remove the last header row from the headers container."""
        container = self.query_one("#headers-container")
        rows = container.query(HeaderRow)
        if len(rows) > 0:
            rows.last().remove()
