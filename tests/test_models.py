"""
Unit tests for data models.

Tests validation rules and constraints for all Pydantic models.
"""

import pytest
from datetime import datetime
from uuid import uuid4
from pydantic import ValidationError

from src.models import (
    Claim, Evidence, NLIResult, VerificationScore, ToneScore,
    EvidenceCard, ClaimVerdict, FinalVerdict, ArticleInput,
    SourceCredibility, ImageMatch, ManipulationReport,
    PropagationNode, ChainOfCustody,
    InputType, RelationshipLabel, VerdictType, OverallVerdictType,
    SourceCategory, ManipulationType
)


class TestClaim:
    """Tests for Claim model."""
    
    def test_valid_claim(self):
        """Test creating a valid claim."""
        claim = Claim(text="The sky is blue", context="Weather discussion", importance=0.8)
        assert claim.text == "The sky is blue"
        assert claim.context == "Weather discussion"
        assert claim.importance == 0.8
        assert claim.id is not None
    
    def test_claim_text_stripped(self):
        """Test that claim text is stripped of whitespace."""
        claim = Claim(text="  Test claim  ", importance=0.5)
        assert claim.text == "Test claim"
    
    def test_claim_empty_text_fails(self):
        """Test that empty claim text raises validation error."""
        with pytest.raises(ValidationError):
            Claim(text="", importance=0.5)
    
    def test_claim_whitespace_only_fails(self):
        """Test that whitespace-only claim text raises validation error."""
        with pytest.raises(ValueError, match="Claim text cannot be empty"):
            Claim(text="   ", importance=0.5)
    
    def test_claim_importance_bounds(self):
        """Test that importance score is bounded between 0 and 1."""
        # Valid bounds
        Claim(text="Test", importance=0.0)
        Claim(text="Test", importance=1.0)
        Claim(text="Test", importance=0.5)
        
        # Invalid bounds
        with pytest.raises(ValueError):
            Claim(text="Test", importance=-0.1)
        with pytest.raises(ValueError):
            Claim(text="Test", importance=1.1)


class TestEvidence:
    """Tests for Evidence model."""
    
    def test_valid_evidence(self):
        """Test creating valid evidence."""
        evidence = Evidence(
            sourceURL="https://example.com/article",
            sourceDomain="example.com",
            snippet="This is evidence text",
            credibilityScore=0.8,
            relevanceScore=0.9
        )
        assert evidence.sourceURL == "https://example.com/article"
        assert evidence.credibilityScore == 0.8
        assert evidence.relevanceScore == 0.9
    
    def test_evidence_score_bounds(self):
        """Test that credibility and relevance scores are bounded."""
        # Valid bounds
        Evidence(
            sourceURL="https://test.com",
            sourceDomain="test.com",
            snippet="Test",
            credibilityScore=0.0,
            relevanceScore=1.0
        )
        
        # Invalid credibility score
        with pytest.raises(ValueError):
            Evidence(
                sourceURL="https://test.com",
                sourceDomain="test.com",
                snippet="Test",
                credibilityScore=1.5,
                relevanceScore=0.5
            )
        
        # Invalid relevance score
        with pytest.raises(ValueError):
            Evidence(
                sourceURL="https://test.com",
                sourceDomain="test.com",
                snippet="Test",
                credibilityScore=0.5,
                relevanceScore=-0.1
            )
    
    def test_evidence_empty_fields_fail(self):
        """Test that empty required fields raise validation errors."""
        with pytest.raises(ValueError):
            Evidence(
                sourceURL="",
                sourceDomain="test.com",
                snippet="Test",
                credibilityScore=0.5,
                relevanceScore=0.5
            )


class TestNLIResult:
    """Tests for NLIResult model."""
    
    def test_valid_nli_result(self):
        """Test creating a valid NLI result."""
        claim_id = uuid4()
        evidence_id = uuid4()
        result = NLIResult(
            claimID=claim_id,
            evidenceID=evidence_id,
            entailmentScore=0.7,
            contradictionScore=0.2,
            neutralScore=0.1,
            label=RelationshipLabel.SUPPORTS
        )
        assert result.claimID == claim_id
        assert result.label == RelationshipLabel.SUPPORTS
    
    def test_nli_scores_must_sum_to_one(self):
        """Test that NLI scores must sum to approximately 1.0."""
        claim_id = uuid4()
        evidence_id = uuid4()
        
        # Valid sum (exactly 1.0)
        NLIResult(
            claimID=claim_id,
            evidenceID=evidence_id,
            entailmentScore=0.5,
            contradictionScore=0.3,
            neutralScore=0.2,
            label=RelationshipLabel.SUPPORTS
        )
        
        # Valid sum (within tolerance)
        NLIResult(
            claimID=claim_id,
            evidenceID=evidence_id,
            entailmentScore=0.5,
            contradictionScore=0.3,
            neutralScore=0.205,  # Sum = 1.005, within 0.01 tolerance
            label=RelationshipLabel.SUPPORTS
        )
        
        # Invalid sum (outside tolerance)
        with pytest.raises(ValueError, match="NLI scores must sum to 1.0"):
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_id,
                entailmentScore=0.5,
                contradictionScore=0.3,
                neutralScore=0.3,  # Sum = 1.1
                label=RelationshipLabel.SUPPORTS
            )
    
    def test_nli_label_must_match_max_score(self):
        """Test that label must match the highest score."""
        claim_id = uuid4()
        evidence_id = uuid4()
        
        # Valid: SUPPORTS label with highest entailment score
        NLIResult(
            claimID=claim_id,
            evidenceID=evidence_id,
            entailmentScore=0.7,
            contradictionScore=0.2,
            neutralScore=0.1,
            label=RelationshipLabel.SUPPORTS
        )
        
        # Invalid: SUPPORTS label but contradiction score is highest
        with pytest.raises(ValueError, match="Label .* does not match highest score"):
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_id,
                entailmentScore=0.2,
                contradictionScore=0.7,
                neutralScore=0.1,
                label=RelationshipLabel.SUPPORTS
            )


class TestVerificationScore:
    """Tests for VerificationScore model."""
    
    def test_valid_verification_score(self):
        """Test creating a valid verification score."""
        claim_id = uuid4()
        score = VerificationScore(
            claimID=claim_id,
            supportCount=3,
            refuteCount=1,
            neutralCount=1,
            confidenceScore=75.0,
            verdict=VerdictType.TRUE
        )
        assert score.supportCount == 3
        assert score.confidenceScore == 75.0
        assert score.verdict == VerdictType.TRUE
    
    def test_confidence_score_bounds(self):
        """Test that confidence score is bounded between 0 and 100."""
        claim_id = uuid4()
        
        # Valid bounds
        VerificationScore(
            claimID=claim_id,
            supportCount=0,
            refuteCount=0,
            neutralCount=0,
            confidenceScore=0.0,
            verdict=VerdictType.UNVERIFIED
        )
        
        VerificationScore(
            claimID=claim_id,
            supportCount=5,
            refuteCount=0,
            neutralCount=0,
            confidenceScore=100.0,
            verdict=VerdictType.TRUE
        )
        
        # Invalid bounds
        with pytest.raises(ValueError):
            VerificationScore(
                claimID=claim_id,
                supportCount=0,
                refuteCount=0,
                neutralCount=0,
                confidenceScore=-1.0,
                verdict=VerdictType.UNVERIFIED
            )
        
        with pytest.raises(ValueError):
            VerificationScore(
                claimID=claim_id,
                supportCount=0,
                refuteCount=0,
                neutralCount=0,
                confidenceScore=101.0,
                verdict=VerdictType.TRUE
            )


class TestFinalVerdict:
    """Tests for FinalVerdict model."""
    
    def test_valid_final_verdict(self):
        """Test creating a valid final verdict."""
        verdict = FinalVerdict(
            overallVerdict=OverallVerdictType.LIKELY_TRUE,
            confidenceScore=80.0,
            factualAccuracyScore=85.0,
            emotionalManipulationScore=20.0,
            explanation="The article is mostly accurate based on evidence."
        )
        assert verdict.overallVerdict == OverallVerdictType.LIKELY_TRUE
        assert verdict.confidenceScore == 80.0
        assert verdict.factualAccuracyScore == 85.0
    
    def test_final_verdict_score_bounds(self):
        """Test that all scores are bounded between 0 and 100."""
        # Valid scores
        FinalVerdict(
            overallVerdict=OverallVerdictType.LIKELY_TRUE,
            confidenceScore=50.0,
            factualAccuracyScore=60.0,
            emotionalManipulationScore=30.0,
            explanation="Test"
        )
        
        # Invalid confidence score
        with pytest.raises(ValueError):
            FinalVerdict(
                overallVerdict=OverallVerdictType.LIKELY_TRUE,
                confidenceScore=150.0,
                factualAccuracyScore=60.0,
                emotionalManipulationScore=30.0,
                explanation="Test"
            )
    
    def test_final_verdict_empty_explanation_fails(self):
        """Test that empty explanation raises validation error."""
        with pytest.raises(ValidationError):
            FinalVerdict(
                overallVerdict=OverallVerdictType.LIKELY_TRUE,
                confidenceScore=80.0,
                factualAccuracyScore=85.0,
                emotionalManipulationScore=20.0,
                explanation=""
            )


class TestArticleInput:
    """Tests for ArticleInput model."""
    
    def test_valid_url_input(self):
        """Test creating valid URL input."""
        article = ArticleInput(
            inputType=InputType.URL,
            content="https://example.com/article"
        )
        assert article.inputType == InputType.URL
        assert article.content == "https://example.com/article"
    
    def test_valid_text_input(self):
        """Test creating valid text input."""
        article = ArticleInput(
            inputType=InputType.TEXT,
            content="This is article text"
        )
        assert article.inputType == InputType.TEXT
    
    def test_url_must_have_protocol(self):
        """Test that URL input must start with http:// or https://."""
        with pytest.raises(ValueError, match="URL must start with http"):
            ArticleInput(
                inputType=InputType.URL,
                content="example.com/article"
            )
    
    def test_empty_content_fails(self):
        """Test that empty content raises validation error."""
        with pytest.raises(ValidationError):
            ArticleInput(
                inputType=InputType.TEXT,
                content=""
            )


class TestSourceCredibility:
    """Tests for SourceCredibility model."""
    
    def test_valid_source_credibility(self):
        """Test creating valid source credibility."""
        source = SourceCredibility(
            domain="example.com",
            credibilityScore=0.85,
            category=SourceCategory.TRUSTED
        )
        assert source.domain == "example.com"
        assert source.credibilityScore == 0.85
        assert source.category == SourceCategory.TRUSTED
    
    def test_category_must_match_score(self):
        """Test that category must match credibility score range."""
        # Valid: TRUSTED (0.8-1.0)
        SourceCredibility(
            domain="trusted.com",
            credibilityScore=0.9,
            category=SourceCategory.TRUSTED
        )
        
        # Valid: MAINSTREAM (0.5-0.79)
        SourceCredibility(
            domain="mainstream.com",
            credibilityScore=0.6,
            category=SourceCategory.MAINSTREAM
        )
        
        # Valid: QUESTIONABLE (0.3-0.49)
        SourceCredibility(
            domain="questionable.com",
            credibilityScore=0.4,
            category=SourceCategory.QUESTIONABLE
        )
        
        # Valid: UNRELIABLE (0.0-0.29)
        SourceCredibility(
            domain="unreliable.com",
            credibilityScore=0.2,
            category=SourceCategory.UNRELIABLE
        )
        
        # Invalid: TRUSTED category but score too low
        with pytest.raises(ValueError, match="Category .* does not match score"):
            SourceCredibility(
                domain="test.com",
                credibilityScore=0.5,
                category=SourceCategory.TRUSTED
            )
    
    def test_domain_normalized_to_lowercase(self):
        """Test that domain is normalized to lowercase."""
        source = SourceCredibility(
            domain="Example.COM",
            credibilityScore=0.8,
            category=SourceCategory.TRUSTED
        )
        assert source.domain == "example.com"


class TestChainOfCustody:
    """Tests for ChainOfCustody model."""
    
    def test_valid_chain_of_custody(self):
        """Test creating valid chain of custody."""
        now = datetime.now()
        chain = ChainOfCustody(
            originalSource="original.com",
            firstPublished=now,
            viralityScore=0.7
        )
        assert chain.originalSource == "original.com"
        assert chain.viralityScore == 0.7
    
    def test_propagation_path_must_be_chronological(self):
        """Test that propagation path must be in chronological order."""
        now = datetime.now()
        from datetime import timedelta
        
        # Valid: chronological order
        ChainOfCustody(
            originalSource="original.com",
            firstPublished=now,
            propagationPath=[
                PropagationNode(source="site1.com", timestamp=now),
                PropagationNode(source="site2.com", timestamp=now + timedelta(hours=1)),
                PropagationNode(source="site3.com", timestamp=now + timedelta(hours=2))
            ],
            viralityScore=0.8
        )
        
        # Invalid: not chronological
        with pytest.raises(ValueError, match="chronological order"):
            ChainOfCustody(
                originalSource="original.com",
                firstPublished=now,
                propagationPath=[
                    PropagationNode(source="site1.com", timestamp=now + timedelta(hours=2)),
                    PropagationNode(source="site2.com", timestamp=now),  # Earlier than previous
                ],
                viralityScore=0.8
            )


class TestToneScore:
    """Tests for ToneScore model."""
    
    def test_valid_tone_score(self):
        """Test creating valid tone score."""
        tone = ToneScore(
            emotionalIntensity=0.6,
            sensationalismScore=0.4,
            manipulativePhrases=["shocking", "you won't believe"],
            objectivityScore=0.6
        )
        assert tone.emotionalIntensity == 0.6
        assert len(tone.manipulativePhrases) == 2
    
    def test_tone_score_bounds(self):
        """Test that tone scores are bounded between 0 and 1."""
        # Valid bounds
        ToneScore(
            emotionalIntensity=0.0,
            sensationalismScore=1.0,
            objectivityScore=0.5
        )
        
        # Invalid bounds
        with pytest.raises(ValueError):
            ToneScore(
                emotionalIntensity=1.5,
                sensationalismScore=0.5,
                objectivityScore=0.5
            )


class TestEvidenceCard:
    """Tests for EvidenceCard model."""
    
    def test_valid_evidence_card(self):
        """Test creating valid evidence card."""
        card = EvidenceCard(
            claim="The sky is blue",
            evidenceSnippet="Scientific studies confirm the sky appears blue",
            sourceURL="https://science.com/article",
            sourceName="Science Daily",
            relationship=RelationshipLabel.SUPPORTS
        )
        assert card.claim == "The sky is blue"
        assert card.relationship == RelationshipLabel.SUPPORTS
    
    def test_evidence_card_empty_fields_fail(self):
        """Test that empty required fields raise validation errors."""
        with pytest.raises(ValueError):
            EvidenceCard(
                claim="",
                evidenceSnippet="Test",
                sourceURL="https://test.com",
                sourceName="Test",
                relationship=RelationshipLabel.SUPPORTS
            )
