print("=== DevOps Server Checks ===")

servers = ["web-01", "web-02", "db-01"]
ports = [22, 80, 443]

for number, server in enumerate(servers, start=1):
    print()
    print(f"Server {number}: {server}")

    for port in ports:
        if port == 22:
            service = "SSH"
        elif port == 80:
            service = "HTTP"
        elif port == 443:
            service = "HTTPS"
        else:
            service = "OTHER"

        print(f"Checking port {port} ({service})")

print()
print("All checks completed")