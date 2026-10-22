import argparse
import json
import sys

from part21.health_checker import check_endpoint


def parse_args():
    parser = argparse.ArgumentParser(
        description="Check the health of an HTTP or HTTPS endpoint."
    )

    parser.add_argument(
        "--url",
        required=True,
        help="HTTP or HTTPS URL to check",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Request timeout in seconds (default: 5)",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    try:
        result = check_endpoint(args.url, timeout=args.timeout)
    except (ValueError, TypeError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2))

    return 0 if result["healthy"] else 1


if __name__ == "__main__":
    sys.exit(main())
