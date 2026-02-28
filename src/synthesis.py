"""
Synthesis Module for Final Verdict Generation.

This module combines evidence verification, source credibility, and tone analysis
to generate a final verdict with confidence scores and explanations.
"""

from typing import List, Dict
from uuid import UUID
import logging

from src.models import (
    VerificationScore, ToneScore, FinalVerdict, EvidenceCard,
    VerdictType, Claim, Evidence, NLIResult, RelationshipLabel, ClaimVerdict,
    OverallVerdictType
)

logger = logging.getLogger(__name__)


def calculateFinalScore(
    verificationScores: List[VerificationScore],
    toneScore: ToneScore,
    sourceCredibility: float
) -> float:
    """
    Calculate final score combining evidence, credibility, and writing style.
    
    This function implements the weighted scoring algorithm:
    - 60% evidence match (percentage of TRUE claims)
    - 20% source credibility
    - 20% writing style (objectivity)
    
    Penalties are applied for:
    - Misleading claims: -20% per misleading claim
    - Majority false claims: -50% if more than half are false
    
    Args:
        verificationScores: List of verification scores for all claims
        toneScore: Tone analysis results
        sourceCredibility: Average source credibility score [0, 1]
    
    Returns:
        Final score in range [0, 100]
    
    Preconditions:
        - verificationScores is non-empty
        - toneScore is valid ToneScore object
        - sourceCredibility is in range [0, 1]
    
    Postconditions:
        - Returns score in range [0, 100]
        - Score reflects weighted combination
        - Penalties applied appropriately
    
    Requirements: 5.2, 5.9, 7.3
    """
    # Preconditions
    assert len(verificationScores) > 0, "verificationScores must not be empty"
    assert toneScore is not None, "toneScore must not be None"
    assert 0.0 <= sourceCredibility <= 1.0, "sourceCredibility must be in [0, 1]"
    
    # Step 1: Calculate evidence match score
    total_claims = len(verificationScores)
    true_count = sum(1 for v in verificationScores if v.verdict == VerdictType.TRUE)
    false_count = sum(1 for v in verificationScores if v.verdict == VerdictType.FALSE)
    misleading_count = sum(1 for v in verificationScores if v.verdict == VerdictType.MISLEADING)
    
    evidence_match_score = (true_count / total_claims) * 100
    
    # Step 2: Calculate writing style score
    writing_style_score = (1.0 - toneScore.sensationalismScore) * 100
    
    # Step 3: Apply weighted formula
    final_score = (
        0.6 * evidence_match_score +
        0.2 * sourceCredibility * 100 +
        0.2 * writing_style_score
    )
    
    # Step 4: Apply penalties
    if misleading_count > 0:
        penalty = (misleading_count / total_claims) * 20
        final_score = final_score - penalty
        logger.debug(f"Applied misleading penalty: -{penalty:.2f}")
    
    if false_count > total_claims / 2:
        final_score = final_score * 0.5
        logger.debug(f"Applied majority false penalty: 50% reduction")
    
    # Step 5: Clamp to valid range
    final_score = max(0.0, min(100.0, final_score))
    
    # Postcondition
    assert 0.0 <= final_score <= 100.0, "Final score must be in [0, 100]"
    
    logger.info(
        f"Final score calculated: {final_score:.2f} "
        f"(evidence={evidence_match_score:.2f}, credibility={sourceCredibility*100:.2f}, "
        f"style={writing_style_score:.2f}, true={true_count}, false={false_count}, "
        f"misleading={misleading_count})"
    )
    
    return final_score


__all__ = ["calculateFinalScore"]


def highlightDiscrepancies(claim: Claim, evidence: Evidence, nliResult: NLIResult) -> List[str]:
    """
    Identify specific discrepancies between claim and evidence.
    
    This function analyzes contradicting evidence to identify specific
    portions that contradict the claim. It uses simple keyword matching
    and negation detection.
    
    Args:
        claim: The claim being verified
        evidence: The evidence being compared
        nliResult: NLI result showing the relationship
    
    Returns:
        List of specific discrepancies found (may be empty)
    
    Requirements: 6.2, 6.3
    """
    discrepancies = []
    
    # Only look for discrepancies if evidence refutes the claim
    if nliResult.label != RelationshipLabel.REFUTES:
        return discrepancies
    
    claim_text = claim.text.lower()
    evidence_text = evidence.snippet.lower()
    
    # Look for negation patterns
    negation_patterns = [
        ("is", "is not"),
        ("was", "was not"),
        ("has", "has not"),
        ("have", "have not"),
        ("did", "did not"),
        ("does", "does not"),
        ("will", "will not"),
        ("can", "cannot"),
        ("true", "false"),
        ("yes", "no"),
        ("confirmed", "denied"),
        ("increased", "decreased"),
        ("rose", "fell")
    ]
    
    # Check for direct contradictions
    for positive, negative in negation_patterns:
        if positive in claim_text and negative in evidence_text:
            discrepancies.append(f"Claim states '{positive}' but evidence shows '{negative}'")
        elif negative in claim_text and positive in evidence_text:
            discrepancies.append(f"Claim states '{negative}' but evidence shows '{positive}'")
    
    # If no specific discrepancies found but it's a refutation, add generic message
    if not discrepancies:
        discrepancies.append("Evidence contradicts the claim")
    
    logger.debug(f"Found {len(discrepancies)} discrepancies for claim {claim.id}")
    return discrepancies


def createEvidenceCards(
    claims: List[Claim],
    evidence: Dict[UUID, List[Evidence]],
    nliResults: Dict[UUID, List[NLIResult]]
) -> List[EvidenceCard]:
    """
    Create evidence cards for all claims showing supporting/refuting evidence.
    
    This function generates visual evidence cards that pair each claim with
    its most relevant evidence. Each card shows:
    - The claim text
    - Evidence snippet
    - Source information
    - Relationship (SUPPORTS/REFUTES/NEUTRAL)
    - Highlighted discrepancies (for refuting evidence)
    
    Args:
        claims: List of all claims extracted from the article
        evidence: Dictionary mapping claimID to list of evidence
        nliResults: Dictionary mapping claimID to list of NLI results
    
    Returns:
        List of EvidenceCard objects (at least one per claim)
    
    Preconditions:
        - claims is non-empty
        - Every claim has at least one evidence item
        - Every claim has corresponding NLI results
    
    Postconditions:
        - Returns at least one card per claim
        - All cards have valid relationships
        - Refuting evidence has discrepancies highlighted
    
    Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
    """
    assert len(claims) > 0, "Claims list must not be empty"
    
    evidence_cards = []
    
    for claim in claims:
        claim_evidence = evidence.get(claim.id, [])
        claim_nli_results = nliResults.get(claim.id, [])
        
        # Ensure every claim has at least one evidence item
        if not claim_evidence or not claim_nli_results:
            logger.warning(f"Claim {claim.id} has no evidence or NLI results")
            continue
        
        # Create evidence-NLI pairs
        evidence_nli_pairs = []
        for ev in claim_evidence:
            # Find corresponding NLI result
            nli = next((n for n in claim_nli_results if n.evidenceID == ev.id), None)
            if nli:
                evidence_nli_pairs.append((ev, nli))
        
        if not evidence_nli_pairs:
            logger.warning(f"No matching evidence-NLI pairs for claim {claim.id}")
            continue
        
        # Sort by relationship priority: REFUTES > SUPPORTS > NEUTRAL
        # This ensures contradicting evidence is shown first
        relationship_priority = {
            RelationshipLabel.REFUTES: 0,
            RelationshipLabel.SUPPORTS: 1,
            RelationshipLabel.NEUTRAL: 2
        }
        evidence_nli_pairs.sort(key=lambda x: relationship_priority[x[1].label])
        
        # Create card for the most relevant evidence (first in sorted list)
        ev, nli = evidence_nli_pairs[0]
        
        # Extract source name from URL (domain)
        source_name = ev.sourceDomain if hasattr(ev, 'sourceDomain') else ev.sourceURL.split('/')[2]
        
        # Highlight discrepancies for refuting evidence
        discrepancies = highlightDiscrepancies(claim, ev, nli)
        
        card = EvidenceCard(
            claim=claim.text,
            evidenceSnippet=ev.snippet,
            sourceURL=ev.sourceURL,
            sourceName=source_name,
            relationship=nli.label,
            highlightedDiscrepancies=discrepancies
        )
        
        evidence_cards.append(card)
        logger.debug(f"Created evidence card for claim {claim.id} with {nli.label} relationship")
    
    # Log warning if we have fewer cards than expected
    if len(evidence_cards) < len(claims) * 0.9:
        logger.warning(
            f"Created only {len(evidence_cards)} evidence cards for {len(claims)} claims "
            f"({len(evidence_cards)/len(claims)*100:.1f}%). Some claims may lack evidence."
        )
    else:
        logger.info(f"Created {len(evidence_cards)} evidence cards for {len(claims)} claims")
    
    return evidence_cards


__all__ = ["calculateFinalScore", "createEvidenceCards", "highlightDiscrepancies"]


def generateExplanation(
    verificationScores: List[VerificationScore],
    claims: List[Claim],
    finalScore: float,
    overallVerdict: VerdictType
) -> str:
    """
    Generate a simple, non-technical explanation of the verification results.
    
    This function creates a user-friendly explanation that:
    - Explains the overall verdict
    - Provides claim-by-claim breakdown
    - Uses simple language without technical jargon
    - Explains why claims are marked TRUE, FALSE, or MISLEADING
    
    Args:
        verificationScores: List of verification scores for all claims
        claims: List of all claims
        finalScore: The calculated final score
        overallVerdict: The overall verdict for the article
    
    Returns:
        Human-readable explanation string
    
    Requirements: 9.1, 9.2, 9.3, 9.4, 9.5
    """
    explanation_parts = []
    
    # Overall verdict explanation
    if overallVerdict == VerdictType.TRUE:
        explanation_parts.append(
            f"This article appears to be largely accurate (confidence: {finalScore:.0f}%). "
            "Most of the factual claims are supported by credible evidence."
        )
    elif overallVerdict == VerdictType.FALSE:
        explanation_parts.append(
            f"This article contains significant inaccuracies (confidence: {finalScore:.0f}%). "
            "Many of the factual claims are contradicted by credible evidence."
        )
    elif overallVerdict == VerdictType.MISLEADING:
        explanation_parts.append(
            f"This article is misleading (confidence: {finalScore:.0f}%). "
            "It contains a mix of accurate and inaccurate information, "
            "or presents facts in a way that could mislead readers."
        )
    else:  # UNVERIFIED
        explanation_parts.append(
            f"We couldn't verify this article (confidence: {finalScore:.0f}%). "
            "There isn't enough reliable evidence available to confirm or deny the claims."
        )
    
    # Count verdicts
    true_count = sum(1 for v in verificationScores if v.verdict == VerdictType.TRUE)
    false_count = sum(1 for v in verificationScores if v.verdict == VerdictType.FALSE)
    misleading_count = sum(1 for v in verificationScores if v.verdict == VerdictType.MISLEADING)
    unverified_count = sum(1 for v in verificationScores if v.verdict == VerdictType.UNVERIFIED)
    total_claims = len(verificationScores)
    
    # Summary of claims
    explanation_parts.append(
        f"\n\nWe analyzed {total_claims} factual claim{'s' if total_claims != 1 else ''} "
        f"from this article:"
    )
    
    if true_count > 0:
        explanation_parts.append(
            f"- {true_count} claim{'s' if true_count != 1 else ''} "
            f"{'are' if true_count != 1 else 'is'} supported by evidence"
        )
    
    if false_count > 0:
        explanation_parts.append(
            f"- {false_count} claim{'s' if false_count != 1 else ''} "
            f"{'are' if false_count != 1 else 'is'} contradicted by evidence"
        )
    
    if misleading_count > 0:
        explanation_parts.append(
            f"- {misleading_count} claim{'s' if misleading_count != 1 else ''} "
            f"{'are' if misleading_count != 1 else 'is'} misleading or partially true"
        )
    
    if unverified_count > 0:
        explanation_parts.append(
            f"- {unverified_count} claim{'s' if unverified_count != 1 else ''} "
            f"could not be verified"
        )
    
    # Claim-by-claim breakdown
    explanation_parts.append("\n\nClaim-by-claim analysis:")
    
    # Create claim-score pairs
    claim_score_pairs = list(zip(claims, verificationScores))
    
    for i, (claim, score) in enumerate(claim_score_pairs, 1):
        claim_text = claim.text[:100] + "..." if len(claim.text) > 100 else claim.text
        
        if score.verdict == VerdictType.TRUE:
            explanation_parts.append(
                f"\n{i}. \"{claim_text}\"\n"
                f"   ✓ SUPPORTED: This claim is backed by {score.supportCount} credible source(s). "
                f"The evidence confirms this information."
            )
        elif score.verdict == VerdictType.FALSE:
            explanation_parts.append(
                f"\n{i}. \"{claim_text}\"\n"
                f"   ✗ FALSE: This claim is contradicted by {score.refuteCount} credible source(s). "
                f"The evidence shows this is not accurate."
            )
        elif score.verdict == VerdictType.MISLEADING:
            explanation_parts.append(
                f"\n{i}. \"{claim_text}\"\n"
                f"   ⚠ MISLEADING: This claim has conflicting evidence "
                f"({score.supportCount} supporting, {score.refuteCount} contradicting). "
                f"The truth is more nuanced than presented."
            )
        else:  # UNVERIFIED
            explanation_parts.append(
                f"\n{i}. \"{claim_text}\"\n"
                f"   ? UNVERIFIED: We couldn't find enough reliable evidence to verify this claim."
            )
    
    explanation = "".join(explanation_parts)
    logger.info(f"Generated explanation with {len(explanation)} characters")
    
    return explanation


__all__ = [
    "calculateFinalScore",
    "createEvidenceCards",
    "highlightDiscrepancies",
    "generateExplanation"
]


def generateVerdict(
    claims: List[Claim],
    verificationScores: List[VerificationScore],
    evidence: Dict[UUID, List[Evidence]],
    nliResults: Dict[UUID, List[NLIResult]],
    toneScore: ToneScore,
    sourceCredibility: float
) -> FinalVerdict:
    """
    Generate complete final verdict combining all analysis components.
    
    This is the main synthesis function that:
    1. Calculates the final score
    2. Determines the overall verdict
    3. Generates evidence cards
    4. Creates a human-readable explanation
    5. Calculates factual accuracy and emotional manipulation scores
    
    Args:
        claims: List of all claims extracted from the article
        verificationScores: List of verification scores for all claims
        evidence: Dictionary mapping claimID to list of evidence
        nliResults: Dictionary mapping claimID to list of NLI results
        toneScore: Tone analysis results
        sourceCredibility: Average source credibility score
    
    Returns:
        Complete FinalVerdict object with all components
    
    Preconditions:
        - claims and verificationScores have same length
        - All claims have corresponding verification scores
        - toneScore is valid
        - sourceCredibility is in [0, 1]
    
    Postconditions:
        - Returns valid FinalVerdict object
        - All scores are in valid ranges
        - Explanation is non-empty
        - Evidence cards exist for claims
    
    Requirements: 5.1, 5.2, 5.7, 7.3, 7.5
    """
    # Preconditions
    assert len(claims) == len(verificationScores), \
        "Claims and verification scores must have same length"
    assert toneScore is not None, "Tone score must not be None"
    assert 0.0 <= sourceCredibility <= 1.0, "Source credibility must be in [0, 1]"
    
    logger.info("Starting verdict synthesis...")
    
    # Step 1: Calculate final score
    final_score = calculateFinalScore(verificationScores, toneScore, sourceCredibility)
    
    # Step 2: Determine overall verdict based on score and patterns
    true_count = sum(1 for v in verificationScores if v.verdict == VerdictType.TRUE)
    false_count = sum(1 for v in verificationScores if v.verdict == VerdictType.FALSE)
    misleading_count = sum(1 for v in verificationScores if v.verdict == VerdictType.MISLEADING)
    total_claims = len(verificationScores)
    
    # Determine overall verdict with stricter logic
    # Priority: FALSE > MISLEADING > TRUE > UNVERIFIED
    
    # If majority of claims are FALSE, verdict is FALSE
    if false_count > total_claims * 0.4:  # More than 40% false
        overall_verdict = OverallVerdictType.LIKELY_FALSE
    # If score is very low, verdict is FALSE
    elif final_score < 40:
        overall_verdict = OverallVerdictType.LIKELY_FALSE
    # If significant misleading content, verdict is MISLEADING
    elif misleading_count > total_claims * 0.3:  # More than 30% misleading
        overall_verdict = OverallVerdictType.MISLEADING
    # If score is medium range, verdict is MISLEADING
    elif 40 <= final_score < 65:
        overall_verdict = OverallVerdictType.MISLEADING
    # If majority of claims are TRUE and score is high, verdict is TRUE
    elif true_count > total_claims * 0.6 and final_score >= 65:
        overall_verdict = OverallVerdictType.LIKELY_TRUE
    # Default to UNVERIFIED if unclear
    else:
        overall_verdict = OverallVerdictType.UNVERIFIED
    
    # Step 3: Calculate factual accuracy score (based on evidence match)
    factual_accuracy_score = (true_count / total_claims) * 100
    
    # Step 4: Calculate emotional manipulation score (from tone analysis)
    emotional_manipulation_score = toneScore.sensationalismScore * 100
    
    # Step 5: Generate evidence cards
    evidence_cards = createEvidenceCards(claims, evidence, nliResults)
    
    # Step 6: Create claim breakdown
    claim_breakdown = []
    for claim, score in zip(claims, verificationScores):
        # Get supporting and contradicting evidence for this claim
        claim_evidence = evidence.get(claim.id, [])
        claim_nli = nliResults.get(claim.id, [])
        
        supporting_evidence = []
        contradicting_evidence = []
        
        for ev in claim_evidence:
            nli = next((n for n in claim_nli if n.evidenceID == ev.id), None)
            if nli:
                if nli.label == RelationshipLabel.SUPPORTS:
                    supporting_evidence.append(ev)
                elif nli.label == RelationshipLabel.REFUTES:
                    contradicting_evidence.append(ev)
        
        claim_verdict = ClaimVerdict(
            claim=claim,
            verdict=score.verdict,
            confidence=score.confidenceScore,
            supportingEvidence=supporting_evidence,
            contradictingEvidence=contradicting_evidence
        )
        claim_breakdown.append(claim_verdict)
    
    # Step 7: Generate explanation
    explanation = generateExplanation(
        verificationScores,
        claims,
        final_score,
        overall_verdict
    )
    
    # Step 8: Create FinalVerdict object
    final_verdict = FinalVerdict(
        overallVerdict=overall_verdict,
        confidenceScore=final_score,
        factualAccuracyScore=factual_accuracy_score,
        emotionalManipulationScore=emotional_manipulation_score,
        claimBreakdown=claim_breakdown,
        evidenceCards=evidence_cards,
        explanation=explanation
    )
    
    # Postconditions
    assert 0.0 <= final_verdict.confidenceScore <= 100.0, \
        "Confidence score must be in [0, 100]"
    assert 0.0 <= final_verdict.factualAccuracyScore <= 100.0, \
        "Factual accuracy score must be in [0, 100]"
    assert 0.0 <= final_verdict.emotionalManipulationScore <= 100.0, \
        "Emotional manipulation score must be in [0, 100]"
    assert len(final_verdict.explanation) > 0, "Explanation must not be empty"
    
    logger.info(
        f"Verdict synthesis complete: {overall_verdict.value} "
        f"(confidence={final_score:.1f}, factual={factual_accuracy_score:.1f}, "
        f"manipulation={emotional_manipulation_score:.1f})"
    )
    
    return final_verdict


__all__ = [
    "calculateFinalScore",
    "createEvidenceCards",
    "highlightDiscrepancies",
    "generateExplanation",
    "generateVerdict"
]
