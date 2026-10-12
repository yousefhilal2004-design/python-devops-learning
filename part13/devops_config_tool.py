
import json
import os
import platform
import shutil
import subprocess
import sys

from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"

# Only these predefined commands can be selected by the config file.
ALLOWED_CHECKS = {
    "disk": ["df", "-h"],
    "memory": ["free", "-h"],
    "uptime": ["uptime"],
    "network": ["ip", "addr"],
}


def load_config() -> dict:
    """Load JSON configuration and check its top-level type."""

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
    """Return a list of configuration validation errors."""

    errors = []

    app_name = config.get("app_name")
    if not isinstance(app_name, str) or not app_name.strip():
        errors.append("app_name must be a non-empty string.")

    environment = config.get("environment")
    allowed_environments = {
        "development",
        "staging",
        "production",
    }

    if environment not in allowed_environments:
        errors.append(
            "environment must be development, staging, or production."
        )

    timeout = config.get("timeout_seconds")

    if isinstance(timeout, bool) or not isinstance(timeout, int):
        errors.append("timeout_seconds must be an integer.")
    elif not 1 <= timeout <= 60:
        errors.append("timeout_seconds must be between 1 and 60.")

    checks = config.get("enabled_checks")

    if not isinstance(checks, list) or not checks:
        errors.append("enabled_checks must be a non-empty list.")
    else:
        if not all(isinstance(item, str) for item in checks):
            errors.append("Every enabled check must be a string.")
        else:
            if len(checks) != len(set(checks)):
                errors.append("enabled_checks contains duplicates.")

            unknown = sorted(set(checks) - set(ALLOWED_CHECKS))

            if unknown:
                errors.append(
                    f"Unknown checks: {', '.join(unknown)}."
                )

    report_directory = config.get("report_directory")

    if (
        not isinstance(report_directory, str)
        or not report_directory.strip()
    ):
        errors.append(
            "report_directory must be a non-empty string."
        )
    elif Path(report_directory).is_absolute():
        errors.append("report_directory must be a relative path.")
    elif ".." in Path(report_directory).parts:
        errors.append(
            "report_directory cannot contain parent-directory traversal."
        )

    return errors


def run_check(name: str, timeout: int) -> dict:
    """Run one predefined diagnostic command."""

    command = ALLOWED_CHECKS[name]

    if shutil.which(command[0]) is None:
        return {
            "name": name,
            "command": command,
            "status": "SKIPPED",
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "message": f"Executable not found: {command[0]}",
        }

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

        status = (
            "SUCCESS" if result.returncode == 0 else "FAILED"
        )

        return {
            "name": name,
            "command": command,
            "status": status,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "message": (
                "Command completed."
                if status == "SUCCESS"
                else "Command returned a nonzero exit code."
            ),
        }

    except subprocess.TimeoutExpired:
        return {
            "name": name,
            "command": command,
            "status": "FAILED",
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "message": f"Command timed out after {timeout} seconds.",
        }

    except OSError as error:
        return {
            "name": name,
            "command": command,
            "status": "FAILED",
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "message": f"Operating system error: {error}",
        }


def build_report(
    config: dict,
    results: list[dict],
) -> str:
    """Create a text report from the configuration and results."""

    successful = sum(
        item["status"] == "SUCCESS" for item in results
    )
    failed = sum(
        item["status"] == "FAILED" for item in results
    )
    skipped = sum(
        item["status"] == "SKIPPED" for item in results
    )

    lines = [
        "=" * 60,
        config["app_name"],
        "=" * 60,
        f"Generated: {datetime.now().astimezone().isoformat()}",
        f"Environment: {config['environment']}",
        f"Operating system: {platform.platform()}",
        f"Python version: {platform.python_version()}",
        "",
        "SUMMARY",
        "-" * 60,
        f"Total checks: {len(results)}",
        f"Successful: {successful}",
        f"Failed: {failed}",
        f"Skipped: {skipped}",
        "",
        "DETAILS",
        "-" * 60,
    ]

    for item in results:
        lines.extend([
            "",
            f"Check: {item['name']}",
            f"Command: {' '.join(item['command'])}",
            f"Status: {item['status']}",
            f"Exit code: {item['returncode']}",
            f"Message: {item['message']}",
        ])

        if item["stdout"]:
            lines.extend(["STDOUT:", item["stdout"]])

        if item["stderr"]:
            lines.extend(["STDERR:", item["stderr"]])

    lines.extend(["", "=" * 60, "END OF REPORT"])

    return "\n".join(lines) + "\n"


def save_report(config: dict, report: str) -> Path:
    """Save a timestamped report under the project directory."""

    report_dir = Path(config["report_directory"])
    output_dir = (BASE_DIR / report_dir).resolve()

    # Ensure the resolved destination stays inside BASE_DIR.
    if not output_dir.is_relative_to(BASE_DIR):
        raise ValueError("Report directory must remain in the project.")

    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output_path = output_dir / f"report_{timestamp}.txt"

    output_path.write_text(report, encoding="utf-8")

    return output_path


def main() -> int:
    """Load settings, validate, run checks, and save a report."""

    try:
        config = load_config()

        # APP_ENV, when set, overrides the file's environment.
        config = config.copy()
        config["environment"] = os.getenv(
            "APP_ENV",
            config.get("environment"),
        )

        errors = validate_config(config)

        if errors:
            print("Configuration errors:", file=sys.stderr)

            for error in errors:
                print(f"- {error}", file=sys.stderr)

            return 2

        print(config["app_name"])
        print(f"Environment: {config['environment']}")
        print("Starting diagnostic checks...\n")

        results = []

        for name in config["enabled_checks"]:
            print(f"Running check: {name}")

            result = run_check(
                name,
                config["timeout_seconds"],
            )

            results.append(result)
            print(f"Status: {result['status']}\n")

        report = build_report(config, results)
        report_path = save_report(config, report)

        print(f"Report saved to: {report_path}")

        failed = sum(
            item["status"] == "FAILED" for item in results
        )
        skipped = sum(
            item["status"] == "SKIPPED" for item in results
        )

        if failed:
            print(f"Completed with {failed} failed check(s).")
            return 1

        if skipped:
            print(f"Completed with {skipped} skipped check(s).")

        else:
            print("All selected checks completed successfully.")

        return 0

    except (ValueError, OSError) as error:
        print(f"Automation error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
