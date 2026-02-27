"""
Unit tests for the evidence retrieval module.

Tests the search API integration, error handling, and rate limit handling.

Requirements: 3.1, 11.3, 16.2
"""

import pytest
from unittest.mock import patch, Mock
import requests

from src.evidence_retrieval import (
    callSearchAPI,
    extractDomain,
    SearchResult,
    SearchAPIError,
    RateLimitError,
    _parse_serper_results,
    _parse_tavily_results
)


class TestExtractDomain:
    """Test domain extraction from URLs."""
    
    def test_extract_domain_basic(self):
        """Test basic domain extraction."""
        url = "https://example.com/article/123"
        assert extractDomain(url) == "example.com"
    
    def test_extract_domain_with_www(self):
        """Test domain extraction removes www prefix."""
        url = "https://www.example.com/article"
        assert extractDomain(url) == "example.com"
    
    def test_extract_domain_with_subdomain(self):
        """Test domain extraction with subdomain."""
        url = "https://news.example.com/article"
        assert extractDomain(url) == "news.example.com"
    
    def test_extract_domain_http(self):
        """Test domain extraction with HTTP."""
        url = "http://example.com/page"
        assert extractDomain(url) == "example.com"
    
    def test_extract_domain_with_port(self):
        """Test domain extraction with port number."""
        url = "https://example.com:8080/page"
        assert extractDomain(url) == "example.com:8080"
    
    def test_extract_domain_invalid_url(self):
        """Test domain extraction with invalid URL."""
        url = "not-a-valid-url"
        result = extractDomain(url)
        assert result == ""
    
    def test_extract_domain_empty_url(self):
        """Test domain extraction with empty URL."""
        result = extractDomain("")
        assert result == ""


class TestSearchResult:
    """Test SearchResult class."""
    
    def test_search_result_creation(self):
        """Test creating a SearchResult object."""
        result = SearchResult(
            url="https://example.com/article",
            snippet="This is a test snippet",
            title="Test Article"
        )
        assert result.url == "https://example.com/article"
        assert result.snippet == "This is a test snippet"
        assert result.title == "Test Article"
        assert result.domain == "example.com"
    
    def test_search_result_domain_extraction(self):
        """Test automatic domain extraction in SearchResult."""
        result = SearchResult(
            url="https://www.news.example.com/article",
            snippet="Test"
        )
        assert result.domain == "news.example.com"
    
    def test_search_result_with_date(self):
        """Test SearchResult with date."""
        result = SearchResult(
            url="https://example.com/article",
            snippet="Test",
            date="2024-01-15"
        )
        assert result.date == "2024-01-15"


class TestParseSerperResults:
    """Test parsing Serper API responses."""
    
    def test_parse_serper_results_basic(self):
        """Test parsing basic Serper response."""
        data = {
            "organic": [
                {
                    "link": "https://example.com/article1",
                    "snippet": "First article snippet",
                    "title": "Article 1"
                },
                {
                    "link": "https://example.com/article2",
                    "snippet": "Second article snippet",
                    "title": "Article 2"
                }
            ]
        }
        
        results = _parse_serper_results(data)
        assert len(results) == 2
        assert results[0].url == "https://example.com/article1"
        assert results[0].snippet == "First article snippet"
        assert results[1].url == "https://example.com/article2"
    
    def test_parse_serper_results_with_date(self):
        """Test parsing Serper response with dates."""
        data = {
            "organic": [
                {
                    "link": "https://example.com/article",
                    "snippet": "Article snippet",
                    "title": "Article",
                    "date": "2024-01-15"
                }
            ]
        }
        
        results = _parse_serper_results(data)
        assert len(results) == 1
        assert results[0].date == "2024-01-15"
    
    def test_parse_serper_results_empty(self):
        """Test parsing empty Serper response."""
        data = {"organic": []}
        results = _parse_serper_results(data)
        assert len(results) == 0
    
    def test_parse_serper_results_missing_fields(self):
        """Test parsing Serper response with missing fields."""
        data = {
            "organic": [
                {
                    "link": "https://example.com/article",
                    "snippet": "Valid snippet"
                },
                {
                    "link": "https://example.com/article2"
                    # Missing snippet - should be skipped
                },
                {
                    "snippet": "Snippet without URL"
                    # Missing link - should be skipped
                }
            ]
        }
        
        results = _parse_serper_results(data)
        assert len(results) == 1
        assert results[0].url == "https://example.com/article"


class TestParseTavilyResults:
    """Test parsing Tavily API responses."""
    
    def test_parse_tavily_results_basic(self):
        """Test parsing basic Tavily response."""
        data = {
            "results": [
                {
                    "url": "https://example.com/article1",
                    "content": "First article content",
                    "title": "Article 1"
                },
                {
                    "url": "https://example.com/article2",
                    "content": "Second article content",
                    "title": "Article 2"
                }
            ]
        }
        
        results = _parse_tavily_results(data)
        assert len(results) == 2
        assert results[0].url == "https://example.com/article1"
        assert results[0].snippet == "First article content"
        assert results[1].url == "https://example.com/article2"
    
    def test_parse_tavily_results_with_date(self):
        """Test parsing Tavily response with dates."""
        data = {
            "results": [
                {
                    "url": "https://example.com/article",
                    "content": "Article content",
                    "title": "Article",
                    "published_date": "2024-01-15"
                }
            ]
        }
        
        results = _parse_tavily_results(data)
        assert len(results) == 1
        assert results[0].date == "2024-01-15"
    
    def test_parse_tavily_results_empty(self):
        """Test parsing empty Tavily response."""
        data = {"results": []}
        results = _parse_tavily_results(data)
        assert len(results) == 0
    
    def test_parse_tavily_results_missing_fields(self):
        """Test parsing Tavily response with missing fields."""
        data = {
            "results": [
                {
                    "url": "https://example.com/article",
                    "content": "Valid content"
                },
                {
                    "url": "https://example.com/article2"
                    # Missing content - should be skipped
                },
                {
                    "content": "Content without URL"
                    # Missing url - should be skipped
                }
            ]
        }
        
        results = _parse_tavily_results(data)
        assert len(results) == 1
        assert results[0].url == "https://example.com/article"


class TestCallSearchAPI:
    """Test the main callSearchAPI function."""
    
    @patch('src.evidence_retrieval.requests.post')
    @patch('src.evidence_retrieval.settings')
    def test_call_serper_api_success(self, mock_settings, mock_post):
        """Test successful Serper API call."""
        # Configure mock settings
        mock_settings.SERPER_API_KEY = "test_serper_key"
        mock_settings.TAVILY_API_KEY = None
        mock_settings.MAX_EVIDENCE_PER_CLAIM = 5
        mock_settings.REQUEST_TIMEOUT_SECONDS = 10
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "organic": [
                {
                    "link": "https://example.com/article",
                    "snippet": "Test snippet",
                    "title": "Test Article"
                }
            ]
        }
        mock_post.return_value = mock_response
        
        results = callSearchAPI("test query")
        
        assert len(results) == 1
        assert results[0].url == "https://example.com/article"
        assert results[0].snippet == "Test snippet"
        
        # Verify API was called correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://google.serper.dev/search"
        assert call_args[1]['json']['q'] == "test query"
    
    @patch('src.evidence_retrieval.requests.post')
    @patch('src.evidence_retrieval.settings')
    def test_call_tavily_api_success(self, mock_settings, mock_post):
        """Test successful Tavily API call."""
        # Configure mock settings
        mock_settings.SERPER_API_KEY = None
        mock_settings.TAVILY_API_KEY = "test_tavily_key"
        mock_settings.MAX_EVIDENCE_PER_CLAIM = 5
        mock_settings.REQUEST_TIMEOUT_SECONDS = 10
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "url": "https://example.com/article",
                    "content": "Test content",
                    "title": "Test Article"
                }
            ]
        }
        mock_post.return_value = mock_response
        
        results = callSearchAPI("test query")
        
        assert len(results) == 1
        assert results[0].url == "https://example.com/article"
        assert results[0].snippet == "Test content"
        
        # Verify API was called correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://api.tavily.com/search"
        assert call_args[1]['json']['query'] == "test query"
    
    @patch('src.evidence_retrieval.settings')
    def test_call_search_api_no_key(self, mock_settings):
        """Test error when no API key is configured."""
        mock_settings.SERPER_API_KEY = None
        mock_settings.TAVILY_API_KEY = None
        
        with pytest.raises(SearchAPIError, match="No search API key configured"):
            callSearchAPI("test query")
    
    @patch('src.evidence_retrieval.settings')
    def test_call_search_api_empty_query(self, mock_settings):
        """Test handling of empty query."""
        mock_settings.SERPER_API_KEY = "test_key"
        
        results = callSearchAPI("")
        assert len(results) == 0
        
        results = callSearchAPI("   ")
        assert len(results) == 0
    
    @patch('src.evidence_retrieval.requests.post')
    @patch('src.evidence_retrieval.settings')
    def test_call_search_api_rate_limit(self, mock_settings, mock_post):
        """Test handling of rate limit error (429)."""
        mock_settings.SERPER_API_KEY = "test_key"
        mock_settings.TAVILY_API_KEY = None
        mock_settings.MAX_EVIDENCE_PER_CLAIM = 5
        mock_settings.REQUEST_TIMEOUT_SECONDS = 10
        
        # Mock rate limit response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_post.return_value = mock_response
        
        with pytest.raises(RateLimitError, match="rate limit exceeded"):
            callSearchAPI("test query")
    
    @patch('src.evidence_retrieval.requests.post')
    @patch('src.evidence_retrieval.settings')
    def test_call_search_api_error_status(self, mock_settings, mock_post):
        """Test handling of API error status codes."""
        mock_settings.SERPER_API_KEY = "test_key"
        mock_settings.TAVILY_API_KEY = None
        mock_settings.MAX_EVIDENCE_PER_CLAIM = 5
        mock_settings.REQUEST_TIMEOUT_SECONDS = 10
        
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        with pytest.raises(SearchAPIError, match="returned status 500"):
            callSearchAPI("test query")
    
    @patch('src.evidence_retrieval.requests.post')
    @patch('src.evidence_retrieval.settings')
    def test_call_search_api_timeout(self, mock_settings, mock_post):
        """Test handling of request timeout."""
        mock_settings.SERPER_API_KEY = "test_key"
        mock_settings.TAVILY_API_KEY = None
        mock_settings.MAX_EVIDENCE_PER_CLAIM = 5
        mock_settings.REQUEST_TIMEOUT_SECONDS = 10
        
        # Mock timeout
        mock_post.side_effect = requests.Timeout("Request timed out")
        
        with pytest.raises(SearchAPIError, match="timed out"):
            callSearchAPI("test query")
    
    @patch('src.evidence_retrieval.requests.post')
    @patch('src.evidence_retrieval.settings')
    def test_call_search_api_connection_error(self, mock_settings, mock_post):
        """Test handling of connection errors."""
        mock_settings.SERPER_API_KEY = "test_key"
        mock_settings.TAVILY_API_KEY = None
        mock_settings.MAX_EVIDENCE_PER_CLAIM = 5
        mock_settings.REQUEST_TIMEOUT_SECONDS = 10
        
        # Mock connection error
        mock_post.side_effect = requests.ConnectionError("Connection failed")
        
        with pytest.raises(SearchAPIError, match="request failed"):
            callSearchAPI("test query")
    
    @patch('src.evidence_retrieval.requests.post')
    @patch('src.evidence_retrieval.settings')
    def test_call_search_api_prefers_serper(self, mock_settings, mock_post):
        """Test that Serper is preferred when both keys are available."""
        mock_settings.SERPER_API_KEY = "test_serper_key"
        mock_settings.TAVILY_API_KEY = "test_tavily_key"
        mock_settings.MAX_EVIDENCE_PER_CLAIM = 5
        mock_settings.REQUEST_TIMEOUT_SECONDS = 10
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"organic": []}
        mock_post.return_value = mock_response
        
        callSearchAPI("test query")
        
        # Verify Serper API was called
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://google.serper.dev/search"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
