import os
import sys
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

_OTEL_PROVIDER: Optional[LoggerProvider] = None


def setup_logging(
    service_name: str,
    app_name: str,
    log_level: Optional[str] = None,
    otlp_endpoint: Optional[str] = None,
) -> "Logger":
    """
    Configure Loguru to send structured logs to SigNoz via OpenTelemetry.
    If no OTLP endpoint is specified, only console logging will be configured.
    """
    global _OTEL_PROVIDER

    log_level = log_level or os.getenv("LOG_LEVEL", "DEBUG")
    otlp_endpoint = otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

    # Pretty console format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
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

    # Only initialize OTLP if an endpoint is explicitly provided
    if otlp_endpoint:
        if _OTEL_PROVIDER is None:
            # Initialize the OTel LoggerProvider once
            _OTEL_PROVIDER = LoggerProvider()
            exporter = OTLPLogExporter(endpoint=otlp_endpoint, insecure=True)
            _OTEL_PROVIDER.add_log_record_processor(BatchLogRecordProcessor(exporter))
            set_logger_provider(_OTEL_PROVIDER)

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
