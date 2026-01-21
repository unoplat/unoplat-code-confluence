import os
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from loguru import logger

from unoplat_code_confluence_query_engine.utils.trace_utils import (
    trace_id_var,
    workflow_id_var,
    workflow_run_id_var,
)

if TYPE_CHECKING:
    from loguru import Logger


def setup_logging(
    service_name: str,
    app_name: str,
    log_level: Optional[str] = None,
    log_dir: Optional[str] = None,
) -> "Logger":
    """
    Configure Loguru with console and file logging, including trace context injection.

    Args:
        service_name: Service name for identification (e.g., 'unoplat-code-confluence-query-engine')
        app_name: Application name included in log records (e.g., 'query-engine')
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR). Defaults to LOG_LEVEL env var or DEBUG
        log_dir: Directory for log files. Defaults to LOG_DIR env var or ./logs

    Returns:
        Configured Loguru logger instance
    """
    log_level = log_level or os.getenv("LOG_LEVEL", "DEBUG")

    # Default log directory: project_root/logs (absolute path for predictability)
    # Project root is 4 levels up from this file: config/ -> query_engine/ -> src/ -> query-engine/
    default_log_dir = str(Path(__file__).parent.parent.parent.parent / "logs")
    log_dir = log_dir or os.getenv("LOG_DIR", default_log_dir)

    # Pretty console format with app_name
    console_log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "{extra[app_name]} | "
        "<level>{message}</level>"
    )

    # Plain text format for file logging (no ANSI color codes)
    file_log_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{extra[app_name]} | "
        "{message}"
    )

    handlers: List[Dict[str, Any]] = [
        {
            "sink": sys.stdout,
            "format": console_log_format,
            "level": log_level,
            "colorize": True,
            "diagnose": False,  # Safe for production - don't expose sensitive data
            "backtrace": True,  # Include stack traces
        }
    ]

    # Setup file logging with datetime timestamp and autorotation
    # Create log directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Generate log filename with startup timestamp
    # Format: app_name_YYYY-MM-DD_HH-MM-SS.log (new file per run)
    startup_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = log_path / f"{app_name}_{startup_timestamp}.log"

    handlers.append(
        {
            "sink": str(log_file),
            "format": file_log_format,
            "level": log_level,
            "rotation": "50 MB",  # Rotate when file reaches 50 MB
            "retention": "10 days",  # Keep logs for 10 days
            "compression": "gz",  # Compress rotated files with gzip
            "enqueue": False,  # Thread-safe but NOT multiprocess (Temporal sandbox compatibility)
            "encoding": "utf-8",
            "diagnose": False,  # Don't expose sensitive data in production
            "backtrace": True,  # Include stack traces
        }
    )

    # Configure logger with handlers, extra context, and trace context patcher
    logger.configure(
        handlers=handlers,  # type: ignore[arg-type]
        extra={"app_name": app_name},
        patcher=lambda record: record["extra"].update(
            {
                "app_trace_id": trace_id_var.get(""),
                "workflow_id": workflow_id_var.get(""),
                "workflow_run_id": workflow_run_id_var.get(""),
            }
        )
        if trace_id_var.get()
        else None,
    )

    logger.info("Logging system initialized for {}", service_name)

    return logger
