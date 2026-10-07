print("========================================")
print(" Python DevOps - Loops Practice")
print("========================================")

servers = [
    "web-01",
    "web-02",
    "db-01",
]

ports = [
    22,
    53,
    80,
    443,
    3306,
]

# ============================================================
# 1. BASIC FOR LOOP
# ============================================================

print("\n=== SERVERS ===")

for server in servers:
    print(f"Checking server: {server}")


# ============================================================
# 2. ENUMERATE
# ============================================================

print("\n=== NUMBERED SERVERS ===")

for number, server in enumerate(servers, start=1):
    print(f"{number}. {server}")


# ============================================================
# 3. LOOP + CONDITIONS
# ============================================================

print("\n=== PORT CLASSIFICATION ===")

for port in ports:

    if port == 22:
        service = "SSH"

    elif port == 53:
        service = "DNS"

    elif port == 80:
        service = "HTTP"

    elif port == 443:
        service = "HTTPS"

    else:
        service = "OTHER"

    print(f"Port {port}: {service}")


# ============================================================
# 4. CONTINUE
# ============================================================

print("\n=== WEB PORT CHECK ===")

for port in ports:

    if port not in (80, 443):
        print(f"Skipping port {port}")
        continue

    print(f"Checking web port {port}")


# ============================================================
# 5. BREAK
# ============================================================

print("\n=== SEARCH FOR HTTPS ===")

for port in ports:

    print(f"Checking port {port}")

    if port == 443:
        print("HTTPS port found")
        break


# ============================================================
# 6. RANGE
# ============================================================

print("\n=== RETRY ATTEMPTS ===")

for attempt in range(1, 4):
    print(f"Attempt {attempt}/3")


# ============================================================
# 7. SIMULATED RETRY WITH BREAK
# ============================================================

print("\n=== CONNECTION RETRY ===")

max_attempts = 3

for attempt in range(1, max_attempts + 1):

    print(f"Connection attempt {attempt}")

    # Simulate success on attempt 2
    success = attempt == 2

    if success:
        print("Connection successful")
        break

    print("Connection failed")


# ============================================================
# 8. WHILE LOOP
# ============================================================

print("\n=== WHILE LOOP ===")

attempt = 1

while attempt <= 3:

    print(f"Attempt {attempt}")

    attempt += 1


# ============================================================
# 9. NESTED LOOPS
# ============================================================

print("\n=== SERVER + PORT CHECKS ===")

web_ports = [80, 443]

for server in servers:

    print(f"\nServer: {server}")

    for port in web_ports:
        print(f"  Checking {server}:{port}")


# ============================================================
# 10. COUNTERS
# ============================================================

print("\n=== STATUS COUNTER ===")

statuses = [
    True,
    True,
    False,
    True,
    False,
]

successful = 0
failed = 0

for status in statuses:

    if status:
        successful += 1

    else:
        failed += 1


print(f"Total: {len(statuses)}")
print(f"Successful: {successful}")
print(f"Failed: {failed}")


print("\n========================================")
print(" Part 4 completed")
print("========================================")