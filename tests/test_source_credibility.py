"""
Unit tests for the source credibility lookup system.

Tests cover:
- Loading credibility database from JSON
- Looking up known trusted sources
- Looking up unknown domains (default score)
- Category mapping correctness
- Domain extraction from URLs
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from src.models import SourceCategory, SourceCredibility
from src.source_credibility import SourceCredibilityDatabase, lookup_source_credibility


class TestSourceCredibilityDatabase:
    """Tests for SourceCredibilityDatabase class."""
    
    @pytest.fixture
    def sample_db_file(self):
        """Create a temporary database file for testing."""
        db_data = {
            "sources": {
                "apnews.com": {
                    "credibilityScore": 0.95,
                    "category": "TRUSTED",
                    "description": "Associated Press"
                },
                "reuters.com": {
                    "credibilityScore": 0.95,
                    "category": "TRUSTED",
                    "description": "Reuters"
                },
                "cnn.com": {
                    "credibilityScore": 0.7,
                    "category": "MAINSTREAM",
                    "description": "CNN"
                },
                "foxnews.com": {
                    "credibilityScore": 0.6,
                    "category": "MAINSTREAM",
                    "description": "Fox News"
                },
                "dailymail.co.uk": {
                    "credibilityScore": 0.45,
                    "category": "QUESTIONABLE",
                    "description": "Daily Mail"
                },
                "infowars.com": {
                    "credibilityScore": 0.1,
                    "category": "UNRELIABLE",
                    "description": "InfoWars"
                }
            },
            "defaultCredibilityScore": 0.5,
            "lastUpdated": "2024-01-01T00:00:00Z"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(db_data, f)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        Path(temp_path).unlink()
    
    def test_load_database(self, sample_db_file):
        """Test loading database from JSON file."""
        db = SourceCredibilityDatabase(sample_db_file)
        
        assert len(db.sources) == 6
        assert db.default_score == 0.5
        assert db.last_updated is not None
    
    def test_lookup_trusted_source(self, sample_db_file):
        """Test looking up a known trusted source."""
        db = SourceCredibilityDatabase(sample_db_file)
        
        result = db.lookup_source_credibility("apnews.com")
        
        assert isinstance(result, SourceCredibility)
        assert result.domain == "apnews.com"
        assert result.credibilityScore == 0.95
        assert result.category == SourceCategory.TRUSTED
    
    def test_lookup_mainstream_source(self, sample_db_file):
        """Test looking up a mainstream source."""
        db = SourceCredibilityDatabase(sample_db_file)
        
        result = db.lookup_source_credibility("cnn.com")
        
        assert result.domain == "cnn.com"
        assert result.credibilityScore == 0.7
        assert result.category == SourceCategory.MAINSTREAM
    
    def test_lookup_questionable_source(self, sample_db_file):
        """Test looking up a questionable source."""
        db = SourceCredibilityDatabase(sample_db_file)
        
        result = db.lookup_source_credibility("dailymail.co.uk")
        
        assert result.domain == "dailymail.co.uk"
        assert result.credibilityScore == 0.45
        assert result.category == SourceCategory.QUESTIONABLE
    
    def test_lookup_unreliable_source(self, sample_db_file):
        """Test looking up an unreliable source."""
        db = SourceCredibilityDatabase(sample_db_file)
        
        result = db.lookup_source_credibility("infowars.com")
        
        assert result.domain == "infowars.com"
        assert result.credibilityScore == 0.1
        assert result.category == SourceCategory.UNRELIABLE
    
    def test_lookup_unknown_domain_returns_default(self, sample_db_file):
        """Test that unknown domains return default credibility score of 0.5."""
        db = SourceCredibilityDatabase(sample_db_file)
        
        result = db.lookup_source_credibility("unknown-news-site.com")
        
        assert result.domain == "unknown-news-site.com"
        assert result.credibilityScore == 0.5
        assert result.category == SourceCategory.MAINSTREAM  # 0.5 falls in MAINSTREAM range
    
    def test_extract_domain_from_url(self, sample_db_file):
        """Test extracting domain from full URL."""
        db = SourceCredibilityDatabase(sample_db_file)
        
        result = db.lookup_source_credibility("https://apnews.com/article/12345")
        
        assert result.domain == "apnews.com"
        assert result.credibilityScore == 0.95
    
    def test_extract_domain_removes_www(self, sample_db_file):
        """Test that www. prefix is removed from domains."""
        db = SourceCredibilityDatabase(sample_db_file)
        
        result = db.lookup_source_credibility("www.reuters.com")
        
        assert result.domain == "reuters.com"
        assert result.credibilityScore == 0.95
    
    def test_domain_case_insensitive(self, sample_db_file):
        """Test that domain lookup is case-insensitive."""
        db = SourceCredibilityDatabase(sample_db_file)
        
        result1 = db.lookup_source_credibility("CNN.COM")
        result2 = db.lookup_source_credibility("cnn.com")
        
        assert result1.domain == result2.domain == "cnn.com"
        assert result1.credibilityScore == result2.credibilityScore
    
    def test_category_mapping_trusted(self, sample_db_file):
        """Test category mapping for TRUSTED range (0.8-1.0)."""
        db = SourceCredibilityDatabase(sample_db_file)
        
        # Test boundary values
        assert db._determine_category(0.8) == SourceCategory.TRUSTED
        assert db._determine_category(0.9) == SourceCategory.TRUSTED
        assert db._determine_category(1.0) == SourceCategory.TRUSTED
    
    def test_category_mapping_mainstream(self, sample_db_file):
        """Test category mapping for MAINSTREAM range (0.5-0.79)."""
        db = SourceCredibilityDatabase(sample_db_file)
        
        assert db._determine_category(0.5) == SourceCategory.MAINSTREAM
        assert db._determine_category(0.65) == SourceCategory.MAINSTREAM
        assert db._determine_category(0.79) == SourceCategory.MAINSTREAM
    
    def test_category_mapping_questionable(self, sample_db_file):
        """Test category mapping for QUESTIONABLE range (0.3-0.49)."""
        db = SourceCredibilityDatabase(sample_db_file)
        
        assert db._determine_category(0.3) == SourceCategory.QUESTIONABLE
        assert db._determine_category(0.4) == SourceCategory.QUESTIONABLE
        assert db._determine_category(0.49) == SourceCategory.QUESTIONABLE
    
    def test_category_mapping_unreliable(self, sample_db_file):
        """Test category mapping for UNRELIABLE range (0.0-0.29)."""
        db = SourceCredibilityDatabase(sample_db_file)
        
        assert db._determine_category(0.0) == SourceCategory.UNRELIABLE
        assert db._determine_category(0.15) == SourceCategory.UNRELIABLE
        assert db._determine_category(0.29) == SourceCategory.UNRELIABLE
    
    def test_get_all_sources(self, sample_db_file):
        """Test getting all sources from database."""
        db = SourceCredibilityDatabase(sample_db_file)
        
        all_sources = db.get_all_sources()
        
        assert len(all_sources) == 6
        assert "apnews.com" in all_sources
        assert "infowars.com" in all_sources
    
    def test_get_sources_by_category(self, sample_db_file):
        """Test filtering sources by category."""
        db = SourceCredibilityDatabase(sample_db_file)
        
        trusted = db.get_sources_by_category(SourceCategory.TRUSTED)
        mainstream = db.get_sources_by_category(SourceCategory.MAINSTREAM)
        questionable = db.get_sources_by_category(SourceCategory.QUESTIONABLE)
        unreliable = db.get_sources_by_category(SourceCategory.UNRELIABLE)
        
        assert len(trusted) == 2  # apnews.com, reuters.com
        assert len(mainstream) == 2  # cnn.com, foxnews.com
        assert len(questionable) == 1  # dailymail.co.uk
        assert len(unreliable) == 1  # infowars.com
    
    def test_missing_database_file(self):
        """Test handling of missing database file."""
        db = SourceCredibilityDatabase("/nonexistent/path/db.json")
        
        # Should still work with empty database
        assert len(db.sources) == 0
        
        # Should return default for any lookup
        result = db.lookup_source_credibility("example.com")
        assert result.credibilityScore == 0.5


class TestGlobalFunctions:
    """Tests for global convenience functions."""
    
    def test_lookup_source_credibility_function(self):
        """Test the global lookup_source_credibility function."""
        # This uses the real database file
        result = lookup_source_credibility("apnews.com")
        
        assert isinstance(result, SourceCredibility)
        assert result.domain == "apnews.com"
        # Should be a trusted source in the real database
        assert result.credibilityScore >= 0.8
        assert result.category == SourceCategory.TRUSTED
    
    def test_lookup_unknown_domain_global(self):
        """Test global function with unknown domain."""
        result = lookup_source_credibility("totally-unknown-site-12345.com")
        
        assert result.credibilityScore == 0.5
        assert result.category == SourceCategory.MAINSTREAM


class TestSourceCredibilityModel:
    """Tests for SourceCredibility model validation."""
    
    def test_valid_source_credibility(self):
        """Test creating valid SourceCredibility object."""
        source = SourceCredibility(
            domain="example.com",
            credibilityScore=0.85,
            category=SourceCategory.TRUSTED
        )
        
        assert source.domain == "example.com"
        assert source.credibilityScore == 0.85
        assert source.category == SourceCategory.TRUSTED
    
    def test_category_score_mismatch_raises_error(self):
        """Test that mismatched category and score raises validation error."""
        with pytest.raises(ValueError, match="does not match score"):
            SourceCredibility(
                domain="example.com",
                credibilityScore=0.9,  # Should be TRUSTED
                category=SourceCategory.MAINSTREAM  # Wrong category
            )
    
    def test_score_out_of_range_raises_error(self):
        """Test that score outside [0, 1] raises validation error."""
        with pytest.raises(ValueError):
            SourceCredibility(
                domain="example.com",
                credibilityScore=1.5,  # Invalid
                category=SourceCategory.TRUSTED
            )
        
        with pytest.raises(ValueError):
            SourceCredibility(
                domain="example.com",
                credibilityScore=-0.1,  # Invalid
                category=SourceCategory.UNRELIABLE
            )
    
    def test_empty_domain_raises_error(self):
        """Test that empty domain raises validation error."""
        with pytest.raises(ValueError):
            SourceCredibility(
                domain="",
                credibilityScore=0.5,
                category=SourceCategory.MAINSTREAM
            )
    
    def test_domain_normalized_to_lowercase(self):
        """Test that domain is normalized to lowercase."""
        source = SourceCredibility(
            domain="EXAMPLE.COM",
            credibilityScore=0.7,
            category=SourceCategory.MAINSTREAM
        )
        
        assert source.domain == "example.com"
