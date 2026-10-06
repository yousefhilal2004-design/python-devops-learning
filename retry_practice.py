max_attempts = 3

for attempt in range(1, max_attempts + 1):
    print(f"Attempt {attempt}/{max_attempts}")

    if attempt == 2:
        print("Operation successful")
        break

    print("Operation failed, trying again...")