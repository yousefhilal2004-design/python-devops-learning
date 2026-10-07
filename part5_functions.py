print("========================================")
print(" Python DevOps - Functions Practice")
print("========================================")


# ============================================================
# 1. SIMPLE FUNCTION
# ============================================================

def show_start_message() -> None:
    """Display a start message."""

    print("Starting DevOps service checks...")


# ============================================================
# 2. FUNCTION WITH PARAMETER
# ============================================================

def check_server(server: str) -> None:
    """Display the server currently being checked."""

    print(f"Checking server: {server}")


# ============================================================
# 3. MULTIPLE PARAMETERS
# ============================================================

def check_service(host: str, port: int) -> None:
    """Display a host and port check."""

    print(f"Checking {host}:{port}")


# ============================================================
# 4. DEFAULT PARAMETER
# ============================================================

def build_url(host: str, port: int = 443) -> str:
    """Build a simple HTTPS URL."""

    return f"https://{host}:{port}"


# ============================================================
# 5. RETURN VALUE
# ============================================================

def classify_port(port: int) -> str:
    """Return a service name for common ports."""

    if port == 22:
        return "SSH"

    elif port == 53:
        return "DNS"

    elif port == 80:
        return "HTTP"

    elif port == 443:
        return "HTTPS"

    else:
        return "OTHER"


# ============================================================
# 6. HTTP STATUS FUNCTION
# ============================================================

def classify_http_status(status_code: int) -> str:
    """Classify an HTTP status code."""

    if 200 <= status_code < 300:
        return "SUCCESS"

    elif 300 <= status_code < 400:
        return "REDIRECT"

    elif 400 <= status_code < 500:
        return "CLIENT_ERROR"

    elif 500 <= status_code < 600:
        return "SERVER_ERROR"

    else:
        return "UNKNOWN"


# ============================================================
# 7. BOOLEAN RETURN
# ============================================================

def is_web_port(port: int) -> bool:
    """Return True when the port is a common HTTP/HTTPS port."""

    return port == 80 or port == 443


# ============================================================
# 8. RESOURCE USAGE FUNCTION
# ============================================================

def classify_resource_usage(
    usage: float,
    warning: float = 80,
    critical: float = 90
) -> str:
    """Classify CPU or disk usage."""

    if usage >= critical:
        return "CRITICAL"

    elif usage >= warning:
        return "WARNING"

    else:
        return "NORMAL"


# ============================================================
# 9. FUNCTION RETURNING MULTIPLE VALUES
# ============================================================

def get_server_endpoint() -> tuple:
    """Return a simple host and port pair."""

    host = "github.com"
    port = 443

    return host, port


# ============================================================
# 10. LOCAL SCOPE
# ============================================================

def demonstrate_scope() -> str:
    """Demonstrate a local variable."""

    local_status = "UP"

    return local_status


# ============================================================
# MAIN PROGRAM
# ============================================================

show_start_message()

servers = [
    "web-01",
    "web-02",
    "db-01",
]

print("\n=== SERVERS ===")

for server in servers:
    check_server(server)


print("\n=== SERVICE CHECK ===")

check_service(
    "github.com",
    443
)


print("\n=== URL ===")

url = build_url("github.com")

print(url)


print("\n=== PORT CLASSIFICATION ===")

ports = [
    22,
    53,
    80,
    443,
    3306,
]

for port in ports:

    service = classify_port(port)

    print(
        f"Port {port}: {service}"
    )


print("\n=== HTTP STATUS ===")

status_codes = [
    200,
    301,
    404,
    503,
]

for status_code in status_codes:

    result = classify_http_status(
        status_code
    )

    print(
        f"HTTP {status_code}: {result}"
    )


print("\n=== WEB PORT ===")

port = 443

print(
    f"Is {port} a web port? "
    f"{is_web_port(port)}"
)


print("\n=== RESOURCE USAGE ===")

cpu_usage = 85.5
disk_usage = 93.2

cpu_status = classify_resource_usage(
    cpu_usage
)

disk_status = classify_resource_usage(
    disk_usage
)

print(
    f"CPU: {cpu_usage}% "
    f"({cpu_status})"
)

print(
    f"Disk: {disk_usage}% "
    f"({disk_status})"
)


print("\n=== MULTIPLE RETURN VALUES ===")

host, port = get_server_endpoint()

print(f"Host: {host}")
print(f"Port: {port}")


print("\n=== LOCAL SCOPE ===")

status = demonstrate_scope()

print(f"Returned status: {status}")


print("\n========================================")
print(" Part 5 completed")
print("========================================")