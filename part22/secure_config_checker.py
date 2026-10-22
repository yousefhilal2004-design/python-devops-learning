import argparse
import json
import os
import sys
from collections.abc import Mapping


ALLOWED_ENVIRONMENTS = {
    "development",
    "testing",
    "staging",
    "production",
}

PLACEHOLDER_VALUES = {
    "replace-me",
    "replace-with-a-local-test-value",
    "your-api-key",
    "your-secret",
    "changeme",
    "todo",
}


def check_configuration(env: Mapping[str, str]) -> list[str]:
    """
    Validate required configuration without exposing secret values.

    Returns a list of safe-to-display error messages.
    An empty list means the configuration passed these checks.
    """
    errors = []

    app_env = env.get("APP_ENV", "").strip().lower()

    if not app_env:
        errors.append("APP_ENV is missing")
    elif app_env not in ALLOWED_ENVIRONMENTS:
        errors.append("APP_ENV has an unsupported value")

    api_key = env.get("API_KEY", "").strip()

    if not api_key:
        errors.append("API_KEY is missing")
    elif api_key.lower() in PLACEHOLDER_VALUES:
        errors.append("API_KEY still contains a placeholder value")

    return errors


def parse_args():
    parser = argparse.ArgumentParser(
        description="Validate required application configuration safely."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the result as JSON",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    # Read values from the process environment.
    # Do not print the environment or secret values.
    errors = check_configuration(os.environ)

    result = {
        "valid": not errors,
        "errors": errors,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    elif errors:
        print("Configuration check failed:")
        for error in errors:
            print(f"- {error}")
    else:
        print("Configuration check passed.")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
