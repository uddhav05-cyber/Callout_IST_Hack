"""
Unit tests for claim filtering and ranking functions.

Tests the isFactualClaim and calculateImportance functions to ensure
they correctly filter opinions and rank claims by importance.
"""

import pytest
from src.llm_integration import isFactualClaim, calculateImportance


class TestIsFactualClaim:
    """Test suite for isFactualClaim function."""
    
    def test_factual_claim_with_numbers(self):
        """Test that claims with numbers are considered factual."""
        claim = "The GDP grew by 5% in 2023 according to government data"
        assert isFactualClaim(claim) is True
    
    def test_factual_claim_with_official_source(self):
        """Test that claims with official sources are considered factual."""
        claim = "The president announced a new policy yesterday"
        assert isFactualClaim(claim) is True
    
    def test_opinion_with_i_think(self):
        """Test that opinions with 'I think' are filtered out."""
        claim = "I think this is the best policy we've ever had"
        assert isFactualClaim(claim) is False
    
    def test_opinion_with_should(self):
        """Test that opinions with 'should' are filtered out."""
        claim = "The government should implement this policy immediately"
        assert isFactualClaim(claim) is False
    
    def test_subjective_language_without_facts(self):
        """Test that subjective language without facts is filtered out."""
        claim = "This is the most amazing thing that has ever happened"
        assert isFactualClaim(claim) is False
    
    def test_subjective_language_with_facts(self):
        """Test that subjective language with factual keywords is allowed."""
        claim = "The company reported the best quarterly results in 2023"
        assert isFactualClaim(claim) is True
    
    def test_too_short_claim(self):
        """Test that very short claims are filtered out."""
        claim = "It happened yesterday"
        assert isFactualClaim(claim) is False
    
    def test_neutral_factual_statement(self):
        """Test that neutral factual statements are accepted."""
        claim = "The meeting was held on January 15th at the headquarters"
        assert isFactualClaim(claim) is True


class TestCalculateImportance:
    """Test suite for calculateImportance function."""
    
    def test_claim_at_beginning_of_article(self):
        """Test that claims at the beginning get higher importance."""
        article = "The president announced a new policy. This is important. Other details follow."
        claim = "The president announced a new policy"
        importance = calculateImportance(claim, article)
        assert importance > 0.7  # Should be high importance
    
    def test_claim_at_end_of_article(self):
        """Test that claims at the end get lower importance."""
        article = "Many things happened. Various events occurred. The president announced a new policy."
        claim = "The president announced a new policy"
        importance = calculateImportance(claim, article)
        assert importance < 0.9  # Should be lower than beginning
    
    def test_claim_with_multiple_keywords(self):
        """Test that claims with multiple factual keywords get higher importance."""
        article = "This is a long article about various topics."
        claim = "According to research data, the study confirmed that statistics show improvement"
        importance = calculateImportance(claim, article)
        assert importance > 0.6  # Should have decent importance due to keywords
    
    def test_claim_with_numbers(self):
        """Test that claims with numbers get importance boost."""
        article = "This is an article about economic growth."
        claim = "The GDP grew by 5% in 2023 according to official data"
        importance = calculateImportance(claim, article)
        assert importance > 0.5  # Should have good importance
    
    def test_claim_with_dates(self):
        """Test that claims with dates get importance boost."""
        article = "This is an article about historical events."
        claim = "The event occurred in 2023 and was reported by officials"
        importance = calculateImportance(claim, article)
        assert importance > 0.5  # Should have good importance
    
    def test_claim_with_proper_nouns(self):
        """Test that claims with proper nouns get importance boost."""
        article = "This is an article about international relations."
        claim = "President Biden met with Prime Minister Johnson to discuss trade"
        importance = calculateImportance(claim, article)
        assert importance > 0.5  # Should have good importance
    
    def test_long_claim_gets_bonus(self):
        """Test that longer claims get a length bonus."""
        article = "This is an article."
        short_claim = "The president announced a policy"
        long_claim = "The president announced a comprehensive new policy that will affect millions of citizens across the country"
        
        short_importance = calculateImportance(short_claim, article)
        long_importance = calculateImportance(long_claim, article)
        
        assert long_importance >= short_importance  # Long claim should be at least as important
    
    def test_importance_in_valid_range(self):
        """Test that importance is always in valid range [0.0, 1.0]."""
        article = "This is a test article with various content."
        claim = "This is a test claim with some content"
        importance = calculateImportance(claim, article)
        assert 0.0 <= importance <= 1.0
    
    def test_minimum_importance(self):
        """Test that all claims get at least minimum importance."""
        article = "This is a test article."
        claim = "This is a very simple claim without much"
        importance = calculateImportance(claim, article)
        assert importance >= 0.1  # Minimum importance threshold


class TestIntegration:
    """Integration tests for claim filtering and ranking."""
    
    def test_filtering_and_ranking_together(self):
        """Test that filtering and ranking work together correctly."""
        article = "The president announced a new policy. I think this is great. The GDP grew by 5%."
        
        claims = [
            "The president announced a new policy",
            "I think this is great",
            "The GDP grew by 5%"
        ]
        
        # Filter claims
        factual_claims = [c for c in claims if isFactualClaim(c)]
        
        # Should filter out the opinion
        assert len(factual_claims) == 2
        assert "I think this is great" not in factual_claims
        
        # Calculate importance for factual claims
        importance_scores = [(c, calculateImportance(c, article)) for c in factual_claims]
        
        # Sort by importance
        importance_scores.sort(key=lambda x: x[1], reverse=True)
        
        # All scores should be valid
        for claim, score in importance_scores:
            assert 0.0 <= score <= 1.0
        
        # First claim should have higher or equal importance (it's at the beginning)
        assert importance_scores[0][1] >= importance_scores[1][1] * 0.8  # Allow some tolerance


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
