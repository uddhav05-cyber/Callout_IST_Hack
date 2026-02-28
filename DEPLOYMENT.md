# Streamlit Cloud Deployment Guide

## Quick Deploy to Streamlit Cloud

### Step 1: Prepare Your Repository

1. Make sure `app_llm_only.py` is in your repository root
2. Use `requirements-simple.txt` instead of `requirements.txt` for deployment
3. Commit and push all changes to GitHub

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `uddhav05-cyber/Callout_IST_Hack`
5. Set these values:
   - **Branch**: `main`
   - **Main file path**: `app_llm_only.py`
   - **App URL**: Choose your custom URL
6. Click "Advanced settings"
7. Set **Python version**: `3.11`
8. Set **Requirements file**: `requirements-simple.txt`

### Step 3: Add Secrets

In the "Advanced settings" or after deployment in "App settings":

1. Click "Secrets"
2. Add your API key:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

3. Save

### Step 4: Deploy

Click "Deploy!" and wait for the app to build (2-3 minutes)

## Local Testing with Streamlit Secrets

Create `.streamlit/secrets.toml` (this file is gitignored):

```toml
GROQ_API_KEY = "your_api_key_here"
```

Then run:
```bash
streamlit run app_llm_only.py
```

## Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution**: Make sure you're using `requirements-simple.txt` in deployment settings

### Issue: "API Key not found"
**Solution**: Add GROQ_API_KEY in Streamlit Cloud secrets (Settings → Secrets)

### Issue: "App is too large"
**Solution**: Use `requirements-simple.txt` which excludes heavy packages like torch and transformers

### Issue: "Background image not loading"
**Solution**: The Unsplash image URL should work. If not, you can:
1. Upload an image to your repo (e.g., `assets/background.jpg`)
2. Update the URL in `app_llm_only.py` to use the local image

## Files for Deployment

- `app_llm_only.py` - Main application
- `requirements-simple.txt` - Minimal dependencies
- `.streamlit/config.toml` - Streamlit configuration
- `.streamlit/secrets.toml` - API keys (local only, not committed)

## Important Notes

1. **Never commit API keys** to GitHub
2. Use Streamlit Cloud secrets for production
3. The simple app (`app_llm_only.py`) doesn't need heavy ML packages
4. Deployment typically takes 2-3 minutes

## Alternative: Use .env file locally

For local development, you can still use `.env`:

```
GROQ_API_KEY=your_key_here
```

The app will automatically try Streamlit secrets first, then fall back to .env
