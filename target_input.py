host = input("Enter target hostname: ").strip()
port_text = input("Enter target port: ").strip()

port = int(port_text)

print()
print("=== Target Information ===")
print(f"Host: {host}")
print(f"Port: {port}")

print()
print("=== Types ===")
print(f"Host type: {type(host)}")
print(f"Port type: {type(port)}")

print()
print("=== Basic Checks ===")
print(f"Is HTTP port: {port == 80}")
print(f"Is HTTPS port: {port == 443}")
print(f"Is common web port: {port == 80 or port == 443}")