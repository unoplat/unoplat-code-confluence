from src.code_confluence_flow_bridge.logging.loguru_oltp_handler import OTLPHandler
from src.code_confluence_flow_bridge.logging.trace_utils import trace_id_var

import os
import sys
from typing import TYPE_CHECKING

from loguru import logger
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

if TYPE_CHECKING:
    from loguru import Logger

_OTEL_PROVIDER: LoggerProvider | None = None

def setup_logging(
    service_name: str,
    app_name: str,
    log_level: str | None = None,
    otlp_endpoint: str | None = None
) -> "Logger":
    """
    Configure Loguru to send structured logs to SigNoz via OpenTelemetry.
    """
    global _OTEL_PROVIDER
    if _OTEL_PROVIDER is None:
        # Initialize the OTel LoggerProvider once
        endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://signoz-otel-collector:4317")
        _OTEL_PROVIDER = LoggerProvider()
        exporter = OTLPLogExporter(endpoint=endpoint, insecure=True)
        _OTEL_PROVIDER.add_log_record_processor(BatchLogRecordProcessor(exporter))
        set_logger_provider(_OTEL_PROVIDER)

    log_level = log_level or os.getenv("LOG_LEVEL", "DEBUG")
    otlp_endpoint = otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

    # Build OTLPHandler util
    otlp_handler = OTLPHandler(
        service_name=service_name,
        exporter=OTLPLogExporter(endpoint=otlp_endpoint, insecure=True)
    )

    # Pretty console format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "{extra[app_name]} | "
        "{message}"
    )

    # Configure both console and OTLP sinks
    logger.configure(  # type: ignore
        handlers=[
            {  # type: ignore
                "sink": sys.stdout,
                "format": log_format,
                "level": log_level,
                "colorize": True,
            },
            {  # type: ignore
                "sink": otlp_handler.sink,
                "level": log_level,
                "serialize": False,
            },
        ],
        extra={"app_name": app_name},
        patcher=lambda record: record["extra"].update(
            {"app_trace_id": trace_id_var.get()}
        ) if trace_id_var.get() else None
    )

    return logger
