"""
API Wrapper - Automatically routes to self-hosted or external APIs

This module provides a unified interface that automatically uses:
- Self-hosted API (if USE_SELF_HOSTED_API=true)
- External APIs (OpenAI/Groq, Serper/Tavily) as fallback

No code changes needed in your existing modules!
"""

import logging
from typing import List, Tuple, Optional

from config.settings import settings


logger = logging.getLogger(__name__)


def extract_claims_unified(
    article_text: str,
    language: Optional[str] = None,
    max_retries: int = 3
) -> List[Tuple[str, float, str]]:
    """
    Extract claims using self-hosted API or external APIs.
    
    Automatically routes based on USE_SELF_HOSTED_API setting.
    
    Args:
        article_text: Article text to extract claims from
        language: Language code (auto-detected if None)
        max_retries: Maximum number of retry attempts
    
    Returns:
        List of (claim_text, importance, context) tuples
    """
    if settings.USE_SELF_HOSTED_API:
        # Use self-hosted API
        logger.info("Using self-hosted API for claim extraction")
        from src.self_hosted_api_client import get_client
        
        try:
            client = get_client()
            return client.extract_claims(article_text, language, max_retries)
        except Exception as e:
            logger.error(f"Self-hosted API failed: {e}")
            raise
    
    else:
        # Use external APIs (existing code)
        logger.info("Using external APIs for claim extraction")
        from src.llm_integration import buildClaimExtractionPrompt, callLLM, parseLLMResponse
        from src.language_support import Language, detectLanguage
        
        # Auto-detect language if not provided
        if language is None or language == "auto":
            lang_enum = detectLanguage(article_text)
        else:
            lang_enum = Language(language)
        
        prompt = buildClaimExtractionPrompt(article_text, lang_enum)
        llm_response = callLLM(prompt, max_retries)
        return parseLLMResponse(llm_response)


def search_unified(
    query: str,
    max_results: Optional[int] = None,
    max_retries: int = 3
) -> List[dict]:
    """
    Search for evidence using self-hosted API or external APIs.
    
    Automatically routes based on USE_SELF_HOSTED_API setting.
    
    Args:
        query: Search query
        max_results: Maximum number of results
        max_retries: Maximum number of retry attempts
    
    Returns:
        List of search result dictionaries with keys:
        - url: str
        - title: str
        - snippet: str
        - domain: str
        - published_date: Optional[str]
    """
    if settings.USE_SELF_HOSTED_API:
        # Use self-hosted API
        logger.info("Using self-hosted API for search")
        from src.self_hosted_api_client import get_client
        
        try:
            client = get_client()
            return client.search(query, max_results, max_retries)
        except Exception as e:
            logger.error(f"Self-hosted API search failed: {e}")
            raise
    
    else:
        # Use external APIs (existing code)
        logger.info("Using external APIs for search")
        from src.evidence_retrieval import callSearchAPI
        
        search_results = callSearchAPI(query)
        
        # Convert SearchResult objects to dictionaries
        return [
            {
                "url": result.url,
                "title": result.title,
                "snippet": result.snippet,
                "domain": result.domain,
                "published_date": result.date
            }
            for result in search_results
        ]


__all__ = [
    'extract_claims_unified',
    'search_unified'
]
