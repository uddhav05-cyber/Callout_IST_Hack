"""
Streamlit UI for Fake News Detection System.

This application provides a user-friendly interface for verifying article authenticity.
"""

import streamlit as st
from src.verification_pipeline import verifyArticle
from src.models import VerdictType
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Page configuration
st.set_page_config(
    page_title="Fake News Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .verdict-true {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
    }
    .verdict-false {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1rem;
        border-radius: 5px;
    }
    .verdict-misleading {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
    }
    .verdict-unverified {
        background-color: #e2e3e5;
        border-left: 5px solid #6c757d;
        padding: 1rem;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<div class="main-header">🔍 Fake News Detector</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">AI-powered article verification using Natural Language Inference</div>',
    unsafe_allow_html=True
)

# Sidebar with information
with st.sidebar:
    st.header("About")
    st.write("""
    This tool analyzes articles to detect misinformation by:
    - Extracting factual claims
    - Retrieving evidence from credible sources
    - Verifying claims using AI
    - Analyzing tone and manipulation
    - Generating comprehensive verdicts
    """)
    
    st.header("How It Works")
    st.write("""
    1. 🔍 **Extract Claims** - Identify factual statements
    2. 🌐 **Search Evidence** - Find credible sources
    3. 🤖 **Verify with AI** - Use NLI model to check
    4. 📊 **Analyze Tone** - Detect manipulation
    5. ✅ **Generate Verdict** - Transparent results
    """)
    
    st.header("Why Different?")
    st.success("""
    💡 **Unlike ChatGPT:**
    - We show EVIDENCE, not opinions
    - We verify against REAL sources
    - We show our REASONING
    - You can VERIFY our work
    """)
    
    st.header("Our Unique Features")
    st.markdown("""
    ✅ **Evidence-Based Verification**
    - Retrieves actual sources
    - Shows supporting/contradicting evidence
    
    ✅ **Source Credibility Scoring**
    - 46+ news sources rated
    - Trusted sources weighted higher
    
    ✅ **Claim-by-Claim Analysis**
    - Verifies each statement separately
    - Shows which parts are accurate
    
    ✅ **Tone Analysis**
    - Detects emotional manipulation
    - Separate from factual accuracy
    
    ✅ **Transparent Reasoning**
    - Evidence cards with sources
    - Confidence score breakdown
    - Exportable reports
    """)
    
    st.header("How to Use")
    st.write("""
    1. Choose input method (URL or Text)
    2. Enter article content
    3. Click 'Analyze Article'
    4. Review the detailed results
    """)
    
    st.header("Verdict Types")
    st.success("✓ TRUE - Claims are supported by evidence")
    st.error("✗ FALSE - Claims are contradicted by evidence")
    st.warning("⚠ MISLEADING - Mixed or partial truth")
    st.info("? UNVERIFIED - Insufficient evidence")

# Main content area
st.markdown("---")

# Add key features highlight
st.markdown("### ✨ What Makes Us Different")

feature_col1, feature_col2, feature_col3, feature_col4 = st.columns(4)

with feature_col1:
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background-color: #f0f2f6; border-radius: 10px;">
        <h3 style="margin: 0;">🔍</h3>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;"><strong>Evidence-Based</strong></p>
        <p style="margin: 0; font-size: 0.8rem; color: #666;">Real sources, not opinions</p>
    </div>
    """, unsafe_allow_html=True)

with feature_col2:
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background-color: #f0f2f6; border-radius: 10px;">
        <h3 style="margin: 0;">📊</h3>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;"><strong>Claim-by-Claim</strong></p>
        <p style="margin: 0; font-size: 0.8rem; color: #666;">Verify each statement</p>
    </div>
    """, unsafe_allow_html=True)

with feature_col3:
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background-color: #f0f2f6; border-radius: 10px;">
        <h3 style="margin: 0;">🎯</h3>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;"><strong>Transparent</strong></p>
        <p style="margin: 0; font-size: 0.8rem; color: #666;">See our reasoning</p>
    </div>
    """, unsafe_allow_html=True)

with feature_col4:
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background-color: #f0f2f6; border-radius: 10px;">
        <h3 style="margin: 0;">⚡</h3>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;"><strong>Fast & Free</strong></p>
        <p style="margin: 0; font-size: 0.8rem; color: #666;">Results in 30 seconds</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Input section with tabs
tab1, tab2 = st.tabs(["📰 URL Input", "📝 Text Input"])

with tab1:
    st.subheader("Enter Article URL")
    url_input = st.text_input(
        "Article URL",
        placeholder="https://example.com/article",
        help="Enter the full URL of the article you want to verify"
    )
    
    if st.button("Analyze Article from URL", key="url_button", type="primary"):
        if not url_input:
            st.error("Please enter a URL")
        elif not url_input.startswith(('http://', 'https://')):
            st.error("Please enter a valid URL starting with http:// or https://")
        else:
            st.session_state['input'] = url_input
            st.session_state['input_type'] = 'url'
            st.session_state['analyze'] = True

with tab2:
    st.subheader("Enter Article Text")
    text_input = st.text_area(
        "Article Text",
        placeholder="Paste the article text here...",
        height=200,
        help="Paste the full text of the article you want to verify"
    )
    
    if st.button("Analyze Article from Text", key="text_button", type="primary"):
        if not text_input or len(text_input.strip()) == 0:
            st.error("Please enter article text")
        elif len(text_input) > 50000:
            st.error("Article text is too long (max 50,000 characters)")
        else:
            st.session_state['input'] = text_input
            st.session_state['input_type'] = 'text'
            st.session_state['analyze'] = True

# Example articles section
st.markdown("---")
st.subheader("📚 Try Example Articles")
st.write("Test the system with these curated examples:")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("✅ Factual News", use_container_width=True):
        st.session_state['input'] = """
        The World Health Organization announced today that global COVID-19 cases have decreased 
        by 15% over the past month. According to WHO data, vaccination rates have increased 
        significantly in developing countries, contributing to the decline. Dr. Maria Santos, 
        WHO spokesperson, stated that this trend is encouraging but urged continued vigilance.
        The organization reported that over 70% of the global population has now received at least 
        one dose of a COVID-19 vaccine.
        """
        st.session_state['input_type'] = 'text'
        st.session_state['analyze'] = True
        st.rerun()

with col2:
    if st.button("❌ Fake News", use_container_width=True):
        st.session_state['input'] = """
        BREAKING: Scientists have discovered that drinking coffee cures cancer! A new study shows 
        that 100% of cancer patients who drank 10 cups of coffee per day were completely cured 
        within one week. Big Pharma is trying to hide this information because they don't want 
        you to know the truth. Doctors are shocked by these results but refuse to recommend this 
        simple cure. Share this before it gets deleted!
        """
        st.session_state['input_type'] = 'text'
        st.session_state['analyze'] = True
        st.rerun()

with col3:
    if st.button("⚠️ Misleading", use_container_width=True):
        st.session_state['input'] = """
        Crime rates have SKYROCKETED by 300% in the past year! The city is becoming increasingly 
        dangerous and unsafe. Residents are terrified to leave their homes. This alarming trend 
        shows that current policies have completely failed. The statistics are undeniable - 
        crime has increased from 2 incidents to 8 incidents in the downtown area.
        """
        st.session_state['input_type'] = 'text'
        st.session_state['analyze'] = True
        st.rerun()

with col4:
    if st.button("💭 Opinion Piece", use_container_width=True):
        st.session_state['input'] = """
        I think the new policy is the best decision ever made. In my opinion, everyone should 
        support this initiative. It seems like the perfect solution to all our problems. 
        I believe this will change everything for the better. My feeling is that this is 
        exactly what we need right now.
        """
        st.session_state['input_type'] = 'text'
        st.session_state['analyze'] = True
        st.rerun()

# Initialize session state
if 'analyze' not in st.session_state:
    st.session_state['analyze'] = False

# Analysis with progress indicators
if st.session_state.get('analyze', False):
    st.markdown("---")
    st.header("🔄 Analysis in Progress")
    
    # Create a progress container
    progress_container = st.container()
    
    with progress_container:
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Stage 1: Parsing article
            status_text.text("📄 Stage 1/5: Parsing article content...")
            progress_bar.progress(10)
            
            article_input = st.session_state['input']
            
            # Stage 2: Extracting claims
            status_text.text("🔍 Stage 2/5: Extracting factual claims from article...")
            progress_bar.progress(25)
            
            # Stage 3: Retrieving evidence
            status_text.text("🌐 Stage 3/5: Retrieving evidence from credible sources...")
            progress_bar.progress(45)
            
            # Stage 4: Verifying claims
            status_text.text("✓ Stage 4/5: Verifying claims using AI (NLI)...")
            progress_bar.progress(70)
            
            # Stage 5: Synthesizing verdict
            status_text.text("📊 Stage 5/5: Analyzing tone and synthesizing final verdict...")
            progress_bar.progress(90)
            
            # Call verification pipeline
            verdict = verifyArticle(article_input)
            
            # Complete
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            
            # Store verdict in session state for display
            st.session_state['verdict'] = verdict
            st.session_state['analyze'] = False
            
            st.success("Analysis complete! Scroll down to see results.")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
            logging.error(f"Verification error: {str(e)}", exc_info=True)
            st.session_state['analyze'] = False

# Display results if available
if 'verdict' in st.session_state:
    verdict = st.session_state['verdict']
    
    # Overall verdict display with enhanced styling
    st.subheader("📊 Overall Verdict")
    
    verdict_colors = {
        "LIKELY_TRUE": "success",
        "LIKELY_FALSE": "error",
        "MISLEADING": "warning",
        "UNVERIFIED": "info"
    }
    
    verdict_icons = {
        "LIKELY_TRUE": "✓",
        "LIKELY_FALSE": "✗",
        "MISLEADING": "⚠",
        "UNVERIFIED": "?"
    }
    
    verdict_value = verdict.overallVerdict.value if hasattr(verdict.overallVerdict, 'value') else str(verdict.overallVerdict)
    verdict_method = getattr(st, verdict_colors.get(verdict_value, "info"))
    verdict_method(
        f"{verdict_icons.get(verdict_value, '?')} {verdict_value} "
        f"(Confidence: {verdict.confidenceScore:.1f}%)"
    )
    
    # Enhanced metrics display with progress bars
    st.markdown("### 📈 Detailed Scores")
    
    # Add explanation of what these scores mean
    with st.expander("ℹ️ What do these scores mean?", expanded=False):
        st.write("""
        **Confidence Score:** Overall certainty in the verdict based on evidence quality and quantity
        
        **Factual Accuracy:** Percentage of claims supported by credible evidence
        
        **Emotional Manipulation:** Degree of sensationalism, fear-mongering, and manipulative language detected
        """)
    
    # Add confidence breakdown explanation
    with st.expander("🔍 How was the confidence score calculated?", expanded=False):
        if verdict.claimBreakdown:
            verified_claims = sum(1 for cv in verdict.claimBreakdown if cv.verdict == VerdictType.TRUE)
            total_claims = len(verdict.claimBreakdown)
            avg_credibility = sum(len(cv.supportingEvidence) for cv in verdict.claimBreakdown) / total_claims if total_claims > 0 else 0
            
            st.write(f"""
            **Confidence Score Breakdown ({verdict.confidenceScore:.1f}%):**
            
            - **Claims Verified:** {verified_claims}/{total_claims} claims supported by evidence
            - **Evidence Quality:** Average of {avg_credibility:.1f} evidence sources per claim
            - **Source Credibility:** Evidence from trusted sources weighted higher
            - **Tone Analysis:** Low emotional manipulation increases confidence
            
            **Formula:** 60% evidence match + 20% source credibility + 20% writing style
            """)
        else:
            st.write("No claims were extracted from this article for verification.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Confidence Score", f"{verdict.confidenceScore:.1f}%")
        st.progress(verdict.confidenceScore / 100)
    
    with col2:
        st.metric("Factual Accuracy", f"{verdict.factualAccuracyScore:.1f}%")
        st.progress(verdict.factualAccuracyScore / 100)
    
    with col3:
        st.metric("Emotional Manipulation", f"{verdict.emotionalManipulationScore:.1f}%")
        st.progress(verdict.emotionalManipulationScore / 100)
    
    # Add analysis statistics
    st.markdown("### 📊 Analysis Statistics")
    stat_col1, stat_col2, stat_col3 = st.columns(3)
    
    with stat_col1:
        st.metric("Claims Analyzed", len(verdict.claimBreakdown) if verdict.claimBreakdown else 0)
    
    with stat_col2:
        st.metric("Evidence Sources", len(verdict.evidenceCards) if verdict.evidenceCards else 0)
    
    with stat_col3:
        if verdict.claimBreakdown:
            true_claims = sum(1 for cv in verdict.claimBreakdown if cv.verdict == VerdictType.TRUE)
            st.metric("Verified Claims", f"{true_claims}/{len(verdict.claimBreakdown)}")
        else:
            st.metric("Verified Claims", "0/0")
    
    # Explanation
    st.markdown("### 💡 Explanation")
    st.info(verdict.explanation)
    
    # Add fact-check history simulation
    if verdict.claimBreakdown and len(verdict.claimBreakdown) > 0:
        st.markdown("### 📚 Related Fact-Checks")
        with st.expander("See if similar claims have been verified before", expanded=False):
            st.info("""
            **Feature Preview:** This section will show if similar claims have been fact-checked by:
            - Snopes
            - PolitiFact
            - FactCheck.org
            - AFP Fact Check
            
            **Coming Soon:** Integration with fact-checking databases to show historical verdicts on similar claims.
            
            **Why This Matters:** If a claim has been repeatedly debunked, it's likely misinformation that keeps resurfacing.
            """)
    
    # Add manipulation techniques detected
    if verdict.emotionalManipulationScore > 30:
        st.markdown("### ⚠️ Manipulation Techniques Detected")
        with st.expander("See detected manipulation techniques", expanded=False):
            manipulation_techniques = []
            
            if verdict.emotionalManipulationScore > 60:
                manipulation_techniques.append("🔴 **High Emotional Intensity** - Uses strong emotional language to influence readers")
            elif verdict.emotionalManipulationScore > 30:
                manipulation_techniques.append("🟡 **Moderate Emotional Language** - Contains some emotionally charged words")
            
            # Check for sensationalism based on score
            if verdict.emotionalManipulationScore > 50:
                manipulation_techniques.append("🔴 **Sensationalism** - Uses exaggerated or shocking language to grab attention")
            
            # Check for urgency/fear tactics
            if verdict.emotionalManipulationScore > 40:
                manipulation_techniques.append("🟡 **Urgency Tactics** - Creates false sense of urgency or fear")
            
            if manipulation_techniques:
                for technique in manipulation_techniques:
                    st.markdown(f"- {technique}")
                
                st.info("💡 **Educational Note:** These techniques are designed to bypass critical thinking. Always verify claims with evidence, regardless of how the article makes you feel.")
            else:
                st.success("✓ No significant manipulation techniques detected")
    
    # Add context checker
    st.markdown("### 🔎 Context Analysis")
    with st.expander("Check for missing context or statistical manipulation", expanded=False):
        context_warnings = []
        
        # Check for statistical claims without context
        if verdict.claimBreakdown:
            for claim in verdict.claimBreakdown:
                claim_text = claim.claim.text.lower()
                # Check for percentage/number claims
                if any(indicator in claim_text for indicator in ['%', 'percent', 'increased', 'decreased', 'rose', 'fell']):
                    if not any(context in claim_text for context in ['compared to', 'from', 'since', 'between']):
                        context_warnings.append(f"⚠️ Claim mentions statistics but may lack temporal context: '{claim.claim.text[:100]}...'")
        
        # Check for absolute statements
        if verdict.claimBreakdown:
            for claim in verdict.claimBreakdown:
                claim_text = claim.claim.text.lower()
                if any(absolute in claim_text for absolute in ['always', 'never', 'all', 'none', 'everyone', 'no one']):
                    context_warnings.append(f"⚠️ Claim uses absolute language which is rarely accurate: '{claim.claim.text[:100]}...'")
        
        if context_warnings:
            st.warning("**Potential Context Issues Detected:**")
            for warning in context_warnings[:3]:  # Limit to 3 warnings
                st.markdown(f"- {warning}")
            st.info("💡 **Tip:** Claims with statistics should include timeframes and baselines. Absolute statements ('always', 'never') are often oversimplifications.")
        else:
            st.success("✓ No obvious context issues detected")
    
    # Claim-by-claim breakdown with expandable sections
    if verdict.claimBreakdown and len(verdict.claimBreakdown) > 0:
        st.markdown("### 🔍 Claim-by-Claim Analysis")
        st.write(f"Found {len(verdict.claimBreakdown)} verifiable claims in the article:")
        
        for idx, claim_verdict in enumerate(verdict.claimBreakdown, 1):
            claim_text = claim_verdict.claim.text
            claim_verdict_value = claim_verdict.verdict.value if hasattr(claim_verdict.verdict, 'value') else str(claim_verdict.verdict)
            claim_confidence = claim_verdict.confidence
            
            # Color code based on verdict
            if claim_verdict_value == "TRUE":
                expander_label = f"✓ Claim {idx}: {claim_text[:80]}..." if len(claim_text) > 80 else f"✓ Claim {idx}: {claim_text}"
                border_color = "#28a745"
            elif claim_verdict_value == "FALSE":
                expander_label = f"✗ Claim {idx}: {claim_text[:80]}..." if len(claim_text) > 80 else f"✗ Claim {idx}: {claim_text}"
                border_color = "#dc3545"
            elif claim_verdict_value == "MISLEADING":
                expander_label = f"⚠ Claim {idx}: {claim_text[:80]}..." if len(claim_text) > 80 else f"⚠ Claim {idx}: {claim_text}"
                border_color = "#ffc107"
            else:
                expander_label = f"? Claim {idx}: {claim_text[:80]}..." if len(claim_text) > 80 else f"? Claim {idx}: {claim_text}"
                border_color = "#6c757d"
            
            with st.expander(expander_label, expanded=(idx == 1)):
                st.markdown(f"**Full Claim:** {claim_text}")
                st.markdown(f"**Verdict:** {claim_verdict_value} (Confidence: {claim_confidence:.1f}%)")
                st.progress(claim_confidence / 100)
                
                # Show supporting evidence
                if claim_verdict.supportingEvidence and len(claim_verdict.supportingEvidence) > 0:
                    st.markdown(f"**Supporting Evidence ({len(claim_verdict.supportingEvidence)}):**")
                    for ev in claim_verdict.supportingEvidence:
                        st.markdown(f"- [{ev.sourceDomain}]({ev.sourceURL}): {ev.snippet[:150]}...")
                
                # Show contradicting evidence
                if claim_verdict.contradictingEvidence and len(claim_verdict.contradictingEvidence) > 0:
                    st.markdown(f"**Contradicting Evidence ({len(claim_verdict.contradictingEvidence)}):**")
                    for ev in claim_verdict.contradictingEvidence:
                        st.markdown(f"- [{ev.sourceDomain}]({ev.sourceURL}): {ev.snippet[:150]}...")
    
    # Evidence cards display with visual separation
    if verdict.evidenceCards and len(verdict.evidenceCards) > 0:
        st.markdown("### 📑 Evidence Cards")
        st.write(f"Showing {len(verdict.evidenceCards)} evidence comparisons:")
        
        for idx, card in enumerate(verdict.evidenceCards, 1):
            relationship_value = card.relationship.value if hasattr(card.relationship, 'value') else str(card.relationship)
            
            # Color coding for relationship types
            if relationship_value == "SUPPORTS":
                card_color = "#d4edda"
                border_color = "#28a745"
                icon = "✓"
            elif relationship_value == "REFUTES":
                card_color = "#f8d7da"
                border_color = "#dc3545"
                icon = "✗"
            else:  # NEUTRAL
                card_color = "#e2e3e5"
                border_color = "#6c757d"
                icon = "○"
            
            st.markdown(f"""
            <div style="background-color: {card_color}; border-left: 5px solid {border_color}; 
                        padding: 1rem; border-radius: 5px; margin-bottom: 1rem;">
                <h4>{icon} Evidence Card {idx} - {relationship_value}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**Claim:**")
                st.write(card.claim)
            
            with col2:
                st.markdown("**Evidence:**")
                st.write(card.evidenceSnippet)
                st.markdown(f"**Source:** [{card.sourceName}]({card.sourceURL})")
            
            # Highlight discrepancies if any
            if card.highlightedDiscrepancies and len(card.highlightedDiscrepancies) > 0:
                st.markdown("**⚠️ Discrepancies Detected:**")
                for discrepancy in card.highlightedDiscrepancies:
                    st.markdown(f"- {discrepancy}")
    
    # Export functionality
    st.markdown("---")
    st.markdown("### 💾 Export & Share Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Export to JSON
        import json
        verdict_dict = verdict.model_dump(mode='json')
        json_str = json.dumps(verdict_dict, indent=2, default=str)
        st.download_button(
            label="📥 Download as JSON",
            data=json_str,
            file_name="verification_results.json",
            mime="application/json"
        )
    
    with col2:
        # Export to PDF (simplified text version)
        pdf_text = f"""
FAKE NEWS DETECTION REPORT
==========================

Overall Verdict: {verdict_value}
Confidence Score: {verdict.confidenceScore:.1f}%
Factual Accuracy: {verdict.factualAccuracyScore:.1f}%
Emotional Manipulation: {verdict.emotionalManipulationScore:.1f}%

EXPLANATION
-----------
{verdict.explanation}

CLAIM BREAKDOWN
---------------
"""
        if verdict.claimBreakdown:
            for idx, cv in enumerate(verdict.claimBreakdown, 1):
                cv_verdict = cv.verdict.value if hasattr(cv.verdict, 'value') else str(cv.verdict)
                pdf_text += f"\nClaim {idx}: {cv.claim.text}\n"
                pdf_text += f"Verdict: {cv_verdict} (Confidence: {cv.confidence:.1f}%)\n"
        
        st.download_button(
            label="📥 Download as Text Report",
            data=pdf_text,
            file_name="verification_results.txt",
            mime="text/plain"
        )
    
    with col3:
        # Generate shareable badge text
        verdict_emoji = verdict_icons.get(verdict_value, '?')
        badge_text = f"""
━━━━━━━━━━━━━━━━━━━━━━
   FACT-CHECK RESULT
━━━━━━━━━━━━━━━━━━━━━━

{verdict_emoji} {verdict_value}
Confidence: {verdict.confidenceScore:.0f}%
Factual Accuracy: {verdict.factualAccuracyScore:.0f}%

Verified by AI Fact-Checker
Evidence-based analysis
{len(verdict.claimBreakdown) if verdict.claimBreakdown else 0} claims verified

━━━━━━━━━━━━━━━━━━━━━━
"""
        st.download_button(
            label="📋 Copy Shareable Badge",
            data=badge_text,
            file_name="fact_check_badge.txt",
            mime="text/plain"
        )
    
    # Add comparison with ChatGPT
    st.markdown("---")
    st.markdown("### 🤖 Why This Is Better Than ChatGPT")
    
    comp_col1, comp_col2 = st.columns(2)
    
    with comp_col1:
        st.markdown("**❌ ChatGPT Approach:**")
        st.markdown("""
        - Gives opinions without evidence
        - No source citations
        - Can't verify against real sources
        - Prone to hallucination
        - No transparency in reasoning
        - Simple yes/no answers
        """)
    
    with comp_col2:
        st.markdown("**✅ Our Approach:**")
        st.markdown("""
        - Evidence-based verification
        - Shows actual sources with URLs
        - Retrieves real-time evidence
        - NLI model for fact-checking
        - Complete transparency
        - Claim-by-claim breakdown
        """)
    
    st.success("💡 **Key Difference:** We don't tell you what to think - we show you the evidence and let you decide!")
    
    # Add technical details section
    with st.expander("🔬 Technical Details (For Developers)", expanded=False):
        st.markdown("""
        **Our Verification Pipeline:**
        
        1. **Claim Extraction** - LLM-based extraction of factual claims
        2. **Evidence Retrieval** - Multi-source search using Serper API
        3. **NLI Verification** - BART-large-mnli model for entailment checking
        4. **Source Credibility** - Database of 46+ sources with credibility scores
        5. **Tone Analysis** - Separate analysis of emotional manipulation
        6. **Synthesis** - Weighted scoring: 60% evidence + 20% credibility + 20% tone
        
        **Technologies Used:**
        - Python + Streamlit (UI)
        - LangChain + Groq API (LLM)
        - HuggingFace Transformers (NLI)
        - Serper API (Search)
        - BeautifulSoup (Parsing)
        
        **Why This Matters:**
        Unlike ChatGPT which just generates text, we use a systematic pipeline that retrieves real evidence, 
        verifies it with NLI models, and provides transparent reasoning. Every verdict is backed by actual sources.
        """)
    
    # Clear results button
    st.markdown("---")
    if st.button("🔄 Analyze Another Article", type="primary"):
        del st.session_state['verdict']
        st.rerun()

# Footer with statistics and CTA
st.markdown("---")
st.markdown("### 📊 System Capabilities")

footer_col1, footer_col2, footer_col3, footer_col4 = st.columns(4)

with footer_col1:
    st.metric("Source Database", "46+ sources", help="Credibility-rated news sources")

with footer_col2:
    st.metric("Analysis Speed", "< 30 sec", help="Average time for 5-10 claims")

with footer_col3:
    st.metric("Verification Method", "NLI + Search", help="BART-large-mnli + Serper API")

with footer_col4:
    st.metric("Transparency", "100%", help="All sources and reasoning shown")

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background-color: #f0f2f6; border-radius: 10px;">
    <h3>🎯 Built for Truth, Powered by AI</h3>
    <p style="color: #666; margin-bottom: 1rem;">
        This system combines LLM-based claim extraction, multi-source evidence retrieval, 
        NLI verification, and source credibility analysis to provide transparent, evidence-based fact-checking.
    </p>
    <p style="color: #666; font-size: 0.9rem;">
        <strong>Unlike ChatGPT:</strong> We don't just give opinions - we show you the evidence and let you decide.
    </p>
</div>
""", unsafe_allow_html=True)
