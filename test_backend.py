"""
Backend verification test script for Fake News Detection System.

This script tests the complete verification pipeline with a simple example.
"""

import sys
import logging
from src.verification_pipeline import verifyArticle

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_backend():
    """Test the backend with a simple article."""
    
    print("=" * 80)
    print("FAKE NEWS DETECTION SYSTEM - BACKEND TEST")
    print("=" * 80)
    print()
    
    # Test article (simple factual example)
    test_article = """
    The World Health Organization announced today that global COVID-19 cases have decreased 
    by 15% over the past month. According to WHO data, vaccination rates have increased 
    significantly in developing countries, contributing to the decline. Dr. Maria Santos, 
    WHO spokesperson, stated that this trend is encouraging but urged continued vigilance.
    """
    
    print("Test Article:")
    print("-" * 80)
    print(test_article.strip())
    print("-" * 80)
    print()
    
    try:
        print("Starting verification pipeline...")
        print()
        
        # Run verification
        verdict = verifyArticle(test_article)
        
        print("✅ VERIFICATION COMPLETE!")
        print("=" * 80)
        print()
        
        # Display results
        print(f"Overall Verdict: {verdict.overallVerdict.value}")
        print(f"Confidence Score: {verdict.confidenceScore:.1f}%")
        print(f"Factual Accuracy: {verdict.factualAccuracyScore:.1f}%")
        print(f"Emotional Manipulation: {verdict.emotionalManipulationScore:.1f}%")
        print()
        
        print("Explanation:")
        print("-" * 80)
        print(verdict.explanation)
        print("-" * 80)
        print()
        
        if verdict.claimBreakdown:
            print(f"Claims Analyzed: {len(verdict.claimBreakdown)}")
            print()
            for idx, claim_verdict in enumerate(verdict.claimBreakdown, 1):
                print(f"Claim {idx}: {claim_verdict.claim.text}")
                print(f"  Verdict: {claim_verdict.verdict.value}")
                print(f"  Confidence: {claim_verdict.confidence:.1f}%")
                print(f"  Supporting Evidence: {len(claim_verdict.supportingEvidence)}")
                print(f"  Contradicting Evidence: {len(claim_verdict.contradictingEvidence)}")
                print()
        
        if verdict.evidenceCards:
            print(f"Evidence Cards: {len(verdict.evidenceCards)}")
            print()
        
        print("=" * 80)
        print("✅ BACKEND TEST PASSED!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ BACKEND TEST FAILED!")
        print("=" * 80)
        print()
        print(f"Error: {str(e)}")
        print()
        
        import traceback
        traceback.print_exc()
        
        return False


if __name__ == "__main__":
    success = test_backend()
    sys.exit(0 if success else 1)
