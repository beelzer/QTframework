"""Logging utilities with color support and enhanced configuration."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import ClassVar


class LogFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""

    # ANSI color codes
    COLORS: ClassVar[dict[str, str]] = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def __init__(self, fmt: str | None = None, use_color: bool = True):
        """Initialize formatter.

        Args:
            fmt: Log format string
            use_color: Whether to use color output
        """
        super().__init__(fmt, datefmt="%H:%M:%S")
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with optional color.

        Args:
            record: Log record to format

        Returns:
            Formatted log string
        """
        if self.use_color and sys.stderr.isatty():
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logging(
    log_file: Path | str | None = None,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    log_format: str | None = None,
) -> None:
    """Setup logging configuration.

    Args:
        log_file: Optional path to log file. If None, only console logging is enabled
        console_level: Logging level for console output (default: INFO)
        file_level: Logging level for file output (default: DEBUG)
        log_format: Custom log format string
    """
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture all messages at root level

    # Remove any existing handlers
    root_logger.handlers.clear()

    # Console handler with color
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_formatter = LogFormatter(log_format, use_color=True)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(file_level)
        file_formatter = LogFormatter(log_format, use_color=False)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("PySide6").setLevel(logging.WARNING)
    logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
