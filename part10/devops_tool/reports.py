
from pathlib import Path


def write_report(report_file: Path, result: dict) -> None:
    """Write a DevOps log analysis report."""

    report_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    counts = result["counts"]

    with report_file.open("w", encoding="utf-8") as file:

        file.write("====================================\n")
        file.write(" MODULAR DEVOPS LOG ANALYSIS REPORT\n")
        file.write("====================================\n\n")

        file.write(
            f"Total lines: {result['total_lines']}\n"
        )

        file.write(f"INFO: {counts['INFO']}\n")
        file.write(f"WARNING: {counts['WARNING']}\n")
        file.write(f"ERROR: {counts['ERROR']}\n")

        file.write(
            f"Invalid: {len(result['invalid_lines'])}\n"
        )

        file.write("\n=== ERROR MESSAGES ===\n")

        if result["errors"]:
            for entry in result["errors"]:
                file.write(
                    f"{entry['server']}: "
                    f"{entry['message']}\n"
                )
        else:
            file.write("No errors found.\n")

        file.write("\n=== WARNINGS ===\n")

        if result["warnings"]:
            for entry in result["warnings"]:
                file.write(
                    f"{entry['server']}: "
                    f"{entry['message']}\n"
                )
        else:
            file.write("No warnings found.\n")

        file.write("\n=== INVALID LINES ===\n")

        if result["invalid_lines"]:
            for item in result["invalid_lines"]:
                file.write(
                    f"Line {item['line']}: "
                    f"{item['reason']}\n"
                )
        else:
            file.write("No invalid lines.\n")
