"""
Article parser module for the Fake News Detection System.

This module provides functionality to fetch and parse article content from URLs
with robust error handling and security measures.
"""

import ipaddress
import re
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


class ArticleParserError(Exception):
    """Base exception for article parser errors."""
    pass


class InvalidURLError(ArticleParserError):
    """Raised when URL is invalid or inaccessible."""
    pass


class SecurityError(ArticleParserError):
    """Raised when URL fails security validation."""
    pass


class TextInputError(ArticleParserError):
    """Raised when text input validation fails."""
    pass


def _validate_url_format(url: str) -> None:
    """
    Validate URL format.
    
    Args:
        url: URL string to validate
        
    Raises:
        InvalidURLError: If URL format is invalid
    """
    if not url or not url.strip():
        raise InvalidURLError("URL cannot be empty")
    
    url = url.strip()
    
    # Check if URL starts with http:// or https://
    if not (url.startswith('http://') or url.startswith('https://')):
        raise InvalidURLError("URL must start with http:// or https://")
    
    # Parse URL to validate structure
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            raise InvalidURLError("URL must have a valid domain")
    except Exception as e:
        raise InvalidURLError(f"Invalid URL format: {str(e)}")


def _validate_url_security(url: str) -> None:
    """
    Validate URL for security concerns (block private IPs).
    
    Args:
        url: URL string to validate
        
    Raises:
        SecurityError: If URL points to private IP or localhost
    """
    parsed = urlparse(url)
    hostname = parsed.hostname
    
    if not hostname:
        raise SecurityError("URL must have a valid hostname")
    
    # Check for localhost
    if hostname.lower() in ['localhost', '127.0.0.1', '::1']:
        raise SecurityError("Access to localhost is not allowed")
    
    # Try to resolve hostname to IP and check if it's private
    try:
        # Check if hostname is already an IP address
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            raise SecurityError(f"Access to private IP addresses is not allowed: {hostname}")
    except ValueError:
        # Hostname is not an IP address, which is fine
        # We'll let requests handle DNS resolution
        # Note: In production, you might want to resolve DNS and check the IP
        pass


def _fetch_url_content(url: str, timeout: int = 10, max_redirects: int = 3) -> str:
    """
    Fetch content from URL with timeout and redirect limits.
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds (default: 10)
        max_redirects: Maximum number of redirects to follow (default: 3)
        
    Returns:
        Raw HTML content from the URL
        
    Raises:
        InvalidURLError: If URL is inaccessible or returns error
    """
    try:
        # Configure session with redirect limits
        session = requests.Session()
        session.max_redirects = max_redirects
        
        # Make request with timeout
        response = session.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (compatible; FakeNewsDetector/1.0)'
            }
        )
        
        # Check for HTTP errors
        response.raise_for_status()
        
        return response.text
        
    except requests.exceptions.Timeout:
        raise InvalidURLError(f"Request timed out after {timeout} seconds")
    except requests.exceptions.TooManyRedirects:
        raise InvalidURLError(f"Too many redirects (max: {max_redirects})")
    except requests.exceptions.HTTPError as e:
        raise InvalidURLError(f"HTTP error: {e.response.status_code} - {e.response.reason}")
    except requests.exceptions.ConnectionError:
        raise InvalidURLError("Failed to connect to URL - check your internet connection or the URL")
    except requests.exceptions.RequestException as e:
        raise InvalidURLError(f"Failed to fetch URL: {str(e)}")


def _extract_article_text(html_content: str) -> str:
    """
    Extract main article text from HTML content.
    
    Args:
        html_content: Raw HTML content
        
    Returns:
        Extracted and cleaned article text
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
        element.decompose()
    
    # Try to find main content areas (common article containers)
    article_selectors = [
        'article',
        '[role="main"]',
        '.article-content',
        '.post-content',
        '.entry-content',
        'main',
    ]
    
    article_text = ""
    for selector in article_selectors:
        elements = soup.select(selector)
        if elements:
            # Get text from the first matching element
            article_text = elements[0].get_text(separator=' ', strip=True)
            break
    
    # If no article container found, get all paragraph text
    if not article_text:
        paragraphs = soup.find_all('p')
        article_text = ' '.join(p.get_text(strip=True) for p in paragraphs)
    
    # If still no text, get all text from body
    if not article_text:
        body = soup.find('body')
        if body:
            article_text = body.get_text(separator=' ', strip=True)
        else:
            article_text = soup.get_text(separator=' ', strip=True)
    
    return article_text


def _normalize_text(text: str) -> str:
    """
    Normalize whitespace and handle UTF-8 encoding.
    
    Args:
        text: Text to normalize
        
    Returns:
        Normalized text
    """
    if not text:
        return ""
    
    # Ensure UTF-8 encoding
    if isinstance(text, bytes):
        text = text.decode('utf-8', errors='replace')
    
    # Normalize whitespace
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def parseArticleFromURL(url: str) -> str:
    """
    Parse article content from a URL.
    
    This function fetches content from the provided URL, validates it for security,
    extracts the main article text, and returns cleaned text suitable for claim extraction.
    
    Args:
        url: URL of the article to parse
        
    Returns:
        Cleaned article text with HTML tags stripped and whitespace normalized
        
    Raises:
        InvalidURLError: If URL is invalid, inaccessible, or returns an error
        SecurityError: If URL fails security validation (private IPs, localhost)
        
    Example:
        >>> text = parseArticleFromURL("https://example.com/article")
        >>> print(text[:100])
        This is the article content...
    """
    # Step 1: Validate URL format
    _validate_url_format(url)
    
    # Step 2: Validate URL security (block private IPs)
    _validate_url_security(url)
    
    # Step 3: Fetch content with timeout and redirect limits
    html_content = _fetch_url_content(url, timeout=10, max_redirects=3)
    
    # Step 4: Extract main article text
    article_text = _extract_article_text(html_content)
    
    # Step 5: Normalize whitespace and handle UTF-8 encoding
    normalized_text = _normalize_text(article_text)
    
    if not normalized_text:
        raise InvalidURLError("No article text could be extracted from the URL")
    
    return normalized_text


def _sanitize_html(text: str) -> str:
    """
    Sanitize HTML and script tags from text input.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Text with HTML and script tags removed
    """
    if not text:
        return ""
    
    # Use BeautifulSoup to parse and strip HTML tags
    soup = BeautifulSoup(text, 'html.parser')
    
    # Remove script and style tags completely
    for element in soup(['script', 'style']):
        element.decompose()
    
    # Get text content without HTML tags
    sanitized = soup.get_text(separator=' ')
    
    # Normalize whitespace after sanitization
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    return sanitized


def _validate_utf8_encoding(text: str) -> str:
    """
    Validate and ensure UTF-8 encoding for text input.
    
    Args:
        text: Text to validate
        
    Returns:
        UTF-8 encoded text
        
    Raises:
        TextInputError: If text cannot be properly encoded as UTF-8
    """
    if not text:
        return ""
    
    try:
        # If text is bytes, decode it
        if isinstance(text, bytes):
            text = text.decode('utf-8', errors='strict')
        
        # Ensure text can be encoded as UTF-8
        text.encode('utf-8')
        
        return text
    except UnicodeDecodeError as e:
        raise TextInputError(f"Invalid UTF-8 encoding: {str(e)}")
    except UnicodeEncodeError as e:
        raise TextInputError(f"Text contains characters that cannot be encoded as UTF-8: {str(e)}")


def processTextInput(text: str, max_length: int = 50000) -> str:
    """
    Process and validate direct text input.
    
    This function accepts direct text input, validates its length, sanitizes HTML
    and script tags, validates UTF-8 encoding, and returns cleaned text suitable
    for claim extraction.
    
    Args:
        text: Direct text input to process
        max_length: Maximum allowed text length in characters (default: 50,000)
        
    Returns:
        Cleaned and validated text
        
    Raises:
        TextInputError: If text validation fails (empty, too long, encoding issues)
        
    Example:
        >>> text = processTextInput("This is a news article about...")
        >>> print(len(text))
        42
    """
    # Step 1: Validate text is not empty
    if not text or not text.strip():
        raise TextInputError("Text input cannot be empty")
    
    # Step 2: Validate UTF-8 encoding
    text = _validate_utf8_encoding(text)
    
    # Step 3: Validate text length (before sanitization to prevent abuse)
    if len(text) > max_length:
        raise TextInputError(
            f"Text input exceeds maximum length of {max_length} characters "
            f"(provided: {len(text)} characters)"
        )
    
    # Step 4: Sanitize HTML and script tags
    sanitized_text = _sanitize_html(text)
    
    # Step 5: Normalize whitespace
    normalized_text = _normalize_text(sanitized_text)
    
    # Step 6: Validate that sanitization didn't remove all content
    if not normalized_text:
        raise TextInputError("Text input contains no valid content after sanitization")
    
    return normalized_text

