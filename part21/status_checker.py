def classify_http_status(status_code: int) -> str:
    """Classify an HTTP status code."""
    if not isinstance(status_code, int) or isinstance(status_code, bool):
        raise TypeError("status_code must be an integer")

    if not 100 <= status_code <= 599:
        raise ValueError("status_code must be between 100 and 599")

    if 200 <= status_code <= 299:
        return "success"

    if 300 <= status_code <= 399:
        return "redirect"

    if 400 <= status_code <= 499:
        return "client_error"

    if 500 <= status_code <= 599:
        return "server_error"

    return "informational"
