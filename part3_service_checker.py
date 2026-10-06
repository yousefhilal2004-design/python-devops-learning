print("=== DevOps Service Checker ===")

server = input("Server name: ").strip()
port = int(input("Port: ").strip())
status_code = int(input("HTTP status code: ").strip())
cpu_usage = float(input("CPU usage: ").strip())
disk_usage = float(input("Disk usage: ").strip())

print()
print("=== SERVER REPORT ===")

print(f"Server: {server}")
print(f"Port: {port}")

if port == 22:
    print("Service type: SSH")
elif port == 80:
    print("Service type: HTTP")
elif port == 443:
    print("Service type: HTTPS")
else:
    print("Service type: Other")

if 200 <= status_code < 300:
    print("HTTP: SUCCESS")
elif 300 <= status_code < 400:
    print("HTTP: REDIRECT")
elif 400 <= status_code < 500:
    print("HTTP: CLIENT ERROR")
elif 500 <= status_code < 600:
    print("HTTP: SERVER ERROR")
else:
    print("HTTP: UNKNOWN")

if cpu_usage >= 90:
    print("CPU: CRITICAL")
elif cpu_usage >= 80:
    print("CPU: WARNING")
else:
    print("CPU: NORMAL")

if disk_usage >= 90:
    print("Disk: CRITICAL")
elif disk_usage >= 80:
    print("Disk: WARNING")
else:
    print("Disk: NORMAL")