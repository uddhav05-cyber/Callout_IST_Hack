"""
Source credibility lookup system for the Fake News Detection System.

This module provides functionality to load and query source credibility scores
from a JSON database. It categorizes sources as TRUSTED, MAINSTREAM, QUESTIONABLE,
or UNRELIABLE based on their credibility scores.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse

from src.models import SourceCredibility, SourceCategory

logger = logging.getLogger(__name__)


class SourceCredibilityDatabase:
    """Database for source credibility scores."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the source credibility database.
        
        Args:
            db_path: Path to the JSON database file. If None, uses default path.
        """
        if db_path is None:
            # Default path relative to project root
            db_path = Path(__file__).parent.parent / "data" / "source_credibility.json"
        
        self.db_path = Path(db_path)
        self.sources: Dict[str, dict] = {}
        self.default_score: float = 0.5
        self.last_updated: Optional[datetime] = None
        
        self._load_database()
    
    def _load_database(self) -> None:
        """Load the credibility database from JSON file."""
        try:
            if not self.db_path.exists():
                logger.warning(f"Credibility database not found at {self.db_path}")
                return
            
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.sources = data.get('sources', {})
            self.default_score = data.get('defaultCredibilityScore', 0.5)
            
            # Parse last updated timestamp
            last_updated_str = data.get('lastUpdated')
            if last_updated_str:
                self.last_updated = datetime.fromisoformat(last_updated_str.replace('Z', '+00:00'))
            
            logger.info(f"Loaded {len(self.sources)} sources from credibility database")
            
        except Exception as e:
            logger.error(f"Error loading credibility database: {e}")
            # Continue with empty database
    
    def _extract_domain(self, url_or_domain: str) -> str:
        """
        Extract domain from URL or return domain as-is.
        
        Args:
            url_or_domain: URL or domain string
            
        Returns:
            Normalized domain name (lowercase)
        """
        # If it looks like a URL, parse it
        if '://' in url_or_domain:
            parsed = urlparse(url_or_domain)
            domain = parsed.netloc
        else:
            domain = url_or_domain
        
        # Remove www. prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain.lower().strip()
    
    def _determine_category(self, score: float) -> SourceCategory:
        """
        Determine source category based on credibility score.
        
        Args:
            score: Credibility score (0.0 to 1.0)
            
        Returns:
            SourceCategory enum value
        """
        if 0.8 <= score <= 1.0:
            return SourceCategory.TRUSTED
        elif 0.5 <= score < 0.8:
            return SourceCategory.MAINSTREAM
        elif 0.3 <= score < 0.5:
            return SourceCategory.QUESTIONABLE
        else:  # 0.0 <= score < 0.3
            return SourceCategory.UNRELIABLE
    
    def lookup_source_credibility(self, domain: str) -> SourceCredibility:
        """
        Look up credibility information for a source domain.
        
        Args:
            domain: Domain name or URL to look up
            
        Returns:
            SourceCredibility object with score and category
        """
        # Extract and normalize domain
        normalized_domain = self._extract_domain(domain)
        
        # Look up in database
        source_data = self.sources.get(normalized_domain)
        
        if source_data:
            # Found in database
            score = source_data.get('credibilityScore', self.default_score)
            category_str = source_data.get('category', None)
            
            # Determine category from score if not provided
            if category_str:
                category = SourceCategory(category_str)
            else:
                category = self._determine_category(score)
            
            return SourceCredibility(
                domain=normalized_domain,
                credibilityScore=score,
                category=category,
                lastUpdated=self.last_updated or datetime.now()
            )
        else:
            # Not found - return default
            logger.debug(f"Domain '{normalized_domain}' not in database, using default score {self.default_score}")
            return SourceCredibility(
                domain=normalized_domain,
                credibilityScore=self.default_score,
                category=self._determine_category(self.default_score),
                lastUpdated=datetime.now()
            )
    
    def get_all_sources(self) -> Dict[str, dict]:
        """
        Get all sources in the database.
        
        Returns:
            Dictionary of all sources with their data
        """
        return self.sources.copy()
    
    def get_sources_by_category(self, category: SourceCategory) -> Dict[str, dict]:
        """
        Get all sources in a specific category.
        
        Args:
            category: SourceCategory to filter by
            
        Returns:
            Dictionary of sources in the specified category
        """
        return {
            domain: data
            for domain, data in self.sources.items()
            if data.get('category') == category.value
        }


# Global instance for easy access
_global_db: Optional[SourceCredibilityDatabase] = None


def get_credibility_database() -> SourceCredibilityDatabase:
    """
    Get the global source credibility database instance.
    
    Returns:
        SourceCredibilityDatabase instance
    """
    global _global_db
    if _global_db is None:
        _global_db = SourceCredibilityDatabase()
    return _global_db


def lookup_source_credibility(domain: str) -> SourceCredibility:
    """
    Look up credibility information for a source domain.
    
    This is a convenience function that uses the global database instance.
    
    Args:
        domain: Domain name or URL to look up
        
    Returns:
        SourceCredibility object with score and category
    """
    db = get_credibility_database()
    return db.lookup_source_credibility(domain)
