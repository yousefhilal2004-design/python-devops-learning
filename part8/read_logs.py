info_count = 0
warning_count = 0
error_count = 0

with open("logs/app.log", "r") as file:
    for line in file:
        clean_line = line.strip()

        if clean_line.startswith("INFO"):
            info_count += 1

        elif clean_line.startswith("WARNING"):
            warning_count += 1

        elif clean_line.startswith("ERROR"):
            error_count += 1

print(f"INFO: {info_count}")
print(f"WARNING: {warning_count}")
print(f"ERROR: {error_count}")