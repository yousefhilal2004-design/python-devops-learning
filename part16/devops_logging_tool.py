
import argparse
import logging
import re
import sys

from collections import Counter
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

DEFAULT_LOG_FILE = BASE_DIR / "sample_app.log"
OPERATIONAL_LOG_DIR = BASE_DIR / "logs"
REPORT_DIR = BASE_DIR / "reports"

LOG_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2} "
    r"\d{2}:\d{2}:\d{2} "
    r"(DEBUG|INFO|WARNING|ERROR|CRITICAL) "
    r".+$"
)

LEVELS = [
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]


def parse_args() -> argparse.Namespace:
    """Parse command-line options."""

    parser = argparse.ArgumentParser(
        description=(
            "Analyze application logs and record "
            "operational events."
        )
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_LOG_FILE,
        help="Path to the application log to analyze",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed diagnostic messages",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the input file without analyzing it",
    )

    return parser.parse_args()


def configure_logging(verbose: bool) -> logging.Logger:
    """Configure terminal and rotating-file logging."""

    OPERATIONAL_LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger = logging.getLogger("devops_logging_tool")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Avoid duplicate records if this function is called again.
    for old_handler in logger.handlers[:]:
        logger.removeHandler(old_handler)
        old_handler.close()

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-8s "
        "%(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        OPERATIONAL_LOG_DIR / "devops_tool.log",
        maxBytes=1_000_000,
        backupCount=3,
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


def analyze_log(
    input_path: Path,
    logger: logging.Logger,
) -> dict:
    """Count known levels and identify malformed lines."""

    counts = Counter()
    malformed_lines = []
    total_lines = 0

    logger.info("Starting log analysis: %s", input_path)

    try:
        with input_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            for line_number, raw_line in enumerate(
                file,
                start=1,
            ):
                line = raw_line.strip()

                if not line:
                    continue

                total_lines += 1

                match = LOG_PATTERN.match(line)

                if not match:
                    malformed_lines.append({
                        "line_number": line_number,
                        "content": line,
                    })

                    logger.warning(
                        "Malformed record at line %s",
                        line_number,
                    )
                    continue

                level = match.group(1)
                counts[level] += 1

                if level in {"ERROR", "CRITICAL"}:
                    logger.debug(
                        "Found %s record at line %s",
                        level,
                        line_number,
                    )

    except FileNotFoundError:
        logger.exception(
            "Input log file was not found: %s",
            input_path,
        )
        raise

    except PermissionError:
        logger.exception(
            "Permission denied reading: %s",
            input_path,
        )
        raise

    except UnicodeDecodeError:
        logger.exception(
            "Input file could not be decoded as UTF-8: %s",
            input_path,
        )
        raise

    except OSError:
        logger.exception(
            "Operating-system error reading: %s",
            input_path,
        )
        raise

    results = {
        "input_file": str(input_path),
        "total_lines": total_lines,
        "counts": {
            level: counts.get(level, 0)
            for level in LEVELS
        },
        "malformed_count": len(malformed_lines),
        "malformed_lines": malformed_lines,
    }

    logger.info(
        "Analysis complete: %s lines, %s malformed",
        total_lines,
        len(malformed_lines),
    )

    return results


def build_report(results: dict) -> str:
    """Build a readable report from analysis results."""

    lines = [
        "=" * 60,
        "PYTHON DEVOPS LOG ANALYSIS REPORT",
        "=" * 60,
        f"Generated: {datetime.now().astimezone().isoformat()}",
        f"Input file: {results['input_file']}",
        f"Total non-empty lines: {results['total_lines']}",
        "",
        "LOG LEVEL COUNTS",
        "-" * 60,
    ]

    for level, count in results["counts"].items():
        lines.append(f"{level:<10} {count}")

    lines.extend([
        "",
        f"Malformed records: {results['malformed_count']}",
        "",
        "MALFORMED RECORD DETAILS",
        "-" * 60,
    ])

    if results["malformed_lines"]:
        for item in results["malformed_lines"]:
            lines.append(
                f"Line {item['line_number']}: "
                f"{item['content']}"
            )
    else:
        lines.append("None")

    lines.extend([
        "",
        "=" * 60,
        "END OF REPORT",
        "=" * 60,
    ])

    return "\n".join(lines) + "\n"


def save_report(
    report_text: str,
    logger: logging.Logger,
) -> Path:
    """Write the report to a unique timestamped file."""

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    report_path = REPORT_DIR / f"log_report_{timestamp}.txt"

    try:
        report_path.write_text(
            report_text,
            encoding="utf-8",
        )

    except OSError:
        logger.exception(
            "Could not write report: %s",
            report_path,
        )
        raise

    logger.info("Report saved: %s", report_path)

    return report_path


def main() -> int:
    """Coordinate logging, analysis, and reporting."""

    args = parse_args()

    try:
        logger = configure_logging(args.verbose)

    except OSError as error:
        print(
            f"Could not initialize operational logging: {error}",
            file=sys.stderr,
        )
        return 2

    logger.info("DevOps logging toolkit started")

    try:
        input_path = args.input.expanduser().resolve()

        if not input_path.is_file():
            logger.error(
                "Input path is not a regular file: %s",
                input_path,
            )
            return 2

        if args.dry_run:
            logger.info(
                "Dry run: input file exists; no analysis performed"
            )
            print("Dry run passed. No report was generated.")
            return 0

        results = analyze_log(input_path, logger)
        report_text = build_report(results)
        report_path = save_report(report_text, logger)

        print(f"\nInput lines: {results['total_lines']}")

        for level, count in results["counts"].items():
            print(f"{level:<10} {count}")

        print(f"Malformed: {results['malformed_count']}")
        print(f"Report: {report_path}")

        if results["malformed_count"] > 0:
            logger.warning(
                "Analysis finished with malformed records"
            )
            return 1

        logger.info("Analysis finished successfully")
        return 0

    except (OSError, UnicodeError):
        logger.error(
            "The analysis operation could not be completed"
        )
        return 2

    finally:
        logger.info("DevOps logging toolkit finished")


if __name__ == "__main__":
    raise SystemExit(main())
