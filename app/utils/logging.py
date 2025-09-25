"""Logging configuration for the application."""

import logging
import os
from datetime import datetime
from pathlib import Path


def setup_logging():
    """Setup logging configuration."""
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Console handler
            logging.StreamHandler(),
            # File handler for all logs
            logging.FileHandler(
                logs_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log",
                encoding='utf-8'
            )
        ]
    )
    
    # Configure specific loggers
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)
    
    # Error logger for tracking errors
    error_logger = logging.getLogger("app.errors")
    error_logger.setLevel(logging.ERROR)
    
    # Add file handler for errors only
    error_handler = logging.FileHandler(
        logs_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log",
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(log_format, date_format)
    error_handler.setFormatter(error_formatter)
    error_logger.addHandler(error_handler)
    
    # Tracking logger for tracking events
    tracking_logger = logging.getLogger("app.tracking")
    tracking_logger.setLevel(logging.INFO)
    
    # Add file handler for tracking events
    tracking_handler = logging.FileHandler(
        logs_dir / f"tracking_{datetime.now().strftime('%Y%m%d')}.log",
        encoding='utf-8'
    )
    tracking_handler.setLevel(logging.INFO)
    tracking_formatter = logging.Formatter(log_format, date_format)
    tracking_handler.setFormatter(tracking_formatter)
    tracking_logger.addHandler(tracking_handler)
    
    return app_logger, error_logger, tracking_logger


# Initialize loggers
app_logger, error_logger, tracking_logger = setup_logging()


def log_error(error_message: str, error_details: str = None, user_id: int = None, site_id: str = None):
    """Log an error with context."""
    context = []
    if user_id:
        context.append(f"user_id={user_id}")
    if site_id:
        context.append(f"site_id={site_id}")
    
    context_str = f" [{', '.join(context)}]" if context else ""
    
    error_logger.error(f"{error_message}{context_str}")
    if error_details:
        error_logger.error(f"Details: {error_details}")


def log_tracking_event(event_type: str, site_id: str, ip_address: str = None, user_agent: str = None, is_ai_bot: bool = None, bot_name: str = None):
    """Log a tracking event."""
    context = [f"event_type={event_type}", f"site_id={site_id}"]
    
    if ip_address:
        context.append(f"ip={ip_address}")
    if user_agent:
        context.append(f"user_agent={user_agent[:100]}...")  # Truncate long user agents
    if is_ai_bot is not None:
        context.append(f"is_ai_bot={is_ai_bot}")
    if bot_name:
        context.append(f"bot_name={bot_name}")
    
    context_str = " | ".join(context)
    tracking_logger.info(f"Tracking event: {context_str}")


def log_api_request(method: str, path: str, status_code: int, user_id: int = None, duration_ms: float = None):
    """Log an API request."""
    context = [f"method={method}", f"path={path}", f"status={status_code}"]
    
    if user_id:
        context.append(f"user_id={user_id}")
    if duration_ms:
        context.append(f"duration={duration_ms:.2f}ms")
    
    context_str = " | ".join(context)
    app_logger.info(f"API request: {context_str}")
