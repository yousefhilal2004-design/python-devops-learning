
import argparse
import logging
import platform
import sys
import time

from datetime import datetime, timezone
from pathlib import Path

import psutil


BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "reports"
LOG_FILE = REPORT_DIR / "monitor.log"

CPU_WARNING = 80.0
CPU_CRITICAL = 90.0

MEMORY_WARNING = 80.0
MEMORY_CRITICAL = 90.0

DISK_WARNING = 80.0
DISK_CRITICAL = 90.0


def configure_logging(verbose: bool) -> logging.Logger:
    """Configure UTC logging to a file and the terminal."""

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("system_health_monitor")
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


def classify_usage(
    percent: float,
    warning: float,
    critical: float,
) -> str:
    """Classify a percentage using configurable thresholds."""

    if percent >= critical:
        return "CRITICAL"

    if percent >= warning:
        return "WARNING"

    return "NORMAL"


def format_bytes(value: int) -> str:
    """Convert bytes into a human-readable binary unit."""

    gib = value / (1024 ** 3)
    return f"{gib:.2f} GiB"


def get_uptime_seconds() -> float:
    """Read uptime from Linux /proc/uptime."""

    uptime_file = Path("/proc/uptime")
    uptime_text = uptime_file.read_text(encoding="utf-8")

    return float(uptime_text.split()[0])


def format_duration(seconds: float) -> str:
    """Format a duration as days, hours, minutes, seconds."""

    total_seconds = int(seconds)

    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)

    return (
        f"{days} days, {hours} hours, "
        f"{minutes} minutes, {secs} seconds"
    )


def collect_metrics(disk_path: str) -> dict:
    """Collect system information and resource metrics."""

    started = time.perf_counter()

    # The interval gives CPU sampling a one-second window.
    cpu_percent = psutil.cpu_percent(interval=1)

    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_usage(disk_path)

    disk_percent = (
        disk.used / disk.total * 100
        if disk.total > 0
        else 0.0
    )

    uptime_seconds = get_uptime_seconds()

    # Process inspection is best-effort because processes
    # can disappear or become inaccessible while being read.
    process_count = 0
    process_errors = 0

    for process in psutil.process_iter(["pid"]):
        try:
            if process.info["pid"] is not None:
                process_count += 1
        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            process_errors += 1

    elapsed = time.perf_counter() - started

    return {
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "hostname": platform.node(),
        "operating_system": platform.platform(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "cpu_percent": cpu_percent,
        "cpu_status": classify_usage(
            cpu_percent,
            CPU_WARNING,
            CPU_CRITICAL,
        ),
        "cpu_logical_cores": psutil.cpu_count(
            logical=True
        ),
        "memory_total": memory.total,
        "memory_available": memory.available,
        "memory_percent": memory.percent,
        "memory_status": classify_usage(
            memory.percent,
            MEMORY_WARNING,
            MEMORY_CRITICAL,
        ),
        "swap_total": swap.total,
        "swap_used": swap.used,
        "swap_percent": swap.percent,
        "disk_path": disk_path,
        "disk_total": disk.total,
        "disk_used": disk.used,
        "disk_free": disk.free,
        "disk_percent": disk_percent,
        "disk_status": classify_usage(
            disk_percent,
            DISK_WARNING,
            DISK_CRITICAL,
        ),
        "uptime_seconds": uptime_seconds,
        "process_count": process_count,
        "process_inspection_errors": process_errors,
        "collection_seconds": elapsed,
    }


def build_report(metrics: dict) -> str:
    """Convert collected metrics into a readable report."""

    lines = [
        "PYTHON DEVOPS SYSTEM HEALTH REPORT",
        "=" * 45,
        f"Generated at UTC: {metrics['timestamp_utc']}",
        "",
        "SYSTEM INFORMATION",
        "-" * 45,
        f"Hostname: {metrics['hostname']}",
        f"Operating system: {metrics['operating_system']}",
        f"Machine: {metrics['machine']}",
        f"Python version: {metrics['python_version']}",
        "",
        "CPU",
        "-" * 45,
        f"Usage: {metrics['cpu_percent']:.1f}%",
        f"Status: {metrics['cpu_status']}",
        f"Logical cores: {metrics['cpu_logical_cores']}",
        "",
        "MEMORY",
        "-" * 45,
        f"Total: {format_bytes(metrics['memory_total'])}",
        f"Available: {format_bytes(metrics['memory_available'])}",
        f"Usage: {metrics['memory_percent']:.1f}%",
        f"Status: {metrics['memory_status']}",
        "",
        "SWAP",
        "-" * 45,
        f"Total: {format_bytes(metrics['swap_total'])}",
        f"Used: {format_bytes(metrics['swap_used'])}",
        f"Usage: {metrics['swap_percent']:.1f}%",
        "",
        "DISK",
        "-" * 45,
        f"Path: {metrics['disk_path']}",
        f"Total: {format_bytes(metrics['disk_total'])}",
        f"Used: {format_bytes(metrics['disk_used'])}",
        f"Free: {format_bytes(metrics['disk_free'])}",
        f"Usage: {metrics['disk_percent']:.1f}%",
        f"Status: {metrics['disk_status']}",
        "",
        "PROCESSES AND TIMING",
        "-" * 45,
        f"Process count: {metrics['process_count']}",
        (
            "Process inspection errors: "
            f"{metrics['process_inspection_errors']}"
        ),
        (
            "System uptime: "
            f"{format_duration(metrics['uptime_seconds'])}"
        ),
        (
            "Collection duration: "
            f"{metrics['collection_seconds']:.4f} seconds"
        ),
        "",
    ]

    overall_statuses = [
        metrics["cpu_status"],
        metrics["memory_status"],
        metrics["disk_status"],
    ]

    if "CRITICAL" in overall_statuses:
        overall_status = "CRITICAL"
    elif "WARNING" in overall_statuses:
        overall_status = "WARNING"
    else:
        overall_status = "NORMAL"

    lines.extend([
        "OVERALL RESULT",
        "-" * 45,
        f"Status: {overall_status}",
        "",
        "Note: Metrics are snapshots, not a complete diagnosis.",
        "",
    ])

    return "\n".join(lines)


def save_report(report: str) -> Path:
    """Write a report with a unique UTC-based filename."""

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    report_path = (
        REPORT_DIR / f"system_health_{timestamp}.txt"
    )

    report_path.write_text(
        report,
        encoding="utf-8",
    )

    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Collect Linux system health metrics."
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show debug-level messages.",
    )

    parser.add_argument(
        "--disk-path",
        default="/",
        help="Path whose filesystem will be checked (default: /).",
    )

    args = parser.parse_args()

    disk_path = Path(args.disk_path)

    if not disk_path.exists():
        print(
            f"Error: path does not exist: {disk_path}",
            file=sys.stderr,
        )
        return 2

    if not disk_path.is_dir():
        print(
            f"Error: path is not a directory: {disk_path}",
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

    logger.info("System health monitor started")

    try:
        metrics = collect_metrics(str(disk_path))

        logger.debug(
            "Metrics collected: %s",
            metrics,
        )

        report = build_report(metrics)
        report_path = save_report(report)

        logger.info("Report saved: %s", report_path)
        print(report)
        print(f"\nSaved report: {report_path}")

        statuses = [
            metrics["cpu_status"],
            metrics["memory_status"],
            metrics["disk_status"],
        ]

        if "CRITICAL" in statuses:
            logger.warning("Critical resource threshold reached")
            exit_code = 1
        elif "WARNING" in statuses:
            logger.warning("Resource warning threshold reached")
            exit_code = 0
        else:
            logger.info("System health checks look normal")
            exit_code = 0

        logger.info("System health monitor finished")
        return exit_code

    except (
        OSError,
        ValueError,
        psutil.Error,
    ) as exc:
        logger.exception("System monitoring failed")
        print(
            f"Monitoring failed: {exc}",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

