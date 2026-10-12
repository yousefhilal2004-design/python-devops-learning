
from pathlib import Path
import shutil


def backup_file(source: Path, destination: Path) -> Path:
    """Create a backup copy of a file."""

    if not source.is_file():
        raise FileNotFoundError(
            f"Source file does not exist: {source}"
        )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(source, destination)

    return destination
