
import argparse
import logging
import shutil
import subprocess
import sys
import time

from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "reports"
LOG_FILE = REPORT_DIR / "monitor.log"

COMMANDS = {
    "disk_usage": ["df", "-h"],
    "memory_usage": ["free", "-h"],
    "system_uptime": ["uptime"],
}


def configure_logging(verbose: bool) -> logging.Logger:
    """Configure console and file logging."""

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("datetime_monitor")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s UTC | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

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


def run_command(name: str, command: list[str]) -> dict:
    """Run a read-only system command and measure elapsed time."""

    result = {
        "name": name,
        "command": " ".join(command),
        "status": "UNKNOWN",
        "duration_seconds": 0.0,
        "output": "",
        "error": "",
    }

    # Check that the executable exists.
    if shutil.which(command[0]) is None:
        result["status"] = "SKIPPED"
        result["error"] = (
            f"Command not found: {command[0]}"
        )
        return result

    start = time.perf_counter()

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        result["duration_seconds"] = (
            time.perf_counter() - start
        )

        result["output"] = (
            completed.stdout.strip()
        )

        if completed.returncode == 0:
            result["status"] = "SUCCESS"
        else:
            result["status"] = "FAILED"
            result["error"] = (
                completed.stderr.strip()
                or f"Exit code: {completed.returncode}"
            )

    except subprocess.TimeoutExpired:
        result["duration_seconds"] = (
            time.perf_counter() - start
        )
        result["status"] = "FAILED"
        result["error"] = "Command timed out after 10 seconds"

    except OSError as exc:
        result["duration_seconds"] = (
            time.perf_counter() - start
        )
        result["status"] = "FAILED"
        result["error"] = str(exc)

    return result


def build_report(results: list[dict]) -> str:
    """Build a timestamped report."""

    generated_at = datetime.now(timezone.utc)

    lines = [
        "PYTHON DEVOPS TIMESTAMPED SYSTEM MONITOR",
        "=" * 48,
        f"Generated at UTC: {generated_at.isoformat()}",
        f"Hostname: {__import__('socket').gethostname()}",
        "",
        "CHECK SUMMARY",
        "-" * 48,
    ]

    for result in results:
        lines.append(f"Check: {result['name']}")
        lines.append(f"Command: {result['command']}")
        lines.append(f"Status: {result['status']}")
        lines.append(
            "Duration: "
            f"{result['duration_seconds']:.4f} seconds"
        )

        if result["error"]:
            lines.append(f"Error: {result['error']}")

        if result["output"]:
            lines.append("Output:")
            lines.append(result["output"])

        lines.append("-" * 48)

    successful = sum(
        item["status"] == "SUCCESS" for item in results
    )
    failed = sum(
        item["status"] == "FAILED" for item in results
    )
    skipped = sum(
        item["status"] == "SKIPPED" for item in results
    )

    lines.extend([
        "",
        "FINAL SUMMARY",
        f"Successful checks: {successful}",
        f"Failed checks: {failed}",
        f"Skipped checks: {skipped}",
        f"Total checks: {len(results)}",
        "",
    ])

    return "\n".join(lines)


def save_report(report: str) -> Path:
    """Save the report with a unique timestamped filename."""

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    report_path = (
        REPORT_DIR / f"system_report_{timestamp}.txt"
    )

    report_path.write_text(
        report,
        encoding="utf-8",
    )

    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Timestamped Python DevOps system monitor"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show debug-level messages",
    )

    args = parser.parse_args()

    try:
        logger = configure_logging(args.verbose)
    except OSError as exc:
        print(
            f"Logging setup failed: {exc}",
            file=sys.stderr,
        )
        return 2

    logger.info("System monitor started")

    started_at = time.perf_counter()
    overall_status = 0

    try:
        results = []

        for name, command in COMMANDS.items():
            logger.info("Running check: %s", name)

            result = run_command(name, command)
            results.append(result)

            logger.info(
                "%s: %s (%.4f seconds)",
                name,
                result["status"],
                result["duration_seconds"],
            )

            if result["status"] == "FAILED":
                overall_status = 1
                logger.error(
                    "%s failed: %s",
                    name,
                    result["error"],
                )

            elif result["status"] == "SKIPPED":
                logger.warning(
                    "%s skipped: %s",
                    name,
                    result["error"],
                )

        report = build_report(results)
        report_path = save_report(report)

        total_duration = time.perf_counter() - started_at

        logger.info("Report saved: %s", report_path)
        logger.info(
            "Total monitoring duration: %.4f seconds",
            total_duration,
        )
        logger.info("System monitor finished")

        print(f"\nReport: {report_path}")
        print(f"Exit status: {overall_status}")

        return overall_status

    except (OSError, UnicodeError) as exc:
        logger.exception("Unable to complete monitoring")
        print(f"Monitoring failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

