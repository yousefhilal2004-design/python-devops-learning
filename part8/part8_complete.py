from pathlib import Path
import shutil


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

LOG_DIR = BASE_DIR / "logs"
REPORT_DIR = BASE_DIR / "reports"
BACKUP_DIR = BASE_DIR / "backups"

LOG_FILE = LOG_DIR / "app.log"
AUTOMATION_LOG = LOG_DIR / "automation.log"
REPORT_FILE = REPORT_DIR / "log_report.txt"


# ============================================================
# CREATE REQUIRED DIRECTORIES
# ============================================================

def create_directories() -> None:
    """Create the directories required by the program."""

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# WRITE AUTOMATION LOG
# ============================================================

def write_log(message: str) -> None:
    """Append a message to the automation log."""

    with AUTOMATION_LOG.open(
        "a",
        encoding="utf-8"
    ) as file:
        file.write(f"{message}\n")


# ============================================================
# SHOW FILE INFORMATION
# ============================================================

def show_file_info(file_path: Path) -> None:
    """Display basic information about a file."""

    print("\n=== FILE INFORMATION ===")

    print(f"Path: {file_path}")
    print(f"Name: {file_path.name}")
    print(f"Stem: {file_path.stem}")
    print(f"Extension: {file_path.suffix}")
    print(f"Parent: {file_path.parent}")
    print(f"Exists: {file_path.exists()}")
    print(f"Is file: {file_path.is_file()}")

    if file_path.is_file():
        size = file_path.stat().st_size
        print(f"Size: {size} bytes")


# ============================================================
# READ FILE
# ============================================================

def display_file(file_path: Path) -> None:
    """Read and display a file line by line."""

    print("\n=== LOG CONTENT ===")

    if not file_path.is_file():
        print(f"ERROR: File not found: {file_path}")
        return

    line_count = 0

    with file_path.open(
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:
            clean_line = line.strip()

            if not clean_line:
                continue

            print(clean_line)

            line_count += 1

    print(f"\nTotal non-empty lines: {line_count}")


# ============================================================
# ANALYZE LOG
# ============================================================

def analyze_log(file_path: Path) -> dict:
    """Analyze INFO, WARNING, and ERROR messages."""

    counts = {
        "INFO": 0,
        "WARNING": 0,
        "ERROR": 0,
        "UNKNOWN": 0,
    }

    errors = []
    warnings = []

    if not file_path.is_file():

        return {
            "counts": counts,
            "errors": errors,
            "warnings": warnings,
        }

    with file_path.open(
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            clean_line = line.strip()

            if not clean_line:
                continue

            if clean_line.startswith("INFO"):
                counts["INFO"] += 1

            elif clean_line.startswith("WARNING"):
                counts["WARNING"] += 1
                warnings.append(clean_line)

            elif clean_line.startswith("ERROR"):
                counts["ERROR"] += 1
                errors.append(clean_line)

            else:
                counts["UNKNOWN"] += 1

    return {
        "counts": counts,
        "errors": errors,
        "warnings": warnings,
    }


# ============================================================
# DISPLAY ANALYSIS
# ============================================================

def display_analysis(result: dict) -> None:
    """Display log analysis in the terminal."""

    counts = result["counts"]

    print("\n=== LOG ANALYSIS ===")

    print(f"INFO: {counts['INFO']}")
    print(f"WARNING: {counts['WARNING']}")
    print(f"ERROR: {counts['ERROR']}")
    print(f"UNKNOWN: {counts['UNKNOWN']}")

    print("\n=== WARNINGS ===")

    if result["warnings"]:

        for warning in result["warnings"]:
            print(warning)

    else:
        print("No warnings found.")

    print("\n=== ERRORS ===")

    if result["errors"]:

        for error in result["errors"]:
            print(error)

    else:
        print("No errors found.")


# ============================================================
# WRITE REPORT
# ============================================================

def write_report(
    report_file: Path,
    source_file: Path,
    result: dict
) -> None:
    """Write log analysis to a report file."""

    counts = result["counts"]
    errors = result["errors"]
    warnings = result["warnings"]

    with report_file.open(
        "w",
        encoding="utf-8"
    ) as file:

        file.write("========================================\n")
        file.write(" PYTHON DEVOPS LOG ANALYSIS REPORT\n")
        file.write("========================================\n\n")

        file.write(f"Source: {source_file}\n")
        file.write(f"Source file: {source_file.name}\n\n")

        file.write("=== SUMMARY ===\n")

        file.write(f"INFO: {counts['INFO']}\n")
        file.write(f"WARNING: {counts['WARNING']}\n")
        file.write(f"ERROR: {counts['ERROR']}\n")
        file.write(f"UNKNOWN: {counts['UNKNOWN']}\n")

        file.write("\n=== WARNING LINES ===\n")

        if warnings:

            for warning in warnings:
                file.write(f"{warning}\n")

        else:
            file.write("No warnings found.\n")

        file.write("\n=== ERROR LINES ===\n")

        if errors:

            for error in errors:
                file.write(f"{error}\n")

        else:
            file.write("No errors found.\n")


# ============================================================
# BACKUP FILE
# ============================================================

def backup_file(
    source_file: Path,
    backup_directory: Path
) -> Path | None:
    """Create a backup copy of a file."""

    if not source_file.is_file():
        print(f"Cannot backup missing file: {source_file}")
        return None

    backup_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    backup_file_path = (
        backup_directory
        / f"{source_file.stem}_backup{source_file.suffix}"
    )

    shutil.copy2(
        source_file,
        backup_file_path
    )

    return backup_file_path


# ============================================================
# SCAN LOG DIRECTORY
# ============================================================

def scan_log_directory(directory: Path) -> list:
    """Return all .log files inside a directory."""

    log_files = []

    if not directory.is_dir():
        return log_files

    for file_path in directory.glob("*.log"):

        if file_path.is_file():
            log_files.append(file_path)

    return log_files


# ============================================================
# DISPLAY LOG FILES
# ============================================================

def display_log_files(log_files: list) -> None:
    """Display discovered log files."""

    print("\n=== LOG FILES ===")

    if not log_files:
        print("No log files found.")
        return

    for number, log_file in enumerate(
        log_files,
        start=1
    ):
        print(f"{number}. {log_file.name}")

    print(f"\nTotal log files: {len(log_files)}")


# ============================================================
# MAIN PROGRAM
# ============================================================

def main() -> None:
    """Run the complete Part 8 filesystem automation."""

    print("========================================")
    print(" Python DevOps File Automation Tool")
    print("========================================")

    # Create required directories
    create_directories()

    write_log("Program started")

    # --------------------------------------------------------
    # Check source log
    # --------------------------------------------------------

    if not LOG_FILE.is_file():

        print()
        print("ERROR: Input log file was not found.")
        print(f"Expected file: {LOG_FILE}")

        write_log(
            f"ERROR: Input file not found: {LOG_FILE}"
        )

        return

    write_log(
        f"Input log found: {LOG_FILE}"
    )

    # --------------------------------------------------------
    # File information
    # --------------------------------------------------------

    show_file_info(LOG_FILE)

    # --------------------------------------------------------
    # Read log file
    # --------------------------------------------------------

    display_file(LOG_FILE)

    # --------------------------------------------------------
    # Analyze log
    # --------------------------------------------------------

    result = analyze_log(LOG_FILE)

    display_analysis(result)

    write_log("Log analysis completed")

    # --------------------------------------------------------
    # Generate report
    # --------------------------------------------------------

    write_report(
        REPORT_FILE,
        LOG_FILE,
        result
    )

    print("\n=== REPORT ===")
    print(f"Report created: {REPORT_FILE}")

    write_log(
        f"Report created: {REPORT_FILE}"
    )

    # --------------------------------------------------------
    # Backup report
    # --------------------------------------------------------

    backup_path = backup_file(
        REPORT_FILE,
        BACKUP_DIR
    )

    print("\n=== BACKUP ===")

    if backup_path is not None:

        print(
            f"Backup created: {backup_path}"
        )

        write_log(
            f"Backup created: {backup_path}"
        )

    else:

        print("Backup was not created.")

        write_log(
            "WARNING: Backup was not created"
        )

    # --------------------------------------------------------
    # Scan log directory
    # --------------------------------------------------------

    log_files = scan_log_directory(
        LOG_DIR
    )

    display_log_files(log_files)

    # --------------------------------------------------------
    # Finish
    # --------------------------------------------------------

    write_log("Program completed")

    print("\n========================================")
    print(" Part 8 completed successfully")
    print("========================================")


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()