"""
Unit tests for NLI Engine score aggregation.

Tests the aggregateNLIScores function with various evidence patterns
to ensure correct verdict determination and confidence scoring.
"""

import pytest
from uuid import uuid4
from unittest.mock import patch, MagicMock

from src.models import NLIResult, VerificationScore, VerdictType, RelationshipLabel
from src.nli_engine import aggregateNLIScores, load_nli_model


class TestLoadNLIModel:
    """Test suite for load_nli_model function."""
    
    def test_model_loading_success(self):
        """Test successful model loading and caching."""
        # Reset the cache
        import src.nli_engine as nli_module
        nli_module._nli_model_cache = None
        nli_module._model_load_failed = False
        
        # Mock the transformers library
        with patch('transformers.AutoTokenizer') as mock_tokenizer, \
             patch('transformers.AutoModelForSequenceClassification') as mock_model:
            
            mock_tokenizer_instance = MagicMock()
            mock_model_instance = MagicMock()
            
            mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
            mock_model.from_pretrained.return_value = mock_model_instance
            
            # First call should load the model
            result = load_nli_model()
            
            assert result is not None
            assert result == (mock_model_instance, mock_tokenizer_instance)
            assert mock_model_instance.eval.called
            
            # Second call should return cached model
            result2 = load_nli_model()
            assert result2 == result
            
            # from_pretrained should only be called once (caching works)
            assert mock_tokenizer.from_pretrained.call_count == 1
            assert mock_model.from_pretrained.call_count == 1
    
    def test_model_loading_failure(self):
        """Test model loading failure and fallback behavior."""
        # Reset the cache
        import src.nli_engine as nli_module
        nli_module._nli_model_cache = None
        nli_module._model_load_failed = False
        
        # Mock the transformers library to raise an exception
        with patch('transformers.AutoTokenizer') as mock_tokenizer:
            mock_tokenizer.from_pretrained.side_effect = Exception("Model not found")
            
            # Should return None on failure
            result = load_nli_model()
            assert result is None
            
            # Should not try to load again
            result2 = load_nli_model()
            assert result2 is None
            
            # from_pretrained should only be called once (failure is cached)
            assert mock_tokenizer.from_pretrained.call_count == 1
    
    def test_model_cache_persistence(self):
        """Test that model cache persists across multiple calls."""
        # Reset the cache
        import src.nli_engine as nli_module
        nli_module._nli_model_cache = None
        nli_module._model_load_failed = False
        
        with patch('transformers.AutoTokenizer') as mock_tokenizer, \
             patch('transformers.AutoModelForSequenceClassification') as mock_model:
            
            mock_tokenizer_instance = MagicMock()
            mock_model_instance = MagicMock()
            
            mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
            mock_model.from_pretrained.return_value = mock_model_instance
            
            # Load model multiple times
            result1 = load_nli_model()
            result2 = load_nli_model()
            result3 = load_nli_model()
            
            # All should return the same cached instance
            assert result1 == result2 == result3
            
            # Model should only be loaded once
            assert mock_tokenizer.from_pretrained.call_count == 1
            assert mock_model.from_pretrained.call_count == 1


class TestAggregateNLIScores:
    """Test suite for aggregateNLIScores function."""
    
    def test_all_supporting_evidence(self):
        """Test with all evidence supporting the claim."""
        claim_id = uuid4()
        evidence_ids = [uuid4() for _ in range(3)]
        
        results = [
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[0],
                entailmentScore=0.9,
                contradictionScore=0.05,
                neutralScore=0.05,
                label=RelationshipLabel.SUPPORTS
            ),
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[1],
                entailmentScore=0.85,
                contradictionScore=0.1,
                neutralScore=0.05,
                label=RelationshipLabel.SUPPORTS
            ),
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[2],
                entailmentScore=0.8,
                contradictionScore=0.15,
                neutralScore=0.05,
                label=RelationshipLabel.SUPPORTS
            )
        ]
        
        # Equal weights for all evidence
        weights = {eid: 1.0 for eid in evidence_ids}
        
        score = aggregateNLIScores(results, weights)
        
        assert score.claimID == claim_id
        assert score.supportCount == 3
        assert score.refuteCount == 0
        assert score.neutralCount == 0
        assert score.verdict == VerdictType.TRUE
        assert score.confidenceScore > 60.0
        assert 0.0 <= score.confidenceScore <= 100.0
    
    def test_all_refuting_evidence(self):
        """Test with all evidence refuting the claim."""
        claim_id = uuid4()
        evidence_ids = [uuid4() for _ in range(3)]
        
        results = [
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[0],
                entailmentScore=0.05,
                contradictionScore=0.9,
                neutralScore=0.05,
                label=RelationshipLabel.REFUTES
            ),
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[1],
                entailmentScore=0.1,
                contradictionScore=0.85,
                neutralScore=0.05,
                label=RelationshipLabel.REFUTES
            ),
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[2],
                entailmentScore=0.15,
                contradictionScore=0.8,
                neutralScore=0.05,
                label=RelationshipLabel.REFUTES
            )
        ]
        
        weights = {eid: 1.0 for eid in evidence_ids}
        
        score = aggregateNLIScores(results, weights)
        
        assert score.claimID == claim_id
        assert score.supportCount == 0
        assert score.refuteCount == 3
        assert score.neutralCount == 0
        assert score.verdict == VerdictType.FALSE
        assert score.confidenceScore > 60.0
        assert 0.0 <= score.confidenceScore <= 100.0
    
    def test_mixed_evidence_misleading(self):
        """Test with mixed evidence that should result in MISLEADING verdict."""
        claim_id = uuid4()
        evidence_ids = [uuid4() for _ in range(4)]
        
        results = [
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[0],
                entailmentScore=0.7,
                contradictionScore=0.2,
                neutralScore=0.1,
                label=RelationshipLabel.SUPPORTS
            ),
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[1],
                entailmentScore=0.6,
                contradictionScore=0.3,
                neutralScore=0.1,
                label=RelationshipLabel.SUPPORTS
            ),
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[2],
                entailmentScore=0.2,
                contradictionScore=0.7,
                neutralScore=0.1,
                label=RelationshipLabel.REFUTES
            ),
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[3],
                entailmentScore=0.3,
                contradictionScore=0.6,
                neutralScore=0.1,
                label=RelationshipLabel.REFUTES
            )
        ]
        
        weights = {eid: 1.0 for eid in evidence_ids}
        
        score = aggregateNLIScores(results, weights)
        
        assert score.claimID == claim_id
        assert score.supportCount == 2
        assert score.refuteCount == 2
        assert score.neutralCount == 0
        assert score.verdict == VerdictType.MISLEADING
        assert score.confidenceScore == 50.0
    
    def test_insufficient_evidence_unverified(self):
        """Test with insufficient evidence resulting in UNVERIFIED verdict."""
        claim_id = uuid4()
        evidence_ids = [uuid4() for _ in range(2)]
        
        # Create evidence with low scores that don't meet the 0.2 threshold
        results = [
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[0],
                entailmentScore=0.3,
                contradictionScore=0.1,
                neutralScore=0.6,
                label=RelationshipLabel.NEUTRAL
            ),
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[1],
                entailmentScore=0.2,
                contradictionScore=0.1,
                neutralScore=0.7,
                label=RelationshipLabel.NEUTRAL
            )
        ]
        
        weights = {eid: 1.0 for eid in evidence_ids}
        
        score = aggregateNLIScores(results, weights)
        
        assert score.claimID == claim_id
        # With support_ratio=0.25, refute_ratio=0.1, neither exceeds the other by 0.3
        # and refute < 0.2, so it should be UNVERIFIED
        assert score.verdict == VerdictType.UNVERIFIED
        assert score.confidenceScore == 30.0
    
    def test_weighted_scores_with_credibility(self):
        """Test that evidence credibility weights affect the verdict."""
        claim_id = uuid4()
        evidence_ids = [uuid4() for _ in range(3)]
        
        results = [
            # High credibility source supporting
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[0],
                entailmentScore=0.9,
                contradictionScore=0.05,
                neutralScore=0.05,
                label=RelationshipLabel.SUPPORTS
            ),
            # Low credibility source refuting
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[1],
                entailmentScore=0.1,
                contradictionScore=0.8,
                neutralScore=0.1,
                label=RelationshipLabel.REFUTES
            ),
            # Low credibility source refuting
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[2],
                entailmentScore=0.1,
                contradictionScore=0.8,
                neutralScore=0.1,
                label=RelationshipLabel.REFUTES
            )
        ]
        
        # High weight for first evidence, low for others
        weights = {
            evidence_ids[0]: 0.9,  # High credibility
            evidence_ids[1]: 0.2,  # Low credibility
            evidence_ids[2]: 0.2   # Low credibility
        }
        
        score = aggregateNLIScores(results, weights)
        
        assert score.claimID == claim_id
        assert score.supportCount == 1
        assert score.refuteCount == 2
        # With weighted support=0.81/1.3=0.62 and refute=0.32/1.3=0.25
        # support exceeds refute by 0.37 (>0.3), so verdict should be TRUE
        assert score.verdict == VerdictType.TRUE
    
    def test_neutral_evidence(self):
        """Test with mostly neutral evidence."""
        claim_id = uuid4()
        evidence_ids = [uuid4() for _ in range(3)]
        
        results = [
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[0],
                entailmentScore=0.2,
                contradictionScore=0.2,
                neutralScore=0.6,
                label=RelationshipLabel.NEUTRAL
            ),
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[1],
                entailmentScore=0.25,
                contradictionScore=0.25,
                neutralScore=0.5,
                label=RelationshipLabel.NEUTRAL
            ),
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[2],
                entailmentScore=0.3,
                contradictionScore=0.3,
                neutralScore=0.4,
                label=RelationshipLabel.NEUTRAL
            )
        ]
        
        weights = {eid: 1.0 for eid in evidence_ids}
        
        score = aggregateNLIScores(results, weights)
        
        assert score.claimID == claim_id
        assert score.supportCount == 0
        assert score.refuteCount == 0
        assert score.neutralCount == 3
        assert score.verdict == VerdictType.UNVERIFIED
    
    def test_empty_results_raises_error(self):
        """Test that empty results list raises ValueError."""
        with pytest.raises(ValueError, match="Results list cannot be empty"):
            aggregateNLIScores([], {})
    
    def test_mismatched_claim_ids_raises_error(self):
        """Test that results with different claimIDs raise ValueError."""
        claim_id1 = uuid4()
        claim_id2 = uuid4()
        evidence_id = uuid4()
        
        results = [
            NLIResult(
                claimID=claim_id1,
                evidenceID=evidence_id,
                entailmentScore=0.8,
                contradictionScore=0.1,
                neutralScore=0.1,
                label=RelationshipLabel.SUPPORTS
            ),
            NLIResult(
                claimID=claim_id2,  # Different claim ID
                evidenceID=evidence_id,
                entailmentScore=0.7,
                contradictionScore=0.2,
                neutralScore=0.1,
                label=RelationshipLabel.SUPPORTS
            )
        ]
        
        with pytest.raises(ValueError, match="All results must have the same claimID"):
            aggregateNLIScores(results, {evidence_id: 1.0})
    
    def test_missing_weights_use_default(self):
        """Test that missing evidence weights default to 1.0."""
        claim_id = uuid4()
        evidence_ids = [uuid4() for _ in range(2)]
        
        results = [
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[0],
                entailmentScore=0.8,
                contradictionScore=0.1,
                neutralScore=0.1,
                label=RelationshipLabel.SUPPORTS
            ),
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[1],
                entailmentScore=0.7,
                contradictionScore=0.2,
                neutralScore=0.1,
                label=RelationshipLabel.SUPPORTS
            )
        ]
        
        # Provide weight for only one evidence
        weights = {evidence_ids[0]: 0.8}
        
        # Should not raise error, should use 1.0 for missing weight
        score = aggregateNLIScores(results, weights)
        
        assert score.claimID == claim_id
        assert score.verdict == VerdictType.TRUE
    
    def test_confidence_score_bounds(self):
        """Test that confidence scores are always within [0, 100]."""
        claim_id = uuid4()
        evidence_id = uuid4()
        
        # Test with extreme scores
        results = [
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_id,
                entailmentScore=1.0,
                contradictionScore=0.0,
                neutralScore=0.0,
                label=RelationshipLabel.SUPPORTS
            )
        ]
        
        weights = {evidence_id: 1.0}
        score = aggregateNLIScores(results, weights)
        
        assert 0.0 <= score.confidenceScore <= 100.0
    
    def test_count_aggregation_property(self):
        """Test that support + refute + neutral counts equal total results."""
        claim_id = uuid4()
        evidence_ids = [uuid4() for _ in range(5)]
        
        results = [
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[0],
                entailmentScore=0.7,
                contradictionScore=0.2,
                neutralScore=0.1,
                label=RelationshipLabel.SUPPORTS
            ),
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[1],
                entailmentScore=0.2,
                contradictionScore=0.7,
                neutralScore=0.1,
                label=RelationshipLabel.REFUTES
            ),
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[2],
                entailmentScore=0.3,
                contradictionScore=0.3,
                neutralScore=0.4,
                label=RelationshipLabel.NEUTRAL
            ),
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[3],
                entailmentScore=0.6,
                contradictionScore=0.3,
                neutralScore=0.1,
                label=RelationshipLabel.SUPPORTS
            ),
            NLIResult(
                claimID=claim_id,
                evidenceID=evidence_ids[4],
                entailmentScore=0.25,
                contradictionScore=0.25,
                neutralScore=0.5,
                label=RelationshipLabel.NEUTRAL
            )
        ]
        
        weights = {eid: 1.0 for eid in evidence_ids}
        score = aggregateNLIScores(results, weights)
        
        # Property: counts must sum to total results
        assert score.supportCount + score.refuteCount + score.neutralCount == len(results)
        assert score.supportCount == 2
        assert score.refuteCount == 1
        assert score.neutralCount == 2
