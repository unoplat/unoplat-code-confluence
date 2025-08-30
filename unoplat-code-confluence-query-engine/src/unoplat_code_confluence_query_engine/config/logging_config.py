import sys
from pathlib import Path
from typing import Any

from loguru import logger


def setup_logging(settings: Any) -> None:
    """
    Configure minimal Loguru logging for console and file output
    
    Args:
        settings: Application settings object containing log configuration
    """
    # Remove default handler
    logger.remove()
    
    # Get project root directory (go up 4 levels from this file)
    project_root = Path(__file__).parent.parent.parent.parent
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Console handler with colorization for development
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
        level=settings.log_level,
        colorize=True,
        enqueue=True,  # Async-safe for FastAPI
        diagnose=False,  # Safe for production
        backtrace=True
    )
    
    # File handler with rotation and retention
    logger.add(
        log_dir / "app_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        level=settings.log_level,
        rotation=settings.log_rotation_size,
        retention=f"{settings.log_retention_days} days",
        compression="gz",
        enqueue=True,
        diagnose=False,
        backtrace=True
    )
    
    logger.info("Logging system initialized")