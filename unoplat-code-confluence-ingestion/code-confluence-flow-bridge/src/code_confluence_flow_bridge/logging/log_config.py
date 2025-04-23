import os  # already imported, used for reading environment variables
import sys
from pathlib import Path
from typing import Any, Dict

from loguru import logger


class LogConfig:
    """Logging configuration to be set for the server"""

    @staticmethod
    def make_logger_config(log_path: str = "logs") -> Dict[str, Any]:
        """Return logger configuration"""
        # Use environment variable LOG_LEVEL to control logging level, default is "INFO"
        log_level: str = os.getenv("LOG_LEVEL", "INFO")
        return {
            "handlers": [
                {
                    "sink": sys.stdout,
                    "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                    "colorize": True,
                    "level": log_level,
                },
                {
                    "sink": f"{log_path}/code_confluence_api.log",
                    "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
                    "rotation": "500 MB",
                    "retention": "10 days",
                    "compression": "zip",
                    "level": log_level,
                    "enqueue": True,
                },
            ],
            "extra": {"app_name": "code-confluence-flow-bridge"},
        }


def setup_logging():
    """Configure logging for the application"""
    # Create logs directory
    log_path = Path("logs")
    log_path.mkdir(exist_ok=True)

    # Remove default logger
    logger.remove()

    # Configure logger with our settings
    config = LogConfig.make_logger_config(str(log_path))

    # Add handlers
    for handler in config["handlers"]:
        logger.add(**handler)

    # Set extra attributes
    logger.configure(extra=config["extra"])

    return logger
