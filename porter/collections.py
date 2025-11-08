"""Collections management for saving and loading HTTP requests."""

import json
from pathlib import Path
from typing import Optional


# Default storage location
PORTER_DIR = Path.home() / ".porter"
DEFAULT_COLLECTION = PORTER_DIR / "default.json"


class Request:
    """Represents an HTTP request that can be saved/loaded."""

    def __init__(
        self,
        method: str = "GET",
        url: str = "",
        headers: dict[str, str] | None = None,
        body: str = "",
        name: str = "Untitled Request",
    ):
        self.method = method
        self.url = url
        self.headers = headers or {}
        self.body = body
        self.name = name

    def to_dict(self) -> dict:
        """Convert request to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "method": self.method,
            "url": self.url,
            "headers": self.headers,
            "body": self.body,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Request":
        """Create a Request from a dictionary."""
        return cls(
            name=data.get("name", "Untitled Request"),
            method=data.get("method", "GET"),
            url=data.get("url", ""),
            headers=data.get("headers", {}),
            body=data.get("body", ""),
        )


def ensure_porter_dir() -> None:
    """Create ~/.porter/ directory if it doesn't exist."""
    PORTER_DIR.mkdir(parents=True, exist_ok=True)


def save_request(request: Request, collection_path: Path = DEFAULT_COLLECTION) -> None:
    """
    Save a request to a collection file.

    Args:
        request: The Request object to save
        collection_path: Path to the collection file (defaults to default.json)
    """
    ensure_porter_dir()

    # For now, we just save a single request
    # In Phase 2, we'll support multiple requests per collection
    data = {
        "version": "1.0",
        "requests": [request.to_dict()],
    }

    with open(collection_path, "w") as f:
        json.dump(data, f, indent=2)


def load_request(collection_path: Path = DEFAULT_COLLECTION) -> Optional[Request]:
    """
    Load the most recent request from a collection file.

    Args:
        collection_path: Path to the collection file (defaults to default.json)

    Returns:
        Request object if found, None otherwise
    """
    if not collection_path.exists():
        return None

    try:
        with open(collection_path, "r") as f:
            data = json.load(f)

        requests = data.get("requests", [])
        if not requests:
            return None

        # Return the first (and currently only) request
        return Request.from_dict(requests[0])

    except (json.JSONDecodeError, KeyError, IOError):
        # If the file is corrupted or invalid, return None
        return None


def list_collections() -> list[Path]:
    """
    List all collection files in ~/.porter/.

    Returns:
        List of Path objects for collection files
    """
    ensure_porter_dir()

    # Find all .json files in the porter directory
    collections = sorted(PORTER_DIR.glob("*.json"))
    return collections


def create_collection(name: str) -> Path:
    """
    Create a new empty collection file.

    Args:
        name: Name for the collection (without .json extension)

    Returns:
        Path to the created collection file
    """
    ensure_porter_dir()

    # Sanitize the name to make it a valid filename
    safe_name = name.strip().replace(" ", "-").lower()
    if not safe_name.endswith(".json"):
        safe_name += ".json"

    collection_path = PORTER_DIR / safe_name

    # Create empty collection with default structure
    data = {
        "version": "1.0",
        "requests": [],
    }

    with open(collection_path, "w") as f:
        json.dump(data, f, indent=2)

    return collection_path


def get_collection_name(collection_path: Path) -> str:
    """
    Get a display name for a collection from its path.

    Args:
        collection_path: Path to the collection file

    Returns:
        Display name (filename without .json extension)
    """
    return collection_path.stem.replace("-", " ").title()
