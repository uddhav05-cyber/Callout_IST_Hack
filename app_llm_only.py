"""
Simple Fake News Detection - LLM Only (No Evidence Retrieval)

This version just asks the LLM directly if a claim is TRUE or FALSE.
No complex pipeline, no evidence retrieval, no NLI model.
Just pure LLM judgment.
"""

import streamlit as st
from groq import Groq
import os

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Page config
st.set_page_config(
    page_title="Fake News Detector",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS for cyberpunk theme
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    }
    
    .stTextArea textarea {
        background-color: #1a1f3a !important;
        color: #00ffff !important;
        border: 2px solid #00ffff !important;
        font-size: 16px !important;
    }
    
    .verdict-true {
        background: linear-gradient(135deg, #00ff88 0%, #00cc66 100%);
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        font-size: 80px;
        font-weight: bold;
        color: #000;
        box-shadow: 0 0 40px rgba(0, 255, 136, 0.6);
        animation: pulse 2s infinite;
    }
    
    .verdict-false {
        background: linear-gradient(135deg, #ff0055 0%, #cc0044 100%);
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        font-size: 80px;
        font-weight: bold;
        color: #fff;
        box-shadow: 0 0 40px rgba(255, 0, 85, 0.6);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .explanation {
        background: rgba(26, 31, 58, 0.8);
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #00ffff;
        color: #fff;
        font-size: 18px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 style='text-align: center; color: #00ffff; font-size: 60px;'>🔍 FAKE NEWS DETECTOR</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #fff; font-size: 20px;'>Powered by AI - Simple & Direct</p>", unsafe_allow_html=True)

# Input
st.markdown("---")
claim = st.text_area(
    "Enter a news claim to verify:",
    height=150,
    placeholder="Example: The Earth is flat"
)

# Analyze button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_button = st.button("🔍 ANALYZE", use_container_width=True)

# Quick test buttons
st.markdown("---")
st.markdown("<p style='color: #00ffff;'>Quick Tests:</p>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("✅ Test TRUE Claim", use_container_width=True):
        claim = "The Earth orbits around the Sun"
        analyze_button = True

with col2:
    if st.button("❌ Test FALSE Claim", use_container_width=True):
        claim = "The Earth is flat"
        analyze_button = True

with col3:
    if st.button("🌡️ Test Science Fact", use_container_width=True):
        claim = "Water boils at 100 degrees Celsius at sea level"
        analyze_button = True

# Analysis
if analyze_button and claim:
    with st.spinner("🤖 Analyzing with AI..."):
        try:
            # Initialize Groq client
            client = Groq(api_key=GROQ_API_KEY)
            
            # Create prompt
            prompt = f"""Analyze this claim and determine if it is TRUE or FALSE.

Claim: {claim}

Provide your response in this exact format:
VERDICT: [TRUE or FALSE]
EXPLANATION: [Brief explanation of why this is true or false, 2-3 sentences]

Be direct and clear. Base your judgment on factual accuracy."""
            
            # Call LLM
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a fact-checking AI. You analyze claims and determine if they are TRUE or FALSE based on factual accuracy. You provide clear, direct verdicts with brief explanations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result = response.choices[0].message.content
            
            # Parse result
            verdict = "UNKNOWN"
            explanation = result
            
            if "VERDICT:" in result:
                lines = result.split("\n")
                for line in lines:
                    if "VERDICT:" in line:
                        verdict_text = line.split("VERDICT:")[1].strip()
                        if "TRUE" in verdict_text.upper() and "FALSE" not in verdict_text.upper():
                            verdict = "TRUE"
                        elif "FALSE" in verdict_text.upper():
                            verdict = "FALSE"
                    elif "EXPLANATION:" in line:
                        explanation = line.split("EXPLANATION:")[1].strip()
            else:
                # Fallback parsing
                if "TRUE" in result.upper()[:50] and "FALSE" not in result.upper()[:50]:
                    verdict = "TRUE"
                elif "FALSE" in result.upper()[:50]:
                    verdict = "FALSE"
            
            # Display result
            st.markdown("---")
            st.markdown("<h2 style='text-align: center; color: #00ffff;'>VERDICT</h2>", unsafe_allow_html=True)
            
            if verdict == "TRUE":
                st.markdown("<div class='verdict-true'>✅ TRUE</div>", unsafe_allow_html=True)
            elif verdict == "FALSE":
                st.markdown("<div class='verdict-false'>❌ FALSE</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='verdict-false'>❓ UNCLEAR</div>", unsafe_allow_html=True)
            
            # Display explanation
            st.markdown(f"<div class='explanation'><strong>Explanation:</strong><br>{explanation}</div>", unsafe_allow_html=True)
            
            # Show full response in expander
            with st.expander("🤖 Full AI Response"):
                st.text(result)
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Make sure your Groq API key is valid.")

elif analyze_button:
    st.warning("⚠️ Please enter a claim to analyze.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 20px;'>
    <p>Simple LLM-based fact checking - No complex pipeline required</p>
    <p>Powered by Groq AI</p>
</div>
""", unsafe_allow_html=True)
