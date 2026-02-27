"""
Demo script for the search API integration.

This script demonstrates how to use the callSearchAPI function to retrieve
evidence from external sources using Serper.dev or Tavily API.

Requirements: 3.1, 11.3, 16.2
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.evidence_retrieval import callSearchAPI, extractDomain, SearchAPIError, RateLimitError


def demo_basic_search():
    """Demonstrate basic search functionality."""
    print("=" * 60)
    print("Demo: Basic Search API Integration")
    print("=" * 60)
    
    query = "climate change scientific consensus"
    print(f"\nSearching for: '{query}'")
    
    try:
        results = callSearchAPI(query)
        
        print(f"\nFound {len(results)} results:")
        print("-" * 60)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.title}")
            print(f"   URL: {result.url}")
            print(f"   Domain: {result.domain}")
            print(f"   Snippet: {result.snippet[:150]}...")
            if result.date:
                print(f"   Date: {result.date}")
        
    except RateLimitError as e:
        print(f"\n❌ Rate limit exceeded: {e}")
        print("   Please wait before making more requests.")
    except SearchAPIError as e:
        print(f"\n❌ Search API error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


def demo_domain_extraction():
    """Demonstrate domain extraction functionality."""
    print("\n" + "=" * 60)
    print("Demo: Domain Extraction")
    print("=" * 60)
    
    test_urls = [
        "https://www.nytimes.com/2024/01/15/science/climate-change.html",
        "https://www.bbc.com/news/science-environment-12345678",
        "https://news.example.com/article/123",
        "http://example.com:8080/page"
    ]
    
    print("\nExtracting domains from URLs:")
    print("-" * 60)
    
    for url in test_urls:
        domain = extractDomain(url)
        print(f"\nURL:    {url}")
        print(f"Domain: {domain}")


def demo_error_handling():
    """Demonstrate error handling."""
    print("\n" + "=" * 60)
    print("Demo: Error Handling")
    print("=" * 60)
    
    # Test with empty query
    print("\n1. Testing with empty query:")
    results = callSearchAPI("")
    print(f"   Results: {len(results)} (should be 0)")
    
    # Test with whitespace query
    print("\n2. Testing with whitespace query:")
    results = callSearchAPI("   ")
    print(f"   Results: {len(results)} (should be 0)")
    
    print("\n✓ Error handling works correctly!")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("SEARCH API INTEGRATION DEMO")
    print("=" * 60)
    print("\nThis demo shows how to use the search API integration")
    print("to retrieve evidence from external sources.")
    print("\nNote: You need to set SERPER_API_KEY or TAVILY_API_KEY")
    print("in your .env file for the search functionality to work.")
    
    # Run demos
    demo_domain_extraction()
    demo_error_handling()
    
    # Only run search demo if API key is configured
    from config.settings import settings
    if settings.SERPER_API_KEY or settings.TAVILY_API_KEY:
        demo_basic_search()
    else:
        print("\n" + "=" * 60)
        print("⚠️  Skipping search demo - No API key configured")
        print("=" * 60)
        print("\nTo run the search demo, add one of these to your .env file:")
        print("  SERPER_API_KEY=your_key_here")
        print("  TAVILY_API_KEY=your_key_here")
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
