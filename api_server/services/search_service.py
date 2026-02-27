"""
Local Search Service using DuckDuckGo

This service provides web search without requiring API keys.
Uses DuckDuckGo's free search API.
"""

import logging
from typing import List, Dict, Any
from urllib.parse import urlparse
import asyncio

logger = logging.getLogger(__name__)


class LocalSearchService:
    """Service for web search using DuckDuckGo (no API key needed)"""
    
    def __init__(self):
        self.ready = False
        self._init_duckduckgo()
    
    def _init_duckduckgo(self):
        """Initialize DuckDuckGo search"""
        try:
            from duckduckgo_search import DDGS
            self.ddgs = DDGS()
            self.ready = True
            logger.info("DuckDuckGo search initialized")
        except ImportError:
            logger.error("duckduckgo-search not installed. Install with: pip install duckduckgo-search")
            self.ready = False
        except Exception as e:
            logger.error(f"Failed to initialize DuckDuckGo: {e}")
            self.ready = False
    
    def is_ready(self) -> bool:
        """Check if service is ready"""
        return self.ready
    
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search using DuckDuckGo.
        
        Args:
            query: Search query
            max_results: Maximum number of results
        
        Returns:
            List of search result dictionaries
        """
        if not self.ready:
            raise RuntimeError("Search service not ready")
        
        try:
            # Run search in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: list(self.ddgs.text(query, max_results=max_results))
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "url": result.get("href", ""),
                    "title": result.get("title", ""),
                    "snippet": result.get("body", ""),
                    "domain": self._extract_domain(result.get("href", "")),
                    "published_date": None  # DuckDuckGo doesn't provide dates
                })
            
            logger.info(f"Found {len(formatted_results)} results for query: {query}")
            return formatted_results
        
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain.lower()
        except:
            return ""
