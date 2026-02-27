"""Unit tests for the article parser module."""

import pytest
from unittest.mock import Mock, patch
from src.article_parser import (
    parseArticleFromURL,
    processTextInput,
    InvalidURLError,
    SecurityError,
    TextInputError,
    _validate_url_format,
    _validate_url_security,
    _extract_article_text,
    _normalize_text,
    _sanitize_html,
    _validate_utf8_encoding,
)


def test_valid_http_url():
    """Test that valid HTTP URLs pass validation."""
    _validate_url_format("http://example.com/article")


def test_valid_https_url():
    """Test that valid HTTPS URLs pass validation."""
    _validate_url_format("https://example.com/article")


def test_empty_url_raises_error():
    """Test that empty URLs raise InvalidURLError."""
    with pytest.raises(InvalidURLError, match="URL cannot be empty"):
        _validate_url_format("")


def test_url_without_protocol_raises_error():
    """Test that URLs without protocol raise InvalidURLError."""
    with pytest.raises(InvalidURLError, match="must start with http"):
        _validate_url_format("example.com/article")


def test_localhost_blocked():
    """Test that localhost URLs are blocked."""
    with pytest.raises(SecurityError, match="localhost is not allowed"):
        _validate_url_security("http://localhost/article")


def test_private_ip_blocked():
    """Test that private IP URLs are blocked."""
    with pytest.raises(SecurityError, match="private IP"):
        _validate_url_security("http://192.168.1.1/article")


def test_normalize_multiple_spaces():
    """Test that multiple spaces are normalized to single space."""
    text = "This  has   multiple    spaces"
    normalized = _normalize_text(text)
    assert normalized == "This has multiple spaces"


@patch('src.article_parser.requests.Session')
def test_successful_parsing(mock_session_class):
    """Test successful article parsing from URL."""
    mock_response = Mock()
    mock_response.text = "<html><body><article><p>Test content</p></article></body></html>"
    mock_response.raise_for_status = Mock()
    
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session
    
    text = parseArticleFromURL("https://example.com/article")
    assert "Test content" in text


# Tests for text input handler (Task 5.2)

def test_process_text_input_valid():
    """Test processing valid text input."""
    text = "This is a valid news article about current events."
    result = processTextInput(text)
    assert result == text


def test_process_text_input_empty_raises_error():
    """Test that empty text input raises TextInputError."""
    with pytest.raises(TextInputError, match="cannot be empty"):
        processTextInput("")


def test_process_text_input_whitespace_only_raises_error():
    """Test that whitespace-only text input raises TextInputError."""
    with pytest.raises(TextInputError, match="cannot be empty"):
        processTextInput("   \n\t  ")


def test_process_text_input_exceeds_max_length():
    """Test that text exceeding max length raises TextInputError."""
    long_text = "a" * 50001
    with pytest.raises(TextInputError, match="exceeds maximum length"):
        processTextInput(long_text)


def test_process_text_input_custom_max_length():
    """Test text input with custom max length."""
    text = "a" * 100
    with pytest.raises(TextInputError, match="exceeds maximum length of 50"):
        processTextInput(text, max_length=50)


def test_process_text_input_at_max_length():
    """Test text input at exactly max length is accepted."""
    text = "a" * 50000
    result = processTextInput(text)
    assert len(result) == 50000


def test_sanitize_html_removes_tags():
    """Test that HTML tags are removed from text."""
    text = "<p>This is <b>bold</b> text</p>"
    result = _sanitize_html(text)
    assert result == "This is bold text"
    assert "<p>" not in result
    assert "<b>" not in result


def test_sanitize_html_removes_script_tags():
    """Test that script tags are completely removed."""
    text = "Safe text <script>alert('xss')</script> more text"
    result = _sanitize_html(text)
    assert "alert" not in result
    assert "script" not in result
    assert "Safe text" in result
    assert "more text" in result


def test_sanitize_html_removes_style_tags():
    """Test that style tags are completely removed."""
    text = "Text <style>body { color: red; }</style> more"
    result = _sanitize_html(text)
    assert "color" not in result
    assert "style" not in result
    assert "Text" in result
    assert "more" in result


def test_sanitize_html_complex_html():
    """Test sanitization of complex HTML structure."""
    text = """
    <html>
        <head><title>Title</title></head>
        <body>
            <h1>Heading</h1>
            <p>Paragraph with <a href="link">link</a></p>
            <script>malicious();</script>
        </body>
    </html>
    """
    result = _sanitize_html(text)
    assert "Heading" in result
    assert "Paragraph" in result
    assert "link" in result
    assert "malicious" not in result
    assert "<" not in result


def test_sanitize_html_empty_string():
    """Test sanitization of empty string."""
    result = _sanitize_html("")
    assert result == ""


def test_validate_utf8_encoding_valid():
    """Test UTF-8 validation with valid text."""
    text = "Hello world with émojis 🎉"
    result = _validate_utf8_encoding(text)
    assert result == text


def test_validate_utf8_encoding_bytes():
    """Test UTF-8 validation with bytes input."""
    text_bytes = "Hello world".encode('utf-8')
    result = _validate_utf8_encoding(text_bytes)
    assert result == "Hello world"


def test_validate_utf8_encoding_invalid_bytes():
    """Test UTF-8 validation with invalid bytes."""
    # Create invalid UTF-8 bytes
    invalid_bytes = b'\xff\xfe'
    with pytest.raises(TextInputError, match="Invalid UTF-8 encoding"):
        _validate_utf8_encoding(invalid_bytes)


def test_validate_utf8_encoding_empty():
    """Test UTF-8 validation with empty string."""
    result = _validate_utf8_encoding("")
    assert result == ""


def test_process_text_input_with_html():
    """Test processing text input containing HTML."""
    text = "<p>This is a <strong>news article</strong> with HTML.</p>"
    result = processTextInput(text)
    assert "news article" in result
    assert "<p>" not in result
    assert "<strong>" not in result


def test_process_text_input_with_script():
    """Test processing text input containing script tags."""
    text = "Article text <script>alert('xss')</script> continues here"
    result = processTextInput(text)
    assert "Article text" in result
    assert "continues here" in result
    assert "alert" not in result
    assert "script" not in result


def test_process_text_input_normalizes_whitespace():
    """Test that text input normalizes whitespace."""
    text = "This  has   multiple    spaces\n\nand\n\nnewlines"
    result = processTextInput(text)
    assert "  " not in result
    assert "\n\n" not in result


def test_process_text_input_only_html_raises_error():
    """Test that text with only HTML (no content) raises error."""
    text = "<script>code();</script><style>css</style>"
    with pytest.raises(TextInputError, match="no valid content after sanitization"):
        processTextInput(text)


def test_process_text_input_unicode_characters():
    """Test processing text with various Unicode characters."""
    text = "Article with émojis 🎉, Chinese 中文, Arabic العربية, and symbols ©®™"
    result = processTextInput(text)
    assert "émojis" in result
    assert "🎉" in result
    assert "中文" in result
    assert "العربية" in result
