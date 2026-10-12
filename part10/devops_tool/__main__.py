
from .config import (
    LOG_FILE,
    REPORT_FILE,
    BACKUP_FILE,
    SERVER_CONFIG,
)

from .validators import validate_server_config
from .analyzer import analyze_log
from .reports import write_report
from .backup import backup_file


def main() -> int:
    """Run the complete modular DevOps tool."""

    print("========================================")
    print(" Python DevOps - Part 10")
    print(" Modules, Packages and Automation")
    print("========================================")

    # ========================================================
    # 1. VALIDATE SERVER CONFIGURATION
    # ========================================================

    print("\n=== SERVER CONFIGURATION ===")

    try:
        config = validate_server_config(SERVER_CONFIG)

    except (KeyError, ValueError, TypeError) as error:
        print(f"ERROR: Invalid configuration: {error}")
        return 1

    print(f"Host: {config['host']}")
    print(f"Port: {config['port']}")

    # ========================================================
    # 2. ANALYZE LOG FILE
    # ========================================================

    print("\n=== LOG ANALYSIS ===")

    try:
        result = analyze_log(LOG_FILE)

    except FileNotFoundError:
        print(f"ERROR: Log file missing: {LOG_FILE}")
        return 1

    except PermissionError as error:
        print(f"ERROR: Permission denied: {error}")
        return 1

    except UnicodeError as error:
        print(f"ERROR: Cannot decode log: {error}")
        return 1

    except OSError as error:
        print(f"ERROR: Cannot read log: {error}")
        return 1

    counts = result["counts"]

    print(f"Total lines: {result['total_lines']}")
    print(f"INFO: {counts['INFO']}")
    print(f"WARNING: {counts['WARNING']}")
    print(f"ERROR: {counts['ERROR']}")
    print(f"Invalid: {len(result['invalid_lines'])}")

    # ========================================================
    # 3. GENERATE REPORT
    # ========================================================

    print("\n=== REPORT ===")

    try:
        write_report(REPORT_FILE, result)

    except OSError as error:
        print(f"ERROR: Cannot create report: {error}")
        return 1

    print(f"Report created: {REPORT_FILE}")

    # ========================================================
    # 4. BACKUP REPORT
    # ========================================================

    print("\n=== BACKUP ===")

    try:
        backup_path = backup_file(
            REPORT_FILE,
            BACKUP_FILE,
        )

    except OSError as error:
        print(f"ERROR: Backup failed: {error}")
        return 1

    print(f"Backup created: {backup_path}")

    # ========================================================
    # 5. FINAL RESULT
    # ========================================================

    print("\n========================================")

    if result["invalid_lines"]:
        print("Completed with invalid log entries.")
        return 2

    print("All operations completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
