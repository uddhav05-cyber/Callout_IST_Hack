"""
Configuration module for Fake News Detection System.
"""
from .logging_config import setup_logging, get_logger
from .settings import settings, Settings, ConfigurationError

__all__ = ["setup_logging", "get_logger", "settings", "Settings", "ConfigurationError"]
