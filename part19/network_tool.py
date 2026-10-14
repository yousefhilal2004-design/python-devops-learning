
import argparse
import logging
import socket
import sys
import time

from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests


BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "reports"
LOG_FILE = REPORT_DIR / "network.log"


def configure_logging(verbose: bool) -> logging.Logger:
    """Configure UTC console and file logging."""

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("network_tool")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s UTC | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    formatter.converter = time.gmtime

    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(
        logging.DEBUG if verbose else logging.INFO
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def validate_url(url: str) -> bool:
    """Check basic URL structure."""

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return False

    if not parsed.hostname:
        return False

    try:
        port = parsed.port
    except ValueError:
        return False

    if port is not None and not 1 <= port <= 65535:
        return False

    return True


def resolve_dns(host: str) -> dict:
    """Resolve a hostname and collect unique IP addresses."""

    started = time.perf_counter()

    result = {
        "check": "DNS",
        "target": host,
        "status": "FAILED",
        "duration_seconds": 0.0,
        "details": [],
        "error": "",
    }

    try:
        addresses = socket.getaddrinfo(
            host,
            None,
            type=socket.SOCK_STREAM,
        )

        unique_addresses = sorted({
            item[4][0]
            for item in addresses
        })

        result["details"] = unique_addresses
        result["status"] = (
            "SUCCESS" if unique_addresses else "FAILED"
        )

        if not unique_addresses:
            result["error"] = "No addresses returned"

    except (socket.gaierror, OSError) as exc:
        result["error"] = str(exc)

    finally:
        result["duration_seconds"] = (
            time.perf_counter() - started
        )

    return result


def check_tcp(
    host: str,
    port: int,
    timeout: float,
) -> dict:
    """Check TCP connectivity to a single destination."""

    started = time.perf_counter()

    result = {
        "check": "TCP",
        "target": f"{host}:{port}",
        "status": "FAILED",
        "duration_seconds": 0.0,
        "details": [],
        "error": "",
    }

    try:
        with socket.create_connection(
            (host, port),
            timeout=timeout,
        ):
            result["status"] = "SUCCESS"
            result["details"] = [
                f"TCP connection established to {host}:{port}"
            ]

    except (OSError, TimeoutError) as exc:
        result["error"] = str(exc)

    finally:
        result["duration_seconds"] = (
            time.perf_counter() - started
        )

    return result


def check_http(url: str, timeout: float) -> dict:
    """Make an HTTP GET request and record the result."""

    started = time.perf_counter()

    result = {
        "check": "HTTP",
        "target": url,
        "status": "FAILED",
        "duration_seconds": 0.0,
        "details": [],
        "error": "",
    }

    try:
        response = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
        )

        result["duration_seconds"] = (
            time.perf_counter() - started
        )

        result["details"] = [
            f"HTTP status: {response.status_code}",
            f"Final URL: {response.url}",
            (
                "Content type: "
                f"{response.headers.get('Content-Type', 'unknown')}"
            ),
        ]

        if 200 <= response.status_code < 400:
            result["status"] = "SUCCESS"
        else:
            result["status"] = "FAILED"
            result["error"] = (
                f"Unexpected HTTP status: {response.status_code}"
            )

    except requests.exceptions.Timeout:
        result["error"] = "HTTP request timed out"

    except requests.exceptions.SSLError as exc:
        result["error"] = f"TLS error: {exc}"

    except requests.exceptions.ConnectionError as exc:
        result["error"] = f"Connection error: {exc}"

    except requests.exceptions.RequestException as exc:
        result["error"] = f"Request error: {exc}"

    finally:
        result["duration_seconds"] = (
            time.perf_counter() - started
        )

    return result


def build_report(
    target: str,
    results: list[dict],
) -> str:
    """Build a readable network diagnostic report."""

    lines = [
        "PYTHON DEVOPS NETWORK DIAGNOSTIC REPORT",
        "=" * 48,
        f"Generated at UTC: {datetime.now(timezone.utc).isoformat()}",
        f"Target: {target}",
        "",
        "CHECK RESULTS",
        "-" * 48,
    ]

    for result in results:
        lines.append(f"Check: {result['check']}")
        lines.append(f"Target: {result['target']}")
        lines.append(f"Status: {result['status']}")
        lines.append(
            f"Duration: {result['duration_seconds']:.4f} seconds"
        )

        for detail in result["details"]:
            lines.append(f"Detail: {detail}")

        if result["error"]:
            lines.append(f"Error: {result['error']}")

        lines.append("-" * 48)

    failed = sum(
        result["status"] == "FAILED"
        for result in results
    )

    successful = sum(
        result["status"] == "SUCCESS"
        for result in results
    )

    lines.extend([
        "",
        "SUMMARY",
        f"Successful checks: {successful}",
        f"Failed checks: {failed}",
        f"Total checks: {len(results)}",
        "",
    ])

    return "\n".join(lines)


def save_report(report: str) -> Path:
    """Save the report using a UTC timestamp."""

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    report_path = (
        REPORT_DIR / f"network_report_{timestamp}.txt"
    )

    report_path.write_text(
        report,
        encoding="utf-8",
    )

    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Python network diagnostic toolkit"
    )

    parser.add_argument(
        "--url",
        default="https://example.com",
        help="HTTP or HTTPS URL to check",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="TCP port; defaults to the URL port or 443/80",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Network timeout in seconds (default: 5)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show debug-level logs",
    )

    args = parser.parse_args()

    if not validate_url(args.url):
        print(
            "Error: provide a valid HTTP or HTTPS URL.",
            file=sys.stderr,
        )
        return 2

    if not 0 < args.timeout <= 60:
        print(
            "Error: timeout must be greater than 0 and at most 60 seconds.",
            file=sys.stderr,
        )
        return 2

    parsed_url = urlparse(args.url)
    host = parsed_url.hostname

    try:
        url_port = parsed_url.port
    except ValueError:
        print("Error: invalid URL port.", file=sys.stderr)
        return 2

    port = args.port

    if port is None:
        port = url_port or (
            443 if parsed_url.scheme == "https" else 80
        )

    if not 1 <= port <= 65535:
        print(
            "Error: TCP port must be between 1 and 65535.",
            file=sys.stderr,
        )
        return 2

    try:
        logger = configure_logging(args.verbose)
    except OSError as exc:
        print(
            f"Logging setup failed: {exc}",
            file=sys.stderr,
        )
        return 2

    logger.info("Network diagnostic started for %s", host)

    try:
        results = []

        logger.info("Starting DNS check")
        dns_result = resolve_dns(host)
        results.append(dns_result)

        logger.info(
            "DNS result: %s",
            dns_result["status"],
        )

        logger.info("Starting TCP check")
        tcp_result = check_tcp(
            host,
            port,
            args.timeout,
        )
        results.append(tcp_result)

        logger.info(
            "TCP result: %s",
            tcp_result["status"],
        )

        logger.info("Starting HTTP check")
        http_result = check_http(
            args.url,
            args.timeout,
        )
        results.append(http_result)

        logger.info(
            "HTTP result: %s",
            http_result["status"],
        )

        report = build_report(args.url, results)
        report_path = save_report(report)

        print(report)
        print(f"\nReport saved: {report_path}")

        logger.info("Report saved: %s", report_path)
        logger.info("Network diagnostic finished")

        if any(
            result["status"] == "FAILED"
            for result in results
        ):
            return 1

        return 0

    except (OSError, UnicodeError) as exc:
        logger.exception("Unable to generate network report")
        print(
            f"Diagnostic failed: {exc}",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

