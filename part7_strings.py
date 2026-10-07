print("========================================")
print(" Python DevOps - String Processing")
print("========================================")


# ============================================================
# 1. BASIC STRING
# ============================================================

server = "web-01"

print("\n=== BASIC STRING ===")

print(f"Server: {server}")
print(f"Length: {len(server)}")
print(f"First character: {server[0]}")
print(f"Last character: {server[-1]}")
print(f"First 3 characters: {server[:3]}")


# ============================================================
# 2. STRIP
# ============================================================

raw_host = "   GitHub.COM   "

clean_host = raw_host.strip()

print("\n=== STRIP ===")

print(f"Raw: '{raw_host}'")
print(f"Clean: '{clean_host}'")


# ============================================================
# 3. LOWER / UPPER
# ============================================================

normalized_host = (
    clean_host.lower()
)

print("\n=== CASE NORMALIZATION ===")

print(
    f"Lower: {normalized_host}"
)

print(
    f"Upper: "
    f"{normalized_host.upper()}"
)


# ============================================================
# 4. REPLACE
# ============================================================

url = "http://example.com"

secure_url = url.replace(
    "http://",
    "https://"
)

print("\n=== REPLACE ===")

print(f"Original: {url}")
print(f"Updated: {secure_url}")


# ============================================================
# 5. SPLIT
# ============================================================

server_line = (
    "web-01|10.0.0.10|443|PRODUCTION"
)

parts = server_line.split("|")

print("\n=== SPLIT ===")

print(parts)


# ============================================================
# 6. UNPACK SPLIT VALUES
# ============================================================

name, ip_address, port_text, environment = (
    server_line.split("|")
)

name = name.strip()
ip_address = ip_address.strip()
port = int(port_text.strip())
environment = environment.strip().lower()


print("\n=== PARSED SERVER ===")

print(f"Name: {name}")
print(f"IP: {ip_address}")
print(f"Port: {port}")
print(f"Environment: {environment}")


# ============================================================
# 7. CREATE DICTIONARY FROM TEXT
# ============================================================

server_data = {
    "name": name,
    "ip": ip_address,
    "port": port,
    "environment": environment,
}

print("\n=== STRUCTURED SERVER DATA ===")

for key, value in server_data.items():
    print(f"{key}: {value}")


# ============================================================
# 8. JOIN
# ============================================================

servers = [
    "web-01",
    "web-02",
    "db-01",
]

server_text = ", ".join(
    servers
)

print("\n=== JOIN ===")

print(server_text)


# ============================================================
# 9. STARTSWITH / ENDSWITH
# ============================================================

log_line = (
    "ERROR Database connection failed"
)

filename = "application.log"


print("\n=== STRING CHECKS ===")

print(
    "Starts with ERROR:",
    log_line.startswith("ERROR")
)

print(
    "Ends with .log:",
    filename.endswith(".log")
)


# ============================================================
# 10. IN / NOT IN
# ============================================================

if "Database" in log_line:
    print("Database text found")

if "WARNING" not in log_line:
    print("WARNING text not found")


# ============================================================
# 11. FIND
# ============================================================

position = log_line.find(
    "Database"
)

print(
    f"Database position: {position}"
)


# ============================================================
# 12. COUNT
# ============================================================

message = (
    "ERROR ERROR WARNING ERROR"
)

error_count = message.count(
    "ERROR"
)

print(
    f"ERROR appears {error_count} times"
)


# ============================================================
# 13. BASIC VALIDATION
# ============================================================

port_text = "443"

print("\n=== VALIDATION ===")

print(
    f"'{port_text}' contains digits: "
    f"{port_text.isdigit()}"
)


# ============================================================
# 14. F-STRING FORMATTING
# ============================================================

response_time = 0.187456
cpu_usage = 72.5678

print("\n=== FORMATTING ===")

print(
    f"Response time: "
    f"{response_time:.2f} seconds"
)

print(
    f"CPU usage: "
    f"{cpu_usage:.1f}%"
)


# ============================================================
# 15. NORMALIZATION FUNCTION
# ============================================================

def normalize_hostname(
    hostname: str
) -> str:
    """Clean and normalize a hostname."""

    return hostname.strip().lower()


host = normalize_hostname(
    "   GitHub.COM   "
)

print("\n=== NORMALIZED HOSTNAME ===")

print(host)


# ============================================================
# 16. LOG LEVEL FUNCTION
# ============================================================

def get_log_level(
    line: str
) -> str:
    """Detect a simple log level."""

    clean_line = (
        line.strip().upper()
    )

    if clean_line.startswith("ERROR"):
        return "ERROR"

    elif clean_line.startswith("WARNING"):
        return "WARNING"

    elif clean_line.startswith("INFO"):
        return "INFO"

    else:
        return "UNKNOWN"


# ============================================================
# 17. LOG PROCESSING
# ============================================================

logs = [
    " INFO|web-01|Application started ",
    " ERROR|web-02|Database connection failed ",
    " WARNING|web-01|CPU usage high ",
    " INFO|db-01|Backup completed ",
    " ERROR|db-01|Connection timeout ",
]


info_count = 0
warning_count = 0
error_count = 0

error_servers = set()
error_messages = []


print("\n=== LOG PROCESSING ===")


for line in logs:

    clean_line = line.strip()

    level, server_name, message = (
        clean_line.split("|", 2)
    )

    level = level.strip().upper()

    server_name = (
        server_name.strip().lower()
    )

    message = message.strip()

    print(
        f"{level:<7} | "
        f"{server_name:<6} | "
        f"{message}"
    )

    if level == "INFO":
        info_count += 1

    elif level == "WARNING":
        warning_count += 1

    elif level == "ERROR":

        error_count += 1

        error_servers.add(
            server_name
        )

        error_messages.append(
            message
        )


# ============================================================
# 18. LOG SUMMARY
# ============================================================

print("\n=== LOG SUMMARY ===")

print(f"INFO: {info_count}")
print(f"WARNING: {warning_count}")
print(f"ERROR: {error_count}")

print(
    "Servers with errors: "
    + ", ".join(
        sorted(error_servers)
    )
)


print("\n=== ERROR MESSAGES ===")

for message in error_messages:
    print(f"- {message}")


# ============================================================
# 19. KEY=VALUE PARSING
# ============================================================

config_lines = [
    "ENVIRONMENT=production",
    "PORT=443",
    "TIMEOUT=10",
    "DEBUG=false",
]

config = {}


for line in config_lines:

    key, value = line.split(
        "=",
        1
    )

    key = key.strip()
    value = value.strip()

    config[key] = value


print("\n=== CONFIGURATION ===")

for key, value in config.items():
    print(f"{key}: {value}")


print("\n========================================")
print(" Part 7 completed")
print("========================================")