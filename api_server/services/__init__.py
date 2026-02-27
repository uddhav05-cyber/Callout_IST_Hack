"""
Services package for self-hosted API
"""

from .llm_service import LocalLLMService
from .search_service import LocalSearchService

__all__ = ['LocalLLMService', 'LocalSearchService']
