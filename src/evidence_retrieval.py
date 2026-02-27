"""
Evidence Retrieval Module for the Fake News Detection System.

This module implements search API integration to retrieve evidence from external sources.
It supports Serper.dev and Tavily APIs with rate limit handling and error recovery.

Requirements: 3.1, 11.3, 16.2
"""

import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse

import requests

from config.settings import settings
from src.models import Evidence, Claim


# Configure logging
logger = logging.getLogger(__name__)


class SearchAPIError(Exception):
    """Raised when search API encounters an error."""
    pass


class RateLimitError(Exception):
    """Raised when search API rate limit is exceeded."""
    pass


class SearchResult:
    """Intermediate representation of a search result."""
    
    def __init__(self, url: str, snippet: str, title: str = "", date: Optional[str] = None):
        self.url = url
        self.snippet = snippet
        self.title = title
        self.date = date
        self.domain = self._extract_domain(url)
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            # Remove www. prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception as e:
            logger.warning(f"Failed to extract domain from {url}: {e}")
            return ""


def callSearchAPI(query: str) -> List[SearchResult]:
    """
    Call search API (Serper.dev or Tavily) to retrieve search results.
    
    This function attempts to use the configured search API to find relevant
    information for the given query. It handles API errors, rate limits, and
    parses results into a standardized format.
    
    Args:
        query: The search query string
    
    Returns:
        List of SearchResult objects containing URL, snippet, and domain
    
    Raises:
        SearchAPIError: If the API call fails after retries
        RateLimitError: If rate limit is exceeded
    
    Requirements: 3.1, 11.3, 16.2
    """
    if not query or not query.strip():
        logger.warning("Empty query provided to callSearchAPI")
        return []
    
    # Determine which API to use
    if settings.SERPER_API_KEY:
        return _call_serper_api(query)
    elif settings.TAVILY_API_KEY:
        return _call_tavily_api(query)
    else:
        raise SearchAPIError("No search API key configured")


def _call_serper_api(query: str) -> List[SearchResult]:
    """
    Call Serper.dev API to retrieve search results.
    
    Args:
        query: The search query string
    
    Returns:
        List of SearchResult objects
    
    Raises:
        SearchAPIError: If the API call fails
        RateLimitError: If rate limit is exceeded
    """
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": settings.SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "q": query,
        "num": settings.MAX_EVIDENCE_PER_CLAIM * 2  # Request more to allow filtering
    }
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=settings.REQUEST_TIMEOUT_SECONDS
        )
        
        # Handle rate limiting
        if response.status_code == 429:
            logger.warning(f"Serper API rate limit exceeded for query: {query}")
            raise RateLimitError("Serper API rate limit exceeded")
        
        # Handle other errors
        if response.status_code != 200:
            logger.error(f"Serper API error {response.status_code}: {response.text}")
            raise SearchAPIError(f"Serper API returned status {response.status_code}")
        
        data = response.json()
        return _parse_serper_results(data)
    
    except RateLimitError:
        # Re-raise RateLimitError without wrapping
        raise
    except requests.Timeout:
        logger.error(f"Serper API timeout for query: {query}")
        raise SearchAPIError("Search API request timed out")
    except requests.RequestException as e:
        logger.error(f"Serper API request failed: {e}")
        raise SearchAPIError(f"Search API request failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error calling Serper API: {e}")
        raise SearchAPIError(f"Unexpected error: {e}")


def _parse_serper_results(data: Dict[str, Any]) -> List[SearchResult]:
    """
    Parse Serper.dev API response into SearchResult objects.
    
    Args:
        data: JSON response from Serper API
    
    Returns:
        List of SearchResult objects
    """
    results = []
    
    # Serper returns results in 'organic' field
    organic_results = data.get('organic', [])
    
    for item in organic_results:
        try:
            url = item.get('link', '')
            snippet = item.get('snippet', '')
            title = item.get('title', '')
            date = item.get('date')  # May be None
            
            if url and snippet:
                results.append(SearchResult(
                    url=url,
                    snippet=snippet,
                    title=title,
                    date=date
                ))
        except Exception as e:
            logger.warning(f"Failed to parse Serper result: {e}")
            continue
    
    logger.info(f"Parsed {len(results)} results from Serper API")
    return results


def _call_tavily_api(query: str) -> List[SearchResult]:
    """
    Call Tavily API to retrieve search results.
    
    Args:
        query: The search query string
    
    Returns:
        List of SearchResult objects
    
    Raises:
        SearchAPIError: If the API call fails
        RateLimitError: If rate limit is exceeded
    """
    url = "https://api.tavily.com/search"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "api_key": settings.TAVILY_API_KEY,
        "query": query,
        "max_results": settings.MAX_EVIDENCE_PER_CLAIM * 2,  # Request more to allow filtering
        "search_depth": "basic",
        "include_answer": False,
        "include_raw_content": False
    }
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=settings.REQUEST_TIMEOUT_SECONDS
        )
        
        # Handle rate limiting
        if response.status_code == 429:
            logger.warning(f"Tavily API rate limit exceeded for query: {query}")
            raise RateLimitError("Tavily API rate limit exceeded")
        
        # Handle other errors
        if response.status_code != 200:
            logger.error(f"Tavily API error {response.status_code}: {response.text}")
            raise SearchAPIError(f"Tavily API returned status {response.status_code}")
        
        data = response.json()
        return _parse_tavily_results(data)
    
    except RateLimitError:
        # Re-raise RateLimitError without wrapping
        raise
    except requests.Timeout:
        logger.error(f"Tavily API timeout for query: {query}")
        raise SearchAPIError("Search API request timed out")
    except requests.RequestException as e:
        logger.error(f"Tavily API request failed: {e}")
        raise SearchAPIError(f"Search API request failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error calling Tavily API: {e}")
        raise SearchAPIError(f"Unexpected error: {e}")


def _parse_tavily_results(data: Dict[str, Any]) -> List[SearchResult]:
    """
    Parse Tavily API response into SearchResult objects.
    
    Args:
        data: JSON response from Tavily API
    
    Returns:
        List of SearchResult objects
    """
    results = []
    
    # Tavily returns results in 'results' field
    search_results = data.get('results', [])
    
    for item in search_results:
        try:
            url = item.get('url', '')
            snippet = item.get('content', '')
            title = item.get('title', '')
            # Tavily may include published_date
            date = item.get('published_date')
            
            if url and snippet:
                results.append(SearchResult(
                    url=url,
                    snippet=snippet,
                    title=title,
                    date=date
                ))
        except Exception as e:
            logger.warning(f"Failed to parse Tavily result: {e}")
            continue
    
    logger.info(f"Parsed {len(results)} results from Tavily API")
    return results


def extractDomain(url: str) -> str:
    """
    Extract domain name from a URL.
    
    Args:
        url: The URL to extract domain from
    
    Returns:
        Domain name (without www. prefix)
    
    Requirements: 3.1
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        # Remove www. prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain.lower()
    except Exception as e:
        logger.warning(f"Failed to extract domain from {url}: {e}")
        return ""


def optimizeQueryForSearch(claimText: str) -> str:
    """
    Optimize a claim text for search by extracting key terms.
    
    This function simplifies the claim text to create a more effective search query
    by removing filler words and focusing on key entities and facts.
    
    Args:
        claimText: The original claim text
    
    Returns:
        Optimized search query string
    
    Requirements: 3.1
    """
    if not claimText or not claimText.strip():
        return ""
    
    # For now, use the claim text as-is with some basic cleanup
    # In a production system, this could use NLP to extract key entities
    query = claimText.strip()
    
    # Remove quotes that might interfere with search
    query = query.replace('"', '').replace("'", "")
    
    # Limit query length to avoid API issues
    max_length = 200
    if len(query) > max_length:
        query = query[:max_length].rsplit(' ', 1)[0]  # Cut at word boundary
    
    return query


def calculateRelevance(claimText: str, snippet: str) -> float:
    """
    Calculate relevance score between a claim and an evidence snippet.
    
    This function uses simple text similarity to determine how relevant
    an evidence snippet is to the claim being verified.
    
    Args:
        claimText: The claim text
        snippet: The evidence snippet
    
    Returns:
        Relevance score between 0.0 and 1.0
    
    Requirements: 19.1, 19.2, 19.3
    """
    if not claimText or not snippet:
        return 0.0
    
    # Normalize text to lowercase for comparison
    claim_lower = claimText.lower()
    snippet_lower = snippet.lower()
    
    # Split into words
    claim_words = set(claim_lower.split())
    snippet_words = set(snippet_lower.split())
    
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
        'those', 'it', 'its', 'they', 'them', 'their'
    }
    
    claim_words = claim_words - stop_words
    snippet_words = snippet_words - stop_words
    
    # Calculate Jaccard similarity (intersection over union)
    if not claim_words or not snippet_words:
        return 0.0
    
    intersection = len(claim_words & snippet_words)
    union = len(claim_words | snippet_words)
    
    if union == 0:
        return 0.0
    
    jaccard_score = intersection / union
    
    # Boost score if claim appears as substring in snippet
    if claim_lower in snippet_lower or snippet_lower in claim_lower:
        jaccard_score = min(1.0, jaccard_score * 1.5)
    
    return jaccard_score


def filterTrustedSources(results: List[SearchResult]) -> List[Evidence]:
    """
    Filter search results to include only trusted sources above credibility threshold.
    
    This function looks up the credibility score for each search result and filters
    out sources that don't meet the minimum credibility threshold. It also calculates
    relevance scores for the filtered results.
    
    Args:
        results: List of SearchResult objects from search API
    
    Returns:
        List of Evidence objects for trusted sources
    
    Requirements: 3.2, 3.3, 12.5
    """
    from src.source_credibility import lookup_source_credibility
    
    trusted_evidence = []
    
    for result in results:
        try:
            # Look up source credibility
            credibility = lookup_source_credibility(result.domain)
            
            # Filter by credibility threshold
            if credibility.credibilityScore >= settings.MINIMUM_CREDIBILITY_THRESHOLD:
                # Create Evidence object
                evidence = Evidence(
                    sourceURL=result.url,
                    sourceDomain=result.domain,
                    snippet=result.snippet,
                    publishDate=None,  # Will be set if available
                    credibilityScore=credibility.credibilityScore,
                    relevanceScore=0.0  # Will be calculated later
                )
                
                # Parse date if available
                if result.date:
                    try:
                        # Try to parse date string
                        if isinstance(result.date, str):
                            from dateutil import parser
                            evidence.publishDate = parser.parse(result.date)
                        elif isinstance(result.date, datetime):
                            evidence.publishDate = result.date
                    except Exception as e:
                        logger.debug(f"Failed to parse date '{result.date}': {e}")
                
                trusted_evidence.append(evidence)
            else:
                logger.debug(
                    f"Filtered out {result.domain} with credibility "
                    f"{credibility.credibilityScore} < {settings.MINIMUM_CREDIBILITY_THRESHOLD}"
                )
        
        except Exception as e:
            logger.warning(f"Error processing search result from {result.domain}: {e}")
            continue
    
    logger.info(
        f"Filtered {len(results)} results to {len(trusted_evidence)} trusted sources "
        f"(threshold: {settings.MINIMUM_CREDIBILITY_THRESHOLD})"
    )
    
    return trusted_evidence


def searchEvidence(claim) -> List[Evidence]:
    """
    Main function to search for evidence, filter by credibility, and rank by relevance.
    
    This function orchestrates the complete evidence retrieval process:
    1. Optimize the claim text for search
    2. Query the search API
    3. Filter results by source credibility
    4. Calculate relevance scores
    5. Rank by combined score (70% relevance + 30% credibility)
    6. Return top MAX_EVIDENCE_PER_CLAIM results
    
    Args:
        claim: Claim object to search evidence for
    
    Returns:
        List of Evidence objects, ranked by combined score
    
    Raises:
        SearchAPIError: If search API fails
        RateLimitError: If rate limit is exceeded
    
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 12.5, 19.1, 19.2, 19.3, 19.4
    """
    if not claim or not claim.text:
        logger.warning("Empty claim provided to searchEvidence")
        return []
    
    try:
        # Step 1: Optimize query for search
        search_query = optimizeQueryForSearch(claim.text)
        if not search_query:
            logger.warning(f"Failed to create search query for claim: {claim.text}")
            return []
        
        logger.info(f"Searching for evidence: '{search_query}'")
        
        # Step 2: Query search API
        search_results = callSearchAPI(search_query)
        
        if not search_results:
            logger.warning(f"No search results found for claim: {claim.text}")
            return []
        
        # Step 3: Filter by credibility threshold
        trusted_evidence = filterTrustedSources(search_results)
        
        if not trusted_evidence:
            logger.warning(
                f"No trusted sources found for claim: {claim.text} "
                f"(threshold: {settings.MINIMUM_CREDIBILITY_THRESHOLD})"
            )
            return []
        
        # Step 4: Calculate relevance scores
        for evidence in trusted_evidence:
            evidence.relevanceScore = calculateRelevance(claim.text, evidence.snippet)
        
        # Step 5: Rank by combined score (70% relevance + 30% credibility)
        for evidence in trusted_evidence:
            combined_score = (0.7 * evidence.relevanceScore + 
                            0.3 * evidence.credibilityScore)
            # Store combined score as a temporary attribute for sorting
            evidence._combined_score = combined_score
        
        # Sort by combined score (descending)
        trusted_evidence.sort(key=lambda e: e._combined_score, reverse=True)
        
        # Step 6: Limit to MAX_EVIDENCE_PER_CLAIM top results
        top_evidence = trusted_evidence[:settings.MAX_EVIDENCE_PER_CLAIM]
        
        # Clean up temporary attribute
        for evidence in top_evidence:
            if hasattr(evidence, '_combined_score'):
                delattr(evidence, '_combined_score')
        
        logger.info(
            f"Found {len(top_evidence)} evidence items for claim "
            f"(from {len(search_results)} search results)"
        )
        
        return top_evidence
    
    except RateLimitError:
        # Re-raise rate limit errors for special handling
        logger.error(f"Rate limit exceeded while searching for claim: {claim.text}")
        raise
    
    except SearchAPIError as e:
        # Log and re-raise search API errors
        logger.error(f"Search API error for claim '{claim.text}': {e}")
        raise
    
    except Exception as e:
        # Catch unexpected errors
        logger.error(f"Unexpected error searching evidence for claim '{claim.text}': {e}")
        raise SearchAPIError(f"Unexpected error during evidence search: {e}")


__all__ = [
    'callSearchAPI',
    'extractDomain',
    'optimizeQueryForSearch',
    'calculateRelevance',
    'filterTrustedSources',
    'searchEvidence',
    'SearchResult',
    'SearchAPIError',
    'RateLimitError'
]
