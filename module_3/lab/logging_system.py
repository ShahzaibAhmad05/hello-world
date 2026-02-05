"""Comprehensive Logging System Implementation

Demonstrates zero-shot, one-shot, and few-shot prompting approaches.
This implementation combines all approaches into a complete logging system.
"""

import logging
import json
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum
import threading
import sys


class Environment(Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class ColorCodes:
    """ANSI color codes for console output."""
    RESET = "\033[0m"
    DEBUG = "\033[36m"  # Cyan
    INFO = "\033[32m"   # Green
    WARNING = "\033[33m"  # Yellow
    ERROR = "\033[31m"  # Red
    CRITICAL = "\033[35m"  # Magenta


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'duration'):
            log_data['duration'] = record.duration
        if hasattr(record, 'error'):
            log_data['error'] = record.error

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class ColoredConsoleFormatter(logging.Formatter):
    """Colored console formatter for development."""

    COLORS = {
        'DEBUG': ColorCodes.DEBUG,
        'INFO': ColorCodes.INFO,
        'WARNING': ColorCodes.WARNING,
        'ERROR': ColorCodes.ERROR,
        'CRITICAL': ColorCodes.CRITICAL,
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, ColorCodes.RESET)
        record.levelname = f"{color}{record.levelname}{ColorCodes.RESET}"
        return super().format(record)


class ApplicationLogger:
    """Comprehensive logging system with multiple output destinations and formats."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern for thread-safe logger."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        self.loggers: Dict[str, logging.Logger] = {}
        self.environment = Environment.DEVELOPMENT

    def configure(
        self,
        name: str = "app",
        environment: Environment = Environment.DEVELOPMENT,
        log_dir: str = "logs",
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        console_level: int = logging.DEBUG,
        file_level: int = logging.INFO
    ) -> logging.Logger:
        """
        Configure and return a logger instance.

        Args:
            name: Logger name
            environment: Deployment environment
            log_dir: Directory for log files
            max_file_size: Maximum size before rotation (bytes)
            backup_count: Number of backup files to keep
            console_level: Console logging level
            file_level: File logging level

        Returns:
            Configured logger instance
        """
        self.environment = environment

        if name in self.loggers:
            return self.loggers[name]

        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.handlers.clear()

        # Ensure log directory exists
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        # Console handler with colored output for development
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)

        if environment == Environment.DEVELOPMENT:
            console_format = ColoredConsoleFormatter(
                '[%(asctime)s] %(levelname)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            console_format = logging.Formatter(
                '[%(asctime)s] %(levelname)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)

        # Rotating file handler with JSON format for production
        file_handler = RotatingFileHandler(
            log_path / f"{name}.log",
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        file_handler.setLevel(file_level)

        if environment == Environment.PRODUCTION:
            file_handler.setFormatter(StructuredFormatter())
        else:
            file_handler.setFormatter(
                logging.Formatter(
                    '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
            )
        logger.addHandler(file_handler)

        # Error file handler for ERROR and above
        error_handler = RotatingFileHandler(
            log_path / f"{name}_errors.log",
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter())
        logger.addHandler(error_handler)

        self.loggers[name] = logger
        return logger

    def log_user_action(self, logger: logging.Logger, action: str, user_id: int, **kwargs):
        """Log user action with context (Few-shot example 3 pattern)."""
        extra = {
            'user_id': user_id,
            'action': action,
            **kwargs
        }
        logger.info(
            f"User action performed - UserID: {user_id}, Action: {action}, " +
            ", ".join(f"{k}: {v}" for k, v in kwargs.items()),
            extra=extra
        )

    def log_database_query(self, logger: logging.Logger, query: str, duration: float, **kwargs):
        """Log database query with performance (Few-shot example 1 pattern)."""
        extra = {
            'query': query,
            'duration': duration,
            **kwargs
        }
        logger.debug(
            f"Database query executed - Query: {query[:100]}..., Duration: {duration:.3f}s",
            extra=extra
        )

    def log_error(self, logger: logging.Logger, error_msg: str, user_id: Optional[int] = None, **kwargs):
        """Log error with context (Few-shot example 2 pattern)."""
        extra = kwargs.copy()
        if user_id:
            extra['user_id'] = user_id

        logger.error(
            f"Error occurred - {error_msg}, " +
            ", ".join(f"{k}: {v}" for k, v in kwargs.items()),
            extra=extra,
            exc_info=True
        )


# Example usage demonstrating all patterns
if __name__ == "__main__":
    # Initialize logger
    log_system = ApplicationLogger()

    # Development environment with colored console output
    dev_logger = log_system.configure(
        name="app_dev",
        environment=Environment.DEVELOPMENT,
        console_level=logging.DEBUG
    )

    # Production environment with JSON logging
    prod_logger = log_system.configure(
        name="app_prod",
        environment=Environment.PRODUCTION,
        console_level=logging.INFO
    )

    print("\n=== Few-Shot Example 1: Database Query Logging ===")
    log_system.log_database_query(
        dev_logger,
        "SELECT * FROM users WHERE active=1",
        duration=0.045
    )

    print("\n=== Few-Shot Example 2: Error Logging ===")
    try:
        # Simulate an error
        raise ValueError("Card declined")
    except ValueError as e:
        log_system.log_error(
            dev_logger,
            "Payment processing failed",
            user_id=67890,
            amount="$99.99",
            error="Card declined",
            request_id="req_abc123"
        )

    print("\n=== Few-Shot Example 3: User Action Logging ===")
    log_system.log_user_action(
        dev_logger,
        action="file_upload",
        user_id=11111,
        resource="document.pdf",
        ip="192.168.1.100",
        session_id="sess_xyz789"
    )

    print("\n=== Standard Logging Levels ===")
    dev_logger.debug("Debug message for troubleshooting")
    dev_logger.info("User login successful - UserID: 12345")
    dev_logger.warning("Disk space running low")
    dev_logger.error("Failed to connect to external API")
    dev_logger.critical("System shutdown initiated")

    print("\nLogs written to ./logs/ directory")
