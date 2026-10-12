
from datetime import datetime
from pathlib import Path
import platform
import shutil
import subprocess
import sys


# Keep paths relative to this Python file, not the terminal directory.
BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "reports"

# Read-only Linux diagnostic commands.
COMMANDS = [
    ["df", "-h"],
    ["free", "-h"],
    ["uptime"],
    ["ip", "addr"],
]


def run_command(command: list[str]) -> dict:
    """Run a command and return a consistent result dictionary."""

    command_name = command[0]

    # Check availability before attempting to run the command.
    if shutil.which(command_name) is None:
        return {
            "command": command,
            "status": "SKIPPED",
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "message": f"Executable not found: {command_name}",
        }

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        if result.returncode == 0:
            status = "SUCCESS"
            message = "Command completed successfully."
        else:
            status = "FAILED"
            message = "Command returned a nonzero exit code."

        return {
            "command": command,
            "status": status,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "message": message,
        }

    except subprocess.TimeoutExpired:
        return {
            "command": command,
            "status": "FAILED",
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "message": "Command timed out after 10 seconds.",
        }

    except OSError as error:
        return {
            "command": command,
            "status": "FAILED",
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "message": f"Operating system error: {error}",
        }


def build_report(results: list[dict]) -> str:
    """Create a readable report from all command results."""

    successful = sum(
        result["status"] == "SUCCESS" for result in results
    )
    failed = sum(
        result["status"] == "FAILED" for result in results
    )
    skipped = sum(
        result["status"] == "SKIPPED" for result in results
    )

    lines = [
        "=" * 60,
        "LINUX COMMAND AUTOMATION TOOLKIT",
        "=" * 60,
        f"Generated: {datetime.now().astimezone().isoformat()}",
        f"Operating system: {platform.platform()}",
        f"Python version: {platform.python_version()}",
        "",
        "SUMMARY",
        "-" * 60,
        f"Total commands: {len(results)}",
        f"Successful: {successful}",
        f"Failed: {failed}",
        f"Skipped: {skipped}",
        "",
        "COMMAND DETAILS",
        "-" * 60,
    ]

    for result in results:
        command_text = " ".join(result["command"])

        lines.extend([
            "",
            f"Command: {command_text}",
            f"Status: {result['status']}",
            f"Exit code: {result['returncode']}",
            f"Message: {result['message']}",
        ])

        if result["stdout"]:
            lines.extend([
                "",
                "STDOUT:",
                result["stdout"],
            ])

        if result["stderr"]:
            lines.extend([
                "",
                "STDERR:",
                result["stderr"],
            ])

    lines.extend([
        "",
        "=" * 60,
        "END OF REPORT",
        "=" * 60,
    ])

    return "\n".join(lines) + "\n"


def save_report(report: str) -> Path:
    """Save the report and return its path."""

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORT_DIR / f"diagnostic_{timestamp}.txt"

    report_path.write_text(report, encoding="utf-8")

    return report_path


def main() -> int:
    """Run diagnostics, save a report, and return an exit code."""

    print("Starting Linux diagnostics...")
    print(f"System: {platform.system()}")

    results = []

    for command in COMMANDS:
        print(f"Running: {' '.join(command)}")
        result = run_command(command)
        results.append(result)

        print(f"Status: {result['status']}")

    report = build_report(results)

    try:
        report_path = save_report(report)
    except OSError as error:
        print(f"Could not save report: {error}", file=sys.stderr)
        return 2

    print()
    print("Diagnostics completed.")
    print(f"Report saved to: {report_path}")

    failed = sum(
        result["status"] == "FAILED" for result in results
    )
    skipped = sum(
        result["status"] == "SKIPPED" for result in results
    )

    if failed:
        print(f"Warning: {failed} command(s) failed.")
        return 1

    if skipped:
        print(f"Warning: {skipped} command(s) were skipped.")
        return 0

    print("All diagnostic commands completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
