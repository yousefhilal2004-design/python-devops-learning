#!/usr/bin/env python3

"""
Regex Log Analyzer for DevOps.

Exit codes:
0 = Analysis completed without ERROR or CRITICAL events.
1 = Analysis completed and ERROR or CRITICAL events were found.
2 = Input or report-processing error.
"""

import argparse
import logging
import re
import sys

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_LOG = BASE_DIR / "logs" / "app.log"
REPORT_DIR = BASE_DIR / "reports"

VALID_LEVELS = {
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
}

LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} "
    r"\d{2}:\d{2}:\d{2}) "
    r"(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL) "
    r"(?P<message>.*)$"
)


def setup_logging(verbose=False):
    """Configure console logging."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )


def parse_log_line(line):
    """Parse one line and validate its timestamp."""
    match = LOG_PATTERN.fullmatch(line.strip())

    if not match:
        return None

    entry = match.groupdict()

    try:
        datetime.strptime(
            entry["timestamp"],
            "%Y-%m-%d %H:%M:%S",
        )
    except ValueError:
        return None

    return entry


def analyze_log(log_path):
    """Analyze the log file and collect statistics."""
    counts = Counter()
    errors = []
    warnings = []
    malformed_lines = []
    parsed_count = 0
    total_nonempty_lines = 0

    with log_path.open(
        "r",
        encoding="utf-8",
        errors="replace",
    ) as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            total_nonempty_lines += 1
            entry = parse_log_line(line)

            if entry is None:
                malformed_lines.append({
                    "line_number": line_number,
                    "content": line.strip(),
                })

                logging.debug(
                    "Malformed line: %s",
                    line_number,
                )
                continue

            parsed_count += 1
            level = entry["level"]
            counts[level] += 1

            record = {
                "line_number": line_number,
                **entry,
            }

            if level in {"ERROR", "CRITICAL"}:
                errors.append(record)

            if level == "WARNING":
                warnings.append(record)

    return {
        "counts": counts,
        "errors": errors,
        "warnings": warnings,
        "malformed_lines": malformed_lines,
        "parsed_count": parsed_count,
        "total_nonempty_lines": total_nonempty_lines,
    }


def build_report(results, log_path):
    """Generate a human-readable report."""
    generated_at = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    counts = results["counts"]

    lines = [
        "REGEX LOG ANALYZER REPORT",
        "=" * 60,
        f"Generated: {generated_at}",
        f"Input file: {log_path}",
        "",
        "SUMMARY",
        "-" * 60,
        f"Non-empty lines: {results['total_nonempty_lines']}",
        f"Parsed lines: {results['parsed_count']}",
        f"Malformed lines: {len(results['malformed_lines'])}",
        "",
        "LOG LEVEL COUNTS",
        "-" * 60,
    ]

    for level in sorted(VALID_LEVELS):
        lines.append(f"{level}: {counts[level]}")

    lines.extend(["", "WARNINGS", "-" * 60])

    if results["warnings"]:
        for record in results["warnings"]:
            lines.append(
                f"Line {record['line_number']}: "
                f"{record['timestamp']} WARNING - "
                f"{record['message']}"
            )
    else:
        lines.append("No warnings found.")

    lines.extend([
        "",
        "ERRORS AND CRITICAL EVENTS",
        "-" * 60,
    ])

    if results["errors"]:
        for record in results["errors"]:
            lines.append(
                f"Line {record['line_number']}: "
                f"{record['timestamp']} {record['level']} - "
                f"{record['message']}"
            )
    else:
        lines.append("No errors or critical events found.")

    lines.extend(["", "MALFORMED LINES", "-" * 60])

    if results["malformed_lines"]:
        for record in results["malformed_lines"]:
            lines.append(
                f"Line {record['line_number']}: "
                f"{record['content']}"
            )
    else:
        lines.append("No malformed lines found.")

    lines.extend(["", "END OF REPORT"])

    return "\n".join(lines)


def save_report(report_text):
    """Save a timestamped report."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    report_path = REPORT_DIR / f"report_{timestamp}.txt"

    with report_path.open("w", encoding="utf-8") as file:
        file.write(report_text + "\n")

    return report_path


def parse_args():
    """Configure command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze application logs using Regex."
    )

    parser.add_argument(
        "--log",
        type=Path,
        default=DEFAULT_LOG,
        help="Path to the input log file.",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )

    return parser.parse_args()


def main():
    """Run the analyzer."""
    args = parse_args()
    setup_logging(args.verbose)

    log_path = args.log.expanduser().resolve()

    if not log_path.is_file():
        logging.error("Log file not found: %s", log_path)
        return 2

    logging.info("Starting log analysis.")
    logging.info("Input file: %s", log_path)

    try:
        results = analyze_log(log_path)
        report_text = build_report(results, log_path)
        report_path = save_report(report_text)

    except (OSError, UnicodeError) as exc:
        logging.error("File processing failed: %s", exc)
        return 2

    print()
    print(report_text)
    print()
    print(f"Report saved to: {report_path}")

    if results["malformed_lines"]:
        logging.warning(
            "%s malformed line(s) found.",
            len(results["malformed_lines"]),
        )

    if results["errors"]:
        logging.warning(
            "ERROR or CRITICAL events were detected."
        )
        return 1

    logging.info("No ERROR or CRITICAL events detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
