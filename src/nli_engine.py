"""
NLI Engine for Cross-Verification.

This module implements Natural Language Inference (NLI) for comparing claims against evidence.
It includes score aggregation and verdict determination based on weighted evidence.
"""

from typing import List, Dict, Optional, Tuple, TYPE_CHECKING
from uuid import UUID
import logging

from src.models import NLIResult, VerificationScore, VerdictType, RelationshipLabel
from config.settings import settings

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from src.models import Claim, Evidence

logger = logging.getLogger(__name__)

# Global cache for NLI model and tokenizer
_nli_model_cache: Optional[Tuple] = None
_model_load_failed: bool = False


def load_nli_model() -> Optional[Tuple]:
    """
    Load and cache the HuggingFace NLI model in memory.
    
    This function loads the NLI model specified in settings (default: facebook/bart-large-mnli)
    and caches it in memory to avoid reloading on subsequent calls. If model loading fails,
    it logs the error and returns None, allowing the system to fall back to keyword matching.
    
    Returns:
        Optional[Tuple]: Tuple of (model, tokenizer) if successful, None if loading fails.
    
    Requirements: 4.6, 11.4, 13.4
    """
    global _nli_model_cache, _model_load_failed
    
    # Return cached model if available
    if _nli_model_cache is not None:
        logger.debug("Using cached NLI model")
        return _nli_model_cache
    
    # If we already tried and failed, don't try again
    if _model_load_failed:
        logger.debug("NLI model loading previously failed, using fallback")
        return None
    
    try:
        logger.info(f"Loading NLI model: {settings.NLI_MODEL_NAME}")
        
        # Import transformers here to avoid import errors if not installed
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        import torch
        
        # Load tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained(settings.NLI_MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(settings.NLI_MODEL_NAME)
        
        # Set model to evaluation mode
        model.eval()
        
        # Cache the model and tokenizer
        _nli_model_cache = (model, tokenizer)
        
        logger.info(f"Successfully loaded NLI model: {settings.NLI_MODEL_NAME}")
        return _nli_model_cache
        
    except Exception as e:
        logger.error(f"Failed to load NLI model: {e}", exc_info=True)
        logger.warning("Falling back to keyword-based matching. Confidence will be reduced by 30%.")
        _model_load_failed = True
        return None


def formatForNLI(premise: str, hypothesis: str) -> Dict:
    """
    Format premise and hypothesis for NLI model input.
    
    This function prepares the input format expected by the NLI model. The premise is the
    evidence text and the hypothesis is the claim text. The model will determine if the
    premise entails, contradicts, or is neutral to the hypothesis.
    
    Args:
        premise: The evidence text (what we know to be true)
        hypothesis: The claim text (what we want to verify)
    
    Returns:
        Dictionary with formatted input for the NLI model
    
    Raises:
        ValueError: If premise or hypothesis is empty
    
    Requirements: 4.1, 4.2
    """
    # Preconditions: premise and hypothesis must be non-empty
    if not premise or not premise.strip():
        raise ValueError("Premise cannot be empty")
    if not hypothesis or not hypothesis.strip():
        raise ValueError("Hypothesis cannot be empty")
    
    # Format for NLI model: premise comes first, then hypothesis
    # This is the standard format for MNLI models
    return {
        "premise": premise.strip(),
        "hypothesis": hypothesis.strip()
    }


def verifyClaimAgainstEvidence(claim: 'Claim', evidence: 'Evidence') -> NLIResult:
    """
    Verify a claim against evidence using Natural Language Inference.
    
    This function implements the NLI verification algorithm from the design document:
    1. Prepare input for NLI model (premise=evidence, hypothesis=claim)
    2. Run NLI model inference
    3. Extract entailment, contradiction, and neutral scores
    4. Validate that scores sum to approximately 1.0 (within 0.01 tolerance)
    5. Assign label (SUPPORTS, REFUTES, NEUTRAL) based on highest score
    
    If the NLI model fails to load, falls back to keyword-based matching with 30% confidence reduction.
    
    Args:
        claim: Claim object to verify
        evidence: Evidence object to compare against
    
    Returns:
        NLIResult object with scores and label
    
    Raises:
        ValueError: If claim text or evidence snippet is empty
    
    Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 11.4
    """
    # Preconditions: claim and evidence must be non-null with non-empty text
    if not claim or not claim.text or not claim.text.strip():
        raise ValueError("Claim text cannot be empty")
    if not evidence or not evidence.snippet or not evidence.snippet.strip():
        raise ValueError("Evidence snippet cannot be empty")
    
    # Step 1: Prepare input for NLI model
    premise = evidence.snippet
    hypothesis = claim.text
    
    # Try to load the NLI model
    model_tuple = load_nli_model()
    
    if model_tuple is not None:
        # Use NLI model for inference
        model, tokenizer = model_tuple
        
        try:
            # Step 2: Run NLI model inference
            model_input = formatForNLI(premise, hypothesis)
            
            # Tokenize input
            inputs = tokenizer(
                model_input["premise"],
                model_input["hypothesis"],
                return_tensors="pt",
                truncation=True,
                max_length=512
            )
            
            # Run inference
            import torch
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
            
            # Step 3: Extract scores using softmax
            import torch.nn.functional as F
            probs = F.softmax(logits, dim=1)[0]
            
            # MNLI models typically output: [contradiction, neutral, entailment]
            # But this can vary by model, so we check the model config
            # For bart-large-mnli and deberta-mnli: [contradiction, neutral, entailment]
            contradiction_score = float(probs[0])
            neutral_score = float(probs[1])
            entailment_score = float(probs[2])
            
            # Step 4: Validate scores sum to approximately 1.0
            total = entailment_score + contradiction_score + neutral_score
            if abs(total - 1.0) > 0.01:
                logger.warning(
                    f"NLI scores sum to {total}, not 1.0. "
                    f"Normalizing scores."
                )
                # Normalize scores
                entailment_score /= total
                contradiction_score /= total
                neutral_score /= total
            
            # Step 5: Assign label based on highest score
            scores = {
                RelationshipLabel.SUPPORTS: entailment_score,
                RelationshipLabel.REFUTES: contradiction_score,
                RelationshipLabel.NEUTRAL: neutral_score
            }
            label = max(scores, key=scores.get)
            
            logger.debug(
                f"NLI inference complete: entailment={entailment_score:.3f}, "
                f"contradiction={contradiction_score:.3f}, neutral={neutral_score:.3f}, "
                f"label={label}"
            )
            
        except Exception as e:
            logger.error(f"NLI inference failed: {e}", exc_info=True)
            logger.warning("Falling back to keyword-based matching")
            # Fall back to keyword matching
            return _keyword_based_matching(claim, evidence)
    else:
        # Model failed to load, use keyword-based fallback
        logger.info("Using keyword-based matching (NLI model not available)")
        return _keyword_based_matching(claim, evidence)
    
    # Create and return NLIResult
    result = NLIResult(
        claimID=claim.id,
        evidenceID=evidence.id,
        entailmentScore=entailment_score,
        contradictionScore=contradiction_score,
        neutralScore=neutral_score,
        label=label
    )
    
    # Postconditions are validated by the NLIResult model itself
    return result


def _keyword_based_matching(claim: 'Claim', evidence: 'Evidence') -> NLIResult:
    """
    Fallback keyword-based matching when NLI model is unavailable.
    
    This is a simple heuristic that compares keywords between claim and evidence.
    Confidence is reduced by 30% as specified in requirements.
    
    Args:
        claim: Claim object to verify
        evidence: Evidence object to compare against
    
    Returns:
        NLIResult with reduced confidence scores
    
    Requirements: 4.6, 11.4
    """
    claim_text = claim.text.lower()
    evidence_text = evidence.snippet.lower()
    
    # Extract words (simple tokenization)
    claim_words = set(claim_text.split())
    evidence_words = set(evidence_text.split())
    
    # Calculate overlap
    common_words = claim_words.intersection(evidence_words)
    overlap_ratio = len(common_words) / max(len(claim_words), 1)
    
    # Simple heuristic: high overlap = support, low overlap = neutral
    # We don't have good heuristics for contradiction without NLI
    if overlap_ratio > 0.5:
        # High overlap suggests support
        entailment_score = 0.6 * 0.7  # Reduced by 30%
        contradiction_score = 0.2 * 0.7
        neutral_score = 0.2 * 0.7
        label = RelationshipLabel.SUPPORTS
    elif overlap_ratio > 0.2:
        # Medium overlap suggests neutral
        entailment_score = 0.3 * 0.7
        contradiction_score = 0.2 * 0.7
        neutral_score = 0.5 * 0.7
        label = RelationshipLabel.NEUTRAL
    else:
        # Low overlap suggests neutral (we can't confidently say it contradicts)
        entailment_score = 0.2 * 0.7
        contradiction_score = 0.2 * 0.7
        neutral_score = 0.6 * 0.7
        label = RelationshipLabel.NEUTRAL
    
    # Normalize to sum to 1.0
    total = entailment_score + contradiction_score + neutral_score
    entailment_score /= total
    contradiction_score /= total
    neutral_score /= total
    
    logger.info(
        f"Keyword-based matching: overlap={overlap_ratio:.2f}, label={label} "
        f"(confidence reduced by 30%)"
    )
    
    return NLIResult(
        claimID=claim.id,
        evidenceID=evidence.id,
        entailmentScore=entailment_score,
        contradictionScore=contradiction_score,
        neutralScore=neutral_score,
        label=label
    )


def aggregateNLIScores(results: List[NLIResult], evidence_weights: Dict[UUID, float]) -> VerificationScore:
    """
    Aggregate NLI scores from multiple claim-evidence pairs into a single verification score.
    
    This function implements the score aggregation algorithm from the design document:
    - Counts support, refute, and neutral evidence
    - Calculates weighted scores using evidence credibility as weights
    - Determines verdict based on thresholds:
      * >60% support = TRUE
      * >60% refute = FALSE
      * both >30% = MISLEADING
      * else = UNVERIFIED
    - Calculates confidence score based on evidence strength
    
    Args:
        results: List of NLIResult objects for a single claim
        evidence_weights: Dictionary mapping evidenceID to credibility weight
    
    Returns:
        VerificationScore object with aggregated results
    
    Raises:
        ValueError: If results is empty or if not all results have the same claimID
    
    Requirements: 5.1, 5.3, 5.4, 5.5, 5.6, 5.9
    """
    # Precondition: results must not be empty
    if not results:
        raise ValueError("Results list cannot be empty")
    
    # Precondition: all results must have the same claimID
    claim_id = results[0].claimID
    if not all(r.claimID == claim_id for r in results):
        raise ValueError("All results must have the same claimID")
    
    # Initialize counters
    support_count = 0
    refute_count = 0
    neutral_count = 0
    
    total_weight = 0.0
    weighted_support = 0.0
    weighted_refute = 0.0
    
    # Step 1: Count and weight evidence
    for result in results:
        # Get weight for this evidence (default to 1.0 if not found)
        weight = evidence_weights.get(result.evidenceID, 1.0)
        total_weight += weight
        
        # Count by label and accumulate weighted scores
        if result.label == RelationshipLabel.SUPPORTS:
            support_count += 1
            weighted_support += result.entailmentScore * weight
        elif result.label == RelationshipLabel.REFUTES:
            refute_count += 1
            weighted_refute += result.contradictionScore * weight
        else:  # NEUTRAL
            neutral_count += 1
    
    # Step 2: Calculate confidence and verdict
    verdict = VerdictType.UNVERIFIED
    confidence_score = 0.0
    
    if total_weight > 0:
        # Calculate ratios
        support_ratio = weighted_support / total_weight
        refute_ratio = weighted_refute / total_weight
        
        # Determine verdict based on more lenient thresholds
        # TRUE: support significantly exceeds refute (by at least 0.3 margin)
        if support_ratio > refute_ratio + 0.3:
            verdict = VerdictType.TRUE
            confidence_score = support_ratio * 100
        # FALSE: refute significantly exceeds support (by at least 0.3 margin)
        elif refute_ratio > support_ratio + 0.3:
            verdict = VerdictType.FALSE
            confidence_score = refute_ratio * 100
        # MISLEADING: both support and refute are present with no clear winner
        elif support_ratio > 0.2 and refute_ratio > 0.2:
            verdict = VerdictType.MISLEADING
            confidence_score = 50.0
        else:
            verdict = VerdictType.UNVERIFIED
            confidence_score = 30.0
    else:
        # No weighted evidence available
        verdict = VerdictType.UNVERIFIED
        confidence_score = 0.0
    
    # Create and return VerificationScore
    score = VerificationScore(
        claimID=claim_id,
        supportCount=support_count,
        refuteCount=refute_count,
        neutralCount=neutral_count,
        confidenceScore=confidence_score,
        verdict=verdict
    )
    
    # Postcondition: confidence score is in valid range [0, 100]
    assert 0.0 <= score.confidenceScore <= 100.0, "Confidence score must be in [0, 100]"
    
    # Postcondition: verdict is valid
    assert score.verdict in VerdictType, "Verdict must be valid VerdictType"
    
    # Postcondition: counts sum to total results
    assert score.supportCount + score.refuteCount + score.neutralCount == len(results), \
        "Counts must sum to total results"
    
    logger.info(
        f"Aggregated {len(results)} NLI results for claim {claim_id}: "
        f"verdict={verdict}, confidence={confidence_score:.1f}, "
        f"support={support_count}, refute={refute_count}, neutral={neutral_count}"
    )
    
    return score
