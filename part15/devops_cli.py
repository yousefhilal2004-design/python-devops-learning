
import argparse
import json
import sys
import time

from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG = BASE_DIR / "config.json"
REPORT_DIR = BASE_DIR / "reports"

ENVIRONMENTS = [
    "development",
    "staging",
    "production",
]


def valid_timeout(value: str) -> float:
    """Parse and validate a request timeout."""

    try:
        timeout = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "Timeout must be a number."
        ) from error

    if not 0 < timeout <= 60:
        raise argparse.ArgumentTypeError(
            "Timeout must be greater than 0 and at most 60 seconds."
        )

    return timeout


def parse_args() -> argparse.Namespace:
    """Define the command-line interface."""

    parser = argparse.ArgumentParser(
        prog="devops-cli",
        description=(
            "Validate a JSON configuration and check API endpoints."
        ),
        epilog=(
            "Example: python devops_cli.py "
            "--config config.json --timeout 5 --verbose"
        ),
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to the JSON configuration file",
    )

    parser.add_argument(
        "--timeout",
        type=valid_timeout,
        default=None,
        help="Override the configured timeout in seconds (max 60)",
    )

    parser.add_argument(
        "--environment",
        choices=ENVIRONMENTS,
        default=None,
        help="Override the configured environment",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed information",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration without sending HTTP requests",
    )

    return parser.parse_args()


def load_config(path: Path) -> dict:
    """Load and validate JSON syntax."""

    try:
        with path.open("r", encoding="utf-8") as file:
            config = json.load(file)

    except FileNotFoundError as error:
        raise ValueError(
            f"Configuration file not found: {path}"
        ) from error

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON at line {error.lineno}, "
            f"column {error.colno}: {error.msg}"
        ) from error

    except OSError as error:
        raise ValueError(
            f"Could not read configuration: {error}"
        ) from error

    if not isinstance(config, dict):
        raise ValueError("Configuration must be a JSON object.")

    return config


def validate_config(config: dict) -> list[str]:
    """Validate required configuration fields."""

    errors = []

    app_name = config.get("app_name")
    environment = config.get("environment")
    timeout = config.get("timeout_seconds")
    endpoints = config.get("endpoints")

    if not isinstance(app_name, str) or not app_name.strip():
        errors.append("app_name must be a non-empty string.")

    if environment not in ENVIRONMENTS:
        errors.append(
            f"environment must be one of: {', '.join(ENVIRONMENTS)}."
        )

    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or not 0 < timeout <= 60
    ):
        errors.append(
            "timeout_seconds must be greater than 0 and at most 60."
        )

    if not isinstance(endpoints, list) or not endpoints:
        errors.append("endpoints must be a non-empty list.")
        return errors

    names = set()

    for index, endpoint in enumerate(endpoints, start=1):
        if not isinstance(endpoint, dict):
            errors.append(f"Endpoint {index} must be an object.")
            continue

        name = endpoint.get("name")
        url = endpoint.get("url")
        expected_status = endpoint.get("expected_status")

        if not isinstance(name, str) or not name.strip():
            errors.append(f"Endpoint {index}: name is required.")
        elif name in names:
            errors.append(f"Endpoint {index}: duplicate name {name!r}.")
        else:
            names.add(name)

        if not isinstance(url, str):
            errors.append(f"Endpoint {index}: url must be a string.")
        else:
            parsed = urlparse(url)

            if (
                parsed.scheme not in {"http", "https"}
                or not parsed.hostname
                or parsed.username is not None
                or parsed.password is not None
            ):
                errors.append(
                    f"Endpoint {index}: invalid HTTP(S) URL."
                )

        if (
            isinstance(expected_status, bool)
            or not isinstance(expected_status, int)
            or not 100 <= expected_status <= 599
        ):
            errors.append(
                f"Endpoint {index}: expected_status must be "
                "an integer between 100 and 599."
            )

    return errors


def check_endpoint(
    endpoint: dict,
    timeout: float,
    verbose: bool,
) -> dict:
    """Check one HTTP endpoint."""

    started = time.perf_counter()

    try:
        response = requests.get(
            endpoint["url"],
            headers={"Accept": "application/json"},
            timeout=timeout,
        )

        elapsed_ms = (time.perf_counter() - started) * 1000
        status_ok = (
            response.status_code == endpoint["expected_status"]
        )

        message = (
            "Expected status received."
            if status_ok
            else "Unexpected HTTP status."
        )

        if verbose:
            print(f"  Final URL: {response.url}")
            print(f"  Content-Type: "
                  f"{response.headers.get('Content-Type', 'unknown')}")

        return {
            "name": endpoint["name"],
            "url": endpoint["url"],
            "status": "SUCCESS" if status_ok else "FAILED",
            "http_status": response.status_code,
            "expected_status": endpoint["expected_status"],
            "response_time_ms": round(elapsed_ms, 2),
            "message": message,
        }

    except requests.exceptions.Timeout:
        elapsed_ms = (time.perf_counter() - started) * 1000

        return {
            "name": endpoint["name"],
            "url": endpoint["url"],
            "status": "FAILED",
            "http_status": None,
            "expected_status": endpoint["expected_status"],
            "response_time_ms": round(elapsed_ms, 2),
            "message": f"Request timed out after {timeout} seconds.",
        }

    except requests.exceptions.RequestException as error:
        elapsed_ms = (time.perf_counter() - started) * 1000

        return {
            "name": endpoint["name"],
            "url": endpoint["url"],
            "status": "FAILED",
            "http_status": None,
            "expected_status": endpoint["expected_status"],
            "response_time_ms": round(elapsed_ms, 2),
            "message": f"Request error: {error}",
        }


def save_report(
    results: list[dict],
    environment: str,
) -> Path:
    """Save a text report."""

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    report_path = REPORT_DIR / f"cli_report_{timestamp}.txt"

    passed = sum(
        item["status"] == "SUCCESS" for item in results
    )
    failed = sum(
        item["status"] == "FAILED" for item in results
    )

    lines = [
        "DEVOPS CLI API REPORT",
        "=" * 50,
        f"Generated: {datetime.now().astimezone().isoformat()}",
        f"Environment: {environment}",
        f"Total: {len(results)}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        "",
    ]

    for item in results:
        lines.extend([
            f"Endpoint: {item['name']}",
            f"URL: {item['url']}",
            f"Result: {item['status']}",
            f"HTTP status: {item['http_status']}",
            f"Expected status: {item['expected_status']}",
            f"Response time: {item['response_time_ms']} ms",
            f"Message: {item['message']}",
            "-" * 50,
        ])

    report_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    return report_path


def main() -> int:
    """Run the CLI workflow."""

    args = parse_args()

    try:
        config = load_config(args.config)
    except ValueError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 2

    errors = validate_config(config)

    if errors:
        print("Configuration validation failed:", file=sys.stderr)

        for error in errors:
            print(f"- {error}", file=sys.stderr)

        return 2

    timeout = (
        args.timeout
        if args.timeout is not None
        else config["timeout_seconds"]
    )

    environment = (
        args.environment
        if args.environment is not None
        else config["environment"]
    )

    print(config["app_name"])
    print(f"Environment: {environment}")
    print(f"Timeout: {timeout} seconds")
    print(f"Endpoints: {len(config['endpoints'])}")

    if args.dry_run:
        print("\nDry run: configuration is valid.")
        print("No HTTP requests were sent.")
        return 0

    results = []

    print("\nStarting endpoint checks...\n")

    for endpoint in config["endpoints"]:
        print(f"Checking {endpoint['name']}...")

        result = check_endpoint(
            endpoint,
            timeout,
            args.verbose,
        )

        results.append(result)

        print(
            f"{result['status']} | "
            f"HTTP={result['http_status']} | "
            f"{result['response_time_ms']} ms"
        )

        if args.verbose:
            print(f"  {result['message']}")

        print()

    try:
        report_path = save_report(results, environment)
    except OSError as error:
        print(f"Could not save report: {error}", file=sys.stderr)
        return 2

    print(f"Report saved to: {report_path}")

    failed = sum(
        item["status"] == "FAILED" for item in results
    )

    if failed:
        print(f"Monitoring failed: {failed} endpoint(s) failed.")
        return 1

    print("All endpoint checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
