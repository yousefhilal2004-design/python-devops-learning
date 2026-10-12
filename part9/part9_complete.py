
from pathlib import Path
import shutil
import sys


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

LOG_DIR = BASE_DIR / "logs"
REPORT_DIR = BASE_DIR / "reports"
BACKUP_DIR = BASE_DIR / "backups"

LOG_FILE = LOG_DIR / "app.log"
REPORT_FILE = REPORT_DIR / "log_report.txt"
BACKUP_FILE = BACKUP_DIR / "log_report_backup.txt"


# ============================================================
# 2. CUSTOM EXCEPTION
# ============================================================

class LogFormatError(ValueError):
    """Raised when a log line contains invalid data."""


# ============================================================
# 3. CREATE DIRECTORIES
# ============================================================

def create_directories() -> None:
    """Create directories if they do not exist."""

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 4. VALIDATE PORT
# ============================================================

def validate_port(port_text: str) -> int:
    """Convert and validate a TCP/UDP port."""

    port = int(port_text.strip())

    if not 1 <= port <= 65535:
        raise ValueError(
            "Port must be between 1 and 65535"
        )

    return port


# ============================================================
# 5. VALIDATE HOSTNAME
# ============================================================

def validate_hostname(hostname: str) -> str:
    """Check for an empty hostname and normalize case."""

    hostname = hostname.strip().lower()

    if not hostname:
        raise ValueError("Hostname cannot be empty")

    return hostname


# ============================================================
# 6. SAFE SERVER CONFIGURATION
# ============================================================

def validate_server_config(config: dict) -> dict:
    """Validate required server configuration fields."""

    if "host" not in config:
        raise KeyError("Missing required key: host")

    if "port" not in config:
        raise KeyError("Missing required key: port")

    host = validate_hostname(config["host"])
    port = validate_port(str(config["port"]))

    return {
        "host": host,
        "port": port,
    }


# ============================================================
# 7. PARSE LOG LINE
# ============================================================

def parse_log_line(line: str) -> dict:
    """Parse LEVEL|SERVER|MESSAGE."""

    parts = line.strip().split("|", 2)

    if len(parts) != 3:
        raise LogFormatError(
            "Expected LEVEL|SERVER|MESSAGE"
        )

    level, server, message = parts

    level = level.strip().upper()
    server = server.strip().lower()
    message = message.strip()

    if level not in ("INFO", "WARNING", "ERROR"):
        raise LogFormatError(
            f"Unsupported log level: {level}"
        )

    if not server:
        raise LogFormatError(
            "Server name cannot be empty"
        )

    if not message:
        raise LogFormatError(
            "Log message cannot be empty"
        )

    return {
        "level": level,
        "server": server,
        "message": message,
    }


# ============================================================
# 8. ANALYZE LOG FILE
# ============================================================

def analyze_log(log_file: Path) -> dict:
    """Read log lines and collect results."""

    counts = {
        "INFO": 0,
        "WARNING": 0,
        "ERROR": 0,
    }

    errors = []
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

            else:
                counts[entry["level"]] += 1

                if entry["level"] == "ERROR":
                    errors.append(entry)

    return {
        "counts": counts,
        "errors": errors,
        "invalid_lines": invalid_lines,
        "total_lines": total_lines,
    }


# ============================================================
# 9. WRITE REPORT
# ============================================================

def write_report(report_file: Path, result: dict) -> None:
    """Write log analysis results."""

    counts = result["counts"]

    with report_file.open("w", encoding="utf-8") as file:

        file.write("=== DEVOPS LOG REPORT ===\n\n")

        file.write(f"Total lines: {result['total_lines']}\n")
        file.write(f"INFO: {counts['INFO']}\n")
        file.write(f"WARNING: {counts['WARNING']}\n")
        file.write(f"ERROR: {counts['ERROR']}\n")

        file.write(
            f"Invalid: {len(result['invalid_lines'])}\n"
        )

        file.write("\n=== ERROR MESSAGES ===\n")

        for entry in result["errors"]:
            file.write(
                f"{entry['server']}: "
                f"{entry['message']}\n"
            )

        file.write("\n=== INVALID LINES ===\n")

        for item in result["invalid_lines"]:
            file.write(
                f"Line {item['line']}: "
                f"{item['reason']}\n"
            )


# ============================================================
# 10. BACKUP REPORT
# ============================================================

def backup_report() -> None:
    """Copy report to backup directory."""

    shutil.copy2(REPORT_FILE, BACKUP_FILE)


# ============================================================
# 11. SIMULATED RETRY
# ============================================================

def simulated_service_check(attempt: int) -> bool:
    """Simulate a temporary service timeout."""

    if attempt < 3:
        raise TimeoutError("Service did not respond")

    return True


def retry_service_check(max_attempts: int = 3) -> bool:
    """Retry a simulated service operation."""

    for attempt in range(1, max_attempts + 1):

        try:
            result = simulated_service_check(attempt)

        except TimeoutError as error:
            print(
                f"Attempt {attempt}/{max_attempts} "
                f"failed: {error}"
            )

        else:
            print("Service check successful")
            return result

    print("All service attempts failed")
    return False


# ============================================================
# 12. DISPLAY RESULTS
# ============================================================

def display_results(result: dict) -> None:
    """Display analysis results."""

    counts = result["counts"]

    print("\n=== LOG ANALYSIS ===")

    print(f"Total lines: {result['total_lines']}")
    print(f"INFO: {counts['INFO']}")
    print(f"WARNING: {counts['WARNING']}")
    print(f"ERROR: {counts['ERROR']}")

    print(
        f"Invalid lines: "
        f"{len(result['invalid_lines'])}"
    )

    if result["invalid_lines"]:
        print("\n=== INVALID LOG ENTRIES ===")

        for item in result["invalid_lines"]:
            print(
                f"Line {item['line']}: "
                f"{item['reason']}"
            )


# ============================================================
# 13. MAIN PROGRAM
# ============================================================

def main() -> int:

    print("======================================")
    print(" Python DevOps - Part 9")
    print(" Exceptions & Defensive Scripting")
    print("======================================")

    # --------------------------------------------------------
    # Create directories
    # --------------------------------------------------------

    try:
        create_directories()

    except OSError as error:
        print(f"Directory creation failed: {error}")
        return 1

    # --------------------------------------------------------
    # Validate server configuration
    # --------------------------------------------------------

    config = {
        "host": " GitHub.COM ",
        "port": "443",
    }

    try:
        validated_config = validate_server_config(config)

    except (KeyError, ValueError, TypeError) as error:
        print(f"Configuration error: {error}")
        return 1

    else:
        print("\n=== SERVER CONFIGURATION ===")
        print(f"Host: {validated_config['host']}")
        print(f"Port: {validated_config['port']}")

    # --------------------------------------------------------
    # Simulated retry
    # --------------------------------------------------------

    print("\n=== SERVICE RETRY ===")

    service_ok = retry_service_check()

    if not service_ok:
        return 1

    # --------------------------------------------------------
    # Read and analyze log
    # --------------------------------------------------------

    try:
        result = analyze_log(LOG_FILE)

    except FileNotFoundError:
        print(f"ERROR: File not found: {LOG_FILE}")
        return 1

    except PermissionError as error:
        print(f"ERROR: Permission denied: {error}")
        return 1

    except UnicodeError as error:
        print(f"ERROR: Invalid file encoding: {error}")
        return 1

    except OSError as error:
        print(f"ERROR: Cannot read file: {error}")
        return 1

    else:
        display_results(result)

    # --------------------------------------------------------
    # Write report
    # --------------------------------------------------------

    try:
        write_report(REPORT_FILE, result)

    except OSError as error:
        print(f"ERROR: Report generation failed: {error}")
        return 1

    else:
        print(f"\nReport created: {REPORT_FILE}")

    # --------------------------------------------------------
    # Backup report
    # --------------------------------------------------------

    try:
        backup_report()

    except OSError as error:
        print(f"ERROR: Backup failed: {error}")
        return 1

    else:
        print(f"Backup created: {BACKUP_FILE}")

    finally:
        print("Backup operation finished")

    # --------------------------------------------------------
    # Exit code
    # --------------------------------------------------------

    if result["invalid_lines"]:
        print("\nCompleted with invalid log entries")
        return 2

    print("\nAll operations completed successfully")
    return 0


# ============================================================
# 14. PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    sys.exit(main())

