import os
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from loguru import logger
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

from src.code_confluence_flow_bridge.logging.loguru_oltp_handler import OTLPHandler
from src.code_confluence_flow_bridge.logging.trace_utils import (
    activity_id_var,
    activity_name_var,
    trace_id_var,
    workflow_id_var,
    workflow_run_id_var,
)

if TYPE_CHECKING:
    from loguru import Logger

# Module-level mutable state for OTEL provider singleton
# Using lowercase to indicate this is NOT a constant (it gets reassigned)
_otel_provider: Optional[LoggerProvider] = None


def setup_logging(
    service_name: str,
    app_name: str,
    log_level: Optional[str] = None,
    otlp_endpoint: Optional[str] = None,
    log_dir: Optional[str] = None,
) -> "Logger":
    """
    Configure Loguru with console, file, and optional OTLP logging.

    Args:
        service_name: Service name for OTLP resource identification
        app_name: Application name included in log records
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR). Defaults to LOG_LEVEL env var or DEBUG
        otlp_endpoint: OTLP endpoint URL. Defaults to OTEL_EXPORTER_OTLP_ENDPOINT env var
        log_dir: Directory for log files. Defaults to LOG_DIR env var or ./logs

    Returns:
        Configured Loguru logger instance
    """
    global _otel_provider

    log_level = log_level or os.getenv("LOG_LEVEL", "DEBUG")
    otlp_endpoint = otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

    # Default log directory: project_root/logs (absolute path for predictability)
    # Project root is 2 levels up from this file: logging/ -> code_confluence_flow_bridge/ -> src/ -> project_root/
    default_log_dir = str(Path(__file__).parent.parent.parent.parent / "logs")
    log_dir = log_dir or os.getenv("LOG_DIR", default_log_dir)

    # Pretty console format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "{extra[app_name]} | "
        "{message}"
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
            "format": log_format,
            "level": log_level,
            "colorize": True,
        }
    ]

    # Setup file logging with datetime timestamp and autorotation
    # Create log directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Generate log filename with startup timestamp
    # Format: app_YYYY-MM-DD_HH-mm-ss.log (new file per run)
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
            "enqueue": True,  # Thread-safe async writing
            "encoding": "utf-8",
            "diagnose": False,  # Don't expose sensitive data in production
            "backtrace": True,  # Include stack traces
        }
    )

    # Only initialize OTLP if an endpoint is explicitly provided
    if otlp_endpoint:
        if _otel_provider is None:
            # Initialize the OTel LoggerProvider once
            _otel_provider = LoggerProvider()
            exporter = OTLPLogExporter(endpoint=otlp_endpoint, insecure=True)
            _otel_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
            set_logger_provider(_otel_provider)

        # Add OTLP handler only if endpoint is provided
        otlp_handler = OTLPHandler(
            service_name=service_name,
            exporter=OTLPLogExporter(endpoint=otlp_endpoint, insecure=True),
        )

        handlers.append(
            {
                "sink": otlp_handler.sink,
                "level": log_level,
                "serialize": False,
            }
        )

    # Configure logger
    logger.configure(
        handlers=handlers,  # type: ignore
        extra={"app_name": app_name},
        patcher=lambda record: record["extra"].update(
            {
                "app_trace_id": trace_id_var.get(""),
                "workflow_id": workflow_id_var.get(""),
                "workflow_run_id": workflow_run_id_var.get(""),
                "activity_id": activity_id_var.get(""),
                "activity_name": activity_name_var.get(""),
            }
        )
        if trace_id_var.get()
        else None,
    )

    return logger
