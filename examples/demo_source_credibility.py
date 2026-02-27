"""
Demo script for the source credibility lookup system.

This script demonstrates how to use the source credibility lookup system
to check the credibility of various news sources.
"""

from src.source_credibility import lookup_source_credibility, get_credibility_database


def main():
    """Demonstrate source credibility lookup functionality."""
    print("=" * 70)
    print("Source Credibility Lookup System Demo")
    print("=" * 70)
    print()
    
    # Example 1: Look up trusted sources
    print("1. Trusted Sources (0.8-1.0):")
    print("-" * 70)
    trusted_sources = ["apnews.com", "reuters.com", "bbc.com", "nature.com"]
    for source in trusted_sources:
        result = lookup_source_credibility(source)
        print(f"  {source:20} | Score: {result.credibilityScore:.2f} | {result.category.value}")
    print()
    
    # Example 2: Look up mainstream sources
    print("2. Mainstream Sources (0.5-0.79):")
    print("-" * 70)
    mainstream_sources = ["cnn.com", "foxnews.com", "usatoday.com", "wikipedia.org"]
    for source in mainstream_sources:
        result = lookup_source_credibility(source)
        print(f"  {source:20} | Score: {result.credibilityScore:.2f} | {result.category.value}")
    print()
    
    # Example 3: Look up questionable sources
    print("3. Questionable Sources (0.3-0.49):")
    print("-" * 70)
    questionable_sources = ["dailymail.co.uk", "nypost.com", "buzzfeed.com"]
    for source in questionable_sources:
        result = lookup_source_credibility(source)
        print(f"  {source:20} | Score: {result.credibilityScore:.2f} | {result.category.value}")
    print()
    
    # Example 4: Look up unreliable sources
    print("4. Unreliable Sources (0.0-0.29):")
    print("-" * 70)
    unreliable_sources = ["infowars.com", "breitbart.com", "theonion.com"]
    for source in unreliable_sources:
        result = lookup_source_credibility(source)
        print(f"  {source:20} | Score: {result.credibilityScore:.2f} | {result.category.value}")
    print()
    
    # Example 5: Look up unknown sources (default score)
    print("5. Unknown Sources (default score = 0.5):")
    print("-" * 70)
    unknown_sources = ["unknown-news-site.com", "random-blog.net"]
    for source in unknown_sources:
        result = lookup_source_credibility(source)
        print(f"  {source:20} | Score: {result.credibilityScore:.2f} | {result.category.value}")
    print()
    
    # Example 6: Extract domain from URLs
    print("6. Domain Extraction from URLs:")
    print("-" * 70)
    urls = [
        "https://www.nytimes.com/2024/01/article.html",
        "http://reuters.com/world/news",
        "https://www.bbc.co.uk/news/world"
    ]
    for url in urls:
        result = lookup_source_credibility(url)
        print(f"  URL: {url}")
        print(f"  Domain: {result.domain:15} | Score: {result.credibilityScore:.2f} | {result.category.value}")
        print()
    
    # Example 7: Get statistics
    print("7. Database Statistics:")
    print("-" * 70)
    db = get_credibility_database()
    all_sources = db.get_all_sources()
    print(f"  Total sources in database: {len(all_sources)}")
    
    from src.models import SourceCategory
    for category in SourceCategory:
        sources = db.get_sources_by_category(category)
        print(f"  {category.value:15}: {len(sources)} sources")
    print()
    
    print("=" * 70)
    print("Demo completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
