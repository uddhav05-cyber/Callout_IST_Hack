"""
Mock Search Service for Testing

This provides realistic fake search results when the real API is unavailable.
Use this for testing and development only!
"""

from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


# Mock search results database
MOCK_RESULTS = {
    # Factual claims
    "india cricket world cup 2023": [
        {
            "title": "ICC Cricket World Cup 2023 - Wikipedia",
            "link": "https://en.wikipedia.org/wiki/2023_Cricket_World_Cup",
            "snippet": "The 2023 ICC Cricket World Cup was won by Australia, who defeated India in the final. India finished as runners-up in the tournament held in India.",
            "domain": "wikipedia.org"
        },
        {
            "title": "Australia wins 2023 Cricket World Cup - ESPN",
            "link": "https://www.espn.com/cricket/story/2023-world-cup-final",
            "snippet": "Australia defeated India by 6 wickets in the final to win their 6th Cricket World Cup title. India's dream of winning on home soil was shattered.",
            "domain": "espn.com"
        },
        {
            "title": "Cricket World Cup 2023 Final Result - BBC Sport",
            "link": "https://www.bbc.com/sport/cricket/world-cup-2023",
            "snippet": "Australia beat India in the 2023 Cricket World Cup final in Ahmedabad. Travis Head scored a century to guide Australia to victory.",
            "domain": "bbc.com"
        }
    ],
    
    # Coffee cures cancer (fake news)
    "coffee cures cancer": [
        {
            "title": "Does Coffee Cure Cancer? Fact Check - Snopes",
            "link": "https://www.snopes.com/fact-check/coffee-cure-cancer/",
            "snippet": "FALSE: There is no scientific evidence that drinking coffee cures cancer. While coffee has health benefits, it is not a cancer cure.",
            "domain": "snopes.com"
        },
        {
            "title": "Coffee and Cancer: What the Research Says - Mayo Clinic",
            "link": "https://www.mayoclinic.org/coffee-cancer",
            "snippet": "Coffee consumption may have some protective effects against certain cancers, but it does not cure cancer. Claims of coffee curing cancer are false.",
            "domain": "mayoclinic.org"
        },
        {
            "title": "Debunking Coffee Cancer Cure Myths - Cancer Research UK",
            "link": "https://www.cancerresearchuk.org/coffee-myths",
            "snippet": "No evidence supports claims that coffee cures cancer. While coffee is safe to drink, it cannot treat or cure cancer.",
            "domain": "cancerresearchuk.org"
        }
    ],
    
    # WHO vaccination rates
    "who vaccination rates increased 15 percent": [
        {
            "title": "Global Vaccination Coverage - WHO",
            "link": "https://www.who.int/news/vaccination-coverage-2023",
            "snippet": "WHO reports global vaccination coverage has increased significantly in 2023, with over 70% of the global population receiving at least one dose of COVID-19 vaccine.",
            "domain": "who.int"
        },
        {
            "title": "COVID-19 Vaccination Progress - Reuters",
            "link": "https://www.reuters.com/health/covid-vaccination-2023",
            "snippet": "World Health Organization data shows vaccination rates have risen in developing countries, contributing to a decline in COVID-19 cases globally.",
            "domain": "reuters.com"
        }
    ],
    
    # Crime statistics
    "crime rates increased 300 percent": [
        {
            "title": "Understanding Crime Statistics - FBI",
            "link": "https://www.fbi.gov/crime-statistics",
            "snippet": "Crime statistics must be interpreted carefully. A 300% increase from 2 to 8 incidents, while technically accurate, can be misleading without proper context.",
            "domain": "fbi.gov"
        },
        {
            "title": "How to Read Crime Statistics - FactCheck.org",
            "link": "https://www.factcheck.org/crime-statistics-guide",
            "snippet": "Percentage increases in crime can be misleading when baseline numbers are very small. Context and absolute numbers are essential for accurate interpretation.",
            "domain": "factcheck.org"
        }
    ],
    
    # Default/generic results
    "default": [
        {
            "title": "Search Results - News Source",
            "link": "https://www.example-news.com/article",
            "snippet": "This is a generic search result. For accurate verification, please use a valid search API key.",
            "domain": "example-news.com"
        }
    ]
}


def getMockSearchResults(query: str, num_results: int = 5) -> List[Dict]:
    """
    Get mock search results for a query.
    
    Args:
        query: Search query string
        num_results: Number of results to return
    
    Returns:
        List of mock search result dictionaries
    """
    logger.warning(f"🔶 USING MOCK SEARCH RESULTS for query: '{query}'")
    logger.warning("🔶 For real verification, please configure a valid search API key!")
    
    query_lower = query.lower()
    
    # Try to find matching mock results
    for key in MOCK_RESULTS:
        if key in query_lower:
            results = MOCK_RESULTS[key][:num_results]
            logger.info(f"Found {len(results)} mock results for query")
            return results
    
    # Return default results if no match
    logger.info("Using default mock results")
    return MOCK_RESULTS["default"][:num_results]


def addMockResult(query_key: str, results: List[Dict]):
    """
    Add custom mock results for testing.
    
    Args:
        query_key: Key to match in queries (lowercase)
        results: List of result dictionaries
    """
    MOCK_RESULTS[query_key.lower()] = results
    logger.info(f"Added mock results for key: {query_key}")


__all__ = ["getMockSearchResults", "addMockResult"]
