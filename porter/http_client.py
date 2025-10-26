"""HTTP client for making requests."""

import json
import time
from typing import Any, Dict, Optional

import httpx


class HTTPResponse:
    """Container for HTTP response data."""

    def __init__(
        self,
        status_code: int,
        headers: Dict[str, str],
        body: str,
        duration_ms: int,
        error: Optional[str] = None,
    ):
        self.status_code = status_code
        self.headers = headers
        self.body = body
        self.duration_ms = duration_ms
        self.error = error

    @property
    def status_text(self) -> str:
        """Get human-readable status text."""
        status_texts = {
            200: "OK",
            201: "Created",
            204: "No Content",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable",
        }
        text = status_texts.get(self.status_code, "")
        return f"{self.status_code} {text}" if text else str(self.status_code)


async def send_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    body: Optional[str] = None,
    verify_ssl: bool = True,
    timeout: float = 30.0,
) -> HTTPResponse:
    """
    Send an HTTP request and return the response.

    Args:
        method: HTTP method (GET, POST, etc.)
        url: URL to request
        headers: Optional headers dict
        body: Optional request body
        verify_ssl: Whether to verify SSL certificates
        timeout: Request timeout in seconds

    Returns:
        HTTPResponse object with response data
    """
    start_time = time.time()

    try:
        async with httpx.AsyncClient(verify=verify_ssl, timeout=timeout) as client:
            response = await client.request(
                method=method.upper(),
                url=url,
                headers=headers or {},
                content=body.encode() if body else None,
                follow_redirects=True,
            )

        duration_ms = int((time.time() - start_time) * 1000)

        # Truncate response body if too large (5MB limit)
        response_body = response.text
        max_size = 5 * 1024 * 1024  # 5MB
        if len(response_body) > max_size:
            response_body = response_body[:max_size] + "\n\n[Response truncated at 5MB]"

        return HTTPResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            body=response_body,
            duration_ms=duration_ms,
        )

    except httpx.TimeoutException:
        duration_ms = int((time.time() - start_time) * 1000)
        return HTTPResponse(
            status_code=0,
            headers={},
            body="",
            duration_ms=duration_ms,
            error=f"Request timeout after {timeout}s",
        )

    except httpx.ConnectError as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return HTTPResponse(
            status_code=0,
            headers={},
            body="",
            duration_ms=duration_ms,
            error=f"Connection error: {str(e)}",
        )

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return HTTPResponse(
            status_code=0,
            headers={},
            body="",
            duration_ms=duration_ms,
            error=f"Error: {str(e)}",
        )


def validate_url(url: str) -> tuple[bool, Optional[str]]:
    """
    Validate a URL.

    Args:
        url: URL to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url or not url.strip():
        return False, "URL cannot be empty"

    url = url.strip()

    if not (url.startswith("http://") or url.startswith("https://")):
        return False, "URL must start with http:// or https://"

    # Basic validation - httpx will do more thorough validation
    if " " in url:
        return False, "URL cannot contain spaces"

    return True, None
