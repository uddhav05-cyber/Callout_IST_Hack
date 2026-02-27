# Self-Hosted API Setup Guide

## 🎉 No More External API Dependencies!

This guide shows you how to run Callout with your own self-hosted API, eliminating the need for:
- ❌ OpenAI API keys ($$$)
- ❌ Groq API keys
- ❌ Serper.dev API keys ($$$)
- ❌ Tavily API keys ($$$)

Instead, you'll use:
- ✅ **Ollama** (free, local LLM inference)
- ✅ **DuckDuckGo** (free, no API key needed)
- ✅ **Your own API server** (full control!)

---

## 📋 Prerequisites

1. **Docker & Docker Compose** (recommended) OR
2. **Python 3.11+** and **Ollama** installed locally

---

## 🚀 Quick Start (Docker - Recommended)

### Step 1: Navigate to API Server Directory

```bash
cd api_server
```

### Step 2: Start Services with Docker Compose

```bash
docker-compose up -d
```

This will start:
- **Ollama** service (port 11434) - for LLM inference
- **API server** (port 8000) - your self-hosted API

### Step 3: Pull LLM Model

```bash
# Pull Llama 3.2 (3B parameters - fast and efficient)
docker exec -it callout-ollama ollama pull llama3.2:3b

# Or use Mistral (7B parameters - more powerful)
# docker exec -it callout-ollama ollama pull mistral:7b
```

### Step 4: Test API Server

```bash
curl http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "timestamp": "2024-...",
  "services": {
    "llm": true,
    "search": true
  }
}
```

### Step 5: Configure Main Application

Update your `.env` file in the main project directory:

```bash
# Enable self-hosted API
USE_SELF_HOSTED_API=true
SELF_HOSTED_API_URL=http://localhost:8000

# Optional: Generate and use API key for authentication
# SELF_HOSTED_API_KEY=your_generated_key_here

# External API keys are now OPTIONAL (not needed!)
# OPENAI_API_KEY=
# GROQ_API_KEY=
# SERPER_API_KEY=
# TAVILY_API_KEY=
```

### Step 6: Run Callout

```bash
cd ..  # Back to main directory
streamlit run app.py
```

That's it! Callout now uses your self-hosted API! 🎉

---

## 🛠️ Manual Setup (Without Docker)

### Step 1: Install Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from https://ollama.com/download

### Step 2: Start Ollama Service

```bash
ollama serve
```

### Step 3: Pull LLM Model

```bash
ollama pull llama3.2:3b
```

### Step 4: Install API Server Dependencies

```bash
cd api_server
pip install -r requirements.txt
```

### Step 5: Configure API Server

Create `.env` file in `api_server/`:

```bash
cp .env.example .env
```

Edit `.env`:
```
PORT=8000
LLM_BACKEND=ollama
LLM_MODEL=llama3.2:3b
```

### Step 6: Start API Server

```bash
python app.py
```

### Step 7: Configure Main Application

Same as Docker Step 5 above.

---

## 🧪 Testing Your API

### Test Claim Extraction

```bash
curl -X POST http://localhost:8000/api/v1/extract-claims \
  -H "Content-Type: application/json" \
  -d '{
    "article_text": "The president announced today that the economy grew by 5% in the last quarter. According to official data, unemployment fell to 8%.",
    "language": "en",
    "max_claims": 10
  }'
```

### Test Search

```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "economy growth 5 percent",
    "max_results": 5
  }'
```

---

## 🔧 Configuration Options

### LLM Models (Ollama)

Choose based on your hardware:

| Model | Size | Speed | Quality | RAM Required |
|-------|------|-------|---------|--------------|
| `llama3.2:3b` | 3B | ⚡⚡⚡ Fast | ⭐⭐⭐ Good | 4GB |
| `mistral:7b` | 7B | ⚡⚡ Medium | ⭐⭐⭐⭐ Great | 8GB |
| `llama3.1:8b` | 8B | ⚡⚡ Medium | ⭐⭐⭐⭐ Great | 8GB |
| `llama3.1:70b` | 70B | ⚡ Slow | ⭐⭐⭐⭐⭐ Excellent | 64GB |

**Recommended for most users:** `llama3.2:3b` (fast, efficient, good quality)

### Change Model

Edit `api_server/.env`:
```
LLM_MODEL=mistral:7b
```

Then restart API server:
```bash
docker-compose restart api
# OR
# Ctrl+C and python app.py
```

---

## 🔐 API Key Authentication (Optional)

### Generate API Key

```bash
curl -X POST http://localhost:8000/api/v1/generate-api-key
```

Response:
```json
{
  "api_key": "callout_abc123...",
  "created_at": "2024-...",
  "note": "Store this key securely. It won't be shown again."
}
```

### Use API Key

Update `.env` in main project:
```
SELF_HOSTED_API_KEY=callout_abc123...
```

---

## 📊 Performance Comparison

### External APIs (Before)

| Operation | Time | Cost |
|-----------|------|------|
| Claim Extraction | 2-5s | $0.002/request |
| Search | 1-3s | $0.001/request |
| **Total per article** | **3-8s** | **~$0.05** |

### Self-Hosted API (After)

| Operation | Time | Cost |
|-----------|------|------|
| Claim Extraction | 3-10s* | $0 |
| Search | 1-2s | $0 |
| **Total per article** | **4-12s** | **$0** |

*Depends on hardware and model size

### Cost Savings

- **100 articles/day**: Save ~$5/day = **$150/month**
- **1000 articles/day**: Save ~$50/day = **$1,500/month**

---

## 🚀 Production Deployment

### Deploy to Cloud

#### Option 1: AWS EC2

1. Launch EC2 instance (t3.medium or larger)
2. Install Docker
3. Clone your repo
4. Run `docker-compose up -d`
5. Configure security groups (port 8000)

#### Option 2: Google Cloud Run

1. Build Docker image
2. Push to Google Container Registry
3. Deploy to Cloud Run
4. Set environment variables

#### Option 3: DigitalOcean Droplet

1. Create Droplet (4GB RAM minimum)
2. Install Docker
3. Clone your repo
4. Run `docker-compose up -d`

### Scaling

For high traffic, use:
- **Load balancer** (nginx, HAProxy)
- **Multiple API instances** (docker-compose scale)
- **GPU acceleration** (for faster LLM inference)

---

## 🐛 Troubleshooting

### API Server Won't Start

**Check logs:**
```bash
docker-compose logs api
```

**Common issues:**
- Port 8000 already in use → Change PORT in .env
- Ollama not running → Check `docker-compose logs ollama`

### Ollama Model Not Found

**Pull the model:**
```bash
docker exec -it callout-ollama ollama pull llama3.2:3b
```

### Slow Response Times

**Solutions:**
1. Use smaller model (llama3.2:3b instead of mistral:7b)
2. Enable GPU acceleration (uncomment in docker-compose.yml)
3. Increase Docker memory limit

### Search Not Working

**Check DuckDuckGo:**
```bash
pip install duckduckgo-search
python -c "from duckduckgo_search import DDGS; print(list(DDGS().text('test', max_results=1)))"
```

---

## 🎓 Advanced Configuration

### Use Hugging Face Transformers Instead of Ollama

Edit `api_server/.env`:
```
LLM_BACKEND=transformers
HF_MODEL=microsoft/Phi-3-mini-4k-instruct
```

Install additional dependencies:
```bash
pip install transformers torch
```

### Enable GPU Acceleration

Uncomment in `docker-compose.yml`:
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

### Custom Prompts

Edit `api_server/services/llm_service.py` → `_build_claim_extraction_prompt()`

---

## 📈 Monitoring

### Check API Health

```bash
curl http://localhost:8000/health
```

### View Logs

```bash
# Docker
docker-compose logs -f api

# Manual
# Check terminal where you ran python app.py
```

### Metrics (Optional)

Add Prometheus/Grafana for production monitoring.

---

## 🎉 Benefits Summary

### Cost Savings
- ✅ **$0 per request** (vs $0.05 with external APIs)
- ✅ **No rate limits**
- ✅ **No monthly subscription fees**

### Privacy & Control
- ✅ **Data stays on your server** (no external API calls)
- ✅ **Full control over models and prompts**
- ✅ **No vendor lock-in**

### Customization
- ✅ **Choose your own LLM models**
- ✅ **Customize prompts for your use case**
- ✅ **Add custom features easily**

---

## 🆘 Support

### Issues?

1. Check logs: `docker-compose logs`
2. Verify health: `curl http://localhost:8000/health`
3. Test Ollama: `docker exec -it callout-ollama ollama list`

### Need Help?

- GitHub Issues: [your-repo]/issues
- Documentation: This file!

---

## 📚 Next Steps

1. ✅ Set up self-hosted API (you're here!)
2. ⬜ Test with sample articles
3. ⬜ Deploy to production
4. ⬜ Monitor performance
5. ⬜ Customize for your needs

---

**Congratulations! You now have a fully self-hosted fake news detection system!** 🎉

No more external API dependencies. No more costs. Full control. 🚀

