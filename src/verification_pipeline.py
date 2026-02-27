"""
Main Verification Pipeline for Fake News Detection.

This module orchestrates all components to verify articles end-to-end:
1. Parse article content
2. Extract claims
3. Retrieve evidence
4. Run NLI verification
5. Analyze tone
6. Synthesize final verdict
"""

from typing import Union, Dict, List
from uuid import UUID
import logging

from src.models import ArticleInput, FinalVerdict, Claim, Evidence, NLIResult
from src.article_parser import parseArticleFromURL, processTextInput
from src.llm_integration import extractClaims
from src.evidence_retrieval import searchEvidence
from src.source_credibility import lookup_source_credibility
from src.nli_engine import verifyClaimAgainstEvidence, aggregateNLIScores
from src.tone_analyzer import analyzeTone
from src.synthesis import generateVerdict

logger = logging.getLogger(__name__)


def verifyArticle(article_input: Union[str, ArticleInput]) -> FinalVerdict:
    """
    Main verification pipeline that orchestrates all components.
    
    This function implements the complete verification workflow:
    1. Parse article content from URL or text
    2. Extract atomic claims from the article
    3. Retrieve evidence for each claim (parallel processing)
    4. Run NLI verification for all claim-evidence pairs
    5. Analyze tone separately
    6. Synthesize final verdict
    
    Args:
        article_input: Either a URL string, text string, or ArticleInput object
    
    Returns:
        FinalVerdict object with complete analysis results
    
    Preconditions:
        - article_input is non-null and non-empty
        - If URL, must be accessible
        - If text, must be within length limits
    
    Postconditions:
        - Returns valid FinalVerdict object
        - All scores are in valid ranges
        - Explanation is non-empty
    
    Requirements: 1.1, 1.2, 2.1, 3.1, 4.1, 5.1, 7.1, 20.1, 20.2, 20.3
    """
    logger.info("=" * 80)
    logger.info("Starting article verification pipeline")
    logger.info("=" * 80)
    
    # Step 1: Parse article content
    logger.info("Step 1: Parsing article content...")
    
    if isinstance(article_input, str):
        # Determine if it's a URL or text
        if article_input.startswith(('http://', 'https://')):
            article_text = parseArticleFromURL(article_input)
            logger.info(f"Parsed article from URL: {len(article_text)} characters")
        else:
            article_text = processTextInput(article_input)
            logger.info(f"Processed text input: {len(article_text)} characters")
    elif isinstance(article_input, ArticleInput):
        if article_input.url:
            article_text = parseArticleFromURL(article_input.url)
            logger.info(f"Parsed article from URL: {len(article_text)} characters")
        else:
            article_text = processTextInput(article_input.text)
            logger.info(f"Processed text input: {len(article_text)} characters")
    else:
        raise ValueError("article_input must be a string or ArticleInput object")
    
    assert article_text and len(article_text.strip()) > 0, \
        "Article text must not be empty after parsing"
    
    # Step 2: Extract atomic claims
    logger.info("Step 2: Extracting claims...")
    claims = extractClaims(article_text)
    logger.info(f"Extracted {len(claims)} claims")
    
    if len(claims) == 0:
        logger.warning("No claims extracted - returning UNVERIFIED verdict")
        # Return UNVERIFIED verdict if no claims found
        from src.models import VerdictType, ToneScore
        tone_score = analyzeTone(article_text)
        return FinalVerdict(
            overallVerdict=VerdictType.UNVERIFIED,
            confidenceScore=0.0,
            factualAccuracyScore=0.0,
            emotionalManipulationScore=tone_score.sensationalismScore * 100,
            claimBreakdown=[],
            evidenceCards=[],
            explanation="No factual claims could be extracted from this article for verification."
        )
    
    # Step 3: Retrieve evidence for each claim
    logger.info("Step 3: Retrieving evidence for claims...")
    evidence_by_claim: Dict[UUID, List[Evidence]] = {}
    
    for i, claim in enumerate(claims, 1):
        logger.info(f"  Retrieving evidence for claim {i}/{len(claims)}: {claim.text[:50]}...")
        try:
            claim_evidence = searchEvidence(claim)
            evidence_by_claim[claim.id] = claim_evidence
            logger.info(f"  Found {len(claim_evidence)} evidence items")
        except Exception as e:
            logger.error(f"  Error retrieving evidence for claim {claim.id}: {e}")
            evidence_by_claim[claim.id] = []
    
    # Step 4: Run NLI verification for all claim-evidence pairs
    logger.info("Step 4: Running NLI verification...")
    nli_results_by_claim: Dict[UUID, List[NLIResult]] = {}
    
    for claim in claims:
        claim_evidence = evidence_by_claim.get(claim.id, [])
        if not claim_evidence:
            logger.warning(f"No evidence found for claim {claim.id}")
            nli_results_by_claim[claim.id] = []
            continue
        
        nli_results = []
        for evidence in claim_evidence:
            try:
                nli_result = verifyClaimAgainstEvidence(claim, evidence)
                nli_results.append(nli_result)
            except Exception as e:
                logger.error(f"Error in NLI verification: {e}")
                continue
        
        nli_results_by_claim[claim.id] = nli_results
        logger.info(f"  Completed NLI for claim {claim.id}: {len(nli_results)} results")
    
    # Aggregate NLI scores for each claim
    logger.info("Aggregating NLI scores...")
    verification_scores = []
    
    for claim in claims:
        nli_results = nli_results_by_claim.get(claim.id, [])
        if not nli_results:
            # No evidence or NLI results - mark as UNVERIFIED
            from src.models import VerificationScore, VerdictType
            score = VerificationScore(
                claimID=claim.id,
                supportCount=0,
                refuteCount=0,
                neutralCount=0,
                confidenceScore=0.0,
                verdict=VerdictType.UNVERIFIED
            )
            verification_scores.append(score)
            continue
        
        # Calculate evidence weights based on credibility
        evidence_weights = {}
        for evidence in evidence_by_claim[claim.id]:
            credibility = lookup_source_credibility(evidence.sourceDomain)
            evidence_weights[evidence.id] = credibility.credibilityScore
        
        # Aggregate scores
        score = aggregateNLIScores(nli_results, evidence_weights)
        verification_scores.append(score)
    
    logger.info(f"Aggregated scores for {len(verification_scores)} claims")
    
    # Step 5: Analyze tone
    logger.info("Step 5: Analyzing tone...")
    tone_score = analyzeTone(article_text)
    logger.info(
        f"Tone analysis complete: sensationalism={tone_score.sensationalismScore:.2f}, "
        f"objectivity={tone_score.objectivityScore:.2f}"
    )
    
    # Calculate average source credibility
    all_evidence = [ev for evidence_list in evidence_by_claim.values() for ev in evidence_list]
    if all_evidence:
        avg_credibility = sum(
            lookup_source_credibility(ev.sourceDomain).credibilityScore for ev in all_evidence
        ) / len(all_evidence)
    else:
        avg_credibility = 0.5  # Default neutral credibility
    
    logger.info(f"Average source credibility: {avg_credibility:.2f}")
    
    # Step 6: Synthesize final verdict
    logger.info("Step 6: Synthesizing final verdict...")
    final_verdict = generateVerdict(
        claims=claims,
        verificationScores=verification_scores,
        evidence=evidence_by_claim,
        nliResults=nli_results_by_claim,
        toneScore=tone_score,
        sourceCredibility=avg_credibility
    )
    
    logger.info("=" * 80)
    logger.info(f"Verification complete: {final_verdict.overallVerdict.value}")
    logger.info(f"Confidence: {final_verdict.confidenceScore:.1f}%")
    logger.info(f"Factual Accuracy: {final_verdict.factualAccuracyScore:.1f}%")
    logger.info(f"Emotional Manipulation: {final_verdict.emotionalManipulationScore:.1f}%")
    logger.info("=" * 80)
    
    # Postconditions
    assert final_verdict is not None, "Final verdict must not be None"
    assert 0.0 <= final_verdict.confidenceScore <= 100.0, \
        "Confidence score must be in [0, 100]"
    assert len(final_verdict.explanation) > 0, "Explanation must not be empty"
    
    return final_verdict


__all__ = ["verifyArticle"]
