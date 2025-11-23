# logger.py
import logging
from logging.handlers import RotatingFileHandler
import sys
from config.config import PROJECT_PATH


# ---- CONFIG ----
LOG_FILE = PROJECT_PATH / "logs" / "mobile_app_server.log"
MAX_BYTES = 1_000_000  # 1 MB per file
BACKUP_COUNT = 3       # Keep 3 rotated logs


class ColorFormatter(logging.Formatter):
    """Add colors to console logs."""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[41m"  # Red background
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        message = super().format(record)
        return f"{color}{message}{self.RESET}"


def get_logger(name: str = "server", level=logging.INFO) -> logging.Logger:
    """Create a logger with both console + rotating file handlers."""

    logger = logging.getLogger(name)

    # Prevent duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # ---- Console Handler ----
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_format = ColorFormatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_format)

    # ---- File Handler ----
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT
    )
    file_handler.setLevel(level)
    file_format = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)

    # ---- Add handlers ----
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
