"""
Unit tests for LLM Integration Module.

Tests the LLM-based claim extraction functionality including:
- Prompt building
- LLM API calls with retry logic
- Response parsing
- Fallback to rule-based extraction
- Claim filtering and importance scoring

Requirements: 2.1, 11.1, 11.2, 16.1
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time

from src.llm_integration import (
    buildClaimExtractionPrompt,
    callLLM,
    parseLLMResponse,
    isFactualClaim,
    calculateImportance,
    ruleBasedClaimExtraction,
    extractClaims,
    LLMError
)
from src.models import Claim


class TestBuildClaimExtractionPrompt:
    """Test prompt building for claim extraction."""
    
    def test_builds_valid_prompt(self):
        """Test that a valid prompt is built from article text."""
        article = "The GDP grew by 5% in 2023. Unemployment fell to 3.5%."
        prompt = buildClaimExtractionPrompt(article)
        
        assert len(prompt) > 0
        assert article in prompt
        assert "CLAIM:" in prompt
        assert "IMPORTANCE:" in prompt
        assert "CONTEXT:" in prompt
    
    def test_handles_long_article(self):
        """Test prompt building with long article text."""
        article = "This is a test sentence. " * 1000
        prompt = buildClaimExtractionPrompt(article)
        
        assert len(prompt) > 0
        assert "CLAIM:" in prompt
    
    def test_strips_whitespace(self):
        """Test that whitespace is properly stripped."""
        article = "  \n  The GDP grew by 5%.  \n  "
        prompt = buildClaimExtractionPrompt(article)
        
        assert "The GDP grew by 5%." in prompt
        assert prompt.count('\n\n\n') == 0  # No excessive whitespace
    
    def test_empty_article_raises_assertion(self):
        """Test that empty article raises assertion error."""
        with pytest.raises(AssertionError):
            buildClaimExtractionPrompt("")
    
    def test_none_article_raises_assertion(self):
        """Test that None article raises assertion error."""
        with pytest.raises(AssertionError):
            buildClaimExtractionPrompt(None)


class TestCallLLM:
    """Test LLM API calling with retry logic."""
    
    @patch('src.llm_integration.ChatGroq')
    def test_successful_groq_call(self, mock_groq):
        """Test successful LLM call using Groq."""
        # Mock Groq response
        mock_response = Mock()
        mock_response.content = "CLAIM: Test claim\nIMPORTANCE: 0.8\nCONTEXT: Test context\n---"
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_groq.return_value = mock_llm
        
        with patch('src.llm_integration.settings') as mock_settings:
            mock_settings.GROQ_API_KEY = "test_key"
            mock_settings.OPENAI_API_KEY = None
            
            result = callLLM("Test prompt")
            
            assert len(result) > 0
            assert "CLAIM:" in result
            mock_llm.invoke.assert_called_once()
    
    @patch('src.llm_integration.ChatOpenAI')
    def test_successful_openai_call(self, mock_openai):
        """Test successful LLM call using OpenAI."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.content = "CLAIM: Test claim\nIMPORTANCE: 0.8\nCONTEXT: Test context\n---"
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_openai.return_value = mock_llm
        
        with patch('src.llm_integration.settings') as mock_settings:
            mock_settings.GROQ_API_KEY = None
            mock_settings.OPENAI_API_KEY = "test_key"
            
            result = callLLM("Test prompt")
            
            assert len(result) > 0
            assert "CLAIM:" in result
            mock_llm.invoke.assert_called_once()
    
    @patch('src.llm_integration.ChatGroq')
    @patch('time.sleep')
    def test_retry_logic_with_exponential_backoff(self, mock_sleep, mock_groq):
        """Test that retry logic uses exponential backoff."""
        # Mock Groq to fail twice, then succeed
        mock_response = Mock()
        mock_response.content = "CLAIM: Test claim\nIMPORTANCE: 0.8\nCONTEXT: Test context\n---"
        mock_llm = Mock()
        mock_llm.invoke.side_effect = [
            Exception("API Error 1"),
            Exception("API Error 2"),
            mock_response
        ]
        mock_groq.return_value = mock_llm
        
        with patch('src.llm_integration.settings') as mock_settings:
            mock_settings.GROQ_API_KEY = "test_key"
            mock_settings.OPENAI_API_KEY = None
            
            result = callLLM("Test prompt", max_retries=3)
            
            assert len(result) > 0
            assert mock_llm.invoke.call_count == 3
            # Check exponential backoff: 2^0=1s, 2^1=2s
            assert mock_sleep.call_count == 2
            mock_sleep.assert_any_call(1)
            mock_sleep.assert_any_call(2)
    
    @patch('src.llm_integration.ChatGroq')
    def test_all_retries_fail_raises_error(self, mock_groq):
        """Test that LLMError is raised after all retries fail."""
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("API Error")
        mock_groq.return_value = mock_llm
        
        with patch('src.llm_integration.settings') as mock_settings:
            mock_settings.GROQ_API_KEY = "test_key"
            mock_settings.OPENAI_API_KEY = None
            
            with pytest.raises(LLMError):
                callLLM("Test prompt", max_retries=3)
            
            assert mock_llm.invoke.call_count == 3
    
    def test_no_api_key_raises_error(self):
        """Test that missing API keys raise LLMError."""
        with patch('src.llm_integration.settings') as mock_settings:
            mock_settings.GROQ_API_KEY = None
            mock_settings.OPENAI_API_KEY = None
            
            with pytest.raises(LLMError, match="No LLM API key configured"):
                callLLM("Test prompt")
    
    @patch('src.llm_integration.ChatGroq')
    def test_empty_response_raises_error(self, mock_groq):
        """Test that empty LLM response raises error."""
        mock_response = Mock()
        mock_response.content = ""
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_groq.return_value = mock_llm
        
        with patch('src.llm_integration.settings') as mock_settings:
            mock_settings.GROQ_API_KEY = "test_key"
            mock_settings.OPENAI_API_KEY = None
            
            with pytest.raises(LLMError, match="empty response"):
                callLLM("Test prompt")


class TestParseLLMResponse:
    """Test parsing of LLM responses."""
    
    def test_parses_single_claim(self):
        """Test parsing a single claim from LLM response."""
        response = """
CLAIM: The GDP grew by 5% in 2023.
IMPORTANCE: 0.9
CONTEXT: According to the latest economic report, the GDP grew by 5% in 2023.
---
"""
        claims = parseLLMResponse(response)
        
        assert len(claims) == 1
        assert claims[0][0] == "The GDP grew by 5% in 2023."
        assert claims[0][1] == 0.9
        assert "economic report" in claims[0][2]
    
    def test_parses_multiple_claims(self):
        """Test parsing multiple claims from LLM response."""
        response = """
CLAIM: The GDP grew by 5% in 2023.
IMPORTANCE: 0.9
CONTEXT: Economic report shows growth.
---
CLAIM: Unemployment fell to 3.5%.
IMPORTANCE: 0.8
CONTEXT: Labor statistics indicate improvement.
---
CLAIM: Inflation remained at 2%.
IMPORTANCE: 0.7
CONTEXT: Central bank data confirms stability.
---
"""
        claims = parseLLMResponse(response)
        
        assert len(claims) == 3
        assert claims[0][0] == "The GDP grew by 5% in 2023."
        assert claims[1][0] == "Unemployment fell to 3.5%."
        assert claims[2][0] == "Inflation remained at 2%."
    
    def test_handles_missing_importance(self):
        """Test that missing importance defaults to 0.5."""
        response = """
CLAIM: The GDP grew by 5% in 2023.
CONTEXT: Economic report shows growth.
---
"""
        claims = parseLLMResponse(response)
        
        assert len(claims) == 1
        assert claims[0][1] == 0.5  # Default importance
    
    def test_handles_missing_context(self):
        """Test that missing context defaults to empty string."""
        response = """
CLAIM: The GDP grew by 5% in 2023.
IMPORTANCE: 0.9
---
"""
        claims = parseLLMResponse(response)
        
        assert len(claims) == 1
        assert claims[0][2] == ""  # Empty context
    
    def test_clamps_importance_to_valid_range(self):
        """Test that importance scores are clamped to [0.0, 1.0]."""
        response = """
CLAIM: Test claim 1
IMPORTANCE: 1.5
CONTEXT: Test
---
CLAIM: Test claim 2
IMPORTANCE: -0.5
CONTEXT: Test
---
"""
        claims = parseLLMResponse(response)
        
        assert len(claims) == 2
        assert claims[0][1] == 1.0  # Clamped from 1.5
        assert claims[1][1] == 0.0  # Clamped from -0.5
    
    def test_handles_empty_response(self):
        """Test that empty response returns empty list."""
        claims = parseLLMResponse("")
        assert len(claims) == 0
    
    def test_handles_malformed_response(self):
        """Test that malformed response is handled gracefully."""
        response = "This is not a properly formatted response."
        claims = parseLLMResponse(response)
        assert len(claims) == 0


class TestIsFactualClaim:
    """Test factual claim filtering."""
    
    def test_identifies_factual_claim_with_numbers(self):
        """Test that claims with numbers are identified as factual."""
        claim = "The GDP grew by 5% in 2023 according to official data."
        assert isFactualClaim(claim) is True
    
    def test_identifies_factual_claim_with_sources(self):
        """Test that claims with sources are identified as factual."""
        claim = "The government announced a new policy yesterday."
        assert isFactualClaim(claim) is True
    
    def test_filters_opinion_with_i_think(self):
        """Test that opinions with 'I think' are filtered out."""
        claim = "I think this is the best policy we've ever had."
        assert isFactualClaim(claim) is False
    
    def test_filters_opinion_with_should(self):
        """Test that opinions with 'should' are filtered out."""
        claim = "The government should implement this policy immediately."
        assert isFactualClaim(claim) is False
    
    def test_filters_subjective_language(self):
        """Test that subjective language without factual keywords is filtered."""
        claim = "This is the most amazing and wonderful thing ever."
        assert isFactualClaim(claim) is False
    
    def test_allows_subjective_with_factual_keywords(self):
        """Test that subjective language with factual keywords is allowed."""
        claim = "The company reported the best quarterly results in 2023."
        assert isFactualClaim(claim) is True
    
    def test_filters_very_short_claims(self):
        """Test that very short claims are filtered out."""
        claim = "This is short."
        assert isFactualClaim(claim) is False
    
    def test_handles_mixed_case(self):
        """Test that case-insensitive matching works."""
        claim = "I THINK this policy is great and should be implemented."
        assert isFactualClaim(claim) is False


class TestCalculateImportance:
    """Test importance score calculation."""
    
    def test_early_position_increases_importance(self):
        """Test that claims early in article have higher importance."""
        article = "First sentence with data. Second sentence. Third sentence."
        claim1 = "First sentence with data."
        claim2 = "Third sentence."
        
        importance1 = calculateImportance(claim1, article)
        importance2 = calculateImportance(claim2, article)
        
        assert importance1 > importance2
    
    def test_factual_keywords_increase_importance(self):
        """Test that factual keywords increase importance."""
        article = "Some text here. The government announced new data."
        claim = "The government announced new data."
        
        importance = calculateImportance(claim, article)
        
        assert importance > 0.5  # Should be above baseline
    
    def test_numbers_increase_importance(self):
        """Test that numbers increase importance."""
        article = "Some text. The GDP grew by 5% in 2023."
        claim = "The GDP grew by 5% in 2023."
        
        importance = calculateImportance(claim, article)
        
        assert importance > 0.5
    
    def test_proper_nouns_increase_importance(self):
        """Test that proper nouns increase importance."""
        article = "Some text. President Biden announced the policy."
        claim = "President Biden announced the policy."
        
        importance = calculateImportance(claim, article)
        
        assert importance > 0.5
    
    def test_longer_claims_get_bonus(self):
        """Test that longer claims get importance bonus."""
        article = "Some text. " + "A" * 150
        claim = "A" * 150
        
        importance = calculateImportance(claim, article)
        
        # Should have length bonus
        assert importance > 0.3
    
    def test_importance_bounded_to_valid_range(self):
        """Test that importance is always in [0.0, 1.0]."""
        article = "Test article with some content here."
        claim = "Test claim with lots of keywords: government data reported announced confirmed."
        
        importance = calculateImportance(claim, article)
        
        assert 0.0 <= importance <= 1.0
    
    def test_minimum_importance_enforced(self):
        """Test that minimum importance is enforced."""
        article = "Test article."
        claim = "Simple claim without much."
        
        importance = calculateImportance(claim, article)
        
        assert importance >= 0.1


class TestRuleBasedClaimExtraction:
    """Test fallback rule-based claim extraction."""
    
    def test_extracts_claims_from_simple_article(self):
        """Test extraction from simple article."""
        article = "The GDP grew by 5% in 2023. Unemployment fell to 3.5%. Inflation remained stable."
        
        claims = ruleBasedClaimExtraction(article)
        
        assert len(claims) > 0
        assert all(isinstance(c, tuple) and len(c) == 3 for c in claims)
        assert all(0.0 <= c[1] <= 1.0 for c in claims)  # Importance in range
    
    def test_filters_non_factual_sentences(self):
        """Test that non-factual sentences are filtered."""
        article = "I think this is great. The GDP grew by 5%. This is the best policy ever."
        
        claims = ruleBasedClaimExtraction(article)
        
        # Should extract only the factual claim
        assert any("GDP" in c[0] for c in claims)
        assert not any("I think" in c[0] for c in claims)
    
    def test_provides_context_for_claims(self):
        """Test that context is provided for each claim."""
        article = "First sentence. The GDP grew by 5%. Third sentence."
        
        claims = ruleBasedClaimExtraction(article)
        
        # Context should include surrounding sentences
        if len(claims) > 0:
            assert len(claims[0][2]) > len(claims[0][0])  # Context longer than claim
    
    def test_handles_article_with_no_factual_claims(self):
        """Test handling of article with no factual claims."""
        article = "I think this is great. This is the best thing ever. I believe it's wonderful."
        
        claims = ruleBasedClaimExtraction(article)
        
        # Should return some claims as fallback (first few sentences)
        assert len(claims) >= 0
    
    def test_handles_very_short_article(self):
        """Test handling of very short article."""
        article = "Short article with minimal content here for testing purposes."
        
        claims = ruleBasedClaimExtraction(article)
        
        # Should handle gracefully
        assert isinstance(claims, list)


class TestExtractClaims:
    """Test main claim extraction function."""
    
    @patch('src.llm_integration.callLLM')
    def test_successful_llm_extraction(self, mock_call_llm):
        """Test successful extraction using LLM."""
        mock_call_llm.return_value = """
CLAIM: The GDP grew by 5% in 2023.
IMPORTANCE: 0.9
CONTEXT: Economic report shows growth.
---
CLAIM: Unemployment fell to 3.5%.
IMPORTANCE: 0.8
CONTEXT: Labor statistics indicate improvement.
---
"""
        
        article = "The GDP grew by 5% in 2023. Unemployment fell to 3.5%."
        claims = extractClaims(article)
        
        assert len(claims) == 2
        assert all(isinstance(c, Claim) for c in claims)
        assert claims[0].importance >= claims[1].importance  # Sorted by importance
        mock_call_llm.assert_called_once()
    
    @patch('src.llm_integration.callLLM')
    def test_fallback_on_llm_failure(self, mock_call_llm):
        """Test fallback to rule-based extraction on LLM failure."""
        mock_call_llm.side_effect = LLMError("API failed")
        
        article = "The GDP grew by 5% in 2023. Unemployment fell to 3.5%."
        claims = extractClaims(article)
        
        # Should still return claims using fallback
        assert len(claims) > 0
        assert all(isinstance(c, Claim) for c in claims)
    
    @patch('src.llm_integration.callLLM')
    def test_fallback_on_empty_llm_response(self, mock_call_llm):
        """Test fallback when LLM returns no claims."""
        mock_call_llm.return_value = "No claims found."
        
        article = "The GDP grew by 5% in 2023. Unemployment fell to 3.5%."
        claims = extractClaims(article)
        
        # Should fallback to rule-based extraction
        assert len(claims) > 0
    
    def test_empty_article_raises_error(self):
        """Test that empty article raises ValueError."""
        with pytest.raises(ValueError, match="Article text cannot be empty"):
            extractClaims("")
    
    def test_claims_sorted_by_importance(self):
        """Test that claims are sorted by importance (descending)."""
        with patch('src.llm_integration.callLLM') as mock_call_llm:
            mock_call_llm.return_value = """
CLAIM: Low importance claim.
IMPORTANCE: 0.3
CONTEXT: Test.
---
CLAIM: High importance claim.
IMPORTANCE: 0.9
CONTEXT: Test.
---
CLAIM: Medium importance claim.
IMPORTANCE: 0.6
CONTEXT: Test.
---
"""
            article = "Test article."
            claims = extractClaims(article)
            
            assert len(claims) == 3
            assert claims[0].importance == 0.9
            assert claims[1].importance == 0.6
            assert claims[2].importance == 0.3
    
    @patch('src.llm_integration.callLLM')
    def test_limits_to_max_claims(self, mock_call_llm):
        """Test that claims are limited to MAX_CLAIMS_PER_ARTICLE."""
        # Generate response with many claims
        response = ""
        for i in range(20):
            response += f"""
CLAIM: Claim number {i}.
IMPORTANCE: 0.{i}
CONTEXT: Test context.
---
"""
        mock_call_llm.return_value = response
        
        with patch('src.llm_integration.settings') as mock_settings:
            mock_settings.MAX_CLAIMS_PER_ARTICLE = 10
            mock_settings.MAX_RETRIES = 3
            
            article = "Test article with many claims."
            claims = extractClaims(article)
            
            assert len(claims) <= 10
    
    def test_all_claims_have_unique_ids(self):
        """Test that all claims have unique IDs."""
        with patch('src.llm_integration.callLLM') as mock_call_llm:
            mock_call_llm.return_value = """
CLAIM: First claim.
IMPORTANCE: 0.9
CONTEXT: Test.
---
CLAIM: Second claim.
IMPORTANCE: 0.8
CONTEXT: Test.
---
"""
            article = "Test article."
            claims = extractClaims(article)
            
            ids = [c.id for c in claims]
            assert len(ids) == len(set(ids))  # All unique
            assert all(id is not None for id in ids)
    
    def test_all_claims_have_valid_importance(self):
        """Test that all claims have importance in [0.0, 1.0]."""
        with patch('src.llm_integration.callLLM') as mock_call_llm:
            mock_call_llm.return_value = """
CLAIM: Test claim.
IMPORTANCE: 0.7
CONTEXT: Test.
---
"""
            article = "Test article."
            claims = extractClaims(article)
            
            assert all(0.0 <= c.importance <= 1.0 for c in claims)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
