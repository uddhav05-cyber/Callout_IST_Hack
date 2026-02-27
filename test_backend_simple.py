"""
Simple backend verification test without API requirements.

This script tests individual components without requiring API keys.
"""

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_imports():
    """Test that all modules can be imported."""
    print("=" * 80)
    print("TEST 1: Module Imports")
    print("=" * 80)
    
    try:
        from src.models import Claim, Evidence, FinalVerdict
        print("✅ Models imported successfully")
        
        from src.article_parser import processTextInput
        print("✅ Article parser imported successfully")
        
        from src.source_credibility import lookup_source_credibility
        print("✅ Source credibility imported successfully")
        
        from src.llm_integration import extractClaims
        print("✅ LLM integration imported successfully")
        
        from src.evidence_retrieval import searchEvidence
        print("✅ Evidence retrieval imported successfully")
        
        from src.nli_engine import load_nli_model
        print("✅ NLI engine imported successfully")
        
        from src.tone_analyzer import analyzeTone
        print("✅ Tone analyzer imported successfully")
        
        from src.synthesis import generateVerdict
        print("✅ Synthesis module imported successfully")
        
        from src.verification_pipeline import verifyArticle
        print("✅ Verification pipeline imported successfully")
        
        print()
        print("✅ ALL IMPORTS SUCCESSFUL")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_article_parser():
    """Test article parsing."""
    print()
    print("=" * 80)
    print("TEST 2: Article Parser")
    print("=" * 80)
    
    try:
        from src.article_parser import processTextInput
        
        test_text = "This is a test article with some content."
        result = processTextInput(test_text)
        
        print(f"✅ Processed text: {len(result)} characters")
        assert len(result) > 0, "Processed text should not be empty"
        
        print("✅ ARTICLE PARSER TEST PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Article parser test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_source_credibility():
    """Test source credibility lookup."""
    print()
    print("=" * 80)
    print("TEST 3: Source Credibility")
    print("=" * 80)
    
    try:
        from src.source_credibility import lookup_source_credibility
        
        # Test known source
        result = lookup_source_credibility("bbc.com")
        print(f"✅ BBC credibility: {result.credibilityScore} ({result.category.value})")
        
        # Test unknown source
        result = lookup_source_credibility("unknown-domain.com")
        print(f"✅ Unknown domain credibility: {result.credibilityScore} ({result.category.value})")
        assert result.credibilityScore == 0.5, "Unknown domain should have default score"
        
        print("✅ SOURCE CREDIBILITY TEST PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Source credibility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tone_analyzer():
    """Test tone analysis."""
    print()
    print("=" * 80)
    print("TEST 4: Tone Analyzer")
    print("=" * 80)
    
    try:
        from src.tone_analyzer import analyzeTone
        
        # Test neutral text
        neutral_text = "The company reported quarterly earnings today."
        result = analyzeTone(neutral_text)
        print(f"✅ Neutral text - Sensationalism: {result.sensationalismScore:.2f}, Objectivity: {result.objectivityScore:.2f}")
        
        # Test sensational text
        sensational_text = "SHOCKING! You won't believe what happened! This is UNBELIEVABLE!"
        result = analyzeTone(sensational_text)
        print(f"✅ Sensational text - Sensationalism: {result.sensationalismScore:.2f}, Objectivity: {result.objectivityScore:.2f}")
        assert result.sensationalismScore > 0, "Sensational text should have high sensationalism score"
        
        print("✅ TONE ANALYZER TEST PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Tone analyzer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_models():
    """Test data models."""
    print()
    print("=" * 80)
    print("TEST 5: Data Models")
    print("=" * 80)
    
    try:
        from src.models import Claim, Evidence, ToneScore
        from uuid import uuid4
        
        # Test Claim model
        claim = Claim(
            id=uuid4(),
            text="Test claim",
            context="Test context",
            importance=0.8
        )
        print(f"✅ Claim model: {claim.text}")
        
        # Test Evidence model
        evidence = Evidence(
            id=uuid4(),
            sourceURL="https://example.com",
            sourceDomain="example.com",
            snippet="Test snippet",
            credibilityScore=0.7,
            relevanceScore=0.8
        )
        print(f"✅ Evidence model: {evidence.sourceDomain}")
        
        # Test ToneScore model
        tone = ToneScore(
            emotionalIntensity=0.3,
            sensationalismScore=0.2,
            manipulativePhrases=[],
            objectivityScore=0.8
        )
        print(f"✅ ToneScore model: objectivity={tone.objectivityScore}")
        
        print("✅ DATA MODELS TEST PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Data models test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print()
    print("=" * 80)
    print("FAKE NEWS DETECTION SYSTEM - SIMPLE BACKEND TEST")
    print("=" * 80)
    print()
    
    results = []
    
    results.append(("Module Imports", test_imports()))
    results.append(("Article Parser", test_article_parser()))
    results.append(("Source Credibility", test_source_credibility()))
    results.append(("Tone Analyzer", test_tone_analyzer()))
    results.append(("Data Models", test_data_models()))
    
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    print()
    if all_passed:
        print("=" * 80)
        print("✅ ALL TESTS PASSED - BACKEND IS WORKING!")
        print("=" * 80)
        print()
        print("Note: Full pipeline test requires API keys (GROQ/OPENAI + SERPER/TAVILY)")
        print("The Streamlit app is running at: http://localhost:8501")
    else:
        print("=" * 80)
        print("❌ SOME TESTS FAILED")
        print("=" * 80)
    
    return all_passed


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
