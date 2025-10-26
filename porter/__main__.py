"""Main entry point for the porter CLI."""

import sys
from porter.app import PorterApp


def main():
    """Run the Porter TUI application."""
    app = PorterApp()
    app.run()


if __name__ == "__main__":
    sys.exit(main())
