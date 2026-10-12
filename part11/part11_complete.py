
from pathlib import Path
import os
import platform
import shutil
import stat
import sys


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

LOG_DIR = BASE_DIR / "logs"
REPORT_DIR = BASE_DIR / "reports"
BACKUP_DIR = BASE_DIR / "backups"

REPORT_FILE = REPORT_DIR / "system_audit.txt"
BACKUP_FILE = BACKUP_DIR / "system_audit_backup.txt"


# ============================================================
# 2. CREATE REQUIRED DIRECTORIES
# ============================================================

def create_directories() -> None:
    """Create project directories if needed."""

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 3. COLLECT OPERATING SYSTEM INFORMATION
# ============================================================

def get_system_info() -> dict:
    """Collect basic OS and Python information."""

    return {
        "os_name": platform.system(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "current_directory": str(Path.cwd()),
        "script_directory": str(BASE_DIR),
        "home_directory": str(Path.home()),
        "username": os.getenv("USER", "unknown"),
        "process_id": os.getpid(),
        "parent_process_id": os.getppid(),
        "app_environment": os.getenv(
            "APP_ENV",
            "not configured",
        ),
    }


# ============================================================
# 4. COLLECT DISK INFORMATION
# ============================================================

def get_disk_info(path: Path) -> dict:
    """Collect disk usage for the filesystem containing path."""

    usage = shutil.disk_usage(path)

    gib = 1024 ** 3

    return {
        "path": str(path),
        "total_gib": usage.total / gib,
        "used_gib": usage.used / gib,
        "free_gib": usage.free / gib,
    }


# ============================================================
# 5. SCAN LOG DIRECTORY
# ============================================================

def scan_log_directory(directory: Path) -> dict:
    """Inspect .log files directly inside a directory."""

    files = []
    warnings = []

    if not directory.is_dir():
        return {
            "files": files,
            "warnings": [f"Directory not found: {directory}"],
        }

    try:
        log_paths = sorted(directory.glob("*.log"))

        for file_path in log_paths:

            try:
                if not file_path.is_file():
                    continue

                metadata = file_path.stat()

                files.append({
                    "name": file_path.name,
                    "path": str(file_path.resolve()),
                    "size_bytes": metadata.st_size,
                    "owner_readable_bit": bool(
                        metadata.st_mode & stat.S_IRUSR
                    ),
                    "owner_writable_bit": bool(
                        metadata.st_mode & stat.S_IWUSR
                    ),
                    "owner_executable_bit": bool(
                        metadata.st_mode & stat.S_IXUSR
                    ),
                })

            except OSError as error:
                warnings.append(
                    f"Could not inspect {file_path}: {error}"
                )

    except OSError as error:
        warnings.append(
            f"Could not scan {directory}: {error}"
        )

    return {
        "files": files,
        "warnings": warnings,
    }


# ============================================================
# 6. BUILD REPORT TEXT
# ============================================================

def build_report(
    system_info: dict,
    disk_info: dict,
    scan_result: dict,
) -> str:
    """Build the audit report in memory."""

    lines = [
        "========================================",
        " PYTHON DEVOPS SYSTEM AUDIT",
        "========================================",
        "",
        "=== SYSTEM INFORMATION ===",
        f"Operating system: {system_info['os_name']}",
        f"OS release: {system_info['os_release']}",
        f"Architecture: {system_info['architecture']}",
        f"Python version: {system_info['python_version']}",
        f"Python executable: {system_info['python_executable']}",
        f"Current directory: {system_info['current_directory']}",
        f"Script directory: {system_info['script_directory']}",
        f"Home directory: {system_info['home_directory']}",
        f"Username: {system_info['username']}",
        f"Process ID: {system_info['process_id']}",
        f"Parent process ID: {system_info['parent_process_id']}",
        f"APP_ENV: {system_info['app_environment']}",
        "",
        "=== DISK INFORMATION ===",
        f"Checked path: {disk_info['path']}",
        f"Total: {disk_info['total_gib']:.2f} GiB",
        f"Used: {disk_info['used_gib']:.2f} GiB",
        f"Free: {disk_info['free_gib']:.2f} GiB",
        "",
        "=== LOG FILE AUDIT ===",
        f"Files found: {len(scan_result['files'])}",
        "",
    ]

    if scan_result["files"]:
        for item in scan_result["files"]:
            lines.extend([
                f"Name: {item['name']}",
                f"Path: {item['path']}",
                f"Size: {item['size_bytes']} bytes",
                (
                    "Owner permission bits: "
                    f"read={item['owner_readable_bit']}, "
                    f"write={item['owner_writable_bit']}, "
                    f"execute={item['owner_executable_bit']}"
                ),
                "",
            ])
    else:
        lines.append("No log files found.")
        lines.append("")

    lines.append("=== SCAN WARNINGS ===")

    if scan_result["warnings"]:
        for warning in scan_result["warnings"]:
            lines.append(warning)
    else:
        lines.append("No scan warnings.")

    lines.append("")

    return "\n".join(lines)


# ============================================================
# 7. WRITE REPORT
# ============================================================

def write_report(report_file: Path, content: str) -> None:
    """Write the audit report."""

    report_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_file.write_text(
        content + "\n",
        encoding="utf-8",
    )


# ============================================================
# 8. BACKUP REPORT
# ============================================================

def backup_report(
    source: Path,
    destination: Path,
) -> Path:
    """Copy the report to the backup directory."""

    if not source.is_file():
        raise FileNotFoundError(
            f"Report does not exist: {source}"
        )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(source, destination)

    return destination


# ============================================================
# 9. MAIN APPLICATION
# ============================================================

def main() -> int:
    """Run the complete system audit."""

    print("========================================")
    print(" Python DevOps - Part 11")
    print(" OS Interaction & System Automation")
    print("========================================")

    # Create project directories.
    try:
        create_directories()

    except OSError as error:
        print(f"ERROR: Cannot create directories: {error}")
        return 1

    # Collect operating system information.
    try:
        system_info = get_system_info()

    except OSError as error:
        print(f"ERROR: Cannot collect system information: {error}")
        return 1

    # Collect disk information.
    try:
        disk_info = get_disk_info(BASE_DIR)

    except OSError as error:
        print(f"ERROR: Cannot inspect disk usage: {error}")
        return 1

    # Scan logs.
    scan_result = scan_log_directory(LOG_DIR)

    # Build and write the report.
    content = build_report(
        system_info,
        disk_info,
        scan_result,
    )

    try:
        write_report(REPORT_FILE, content)

    except (OSError, UnicodeError) as error:
        print(f"ERROR: Cannot write report: {error}")
        return 1

    # Create a backup.
    try:
        backup_path = backup_report(
            REPORT_FILE,
            BACKUP_FILE,
        )

    except OSError as error:
        print(f"ERROR: Cannot create backup: {error}")
        return 1

    # Display a summary.
    print("\n=== SYSTEM SUMMARY ===")
    print(f"OS: {system_info['os_name']}")
    print(f"Python: {system_info['python_version']}")
    print(f"Process ID: {system_info['process_id']}")

    print("\n=== FILE AUDIT ===")
    print(f"Log files found: {len(scan_result['files'])}")

    print("\n=== OUTPUT ===")
    print(f"Report: {REPORT_FILE}")
    print(f"Backup: {backup_path}")

    if scan_result["warnings"]:
        print("\nCompleted with scan warnings.")
        return 2

    print("\nSystem audit completed successfully.")
    return 0


# ============================================================
# 10. ENTRY POINT
# ============================================================

if __name__ == "__main__":
    sys.exit(main())

