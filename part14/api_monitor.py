
import json
import sys
import time

from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
REPORT_DIR = BASE_DIR / "reports"


def load_config() -> dict:
    """Read the JSON configuration file."""

    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as file:
            config = json.load(file)

    except FileNotFoundError as error:
        raise ValueError(
            f"Configuration file not found: {CONFIG_PATH}"
        ) from error

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON at line {error.lineno}, "
            f"column {error.colno}: {error.msg}"
        ) from error

    if not isinstance(config, dict):
        raise ValueError("Configuration must be a JSON object.")

    return config


def validate_config(config: dict) -> list[str]:
    """Validate settings before sending any HTTP requests."""

    errors = []

    app_name = config.get("app_name")

    if not isinstance(app_name, str) or not app_name.strip():
        errors.append("app_name must be a non-empty string.")

    timeout = config.get("timeout_seconds")

    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        errors.append("timeout_seconds must be a number.")
    elif not 0 < timeout <= 60:
        errors.append("timeout_seconds must be greater than 0 and at most 60.")

    endpoints = config.get("endpoints")

    if not isinstance(endpoints, list) or not endpoints:
        errors.append("endpoints must be a non-empty list.")
        return errors

    seen_names = set()

    for index, endpoint in enumerate(endpoints, start=1):
        if not isinstance(endpoint, dict):
            errors.append(f"Endpoint {index} must be an object.")
            continue

        name = endpoint.get("name")
        url = endpoint.get("url")
        expected_status = endpoint.get("expected_status")
        expect_json = endpoint.get("expect_json")

        if not isinstance(name, str) or not name.strip():
            errors.append(f"Endpoint {index}: name is required.")
        elif name in seen_names:
            errors.append(f"Endpoint {index}: duplicate name {name!r}.")
        else:
            seen_names.add(name)

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
                    f"Endpoint {index}: URL must be a valid HTTP(S) URL "
                    "without embedded credentials."
                )

        if (
            isinstance(expected_status, bool)
            or not isinstance(expected_status, int)
            or not 100 <= expected_status <= 599
        ):
            errors.append(
                f"Endpoint {index}: expected_status must be "
                "an integer from 100 to 599."
            )

        if not isinstance(expect_json, bool):
            errors.append(
                f"Endpoint {index}: expect_json must be true or false."
            )

    return errors


def check_endpoint(endpoint: dict, timeout: float) -> dict:
    """Request an endpoint and assess its response."""

    name = endpoint["name"]
    url = endpoint["url"]
    expected_status = endpoint["expected_status"]
    expect_json = endpoint["expect_json"]

    started = time.perf_counter()

    try:
        response = requests.get(
            url,
            headers={"Accept": "application/json"},
            timeout=timeout,
            allow_redirects=True,
        )

        elapsed_ms = (time.perf_counter() - started) * 1000

        status_code = response.status_code
        status_ok = status_code == expected_status

        json_ok = True
        json_message = "JSON validation not requested."

        if expect_json:
            content_type = response.headers.get(
                "Content-Type", ""
            ).lower()

            if "json" not in content_type:
                json_ok = False
                json_message = (
                    "Expected a JSON Content-Type, "
                    f"received {content_type or 'none'}."
                )
            else:
                try:
                    response.json()
                    json_message = "Response contains valid JSON."
                except ValueError:
                    json_ok = False
                    json_message = "Response body is not valid JSON."

        success = status_ok and json_ok

        return {
            "name": name,
            "url": url,
            "status": "SUCCESS" if success else "FAILED",
            "status_code": status_code,
            "expected_status": expected_status,
            "response_time_ms": round(elapsed_ms, 2),
            "json_ok": json_ok,
            "message": (
                "Endpoint check passed."
                if success
                else (
                    "Unexpected HTTP status."
                    if not status_ok
                    else json_message
                )
            ),
        }

    except requests.exceptions.Timeout:
        elapsed_ms = (time.perf_counter() - started) * 1000

        return {
            "name": name,
            "url": url,
            "status": "FAILED",
            "status_code": None,
            "expected_status": expected_status,
            "response_time_ms": round(elapsed_ms, 2),
            "json_ok": None,
            "message": f"Request timed out after {timeout} seconds.",
        }

    except requests.exceptions.RequestException as error:
        elapsed_ms = (time.perf_counter() - started) * 1000

        return {
            "name": name,
            "url": url,
            "status": "FAILED",
            "status_code": None,
            "expected_status": expected_status,
            "response_time_ms": round(elapsed_ms, 2),
            "json_ok": None,
            "message": f"Request error: {error}",
        }


def build_report(results: list[dict]) -> str:
    """Create a readable text report."""

    passed = sum(
        result["status"] == "SUCCESS" for result in results
    )
    failed = sum(
        result["status"] == "FAILED" for result in results
    )

    lines = [
        "=" * 65,
        "PYTHON API MONITORING REPORT",
        "=" * 65,
        f"Generated: {datetime.now().astimezone().isoformat()}",
        f"Total endpoints: {len(results)}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        "",
        "ENDPOINT DETAILS",
        "-" * 65,
    ]

    for result in results:
        lines.extend([
            "",
            f"Name: {result['name']}",
            f"URL: {result['url']}",
            f"Status: {result['status']}",
            f"HTTP status: {result['status_code']}",
            f"Expected status: {result['expected_status']}",
            f"Response time: {result['response_time_ms']} ms",
            f"JSON valid: {result['json_ok']}",
            f"Message: {result['message']}",
        ])

    lines.extend([
        "",
        "=" * 65,
        "END OF REPORT",
        "=" * 65,
    ])

    return "\n".join(lines) + "\n"


def save_report(report: str) -> Path:
    """Save a uniquely named report."""

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    report_path = REPORT_DIR / f"api_report_{timestamp}.txt"

    report_path.write_text(report, encoding="utf-8")

    return report_path


def main() -> int:
    """Coordinate configuration, monitoring, and reporting."""

    try:
        config = load_config()
        errors = validate_config(config)

        if errors:
            print("Configuration errors:", file=sys.stderr)

            for error in errors:
                print(f"- {error}", file=sys.stderr)

            return 2

        print(config["app_name"])
        print("Starting API checks...\n")

        results = []

        for endpoint in config["endpoints"]:
            print(f"Checking: {endpoint['name']}")

            result = check_endpoint(
                endpoint,
                config["timeout_seconds"],
            )

            results.append(result)

            print(
                f"Status: {result['status']} | "
                f"HTTP: {result['status_code']} | "
                f"Time: {result['response_time_ms']} ms\n"
            )

        report = build_report(results)
        report_path = save_report(report)

        print(f"Report saved to: {report_path}")

        failed = sum(
            result["status"] == "FAILED" for result in results
        )

        if failed:
            print(f"Monitoring finished: {failed} endpoint(s) failed.")
            return 1

        print("All endpoint checks passed.")
        return 0

    except (ValueError, OSError) as error:
        print(f"Monitoring error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
