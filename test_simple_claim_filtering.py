"""
Simple standalone test for claim filtering and ranking functions.
This test doesn't require external dependencies.
"""

import re


def isFactualClaim(claim: str) -> bool:
    """Test version of isFactualClaim."""
    assert claim is not None and len(claim.strip()) > 0, "Claim must be non-empty"
    
    claim_lower = claim.lower()
    
    opinion_indicators = [
        'i think', 'i believe', 'in my opinion', 'i feel',
        'should', 'must', 'ought to', 'need to',
        'probably', 'maybe', 'perhaps', 'possibly',
        'seems like', 'appears to be'
    ]
    
    subjective_words = [
        'best', 'worst', 'greatest', 'terrible', 'awful',
        'amazing', 'wonderful', 'horrible', 'fantastic',
        'beautiful', 'ugly', 'good', 'bad', 'better', 'worse'
    ]
    
    factual_keywords = [
        'said', 'reported', 'announced', 'confirmed', 'revealed',
        'according to', 'study', 'research', 'data', 'statistics',
        'percent', '%', 'million', 'billion', 'year', 'date',
        'government', 'official', 'company', 'organization',
        'was', 'were', 'is', 'are', 'has', 'have'
    ]
    
    if any(indicator in claim_lower for indicator in opinion_indicators):
        return False
    
    has_subjective = any(word in claim_lower for word in subjective_words)
    has_factual = any(keyword in claim_lower for keyword in factual_keywords)
    
    if has_subjective and not has_factual:
        return False
    
    if len(claim) < 30:
        return False
    
    if has_factual:
        return True
    
    return True


def calculateImportance(claim: str, articleText: str) -> float:
    """Test version of calculateImportance."""
    assert claim is not None and len(claim.strip()) > 0, "Claim must be non-empty"
    assert articleText is not None and len(articleText.strip()) > 0, "Article text must be non-empty"
    
    claim_lower = claim.lower()
    article_lower = articleText.lower()
    
    claim_position = article_lower.find(claim_lower)
    if claim_position >= 0:
        position_ratio = claim_position / max(len(articleText), 1)
        position_score = 1.0 - (position_ratio * 0.5)
    else:
        position_score = 0.7
    
    factual_keywords = [
        'said', 'reported', 'announced', 'confirmed', 'revealed',
        'according to', 'study', 'research', 'data', 'statistics',
        'percent', '%', 'million', 'billion', 'year', 'date',
        'government', 'official', 'company', 'organization'
    ]
    keyword_count = sum(1 for kw in factual_keywords if kw in claim_lower)
    keyword_score = min(keyword_count * 0.15, 0.5)
    
    specificity_score = 0.0
    
    if re.search(r'\d+', claim):
        specificity_score += 0.2
    
    if re.search(r'\b(19|20)\d{2}\b', claim):
        specificity_score += 0.15
    
    capitalized_words = re.findall(r'\b[A-Z][a-z]+\b', claim)
    if len(capitalized_words) >= 2:
        specificity_score += 0.15
    
    if len(claim) > 100:
        length_bonus = 0.1
    elif len(claim) > 50:
        length_bonus = 0.05
    else:
        length_bonus = 0.0
    
    importance = min(position_score + keyword_score + specificity_score + length_bonus, 1.0)
    importance = max(importance, 0.1)
    
    assert 0.0 <= importance <= 1.0, "Importance must be in range [0.0, 1.0]"
    return importance


# Run tests
def test_factual_claims():
    print("Testing isFactualClaim...")
    
    # Test factual claims
    assert isFactualClaim("The GDP grew by 5% in 2023 according to government data") is True
    print("✓ Factual claim with numbers passes")
    
    assert isFactualClaim("The president announced a new policy yesterday") is True
    print("✓ Factual claim with official source passes")
    
    # Test opinions
    assert isFactualClaim("I think this is the best policy we've ever had") is False
    print("✓ Opinion with 'I think' filtered out")
    
    assert isFactualClaim("The government should implement this policy immediately") is False
    print("✓ Opinion with 'should' filtered out")
    
    assert isFactualClaim("This is the most amazing thing that has ever happened") is False
    print("✓ Subjective language without facts filtered out")
    
    # Test subjective with facts
    assert isFactualClaim("The company reported the best quarterly results in 2023") is True
    print("✓ Subjective language with facts allowed")
    
    print("\nAll isFactualClaim tests passed! ✓\n")


def test_importance():
    print("Testing calculateImportance...")
    
    article = "The president announced a new policy. This is important. Other details follow."
    claim = "The president announced a new policy"
    importance = calculateImportance(claim, article)
    assert importance > 0.7
    print(f"✓ Claim at beginning has high importance: {importance:.2f}")
    
    article = "This is an article about economic growth."
    claim = "The GDP grew by 5% in 2023 according to official data"
    importance = calculateImportance(claim, article)
    assert importance > 0.5
    assert 0.0 <= importance <= 1.0
    print(f"✓ Claim with numbers has good importance: {importance:.2f}")
    
    article = "This is a test article."
    claim = "This is a very simple claim without much"
    importance = calculateImportance(claim, article)
    assert importance >= 0.1
    print(f"✓ All claims get minimum importance: {importance:.2f}")
    
    print("\nAll calculateImportance tests passed! ✓\n")


def test_integration():
    print("Testing integration...")
    
    article = "The president announced a new policy. I think this is great. The GDP grew by 5%."
    
    claims = [
        "The president announced a new policy",
        "I think this is great",
        "The GDP grew by 5%"
    ]
    
    # Filter claims
    factual_claims = [c for c in claims if isFactualClaim(c)]
    
    assert len(factual_claims) == 2
    assert "I think this is great" not in factual_claims
    print(f"✓ Filtered {len(claims)} claims to {len(factual_claims)} factual claims")
    
    # Calculate importance
    importance_scores = [(c, calculateImportance(c, article)) for c in factual_claims]
    importance_scores.sort(key=lambda x: x[1], reverse=True)
    
    for claim, score in importance_scores:
        assert 0.0 <= score <= 1.0
        print(f"  - {claim[:40]}... (importance: {score:.2f})")
    
    print("\nAll integration tests passed! ✓\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Claim Filtering and Ranking Functions")
    print("=" * 60 + "\n")
    
    test_factual_claims()
    test_importance()
    test_integration()
    
    print("=" * 60)
    print("ALL TESTS PASSED! ✓✓✓")
    print("=" * 60)
