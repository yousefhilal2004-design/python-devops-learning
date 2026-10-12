
from pathlib import Path

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Directories
LOG_DIR = BASE_DIR / "logs"
REPORT_DIR = BASE_DIR / "reports"
BACKUP_DIR = BASE_DIR / "backups"

# Files
LOG_FILE = LOG_DIR / "app.log"
REPORT_FILE = REPORT_DIR / "summary.txt"
BACKUP_FILE = BACKUP_DIR / "summary_backup.txt"

# Example server configuration
SERVER_CONFIG = {
    "host": "github.com",
    "port": 443,
}
