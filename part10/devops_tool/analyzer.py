
from pathlib import Path

from .validators import (
    LogFormatError,
    parse_log_line,
)


def analyze_log(log_file: Path) -> dict:
    """Read and analyze a structured log file."""

    counts = {
        "INFO": 0,
        "WARNING": 0,
        "ERROR": 0,
    }

    errors = []
    warnings = []
    invalid_lines = []
    total_lines = 0

    with log_file.open("r", encoding="utf-8") as file:

        for line_number, line in enumerate(file, start=1):

            total_lines += 1

            if not line.strip():
                continue

            try:
                entry = parse_log_line(line)

            except LogFormatError as error:
                invalid_lines.append({
                    "line": line_number,
                    "reason": str(error),
                })
                continue

            level = entry["level"]
            counts[level] += 1

            if level == "ERROR":
                errors.append(entry)

            elif level == "WARNING":
                warnings.append(entry)

    return {
        "counts": counts,
        "errors": errors,
        "warnings": warnings,
        "invalid_lines": invalid_lines,
        "total_lines": total_lines,
    }
