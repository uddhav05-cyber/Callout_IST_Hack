"""
Configuration module for the Fake News Detection System.

This module loads API keys from environment variables and defines configurable
constants for the system. It validates that required API keys are present.

Requirements: 16.1, 16.2, 16.3, 16.4, 16.5
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""
    pass


class Settings:
    """Configuration settings for the Fake News Detection System."""
    
    # Self-Hosted API Configuration (NEW - No external API keys needed!)
    USE_SELF_HOSTED_API: bool = os.getenv("USE_SELF_HOSTED_API", "false").lower() == "true"
    SELF_HOSTED_API_URL: str = os.getenv("SELF_HOSTED_API_URL", "http://localhost:8000")
    SELF_HOSTED_API_KEY: Optional[str] = os.getenv("SELF_HOSTED_API_KEY")
    
    # External API Keys (Legacy - Optional if using self-hosted)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    SERPER_API_KEY: Optional[str] = os.getenv("SERPER_API_KEY")
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")
    TINEYE_API_KEY: Optional[str] = os.getenv("TINEYE_API_KEY")
    
    # Configurable constants
    MAX_CLAIMS_PER_ARTICLE: int = int(os.getenv("MAX_CLAIMS_PER_ARTICLE", "10"))
    MAX_EVIDENCE_PER_CLAIM: int = int(os.getenv("MAX_EVIDENCE_PER_CLAIM", "5"))
    MINIMUM_CREDIBILITY_THRESHOLD: float = float(os.getenv("MINIMUM_CREDIBILITY_THRESHOLD", "0.3"))
    
    # Timeout and retry settings
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    CACHE_TTL_HOURS: int = int(os.getenv("CACHE_TTL_HOURS", "24"))
    
    # NLI model configuration
    NLI_MODEL_NAME: str = os.getenv("NLI_MODEL_NAME", "facebook/bart-large-mnli")
    
    @classmethod
    def validate(cls) -> None:
        """
        Validate that required API keys are present.
        
        Raises:
            ConfigurationError: If required API keys are missing.
        """
        # If using self-hosted API, skip external API validation
        if cls.USE_SELF_HOSTED_API:
            if not cls.SELF_HOSTED_API_URL:
                raise ConfigurationError(
                    "SELF_HOSTED_API_URL is required when USE_SELF_HOSTED_API=true"
                )
            logger.info("Using self-hosted API - external API keys not required")
            return
        
        # At least one LLM API key must be present
        if not cls.OPENAI_API_KEY and not cls.GROQ_API_KEY:
            raise ConfigurationError(
                "At least one LLM API key is required. "
                "Please set OPENAI_API_KEY or GROQ_API_KEY in your environment. "
                "Or set USE_SELF_HOSTED_API=true to use your own API."
            )
        
        # At least one search API key must be present
        if not cls.SERPER_API_KEY and not cls.TAVILY_API_KEY:
            raise ConfigurationError(
                "At least one search API key is required. "
                "Please set SERPER_API_KEY or TAVILY_API_KEY in your environment. "
                "Or set USE_SELF_HOSTED_API=true to use your own API."
            )
        
        # Validate numeric ranges
        if cls.MAX_CLAIMS_PER_ARTICLE <= 0:
            raise ConfigurationError("MAX_CLAIMS_PER_ARTICLE must be greater than 0")
        
        if cls.MAX_EVIDENCE_PER_CLAIM <= 0:
            raise ConfigurationError("MAX_EVIDENCE_PER_CLAIM must be greater than 0")
        
        if not (0.0 <= cls.MINIMUM_CREDIBILITY_THRESHOLD <= 1.0):
            raise ConfigurationError("MINIMUM_CREDIBILITY_THRESHOLD must be between 0.0 and 1.0")
        
        if cls.REQUEST_TIMEOUT_SECONDS <= 0:
            raise ConfigurationError("REQUEST_TIMEOUT_SECONDS must be greater than 0")
        
        if cls.MAX_RETRIES < 0:
            raise ConfigurationError("MAX_RETRIES must be non-negative")
        
        if cls.CACHE_TTL_HOURS <= 0:
            raise ConfigurationError("CACHE_TTL_HOURS must be greater than 0")
    
    @classmethod
    def get_llm_api_key(cls) -> str:
        """
        Get the first available LLM API key.
        
        Returns:
            str: The first available LLM API key (Groq preferred, then OpenAI).
        
        Raises:
            ConfigurationError: If no LLM API key is available.
        """
        if cls.GROQ_API_KEY:
            return cls.GROQ_API_KEY
        if cls.OPENAI_API_KEY:
            return cls.OPENAI_API_KEY
        raise ConfigurationError("No LLM API key available")
    
    @classmethod
    def get_search_api_key(cls) -> str:
        """
        Get the first available search API key.
        
        Returns:
            str: The first available search API key (Serper preferred, then Tavily).
        
        Raises:
            ConfigurationError: If no search API key is available.
        """
        if cls.SERPER_API_KEY:
            return cls.SERPER_API_KEY
        if cls.TAVILY_API_KEY:
            return cls.TAVILY_API_KEY
        raise ConfigurationError("No search API key available")


# Create a singleton instance
settings = Settings()

# Validate configuration on module import
try:
    settings.validate()
except ConfigurationError as e:
    # Log the error but don't fail on import (allows testing without API keys)
    import warnings
    warnings.warn(f"Configuration validation failed: {e}", UserWarning)


__all__ = ["settings", "Settings", "ConfigurationError"]
