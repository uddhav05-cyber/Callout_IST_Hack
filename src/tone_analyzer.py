"""
Tone Analysis Module for Emotional Manipulation Detection.

This module analyzes text for emotional manipulation, sensationalism, and objectivity.
It detects manipulative phrases and calculates various tone metrics.
"""

from typing import List
import re
import logging

from src.models import ToneScore

logger = logging.getLogger(__name__)


def detectManipulativePhrases(text: str) -> List[str]:
    """
    Detect manipulative phrases in text using keyword patterns.
    
    This function identifies common manipulative language patterns including:
    - Urgency phrases ("act now", "limited time")
    - Fear-mongering ("shocking", "terrifying")
    - Clickbait patterns ("you won't believe", "what happens next")
    - Absolute claims ("everyone knows", "nobody can deny")
    
    Args:
        text: The text to analyze for manipulative phrases.
    
    Returns:
        List of detected manipulative phrases found in the text.
    
    Preconditions:
        - text is non-null and non-empty
    
    Postconditions:
        - Returns list (may be empty if no phrases detected)
        - All returned phrases are present in the input text
    
    Requirements: 7.1, 7.2
    """
    assert text is not None and len(text.strip()) > 0, "Text must be non-empty"
    
    text_lower = text.lower()
    detected_phrases = []
    
    # Define manipulative phrase patterns
    manipulative_patterns = {
        # Urgency and scarcity
        "urgency": [
            "act now", "limited time", "hurry", "don't miss out", "last chance",
            "urgent", "immediately", "right now", "before it's too late"
        ],
        # Fear-mongering
        "fear": [
            "shocking", "terrifying", "horrifying", "devastating", "catastrophic",
            "alarming", "frightening", "scary", "dangerous", "threat"
        ],
        # Clickbait
        "clickbait": [
            "you won't believe", "what happens next", "will shock you",
            "this one trick", "doctors hate", "they don't want you to know",
            "the truth about", "secret", "revealed", "exposed"
        ],
        # Absolute claims
        "absolute": [
            "everyone knows", "nobody can deny", "always", "never",
            "all experts agree", "undeniable", "proven fact", "absolutely"
        ],
        # Emotional appeals
        "emotional": [
            "heartbreaking", "outrageous", "unbelievable", "incredible",
            "amazing", "stunning", "mind-blowing"
        ]
    }
    
    # Check for each pattern
    for category, phrases in manipulative_patterns.items():
        for phrase in phrases:
            if phrase in text_lower:
                # Find actual occurrence in original text (preserve case)
                pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                matches = pattern.findall(text)
                detected_phrases.extend(matches)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_phrases = []
    for phrase in detected_phrases:
        phrase_lower = phrase.lower()
        if phrase_lower not in seen:
            seen.add(phrase_lower)
            unique_phrases.append(phrase)
    
    logger.debug(f"Detected {len(unique_phrases)} manipulative phrases")
    return unique_phrases


def analyzeTone(text: str) -> ToneScore:
    """
    Analyze text tone for emotional intensity, sensationalism, and objectivity.
    
    This function calculates multiple tone metrics:
    - Emotional intensity: Density of emotional words in text
    - Sensationalism score: Presence of sensationalist language
    - Objectivity score: Inverse of sensationalism (1.0 - sensationalism)
    - Manipulative phrases: List of detected manipulative language
    
    Args:
        text: The text to analyze.
    
    Returns:
        ToneScore object with all calculated metrics.
    
    Preconditions:
        - text is non-null and non-empty
    
    Postconditions:
        - All scores are in range [0.0, 1.0]
        - objectivityScore = 1.0 - sensationalismScore
        - Returns valid ToneScore object
    
    Requirements: 7.1, 7.2, 7.4
    """
    assert text is not None and len(text.strip()) > 0, "Text must be non-empty"
    
    text_lower = text.lower()
    words = text_lower.split()
    word_count = len(words)
    
    if word_count == 0:
        # Empty text after splitting
        return ToneScore(
            emotionalIntensity=0.0,
            sensationalismScore=0.0,
            manipulativePhrases=[],
            objectivityScore=1.0
        )
    
    # Step 1: Calculate emotional intensity
    emotional_words = [
        # Strong emotions
        "love", "hate", "fear", "angry", "furious", "enraged", "terrified",
        "horrified", "shocked", "outraged", "disgusted", "thrilled", "ecstatic",
        # Moderate emotions
        "happy", "sad", "worried", "concerned", "excited", "disappointed",
        "frustrated", "annoyed", "pleased", "upset", "anxious", "nervous",
        # Emotional intensifiers
        "very", "extremely", "incredibly", "absolutely", "totally", "completely"
    ]
    
    emotional_word_count = sum(1 for word in words if word in emotional_words)
    emotional_intensity = min(emotional_word_count / word_count * 5.0, 1.0)
    
    # Step 2: Detect manipulative phrases
    manipulative_phrases = detectManipulativePhrases(text)
    
    # Step 3: Calculate sensationalism score
    sensationalist_indicators = [
        # Exaggeration
        "shocking", "unbelievable", "incredible", "amazing", "stunning",
        "mind-blowing", "explosive", "bombshell", "devastating",
        # Superlatives
        "best", "worst", "greatest", "most", "least", "biggest", "smallest",
        # Dramatic language
        "crisis", "disaster", "catastrophe", "emergency", "chaos", "panic"
    ]
    
    sensationalist_count = sum(1 for word in words if word in sensationalist_indicators)
    
    # Combine factors for sensationalism score
    phrase_factor = min(len(manipulative_phrases) / 10.0, 1.0)  # Cap at 10 phrases
    word_factor = min(sensationalist_count / word_count * 10.0, 1.0)
    
    # Weighted combination
    sensationalism_score = (phrase_factor * 0.6 + word_factor * 0.4)
    sensationalism_score = min(sensationalism_score, 1.0)
    
    # Step 4: Calculate objectivity score (inverse of sensationalism)
    objectivity_score = 1.0 - sensationalism_score
    
    # Create and return ToneScore
    tone_score = ToneScore(
        emotionalIntensity=emotional_intensity,
        sensationalismScore=sensationalism_score,
        manipulativePhrases=manipulative_phrases,
        objectivityScore=objectivity_score
    )
    
    logger.info(
        f"Tone analysis complete: emotional={emotional_intensity:.2f}, "
        f"sensationalism={sensationalism_score:.2f}, objectivity={objectivity_score:.2f}, "
        f"phrases={len(manipulative_phrases)}"
    )
    
    return tone_score


__all__ = ["detectManipulativePhrases", "analyzeTone"]
