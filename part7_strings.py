logs = [
    " INFO|web-01|Application started ",
    " ERROR|web-02|Database connection failed ",
    " WARNING|web-01|CPU usage high ",
    " INFO|db-01|Backup completed ",
    " ERROR|db-01|Connection timeout ",
]

error_count = 0
warning_count = 0
info_count = 0

error_servers = set()

for line in logs:
    clean_line = line.strip()

    level, server, message = clean_line.split("|", 2)

    level = level.strip().upper()
    server = server.strip().lower()
    message = message.strip()

    print(f"{level:<7} | {server:<6} | {message}")

    if level == "ERROR":
        error_count += 1
        error_servers.add(server)

    elif level == "WARNING":
        warning_count += 1

    elif level == "INFO":
        info_count += 1

print()
print("=== LOG SUMMARY ===")
print(f"Errors: {error_count}")
print(f"Warnings: {warning_count}")
print(f"Info: {info_count}")
print(f"Servers with errors: {', '.join(sorted(error_servers))}")