from urllib.parse import urlparse

import requests


def check_endpoint(url: str, timeout: float = 5.0) -> dict:
    """Check an HTTP endpoint and return a structured result."""
    if not isinstance(url, str) or not url.strip():
        raise ValueError("url must be a non-empty string")

    if not isinstance(timeout, (int, float)) or isinstance(timeout, bool):
        raise TypeError("timeout must be a number")

    if timeout <= 0:
        raise ValueError("timeout must be greater than zero")

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("url must be a valid HTTP or HTTPS URL")

    try:
        response = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
        )

        status_code = response.status_code
        healthy = 200 <= status_code < 400

        return {
            "url": url,
            "status_code": status_code,
            "healthy": healthy,
            "message": (
                "Endpoint is healthy"
                if healthy
                else "Endpoint returned an error status"
            ),
        }

    except requests.Timeout:
        return {
            "url": url,
            "status_code": None,
            "healthy": False,
            "message": "Request timed out",
        }

    except requests.RequestException as exc:
        return {
            "url": url,
            "status_code": None,
            "healthy": False,
            "message": f"Request failed: {type(exc).__name__}",
        }
