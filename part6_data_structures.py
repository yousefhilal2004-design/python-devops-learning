servers = [
    {
        "name": "web-01",
        "ip": "10.0.0.10",
        "ports": [80, 443],
        "healthy": True,
    },
    {
        "name": "web-02",
        "ip": "10.0.0.11",
        "ports": [80, 443],
        "healthy": False,
    },
    {
        "name": "db-01",
        "ip": "10.0.0.20",
        "ports": [3306],
        "healthy": True,
    },
]

healthy_count = 0
failed_servers = []
all_ports = set()

for server in servers:
    print()
    print(f"Server: {server['name']}")
    print(f"IP: {server['ip']}")

    if server["healthy"]:
        print("Status: HEALTHY")
        healthy_count += 1
    else:
        print("Status: FAILED")
        failed_servers.append(server["name"])

    print("Ports:")

    for port in server["ports"]:
        print(f"  - {port}")
        all_ports.add(port)

print()
print("=== SUMMARY ===")
print(f"Total servers: {len(servers)}")
print(f"Healthy servers: {healthy_count}")
print(f"Failed servers: {len(failed_servers)}")
print(f"Failed server names: {failed_servers}")
print(f"Unique ports: {sorted(all_ports)}")