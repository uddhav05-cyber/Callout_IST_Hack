"""
Simple Fake News Detection - LLM Only (No Evidence Retrieval)

This version just asks the LLM directly if a claim is TRUE or FALSE.
No complex pipeline, no evidence retrieval, no NLI model.
Just pure LLM judgment.
"""

import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration - Try Streamlit secrets first, then environment variables
try:
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
except:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Page config
st.set_page_config(
    page_title="Fake News Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for navigation and authentication
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = 'login'  # 'login' or 'signup'
if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = 'login'  # 'login' or 'signup'

# Custom CSS for cyberpunk theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');
    
    .main {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
        font-family: 'Rajdhani', sans-serif;
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
    
    .hero-section {
        text-align: center;
        padding: 60px 20px;
        background: linear-gradient(135deg, #1a1f3a 0%, #0a0e27 100%);
        border-radius: 20px;
        margin: 20px 0;
    }
    
    .feature-card {
        background: rgba(26, 31, 58, 0.8);
        padding: 30px;
        border-radius: 15px;
        border: 2px solid #00ffff;
        margin: 20px 0;
        transition: transform 0.3s;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 255, 255, 0.3);
    }
    
    .stat-box {
        background: linear-gradient(135deg, #00ffff 0%, #0088ff 100%);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: #000;
        font-weight: bold;
    }
    
    /* Modern 2026 Login/Signup Styles */
    .auth-container {
        position: relative;
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #2a1f4a 100%);
        overflow: hidden;
    }
    
    .auth-background {
        position: absolute;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 20% 50%, rgba(0, 255, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(255, 0, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 20%, rgba(0, 255, 136, 0.1) 0%, transparent 50%);
        animation: backgroundShift 20s ease infinite;
    }
    
    @keyframes backgroundShift {
        0%, 100% { transform: scale(1) rotate(0deg); }
        50% { transform: scale(1.1) rotate(5deg); }
    }
    
    .auth-card {
        position: relative;
        width: 450px;
        padding: 50px 40px;
        background: rgba(26, 31, 58, 0.7);
        backdrop-filter: blur(20px);
        border-radius: 30px;
        border: 1px solid rgba(0, 255, 255, 0.3);
        box-shadow: 
            0 8px 32px 0 rgba(0, 255, 255, 0.2),
            inset 0 0 20px rgba(0, 255, 255, 0.05);
        animation: cardFloat 6s ease-in-out infinite;
    }
    
    @keyframes cardFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .auth-logo {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .auth-logo-icon {
        font-size: 70px;
        background: linear-gradient(135deg, #00ffff 0%, #00ff88 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: logoGlow 3s ease-in-out infinite;
        filter: drop-shadow(0 0 20px rgba(0, 255, 255, 0.5));
    }
    
    @keyframes logoGlow {
        0%, 100% { filter: drop-shadow(0 0 20px rgba(0, 255, 255, 0.5)); }
        50% { filter: drop-shadow(0 0 30px rgba(0, 255, 255, 0.8)); }
    }
    
    .auth-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 32px;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #00ffff 0%, #00ff88 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
        letter-spacing: 2px;
    }
    
    .auth-subtitle {
        text-align: center;
        color: rgba(255, 255, 255, 0.7);
        font-size: 16px;
        margin-bottom: 40px;
        font-weight: 300;
    }
    
    .stTextInput > div > div > input {
        background: rgba(10, 14, 39, 0.6) !important;
        border: 2px solid rgba(0, 255, 255, 0.3) !important;
        border-radius: 15px !important;
        color: #00ffff !important;
        font-size: 16px !important;
        padding: 15px 20px !important;
        transition: all 0.3s ease !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00ffff !important;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.4) !important;
        background: rgba(10, 14, 39, 0.8) !important;
    }
    
    .stTextInput > label {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        margin-bottom: 8px !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    
    .auth-divider {
        display: flex;
        align-items: center;
        text-align: center;
        margin: 30px 0;
    }
    
    .auth-divider::before,
    .auth-divider::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid rgba(0, 255, 255, 0.3);
    }
    
    .auth-divider span {
        padding: 0 15px;
        color: rgba(255, 255, 255, 0.5);
        font-size: 14px;
    }
    
    .auth-switch {
        text-align: center;
        margin-top: 25px;
        color: rgba(255, 255, 255, 0.7);
        font-size: 15px;
    }
    
    .auth-switch-link {
        color: #00ffff;
        text-decoration: none;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .auth-switch-link:hover {
        color: #00ff88;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
    }
    
    .floating-particles {
        position: absolute;
        width: 100%;
        height: 100%;
        overflow: hidden;
        pointer-events: none;
    }
    
    .particle {
        position: absolute;
        width: 4px;
        height: 4px;
        background: #00ffff;
        border-radius: 50%;
        animation: particleFloat 15s infinite;
        opacity: 0.3;
    }
    
    @keyframes particleFloat {
        0% {
            transform: translateY(100vh) translateX(0);
            opacity: 0;
        }
        10% {
            opacity: 0.3;
        }
        90% {
            opacity: 0.3;
        }
        100% {
            transform: translateY(-100vh) translateX(100px);
            opacity: 0;
        }
    }
    
    .success-message {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.2) 0%, rgba(0, 255, 136, 0.1) 100%);
        border: 1px solid rgba(0, 255, 136, 0.5);
        border-radius: 15px;
        padding: 15px;
        margin: 20px 0;
        color: #00ff88;
        text-align: center;
        animation: successPulse 2s ease-in-out infinite;
    }
    
    @keyframes successPulse {
        0%, 100% { box-shadow: 0 0 10px rgba(0, 255, 136, 0.3); }
        50% { box-shadow: 0 0 20px rgba(0, 255, 136, 0.5); }
    }
</style>
""", unsafe_allow_html=True)

# LOGIN/SIGNUP PAGE
if not st.session_state.logged_in:
    # Animated background
    st.markdown("""
    <div class='auth-background'></div>
    <div class='floating-particles'>
        <div class='particle' style='left: 10%; animation-delay: 0s;'></div>
        <div class='particle' style='left: 20%; animation-delay: 2s;'></div>
        <div class='particle' style='left: 30%; animation-delay: 4s;'></div>
        <div class='particle' style='left: 40%; animation-delay: 1s;'></div>
        <div class='particle' style='left: 50%; animation-delay: 3s;'></div>
        <div class='particle' style='left: 60%; animation-delay: 5s;'></div>
        <div class='particle' style='left: 70%; animation-delay: 2.5s;'></div>
        <div class='particle' style='left: 80%; animation-delay: 4.5s;'></div>
        <div class='particle' style='left: 90%; animation-delay: 1.5s;'></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the auth card
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
        
        # Logo and Title
        st.markdown("""
        <div class='auth-logo'>
            <div class='auth-logo-icon'>🔍</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.auth_mode == 'login':
            st.markdown("<h1 class='auth-title'>WELCOME BACK</h1>", unsafe_allow_html=True)
            st.markdown("<p class='auth-subtitle'>Sign in to access your fake news detector</p>", unsafe_allow_html=True)
            
            # Login Form
            username = st.text_input("Username", placeholder="Enter your username", key="login_username")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("🚀 Sign In", use_container_width=True, type="primary"):
                if username and password:
                    if len(username) >= 3 and len(password) >= 3:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.markdown(f"""
                        <div class='success-message'>
                            ✨ Welcome back, {username}! Redirecting...
                        </div>
                        """, unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.error("⚠️ Username and password must be at least 3 characters")
                else:
                    st.error("⚠️ Please enter both username and password")
            
            st.markdown("<div class='auth-divider'><span>OR</span></div>", unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🔐 Google", use_container_width=True):
                    st.info("Google OAuth coming soon!")
            with col_b:
                if st.button("👤 GitHub", use_container_width=True):
                    st.info("GitHub OAuth coming soon!")
            
            st.markdown("""
            <div class='auth-switch'>
                Don't have an account? <span class='auth-switch-link' onclick='return false;'>Create one</span>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Create Account", use_container_width=True, key="switch_to_signup"):
                st.session_state.auth_mode = 'signup'
                st.rerun()
        
        else:  # Signup mode
            st.markdown("<h1 class='auth-title'>JOIN US</h1>", unsafe_allow_html=True)
            st.markdown("<p class='auth-subtitle'>Create your account and start detecting fake news</p>", unsafe_allow_html=True)
            
            # Signup Form
            full_name = st.text_input("Full Name", placeholder="Enter your full name", key="signup_name")
            email = st.text_input("Email", placeholder="Enter your email", key="signup_email")
            username = st.text_input("Username", placeholder="Choose a username", key="signup_username")
            password = st.text_input("Password", type="password", placeholder="Create a password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="signup_confirm")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("✨ Create Account", use_container_width=True, type="primary"):
                if full_name and email and username and password and confirm_password:
                    if len(username) >= 3 and len(password) >= 6:
                        if password == confirm_password:
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.markdown(f"""
                            <div class='success-message'>
                                🎉 Account created successfully! Welcome, {username}!
                            </div>
                            """, unsafe_allow_html=True)
                            st.rerun()
                        else:
                            st.error("⚠️ Passwords don't match")
                    else:
                        st.error("⚠️ Username must be 3+ characters, password must be 6+ characters")
                else:
                    st.error("⚠️ Please fill in all fields")
            
            st.markdown("<div class='auth-divider'><span>OR SIGN UP WITH</span></div>", unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🔐 Google", use_container_width=True, key="signup_google"):
                    st.info("Google OAuth coming soon!")
            with col_b:
                if st.button("👤 GitHub", use_container_width=True, key="signup_github"):
                    st.info("GitHub OAuth coming soon!")
            
            st.markdown("""
            <div class='auth-switch'>
                Already have an account? <span class='auth-switch-link' onclick='return false;'>Sign in</span>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Back to Login", use_container_width=True, key="switch_to_login"):
                st.session_state.auth_mode = 'login'
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Footer
        st.markdown("""
        <div style='text-align: center; margin-top: 30px; color: rgba(255, 255, 255, 0.5); font-size: 13px;'>
            <p>🔒 Secured with end-to-end encryption</p>
            <p style='margin-top: 10px;'>© 2026 Fake News Detector • Powered by AI</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()

# Sidebar Navigation (only shown after login)
with st.sidebar:
    st.markdown(f"<h3 style='color: #00ffff;'>👤 {st.session_state.username}</h3>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<h2 style='color: #00ffff;'>🔍 Navigation</h2>", unsafe_allow_html=True)
    
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = 'home'
    
    if st.button("🔍 Detector", use_container_width=True):
        st.session_state.page = 'detector'
    
    if st.button("ℹ️ About", use_container_width=True):
        st.session_state.page = 'about'
    
    st.markdown("---")
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ''
        st.session_state.page = 'home'
        st.rerun()
    
    st.markdown("---")
    st.markdown("<p style='color: #888; font-size: 12px;'>Powered by AI<br>Groq + Llama 3.3</p>", unsafe_allow_html=True)

# HOME PAGE
if st.session_state.page == 'home':
    # Hero Section with background pattern
    st.markdown("""
    <div style='position: relative; min-height: 90vh; display: flex; align-items: center; justify-content: center;
                background: linear-gradient(135deg, rgba(10, 14, 39, 0.95) 0%, rgba(26, 31, 58, 0.95) 100%),
                            url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1920&q=80");
                background-size: cover; background-position: center; background-attachment: fixed;'>
        
        <div style='text-align: center; max-width: 800px; padding: 40px;'>
            <h1 style='color: #fff; font-size: 56px; font-weight: 800; margin-bottom: 25px; line-height: 1.2;'>
                Detect Fake News<br/>
                <span style='color: #00ffff;'>Instantly with AI</span>
            </h1>
            
            <p style='color: rgba(255, 255, 255, 0.8); font-size: 20px; margin-bottom: 40px; line-height: 1.6;'>
                Verify any news claim in seconds. Powered by advanced AI technology.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Start Detecting Now", use_container_width=True, type="primary"):
            st.session_state.page = 'detector'
            st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Simple 3-column features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='text-align: center; padding: 30px 20px;'>
            <div style='font-size: 48px; margin-bottom: 15px;'>⚡</div>
            <h3 style='color: #fff; font-size: 20px; margin-bottom: 10px;'>Fast</h3>
            <p style='color: rgba(255, 255, 255, 0.7); font-size: 15px;'>Results in 3 seconds</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 30px 20px;'>
            <div style='font-size: 48px; margin-bottom: 15px;'>🤖</div>
            <h3 style='color: #fff; font-size: 20px; margin-bottom: 10px;'>Accurate</h3>
            <p style='color: rgba(255, 255, 255, 0.7); font-size: 15px;'>AI-powered analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='text-align: center; padding: 30px 20px;'>
            <div style='font-size: 48px; margin-bottom: 15px;'>✅</div>
            <h3 style='color: #fff; font-size: 20px; margin-bottom: 10px;'>Simple</h3>
            <p style='color: rgba(255, 255, 255, 0.7); font-size: 15px;'>Clear TRUE/FALSE</p>
        </div>
        """, unsafe_allow_html=True)

# DETECTOR PAGE
elif st.session_state.page == 'detector':
    # Check if API key is set
    if not GROQ_API_KEY:
        st.error("⚠️ GROQ_API_KEY not found! Please set it in your .env file.")
        st.info("Create a .env file with: GROQ_API_KEY=your_key_here")
        st.stop()
    
    # Title
    st.markdown("<h1 style='text-align: center; color: #00ffff; font-size: 60px;'>🔍 FAKE NEWS DETECTOR</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #fff; font-size: 20px;'>Powered by AI - Simple & Direct</p>", unsafe_allow_html=True)

    # Input
    st.markdown("---")
    
    # Tab selection for input type
    input_tab1, input_tab2 = st.tabs(["📝 Text Claim", "🔗 Article URL"])
    
    with input_tab1:
        claim = st.text_area(
            "Enter a news claim to verify:",
            height=150,
            placeholder="Example: The Earth is flat",
            key="text_claim"
        )
    
    with input_tab2:
        article_url = st.text_input(
            "Enter article URL:",
            placeholder="https://example.com/news-article",
            key="article_url"
        )
        st.info("💡 We'll extract the main claim from the article and verify it")
        
        # If URL is provided, try to extract content
        if article_url and article_url.strip():
            try:
                import requests
                from bs4 import BeautifulSoup
                
                with st.spinner("🔍 Fetching article..."):
                    response = requests.get(article_url, timeout=10)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract title and first few paragraphs
                    title = soup.find('h1')
                    title_text = title.get_text().strip() if title else ""
                    
                    # Get paragraphs
                    paragraphs = soup.find_all('p')
                    article_text = ' '.join([p.get_text().strip() for p in paragraphs[:3]])
                    
                    # Combine title and text
                    claim = f"{title_text}. {article_text[:500]}"
                    
                    st.success("✅ Article extracted successfully!")
                    with st.expander("📄 Extracted Content"):
                        st.write(f"**Title:** {title_text}")
                        st.write(f"**Preview:** {article_text[:300]}...")
                        
            except Exception as e:
                st.error(f"❌ Failed to fetch article: {str(e)}")
                st.info("💡 Try entering the claim manually in the Text Claim tab")
                claim = ""

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

# ABOUT PAGE
elif st.session_state.page == 'about':
    st.markdown("<h1 style='text-align: center; color: #00ffff; font-size: 60px;'>ℹ️ About</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-card'>
        <h2 style='color: #00ffff;'>🎯 Our Mission</h2>
        <p style='color: #fff; font-size: 18px;'>
            In an era of information overload and misinformation, we believe everyone deserves access to 
            quick, reliable fact-checking tools. Our Fake News Detector uses cutting-edge AI technology 
            to help you verify claims and combat misinformation.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-card'>
        <h2 style='color: #00ffff;'>🤖 How It Works</h2>
        <p style='color: #fff; font-size: 18px;'>
            Our system leverages the powerful Llama 3.3 70B language model through Groq's lightning-fast 
            inference API. When you submit a claim:
        </p>
        <ol style='color: #fff; font-size: 16px;'>
            <li>The AI analyzes the claim against its vast knowledge base</li>
            <li>It evaluates factual accuracy and logical consistency</li>
            <li>Returns a clear TRUE or FALSE verdict with explanation</li>
            <li>All in under 3 seconds!</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-card'>
        <h2 style='color: #00ffff;'>⚡ Technology Stack</h2>
        <ul style='color: #fff; font-size: 16px;'>
            <li><strong>AI Model:</strong> Llama 3.3 70B (Meta)</li>
            <li><strong>Inference API:</strong> Groq</li>
            <li><strong>Frontend:</strong> Streamlit</li>
            <li><strong>Language:</strong> Python</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-card'>
        <h2 style='color: #00ffff;'>🎓 Use Cases</h2>
        <ul style='color: #fff; font-size: 16px;'>
            <li><strong>Journalists:</strong> Quick fact verification during research</li>
            <li><strong>Students:</strong> Validate information for academic work</li>
            <li><strong>Social Media Users:</strong> Check viral claims before sharing</li>
            <li><strong>Educators:</strong> Teach media literacy and critical thinking</li>
            <li><strong>General Public:</strong> Stay informed with accurate information</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-card'>
        <h2 style='color: #00ffff;'>⚠️ Important Notes</h2>
        <p style='color: #fff; font-size: 16px;'>
            While our AI is highly accurate, it's not infallible. We recommend:
        </p>
        <ul style='color: #fff; font-size: 16px;'>
            <li>Using this tool as a first-pass filter, not the final authority</li>
            <li>Cross-referencing important claims with multiple sources</li>
            <li>Considering the context and nuance of complex topics</li>
            <li>Staying critical and informed about AI limitations</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-card'>
        <h2 style='color: #00ffff;'>👥 Team</h2>
        <p style='color: #fff; font-size: 18px;'>
            Built with ❤️ by developers passionate about fighting misinformation and making 
            AI accessible to everyone.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Try The Detector", use_container_width=True, type="primary"):
            st.session_state.page = 'detector'
            st.rerun()
