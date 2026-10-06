server = "github.com"
port = 443
response_time = 0.25
is_healthy = True
ip_address = None

print("=== Server Information ===")
print(f"Server: {server}")
print(f"Port: {port}")
print(f"Response Time: {response_time}")
print(f"Healthy: {is_healthy}")
print(f"IP Address: {ip_address}")

print()
print("=== Data Types ===")
print(type(server))
print(type(port))
print(type(response_time))
print(type(is_healthy))
print(type(ip_address))

print()
print("=== Checks ===")
print(f"Is HTTPS port: {port == 443}")
print(f"Fast response: {response_time < 1}")
print(f"Healthy and HTTPS: {is_healthy and port == 443}")