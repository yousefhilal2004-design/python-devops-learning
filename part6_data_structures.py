print("========================================")
print(" Python DevOps - Data Structures")
print("========================================")


# ============================================================
# 1. LIST
# ============================================================

servers = [
    "web-01",
    "web-02",
    "db-01",
]

print("\n=== LIST ===")

print(f"Servers: {servers}")
print(f"First server: {servers[0]}")
print(f"Last server: {servers[-1]}")
print(f"Total servers: {len(servers)}")


# ============================================================
# 2. MODIFY LIST
# ============================================================

servers.append("cache-01")

print("\nAfter append:")
print(servers)

servers.remove("cache-01")

print("\nAfter remove:")
print(servers)


# ============================================================
# 3. LOOP THROUGH LIST
# ============================================================

print("\n=== SERVER LIST ===")

for server in servers:
    print(f"Server: {server}")


# ============================================================
# 4. TUPLE
# ============================================================

endpoint = (
    "github.com",
    443,
)

host, port = endpoint

print("\n=== TUPLE ===")

print(f"Host: {host}")
print(f"Port: {port}")


# ============================================================
# 5. DICTIONARY
# ============================================================

server = {
    "name": "web-01",
    "ip": "10.0.0.10",
    "port": 443,
    "healthy": True,
}

print("\n=== DICTIONARY ===")

print(f"Name: {server['name']}")
print(f"IP: {server['ip']}")
print(f"Port: {server['port']}")
print(f"Healthy: {server['healthy']}")


# ============================================================
# 6. MODIFY DICTIONARY
# ============================================================

server["environment"] = "production"

server["healthy"] = False

print("\n=== UPDATED DICTIONARY ===")

for key, value in server.items():
    print(f"{key}: {value}")


# ============================================================
# 7. DICTIONARY GET
# ============================================================

hostname = server.get(
    "hostname",
    "UNKNOWN"
)

print(
    f"\nHostname: {hostname}"
)


# ============================================================
# 8. SET
# ============================================================

ports = {
    22,
    80,
    443,
    443,
    80,
}

print("\n=== SET ===")

print(f"Unique ports: {sorted(ports)}")

ports.add(8080)

print(
    f"After adding 8080: "
    f"{sorted(ports)}"
)


# ============================================================
# 9. SET COMPARISON
# ============================================================

required_ports = {
    80,
    443,
    8080,
}

open_ports = {
    22,
    80,
    443,
}

missing_ports = (
    required_ports - open_ports
)

common_ports = (
    required_ports & open_ports
)

print("\n=== PORT COMPARISON ===")

print(
    f"Required: "
    f"{sorted(required_ports)}"
)

print(
    f"Open: "
    f"{sorted(open_ports)}"
)

print(
    f"Common: "
    f"{sorted(common_ports)}"
)

print(
    f"Missing: "
    f"{sorted(missing_ports)}"
)


# ============================================================
# 10. LIST OF DICTIONARIES
# ============================================================

server_inventory = [
    {
        "name": "web-01",
        "ip": "10.0.0.10",
        "environment": "production",
        "ports": [80, 443],
        "healthy": True,
    },

    {
        "name": "web-02",
        "ip": "10.0.0.11",
        "environment": "production",
        "ports": [80, 443],
        "healthy": False,
    },

    {
        "name": "db-01",
        "ip": "10.0.0.20",
        "environment": "production",
        "ports": [3306],
        "healthy": True,
    },
]


print("\n=== SERVER INVENTORY ===")

for server in server_inventory:

    print()
    print(f"Name: {server['name']}")
    print(f"IP: {server['ip']}")
    print(
        f"Environment: "
        f"{server['environment']}"
    )

    print("Ports:")

    for port in server["ports"]:
        print(f"  - {port}")

    if server["healthy"]:
        print("Status: HEALTHY")

    else:
        print("Status: FAILED")


# ============================================================
# 11. COLLECT FAILED SERVERS
# ============================================================

failed_servers = []

for server in server_inventory:

    if not server["healthy"]:
        failed_servers.append(
            server["name"]
        )


print("\n=== FAILED SERVERS ===")

print(
    f"Failed: {failed_servers}"
)


# ============================================================
# 12. COLLECT UNIQUE PORTS
# ============================================================

all_ports = set()

for server in server_inventory:

    for port in server["ports"]:
        all_ports.add(port)


print("\n=== ALL UNIQUE PORTS ===")

print(sorted(all_ports))


# ============================================================
# 13. COUNTERS
# ============================================================

healthy_count = 0
failed_count = 0

for server in server_inventory:

    if server["healthy"]:
        healthy_count += 1

    else:
        failed_count += 1


print("\n=== INVENTORY SUMMARY ===")

print(
    f"Total servers: "
    f"{len(server_inventory)}"
)

print(
    f"Healthy: {healthy_count}"
)

print(
    f"Failed: {failed_count}"
)


# ============================================================
# 14. FUNCTION RETURNING DICTIONARY
# ============================================================

def create_server(
    name: str,
    ip: str,
    port: int
) -> dict:
    """Create and return server information."""

    return {
        "name": name,
        "ip": ip,
        "port": port,
    }


new_server = create_server(
    "api-01",
    "10.0.0.30",
    8080,
)

print("\n=== CREATED SERVER ===")

print(new_server)


print("\n========================================")
print(" Part 6 completed")
print("========================================")