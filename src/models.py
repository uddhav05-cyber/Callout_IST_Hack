"""
Data models for the Fake News Detection System.

This module defines all Pydantic models used throughout the system for data validation
and type safety. Models include validation rules to ensure data integrity.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


# Enums for categorical fields
class InputType(str, Enum):
    """Type of input provided by the user."""
    URL = "URL"
    TEXT = "TEXT"
    IMAGE = "IMAGE"


class RelationshipLabel(str, Enum):
    """Relationship between a claim and evidence."""
    SUPPORTS = "SUPPORTS"
    REFUTES = "REFUTES"
    NEUTRAL = "NEUTRAL"


class VerdictType(str, Enum):
    """Verdict for a single claim."""
    TRUE = "TRUE"
    FALSE = "FALSE"
    MISLEADING = "MISLEADING"
    UNVERIFIED = "UNVERIFIED"


class OverallVerdictType(str, Enum):
    """Overall verdict for an article."""
    LIKELY_TRUE = "LIKELY_TRUE"
    LIKELY_FALSE = "LIKELY_FALSE"
    MISLEADING = "MISLEADING"
    UNVERIFIED = "UNVERIFIED"


class SourceCategory(str, Enum):
    """Credibility category for a source."""
    TRUSTED = "TRUSTED"
    MAINSTREAM = "MAINSTREAM"
    QUESTIONABLE = "QUESTIONABLE"
    UNRELIABLE = "UNRELIABLE"


class ManipulationType(str, Enum):
    """Type of image/video manipulation detected."""
    NONE = "NONE"
    EDITED = "EDITED"
    DEEPFAKE = "DEEPFAKE"
    OUT_OF_CONTEXT = "OUT_OF_CONTEXT"


# Core data models
class Claim(BaseModel):
    """Represents an atomic, verifiable claim extracted from an article."""
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the claim")
    text: str = Field(..., min_length=1, description="The claim text")
    context: str = Field(default="", description="Surrounding context for the claim")
    importance: float = Field(..., ge=0.0, le=1.0, description="Importance score for verification priority")

    @field_validator('text')
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        """Ensure claim text is not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError("Claim text cannot be empty")
        return v.strip()


class Evidence(BaseModel):
    """Represents evidence retrieved from external sources."""
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the evidence")
    sourceURL: str = Field(..., min_length=1, description="URL of the evidence source")
    sourceDomain: str = Field(..., min_length=1, description="Domain name of the source")
    snippet: str = Field(..., min_length=1, description="Relevant text snippet from the source")
    publishDate: Optional[datetime] = Field(default=None, description="Publication date of the evidence")
    credibilityScore: float = Field(..., ge=0.0, le=1.0, description="Credibility score of the source")
    relevanceScore: float = Field(..., ge=0.0, le=1.0, description="Relevance score to the claim")

    @field_validator('sourceURL', 'sourceDomain', 'snippet')
    @classmethod
    def fields_not_empty(cls, v: str) -> str:
        """Ensure required string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class NLIResult(BaseModel):
    """Result from Natural Language Inference comparing claim against evidence."""
    claimID: UUID = Field(..., description="ID of the claim being verified")
    evidenceID: UUID = Field(..., description="ID of the evidence being compared")
    entailmentScore: float = Field(..., ge=0.0, le=1.0, description="Probability of entailment")
    contradictionScore: float = Field(..., ge=0.0, le=1.0, description="Probability of contradiction")
    neutralScore: float = Field(..., ge=0.0, le=1.0, description="Probability of neutral relationship")
    label: RelationshipLabel = Field(..., description="Dominant relationship label")

    @model_validator(mode='after')
    def validate_scores_sum(self) -> 'NLIResult':
        """Ensure the three scores sum to approximately 1.0."""
        total = self.entailmentScore + self.contradictionScore + self.neutralScore
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"NLI scores must sum to 1.0 (±0.01), got {total}")
        return self

    @model_validator(mode='after')
    def validate_label_matches_max_score(self) -> 'NLIResult':
        """Ensure label matches the highest score."""
        scores = {
            RelationshipLabel.SUPPORTS: self.entailmentScore,
            RelationshipLabel.REFUTES: self.contradictionScore,
            RelationshipLabel.NEUTRAL: self.neutralScore
        }
        max_label = max(scores, key=scores.get)
        if self.label != max_label:
            raise ValueError(f"Label {self.label} does not match highest score {max_label}")
        return self


class VerificationScore(BaseModel):
    """Aggregated verification score for a claim across multiple evidence items."""
    claimID: UUID = Field(..., description="ID of the claim being scored")
    supportCount: int = Field(..., ge=0, description="Number of supporting evidence items")
    refuteCount: int = Field(..., ge=0, description="Number of refuting evidence items")
    neutralCount: int = Field(..., ge=0, description="Number of neutral evidence items")
    confidenceScore: float = Field(..., ge=0.0, le=100.0, description="Confidence in the verdict (0-100)")
    verdict: VerdictType = Field(..., description="Verdict for this claim")


class ToneScore(BaseModel):
    """Analysis of emotional tone and manipulation in text."""
    emotionalIntensity: float = Field(..., ge=0.0, le=1.0, description="Intensity of emotional language")
    sensationalismScore: float = Field(..., ge=0.0, le=1.0, description="Degree of sensationalism")
    manipulativePhrases: List[str] = Field(default_factory=list, description="Detected manipulative phrases")
    objectivityScore: float = Field(..., ge=0.0, le=1.0, description="Objectivity score (inverse of sensationalism)")


class EvidenceCard(BaseModel):
    """Visual card showing claim-evidence comparison."""
    claim: str = Field(..., min_length=1, description="The claim text")
    evidenceSnippet: str = Field(..., min_length=1, description="Evidence text snippet")
    sourceURL: str = Field(..., min_length=1, description="URL of the evidence source")
    sourceName: str = Field(..., min_length=1, description="Name of the source")
    relationship: RelationshipLabel = Field(..., description="Relationship between claim and evidence")
    highlightedDiscrepancies: List[str] = Field(default_factory=list, description="Specific discrepancies identified")

    @field_validator('claim', 'evidenceSnippet', 'sourceURL', 'sourceName')
    @classmethod
    def fields_not_empty(cls, v: str) -> str:
        """Ensure required string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class ClaimVerdict(BaseModel):
    """Verdict for a single claim with supporting/contradicting evidence."""
    claim: Claim = Field(..., description="The claim being verified")
    verdict: VerdictType = Field(..., description="Verdict for this claim")
    confidence: float = Field(..., ge=0.0, le=100.0, description="Confidence in the verdict (0-100)")
    supportingEvidence: List[Evidence] = Field(default_factory=list, description="Evidence supporting the claim")
    contradictingEvidence: List[Evidence] = Field(default_factory=list, description="Evidence contradicting the claim")


class FinalVerdict(BaseModel):
    """Final verdict for an article with all analysis results."""
    overallVerdict: OverallVerdictType = Field(..., description="Overall verdict for the article")
    confidenceScore: float = Field(..., ge=0.0, le=100.0, description="Overall confidence score (0-100)")
    factualAccuracyScore: float = Field(..., ge=0.0, le=100.0, description="Factual accuracy score (0-100)")
    emotionalManipulationScore: float = Field(..., ge=0.0, le=100.0, description="Emotional manipulation score (0-100)")
    claimBreakdown: List[ClaimVerdict] = Field(default_factory=list, description="Breakdown by individual claims")
    evidenceCards: List[EvidenceCard] = Field(default_factory=list, description="Visual evidence cards")
    explanation: str = Field(..., min_length=1, description="Human-readable explanation of the verdict")

    @field_validator('explanation')
    @classmethod
    def explanation_not_empty(cls, v: str) -> str:
        """Ensure explanation is not empty."""
        if not v or not v.strip():
            raise ValueError("Explanation cannot be empty")
        return v.strip()


# Additional data models from design document
class ArticleInput(BaseModel):
    """Input provided by the user for verification."""
    inputType: InputType = Field(..., description="Type of input (URL, TEXT, or IMAGE)")
    content: str = Field(..., min_length=1, description="The content to verify")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")

    @field_validator('content')
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        """Ensure content is not empty."""
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()

    @model_validator(mode='after')
    def validate_url_format(self) -> 'ArticleInput':
        """Validate URL format if inputType is URL."""
        if self.inputType == InputType.URL:
            content = self.content.strip()
            if not (content.startswith('http://') or content.startswith('https://')):
                raise ValueError("URL must start with http:// or https://")
        return self


class SourceCredibility(BaseModel):
    """Credibility information for a source domain."""
    domain: str = Field(..., min_length=1, description="Domain name")
    credibilityScore: float = Field(..., ge=0.0, le=1.0, description="Credibility score (0-1)")
    category: SourceCategory = Field(..., description="Credibility category")
    lastUpdated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

    @field_validator('domain')
    @classmethod
    def domain_not_empty(cls, v: str) -> str:
        """Ensure domain is not empty."""
        if not v or not v.strip():
            raise ValueError("Domain cannot be empty")
        return v.strip().lower()

    @model_validator(mode='after')
    def validate_category_matches_score(self) -> 'SourceCredibility':
        """Ensure category matches the credibility score range."""
        score = self.credibilityScore
        expected_category = None
        
        if 0.8 <= score <= 1.0:
            expected_category = SourceCategory.TRUSTED
        elif 0.5 <= score < 0.8:
            expected_category = SourceCategory.MAINSTREAM
        elif 0.3 <= score < 0.5:
            expected_category = SourceCategory.QUESTIONABLE
        else:  # 0.0 <= score < 0.3
            expected_category = SourceCategory.UNRELIABLE
        
        if self.category != expected_category:
            raise ValueError(
                f"Category {self.category} does not match score {score} "
                f"(expected {expected_category})"
            )
        return self


class ImageMatch(BaseModel):
    """Result from reverse image search."""
    originalURL: str = Field(..., min_length=1, description="URL of the original image")
    firstSeenDate: datetime = Field(..., description="First publication date")
    context: str = Field(default="", description="Context where image was first used")
    similarity: float = Field(..., ge=0.0, le=1.0, description="Similarity score")

    @field_validator('originalURL')
    @classmethod
    def url_not_empty(cls, v: str) -> str:
        """Ensure URL is not empty."""
        if not v or not v.strip():
            raise ValueError("URL cannot be empty")
        return v.strip()


class ManipulationReport(BaseModel):
    """Report on potential image/video manipulation."""
    isManipulated: bool = Field(..., description="Whether manipulation was detected")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the detection")
    manipulationType: ManipulationType = Field(..., description="Type of manipulation detected")
    details: str = Field(default="", description="Additional details about the manipulation")


class PropagationNode(BaseModel):
    """Node in the chain of custody showing how content propagated."""
    source: str = Field(..., min_length=1, description="Source where content appeared")
    timestamp: datetime = Field(..., description="When content appeared at this source")
    modifications: List[str] = Field(default_factory=list, description="Modifications made at this node")

    @field_validator('source')
    @classmethod
    def source_not_empty(cls, v: str) -> str:
        """Ensure source is not empty."""
        if not v or not v.strip():
            raise ValueError("Source cannot be empty")
        return v.strip()


class ChainOfCustody(BaseModel):
    """Chain of custody tracking content propagation."""
    originalSource: str = Field(..., min_length=1, description="Original source of the content")
    firstPublished: datetime = Field(..., description="First publication date")
    propagationPath: List[PropagationNode] = Field(default_factory=list, description="Propagation path")
    viralityScore: float = Field(..., ge=0.0, le=1.0, description="Virality score")

    @field_validator('originalSource')
    @classmethod
    def source_not_empty(cls, v: str) -> str:
        """Ensure original source is not empty."""
        if not v or not v.strip():
            raise ValueError("Original source cannot be empty")
        return v.strip()

    @model_validator(mode='after')
    def validate_chronological_order(self) -> 'ChainOfCustody':
        """Ensure propagation path is in chronological order."""
        if len(self.propagationPath) > 1:
            for i in range(len(self.propagationPath) - 1):
                if self.propagationPath[i].timestamp > self.propagationPath[i + 1].timestamp:
                    raise ValueError("Propagation path must be in chronological order")
        return self
