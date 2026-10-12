
class LogFormatError(ValueError):
    """Raised when a log line has invalid data."""


def validate_hostname(hostname: str) -> str:
    """Validate a nonempty hostname and normalize it."""

    if not isinstance(hostname, str):
        raise TypeError("Hostname must be a string")

    hostname = hostname.strip().lower()

    if not hostname:
        raise ValueError("Hostname cannot be empty")

    return hostname


def validate_port(port: int) -> int:
    """Validate a TCP/UDP port number."""

    if isinstance(port, bool) or not isinstance(port, int):
        raise TypeError("Port must be an integer")

    if not 1 <= port <= 65535:
        raise ValueError("Port must be between 1 and 65535")

    return port


def validate_server_config(config: dict) -> dict:
    """Validate required server configuration fields."""

    if "host" not in config:
        raise KeyError("Missing host")

    if "port" not in config:
        raise KeyError("Missing port")

    host = validate_hostname(config["host"])
    port = validate_port(config["port"])

    return {
        "host": host,
        "port": port,
    }


def parse_log_line(line: str) -> dict:
    """Parse LEVEL|SERVER|MESSAGE."""

    parts = line.strip().split("|", 2)

    if len(parts) != 3:
        raise LogFormatError(
            "Expected LEVEL|SERVER|MESSAGE"
        )

    level, server, message = parts

    level = level.strip().upper()
    server = server.strip().lower()
    message = message.strip()

    if level not in ("INFO", "WARNING", "ERROR"):
        raise LogFormatError(
            f"Unsupported log level: {level}"
        )

    if not server:
        raise LogFormatError("Server name cannot be empty")

    if not message:
        raise LogFormatError("Message cannot be empty")

    return {
        "level": level,
        "server": server,
        "message": message,
    }
