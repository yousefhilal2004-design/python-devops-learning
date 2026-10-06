def classify_port(port: int) -> str:
    """Return a common service name for a port."""

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


def classify_http_status(status_code: int) -> str:
    """Return a category for an HTTP status code."""

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


def classify_resource_usage(usage: float) -> str:
    """Classify CPU or disk usage."""

    if usage >= 90:
        return "CRITICAL"
    elif usage >= 80:
        return "WARNING"
    else:
        return "NORMAL"


server = input("Server: ").strip()
port = int(input("Port: ").strip())
status_code = int(input("HTTP status: ").strip())
cpu_usage = float(input("CPU usage: ").strip())
disk_usage = float(input("Disk usage: ").strip())

service = classify_port(port)
http_status = classify_http_status(status_code)
cpu_status = classify_resource_usage(cpu_usage)
disk_status = classify_resource_usage(disk_usage)

print()
print("=== DEVOPS SERVICE REPORT ===")
print(f"Server: {server}")
print(f"Port: {port}")
print(f"Service: {service}")
print(f"HTTP: {http_status}")
print(f"CPU: {cpu_usage}% ({cpu_status})")
print(f"Disk: {disk_usage}% ({disk_status})")