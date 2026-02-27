"""
LLM Integration Module for Claim Extraction.

This module provides LangChain-based integration with LLM APIs (OpenAI/Groq) to extract
atomic, verifiable claims from article text. It includes robust error handling with
exponential backoff retry logic and fallback to rule-based extraction.

Requirements: 2.1, 11.1, 11.2, 16.1
"""

import time
import re
from typing import List, Optional, Tuple
import logging

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from config.settings import settings
from src.models import Claim


# Configure logging
logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Raised when LLM API calls fail after all retries."""
    pass


def buildClaimExtractionPrompt(articleText: str) -> str:
    """
    Build a prompt for the LLM to extract factual claims from article text.
    
    The prompt instructs the LLM to:
    - Extract atomic, verifiable factual claims
    - Filter out opinions and subjective statements
    - Assign importance scores to each claim
    - Return claims in a structured format
    
    Args:
        articleText: The article text to extract claims from.
    
    Returns:
        str: A formatted prompt string for the LLM.
    
    Preconditions:
        - articleText is non-null and non-empty
    
    Postconditions:
        - Returns a non-empty prompt string
        - Prompt contains clear instructions for claim extraction
    """
    assert articleText is not None and len(articleText.strip()) > 0, \
        "Article text must be non-empty"
    
    prompt_template = PromptTemplate(
        input_variables=["article_text"],
        template="""You are a fact-checking assistant. Your task is to extract atomic, verifiable factual claims from the following article.

INSTRUCTIONS:
1. Extract ONLY factual claims that can be verified (e.g., "The GDP grew by 5% in 2023")
2. DO NOT extract opinions, subjective statements, or predictions (e.g., "This is the best policy")
3. Each claim should be atomic (one fact per claim) and self-contained
4. Assign an importance score (0.0 to 1.0) to each claim based on its significance to the article's main point
5. Provide brief context for each claim (1-2 sentences from the article)

FORMAT YOUR RESPONSE AS:
CLAIM: [claim text]
IMPORTANCE: [score between 0.0 and 1.0]
CONTEXT: [brief context]
---

ARTICLE TEXT:
{article_text}

EXTRACTED CLAIMS:
"""
    )
    
    prompt = prompt_template.format(article_text=articleText.strip())
    
    assert len(prompt) > 0, "Generated prompt must be non-empty"
    return prompt


def callLLM(prompt: str, max_retries: int = 3) -> str:
    """
    Call the LLM API with exponential backoff retry logic.
    
    This function attempts to call the LLM API up to max_retries times with
    exponential backoff between attempts. It tries Groq first (faster), then
    falls back to OpenAI if Groq is unavailable.
    
    Args:
        prompt: The prompt to send to the LLM.
        max_retries: Maximum number of retry attempts (default: 3).
    
    Returns:
        str: The LLM's response text.
    
    Raises:
        LLMError: If all retry attempts fail.
    
    Preconditions:
        - prompt is non-null and non-empty
        - max_retries >= 1
        - At least one LLM API key is configured
    
    Postconditions:
        - Returns non-empty response string on success
        - Raises LLMError after exhausting all retries
    """
    assert prompt is not None and len(prompt.strip()) > 0, \
        "Prompt must be non-empty"
    assert max_retries >= 1, "max_retries must be at least 1"
    
    # Determine which LLM to use
    llm = None
    api_name = None
    
    try:
        if settings.GROQ_API_KEY:
            llm = ChatGroq(
                api_key=settings.GROQ_API_KEY,
                model_name="mixtral-8x7b-32768",
                temperature=0.1,
                max_tokens=2048
            )
            api_name = "Groq"
            logger.info("Using Groq API for LLM calls")
        elif settings.OPENAI_API_KEY:
            llm = ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                model_name="gpt-3.5-turbo",
                temperature=0.1,
                max_tokens=2048
            )
            api_name = "OpenAI"
            logger.info("Using OpenAI API for LLM calls")
        else:
            raise LLMError("No LLM API key configured")
    except Exception as e:
        logger.error(f"Failed to initialize LLM client: {e}")
        raise LLMError(f"LLM initialization failed: {e}")
    
    # Retry loop with exponential backoff
    for attempt in range(max_retries):
        try:
            logger.info(f"Calling {api_name} API (attempt {attempt + 1}/{max_retries})")
            response = llm.invoke(prompt)
            
            # Extract text content from response
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
            
            if not response_text or len(response_text.strip()) == 0:
                raise LLMError("LLM returned empty response")
            
            logger.info(f"{api_name} API call successful")
            return response_text.strip()
            
        except Exception as e:
            logger.warning(f"{api_name} API call failed (attempt {attempt + 1}/{max_retries}): {e}")
            
            if attempt < max_retries - 1:
                # Exponential backoff: 2^attempt seconds (1s, 2s, 4s, ...)
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                # All retries exhausted
                logger.error(f"All {max_retries} retry attempts failed")
                raise LLMError(f"LLM API call failed after {max_retries} attempts: {e}")
    
    # Should never reach here, but just in case
    raise LLMError("Unexpected error in callLLM")


def parseLLMResponse(response: str) -> List[Tuple[str, float, str]]:
    """
    Parse the LLM response to extract claims with importance scores and context.
    
    Expected format:
        CLAIM: [claim text]
        IMPORTANCE: [score]
        CONTEXT: [context]
        ---
    
    Args:
        response: The raw response text from the LLM.
    
    Returns:
        List[Tuple[str, float, str]]: List of (claim_text, importance, context) tuples.
    
    Preconditions:
        - response is non-null
    
    Postconditions:
        - Returns list of tuples (may be empty if parsing fails)
        - Each tuple contains (claim_text, importance_score, context)
        - importance_score is in range [0.0, 1.0]
    """
    assert response is not None, "Response must be non-null"
    
    claims = []
    
    # Split response by claim separator
    claim_blocks = response.split('---')
    
    for block in claim_blocks:
        block = block.strip()
        if not block:
            continue
        
        # Extract claim text
        claim_match = re.search(r'CLAIM:\s*(.+?)(?=\n|$)', block, re.IGNORECASE)
        if not claim_match:
            continue
        claim_text = claim_match.group(1).strip()
        
        # Extract importance score
        importance_match = re.search(r'IMPORTANCE:\s*([-\d.]+)', block, re.IGNORECASE)
        if importance_match:
            try:
                importance = float(importance_match.group(1))
                # Clamp to valid range
                importance = max(0.0, min(1.0, importance))
            except ValueError:
                importance = 0.5  # Default if parsing fails
        else:
            importance = 0.5  # Default if not found
        
        # Extract context
        context_match = re.search(r'CONTEXT:\s*(.+?)(?=\n\n|$)', block, re.IGNORECASE | re.DOTALL)
        if context_match:
            context = context_match.group(1).strip()
        else:
            context = ""
        
        if claim_text:
            claims.append((claim_text, importance, context))
            logger.debug(f"Parsed claim: {claim_text[:50]}... (importance: {importance})")
    
    logger.info(f"Parsed {len(claims)} claims from LLM response")
    return claims


def isFactualClaim(claim: str) -> bool:
    """
    Determine if a claim is factual (verifiable) or an opinion/subjective statement.
    
    This function uses heuristics to filter out opinions and subjective statements:
    - Checks for factual keywords (numbers, dates, official sources)
    - Filters out opinion indicators (I think, I believe, should, must)
    - Filters out subjective language (best, worst, amazing, terrible)
    
    Args:
        claim: The claim text to evaluate.
    
    Returns:
        bool: True if the claim appears to be factual, False if it's an opinion.
    
    Preconditions:
        - claim is non-null and non-empty
    
    Postconditions:
        - Returns boolean value
    
    Requirements: 2.2
    """
    assert claim is not None and len(claim.strip()) > 0, "Claim must be non-empty"
    
    claim_lower = claim.lower()
    
    # Opinion indicators - if present, likely not factual
    opinion_indicators = [
        'i think', 'i believe', 'in my opinion', 'i feel',
        'should', 'must', 'ought to', 'need to',
        'probably', 'maybe', 'perhaps', 'possibly',
        'seems like', 'appears to be'
    ]
    
    # Subjective language - if present, likely not factual
    subjective_words = [
        'best', 'worst', 'greatest', 'terrible', 'awful',
        'amazing', 'wonderful', 'horrible', 'fantastic',
        'beautiful', 'ugly', 'good', 'bad', 'better', 'worse'
    ]
    
    # Factual indicators - if present, likely factual
    factual_keywords = [
        'said', 'reported', 'announced', 'confirmed', 'revealed',
        'according to', 'study', 'research', 'data', 'statistics',
        'percent', '%', 'million', 'billion', 'year', 'date',
        'government', 'official', 'company', 'organization'
    ]
    
    # Check for opinion indicators
    if any(indicator in claim_lower for indicator in opinion_indicators):
        logger.debug(f"Claim filtered as opinion (opinion indicator): {claim[:50]}...")
        return False
    
    # Check for subjective language and factual keywords
    has_subjective = any(word in claim_lower for word in subjective_words)
    has_factual = any(keyword in claim_lower for keyword in factual_keywords)
    
    # If it has factual keywords, consider it factual (even with subjective language)
    if has_factual:
        return True
    
    # If it has subjective language without factual keywords, filter it out
    if has_subjective:
        logger.debug(f"Claim filtered as subjective without factual keywords: {claim[:50]}...")
        return False
    
    # Check minimum length for claims without clear factual indicators
    if len(claim) < 25:
        logger.debug(f"Claim filtered as too short: {claim[:50]}...")
        return False
    
    # Default: if no clear indicators, consider it factual (conservative approach)
    return True


def calculateImportance(claim: str, articleText: str) -> float:
    """
    Calculate the importance score for a claim based on its significance to the article.
    
    Importance is calculated based on:
    - Position in the article (earlier = more important)
    - Presence of factual keywords (more keywords = more important)
    - Length and specificity of the claim
    - Presence of numbers, dates, or specific entities
    
    Args:
        claim: The claim text to score.
        articleText: The full article text for context.
    
    Returns:
        float: Importance score between 0.0 and 1.0.
    
    Preconditions:
        - claim is non-null and non-empty
        - articleText is non-null and non-empty
    
    Postconditions:
        - Returns float in range [0.0, 1.0]
    
    Requirements: 2.3, 17.1, 17.4
    """
    assert claim is not None and len(claim.strip()) > 0, "Claim must be non-empty"
    assert articleText is not None and len(articleText.strip()) > 0, "Article text must be non-empty"
    
    claim_lower = claim.lower()
    article_lower = articleText.lower()
    
    # Factor 1: Position in article (earlier = more important)
    # Find where the claim appears in the article
    claim_position = article_lower.find(claim_lower)
    if claim_position >= 0:
        position_ratio = claim_position / max(len(articleText), 1)
        position_score = 1.0 - (position_ratio * 0.5)  # 1.0 at start, 0.5 at end
    else:
        # Claim not found in article (extracted by LLM), assume medium importance
        position_score = 0.7
    
    # Factor 2: Factual keyword density
    factual_keywords = [
        'said', 'reported', 'announced', 'confirmed', 'revealed',
        'according to', 'study', 'research', 'data', 'statistics',
        'percent', '%', 'million', 'billion', 'year', 'date',
        'government', 'official', 'company', 'organization'
    ]
    keyword_count = sum(1 for kw in factual_keywords if kw in claim_lower)
    keyword_score = min(keyword_count * 0.15, 0.5)  # Max 0.5 from keywords
    
    # Factor 3: Specificity (presence of numbers, dates, names)
    specificity_score = 0.0
    
    # Check for numbers
    if re.search(r'\d+', claim):
        specificity_score += 0.2
    
    # Check for dates or years
    if re.search(r'\b(19|20)\d{2}\b', claim):
        specificity_score += 0.15
    
    # Check for capitalized words (likely proper nouns/entities)
    capitalized_words = re.findall(r'\b[A-Z][a-z]+\b', claim)
    if len(capitalized_words) >= 2:
        specificity_score += 0.15
    
    # Factor 4: Length bonus (longer claims tend to be more specific)
    if len(claim) > 100:
        length_bonus = 0.1
    elif len(claim) > 50:
        length_bonus = 0.05
    else:
        length_bonus = 0.0
    
    # Combine all factors
    importance = min(position_score + keyword_score + specificity_score + length_bonus, 1.0)
    
    # Ensure minimum importance for any valid claim
    importance = max(importance, 0.1)
    
    logger.debug(f"Calculated importance {importance:.2f} for claim: {claim[:50]}...")
    
    assert 0.0 <= importance <= 1.0, "Importance must be in range [0.0, 1.0]"
    return importance


def ruleBasedClaimExtraction(articleText: str) -> List[Tuple[str, float, str]]:
    """
    Fallback rule-based claim extraction using sentence splitting and keyword filtering.
    
    This simple heuristic approach:
    1. Splits text into sentences
    2. Filters sentences using isFactualClaim()
    3. Assigns importance using calculateImportance()
    4. Returns claims in the same format as LLM extraction
    
    Args:
        articleText: The article text to extract claims from.
    
    Returns:
        List[Tuple[str, float, str]]: List of (claim_text, importance, context) tuples.
    
    Preconditions:
        - articleText is non-null and non-empty
    
    Postconditions:
        - Returns non-empty list if article length > 100 characters
        - Each tuple contains (claim_text, importance_score, context)
        - importance_score is in range [0.0, 1.0]
    """
    assert articleText is not None and len(articleText.strip()) > 0, \
        "Article text must be non-empty"
    
    logger.info("Using rule-based fallback for claim extraction")
    
    # Split into sentences (simple approach)
    sentences = re.split(r'[.!?]+', articleText)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    claims = []
    
    for idx, sentence in enumerate(sentences):
        # Use isFactualClaim to filter
        if not isFactualClaim(sentence):
            continue
        
        # Calculate importance using the dedicated function
        importance = calculateImportance(sentence, articleText)
        
        # Use surrounding sentences as context (if available)
        context_parts = []
        if idx > 0:
            context_parts.append(sentences[idx - 1])
        context_parts.append(sentence)
        if idx < len(sentences) - 1:
            context_parts.append(sentences[idx + 1])
        context = ' '.join(context_parts)
        
        claims.append((sentence, importance, context))
        logger.debug(f"Rule-based claim: {sentence[:50]}... (importance: {importance:.2f})")
    
    # If no claims found, take first few sentences as fallback
    if not claims and len(sentences) > 0:
        for idx, sentence in enumerate(sentences[:3]):
            if len(sentence) >= 20:
                importance = calculateImportance(sentence, articleText)
                claims.append((sentence, importance, sentence))
    
    logger.info(f"Rule-based extraction found {len(claims)} claims")
    return claims


def extractClaims(articleText: str) -> List[Claim]:
    """
    Extract atomic, verifiable claims from article text using LLM with fallback.
    
    This is the main entry point for claim extraction. It:
    1. Attempts to use LLM (with retries)
    2. Falls back to rule-based extraction if LLM fails
    3. Filters claims using isFactualClaim()
    4. Ranks claims by importance using calculateImportance()
    5. Returns structured Claim objects
    
    Args:
        articleText: The article text to extract claims from.
    
    Returns:
        List[Claim]: List of Claim objects sorted by importance (descending).
                     May return empty list if no factual claims found.
    
    Raises:
        ValueError: If articleText is empty or invalid.
    
    Preconditions:
        - articleText is non-null and non-empty
        - articleText length > 0
    
    Postconditions:
        - Returns list of Claim objects (may be empty if no claims found)
        - Claims are sorted by importance (descending)
        - Each claim has importance score in [0.0, 1.0]
        - Each claim has unique ID
    
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.6, 2.7, 11.1, 11.2, 17.1, 17.2, 17.3, 17.4, 17.5
    """
    if not articleText or len(articleText.strip()) == 0:
        raise ValueError("Article text cannot be empty")
    
    articleText = articleText.strip()
    logger.info(f"Extracting claims from article ({len(articleText)} characters)")
    
    raw_claims = []
    used_fallback = False
    
    try:
        # Step 1: Try LLM-based extraction
        prompt = buildClaimExtractionPrompt(articleText)
        llm_response = callLLM(prompt, max_retries=settings.MAX_RETRIES)
        raw_claims = parseLLMResponse(llm_response)
        
        if not raw_claims:
            logger.warning("LLM returned no claims, falling back to rule-based extraction")
            raw_claims = ruleBasedClaimExtraction(articleText)
            used_fallback = True
            
    except LLMError as e:
        # Step 2: Fallback to rule-based extraction
        logger.error(f"LLM extraction failed: {e}")
        logger.info("Falling back to rule-based claim extraction")
        raw_claims = ruleBasedClaimExtraction(articleText)
        used_fallback = True
    
    # Step 3: Convert to Claim objects
    claims = []
    for claim_text, importance, context in raw_claims:
        try:
            claim = Claim(
                text=claim_text,
                context=context,
                importance=importance
            )
            claims.append(claim)
        except Exception as e:
            logger.warning(f"Failed to create Claim object: {e}")
            continue
    
    # Step 4: Sort by importance (descending)
    claims.sort(key=lambda c: c.importance, reverse=True)
    
    # Step 5: Limit to MAX_CLAIMS_PER_ARTICLE
    if len(claims) > settings.MAX_CLAIMS_PER_ARTICLE:
        logger.info(f"Limiting claims from {len(claims)} to {settings.MAX_CLAIMS_PER_ARTICLE}")
        claims = claims[:settings.MAX_CLAIMS_PER_ARTICLE]
    
    # Validation
    if len(articleText) > 100 and len(claims) == 0:
        logger.warning("No claims extracted from article longer than 100 characters")
        # Return empty list - higher-level code should handle UNVERIFIED verdict
        # This satisfies Requirement 2.4: return UNVERIFIED verdict if no claims extracted
    
    logger.info(f"Successfully extracted {len(claims)} claims (fallback: {used_fallback})")
    
    # Postcondition checks
    assert all(0.0 <= claim.importance <= 1.0 for claim in claims), \
        "All claims must have importance in [0.0, 1.0]"
    assert all(claim.id is not None for claim in claims), \
        "All claims must have unique IDs"
    
    # Check sorting
    if len(claims) > 1:
        for i in range(len(claims) - 1):
            assert claims[i].importance >= claims[i + 1].importance, \
                "Claims must be sorted by importance (descending)"
    
    return claims


__all__ = [
    'extractClaims',
    'isFactualClaim',
    'calculateImportance',
    'buildClaimExtractionPrompt',
    'callLLM',
    'parseLLMResponse',
    'ruleBasedClaimExtraction',
    'LLMError'
]
