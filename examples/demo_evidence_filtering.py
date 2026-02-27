"""
Demo script for evidence filtering and ranking (Task 8.2).

This script demonstrates the complete evidence retrieval workflow including:
- Query optimization
- Search API integration
- Source credibility filtering
- Relevance scoring
- Combined ranking

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 12.5, 19.1, 19.2, 19.3, 19.4
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import Claim
from src.evidence_retrieval import (
    optimizeQueryForSearch,
    calculateRelevance,
    filterTrustedSources,
    searchEvidence,
    SearchResult,
    SearchAPIError,
    RateLimitError
)
from config.settings import settings


def demo_query_optimization():
    """Demonstrate query optimization."""
    print("=" * 70)
    print("Demo 1: Query Optimization")
    print("=" * 70)
    
    test_claims = [
        "The president announced a new climate policy yesterday",
        "Scientists discovered a cure for cancer in 2024",
        "The stock market crashed by 50% last week"
    ]
    
    print("\nOptimizing claims for search:")
    print("-" * 70)
    
    for claim_text in test_claims:
        optimized = optimizeQueryForSearch(claim_text)
        print(f"\nOriginal:  {claim_text}")
        print(f"Optimized: {optimized}")
    
    print("\n✓ Query optimization complete!")


def demo_relevance_calculation():
    """Demonstrate relevance scoring."""
    print("\n" + "=" * 70)
    print("Demo 2: Relevance Calculation")
    print("=" * 70)
    
    claim = "Scientists discovered a new species of bird in the Amazon rainforest"
    
    snippets = [
        ("High relevance", "Researchers have found a previously unknown bird species in the Amazon"),
        ("Medium relevance", "A new animal was discovered in South America by scientists"),
        ("Low relevance", "The Amazon rainforest is home to many species"),
        ("No relevance", "The weather forecast predicts rain tomorrow")
    ]
    
    print(f"\nClaim: {claim}")
    print("\nRelevance scores:")
    print("-" * 70)
    
    for label, snippet in snippets:
        score = calculateRelevance(claim, snippet)
        print(f"\n{label}: {score:.3f}")
        print(f"Snippet: {snippet}")
    
    print("\n✓ Relevance calculation complete!")


def demo_source_filtering():
    """Demonstrate source credibility filtering."""
    print("\n" + "=" * 70)
    print("Demo 3: Source Credibility Filtering")
    print("=" * 70)
    
    # Create mock search results
    mock_results = [
        SearchResult(
            url="https://bbc.com/news/science",
            snippet="BBC reports on scientific discovery",
            title="Science News"
        ),
        SearchResult(
            url="https://reuters.com/article",
            snippet="Reuters coverage of the event",
            title="Breaking News"
        ),
        SearchResult(
            url="https://unknown-blog.com/post",
            snippet="Blog post about the topic",
            title="Blog Post"
        ),
        SearchResult(
            url="https://nasa.gov/news",
            snippet="NASA announcement",
            title="NASA News"
        )
    ]
    
    print(f"\nInput: {len(mock_results)} search results")
    print(f"Credibility threshold: {settings.MINIMUM_CREDIBILITY_THRESHOLD}")
    print("\nFiltering by credibility:")
    print("-" * 70)
    
    trusted = filterTrustedSources(mock_results)
    
    print(f"\nFiltered to {len(trusted)} trusted sources:")
    for evidence in trusted:
        print(f"\n  • {evidence.sourceDomain}")
        print(f"    Credibility: {evidence.credibilityScore:.2f}")
        print(f"    Snippet: {evidence.snippet[:60]}...")
    
    print("\n✓ Source filtering complete!")


def demo_complete_workflow():
    """Demonstrate the complete searchEvidence workflow."""
    print("\n" + "=" * 70)
    print("Demo 4: Complete Evidence Search Workflow")
    print("=" * 70)
    
    # Create a test claim
    claim = Claim(
        text="NASA announced the discovery of water on Mars",
        context="Article about space exploration",
        importance=0.9
    )
    
    print(f"\nClaim: {claim.text}")
    print(f"Importance: {claim.importance}")
    
    # Check if API key is configured
    if not (settings.SERPER_API_KEY or settings.TAVILY_API_KEY):
        print("\n⚠️  No search API key configured - skipping live search")
        print("   Add SERPER_API_KEY or TAVILY_API_KEY to .env to test live search")
        return
    
    print("\nSearching for evidence...")
    print("-" * 70)
    
    try:
        evidence_list = searchEvidence(claim)
        
        if not evidence_list:
            print("\n⚠️  No evidence found (no trusted sources met the threshold)")
            print("   This claim would be marked as UNVERIFIED")
        else:
            print(f"\nFound {len(evidence_list)} evidence items:")
            print("(Ranked by combined score: 70% relevance + 30% credibility)")
            print("-" * 70)
            
            for i, evidence in enumerate(evidence_list, 1):
                combined = 0.7 * evidence.relevanceScore + 0.3 * evidence.credibilityScore
                
                print(f"\n{i}. {evidence.sourceDomain}")
                print(f"   Credibility: {evidence.credibilityScore:.2f}")
                print(f"   Relevance:   {evidence.relevanceScore:.2f}")
                print(f"   Combined:    {combined:.2f}")
                print(f"   URL: {evidence.sourceURL}")
                print(f"   Snippet: {evidence.snippet[:100]}...")
        
        print("\n✓ Complete workflow executed successfully!")
    
    except RateLimitError as e:
        print(f"\n❌ Rate limit exceeded: {e}")
        print("   Please wait before making more requests.")
    except SearchAPIError as e:
        print(f"\n❌ Search API error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


def demo_edge_cases():
    """Demonstrate edge case handling."""
    print("\n" + "=" * 70)
    print("Demo 5: Edge Case Handling")
    print("=" * 70)
    
    print("\n1. Very short claim:")
    claim = Claim(text="Test", context="", importance=0.5)
    # searchEvidence would handle this, but we'll skip the API call
    print(f"   Claim created successfully with minimal text")
    
    print("\n2. Empty search results:")
    empty_results = filterTrustedSources([])
    print(f"   Result: {len(empty_results)} evidence items")
    
    print("\n3. Zero relevance:")
    relevance = calculateRelevance("test", "completely different text")
    print(f"   Relevance: {relevance:.3f}")
    
    print("\n4. Empty strings in relevance:")
    relevance = calculateRelevance("", "test")
    print(f"   Empty claim relevance: {relevance:.3f}")
    relevance = calculateRelevance("test", "")
    print(f"   Empty snippet relevance: {relevance:.3f}")
    
    print("\n✓ Edge cases handled correctly!")


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("EVIDENCE FILTERING AND RANKING DEMO (Task 8.2)")
    print("=" * 70)
    print("\nThis demo shows the complete evidence retrieval workflow:")
    print("  1. Query optimization")
    print("  2. Relevance calculation")
    print("  3. Source credibility filtering")
    print("  4. Combined ranking (70% relevance + 30% credibility)")
    print("  5. Edge case handling")
    
    # Run all demos
    demo_query_optimization()
    demo_relevance_calculation()
    demo_source_filtering()
    demo_edge_cases()
    demo_complete_workflow()
    
    print("\n" + "=" * 70)
    print("All demos completed!")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✓ Query optimization for effective search")
    print("  ✓ Text similarity-based relevance scoring")
    print("  ✓ Source credibility filtering")
    print("  ✓ Combined ranking algorithm")
    print("  ✓ Limit to MAX_EVIDENCE_PER_CLAIM results")
    print("  ✓ Handle no trusted sources (UNVERIFIED)")
    print("  ✓ Robust error handling")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
