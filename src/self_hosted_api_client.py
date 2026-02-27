"""
Client for Self-Hosted Callout API

This module replaces external API dependencies (OpenAI, Groq, Serper, Tavily)
with calls to your own self-hosted API server.

No external API keys needed!
"""

import logging
import time
from typing import List, Dict, Any, Optional, Tuple
import requests

from config.settings import settings
from src.models import Claim, Evidence


logger = logging.getLogger(__name__)


class SelfHostedAPIError(Exception):
    """Raised when self-hosted API encounters an error"""
    pass


class SelfHostedAPIClient:
    """Client for self-hosted Callout API"""
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL of your API server (default: from settings)
            api_key: Your API key for authentication (optional)
        """
        self.base_url = base_url or settings.SELF_HOSTED_API_URL
        self.api_key = api_key or settings.SELF_HOSTED_API_KEY
        self.timeout = settings.REQUEST_TIMEOUT_SECONDS
        
        # Remove trailing slash
        if self.base_url.endswith('/'):
            self.base_url = self.base_url[:-1]
        
        logger.info(f"Initialized self-hosted API client: {self.base_url}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    def extract_claims(
        self,
        article_text: str,
        language: Optional[str] = None,
        max_retries: int = 3
    ) -> List[Tuple[str, float, str]]:
        """
        Extract claims from article text using self-hosted API.
        
        Args:
            article_text: Article text to extract claims from
            language: Language code (auto-detected if None)
            max_retries: Maximum number of retry attempts
        
        Returns:
            List of (claim_text, importance, context) tuples
        
        Raises:
            SelfHostedAPIError: If API call fails after retries
        """
        if not article_text or len(article_text.strip()) == 0:
            raise ValueError("Article text cannot be empty")
        
        url = f"{self.base_url}/api/v1/extract-claims"
        payload = {
            "article_text": article_text,
            "language": language or "auto",
            "max_claims": settings.MAX_CLAIMS_PER_ARTICLE
        }
        
        # Retry loop with exponential backoff
        for attempt in range(max_retries):
            try:
                logger.info(f"Calling self-hosted API for claim extraction (attempt {attempt + 1}/{max_retries})")
                
                response = requests.post(
                    url,
                    json=payload,
                    headers=self._get_headers(),
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    claims = data.get("claims", [])
                    
                    # Convert to tuple format
                    result = [
                        (claim["text"], claim["importance"], claim["context"])
                        for claim in claims
                    ]
                    
                    logger.info(f"Successfully extracted {len(result)} claims from self-hosted API")
                    return result
                
                else:
                    logger.warning(f"API returned status {response.status_code}: {response.text}")
                    
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.info(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        raise SelfHostedAPIError(
                            f"API returned status {response.status_code}: {response.text}"
                        )
            
            except requests.Timeout:
                logger.warning(f"API request timed out (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    raise SelfHostedAPIError("API request timed out after all retries")
            
            except requests.RequestException as e:
                logger.error(f"API request failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    raise SelfHostedAPIError(f"API request failed: {e}")
        
        raise SelfHostedAPIError("Unexpected error in extract_claims")
    
    def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        max_retries: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search for evidence using self-hosted API.
        
        Args:
            query: Search query
            max_results: Maximum number of results (default: from settings)
            max_retries: Maximum number of retry attempts
        
        Returns:
            List of search result dictionaries
        
        Raises:
            SelfHostedAPIError: If API call fails after retries
        """
        if not query or len(query.strip()) == 0:
            raise ValueError("Query cannot be empty")
        
        url = f"{self.base_url}/api/v1/search"
        payload = {
            "query": query,
            "max_results": max_results or (settings.MAX_EVIDENCE_PER_CLAIM * 2)
        }
        
        # Retry loop with exponential backoff
        for attempt in range(max_retries):
            try:
                logger.info(f"Calling self-hosted API for search (attempt {attempt + 1}/{max_retries})")
                
                response = requests.post(
                    url,
                    json=payload,
                    headers=self._get_headers(),
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    
                    logger.info(f"Successfully retrieved {len(results)} search results from self-hosted API")
                    return results
                
                else:
                    logger.warning(f"API returned status {response.status_code}: {response.text}")
                    
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.info(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        raise SelfHostedAPIError(
                            f"API returned status {response.status_code}: {response.text}"
                        )
            
            except requests.Timeout:
                logger.warning(f"API request timed out (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    raise SelfHostedAPIError("API request timed out after all retries")
            
            except requests.RequestException as e:
                logger.error(f"API request failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    raise SelfHostedAPIError(f"API request failed: {e}")
        
        raise SelfHostedAPIError("Unexpected error in search")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if API server is healthy.
        
        Returns:
            Health status dictionary
        
        Raises:
            SelfHostedAPIError: If health check fails
        """
        try:
            url = f"{self.base_url}/health"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise SelfHostedAPIError(f"Health check failed: {response.status_code}")
        
        except Exception as e:
            raise SelfHostedAPIError(f"Health check failed: {e}")


# Global client instance
_client = None


def get_client() -> SelfHostedAPIClient:
    """Get or create global API client instance"""
    global _client
    if _client is None:
        _client = SelfHostedAPIClient()
    return _client


__all__ = [
    'SelfHostedAPIClient',
    'SelfHostedAPIError',
    'get_client'
]
