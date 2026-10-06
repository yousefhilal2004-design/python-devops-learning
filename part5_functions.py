def classify_port(port: int) -> str:
    """Return the common service associated with a port."""

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


ports = [22, 53, 80, 443, 3306]

for port in ports:
    service = classify_port(port)
    print(f"Port {port}: {service}")