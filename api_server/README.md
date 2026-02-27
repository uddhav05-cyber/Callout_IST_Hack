# Callout Self-Hosted API Server

## Overview

This is a self-hosted API server for the Callout fake news detection system. It eliminates the need for external API keys by providing:

- **Local LLM inference** using Ollama (Llama, Mistral, etc.)
- **Free web search** using DuckDuckGo (no API key needed)
- **RESTful API** compatible with the main Callout application

## Quick Start

### Using Docker (Recommended)

```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

### Manual Setup

See [SELF_HOSTED_API_SETUP.md](../SELF_HOSTED_API_SETUP.md) for detailed instructions.

## API Endpoints

### Health Check
```
GET /health
```

### Extract Claims
```
POST /api/v1/extract-claims
Content-Type: application/json

{
  "article_text": "Article text here...",
  "language": "en",
  "max_claims": 10
}
```

### Search
```
POST /api/v1/search
Content-Type: application/json

{
  "query": "search query",
  "max_results": 10
}
```

### Generate API Key
```
POST /api/v1/generate-api-key
```

## Configuration

Edit `.env` file:

```bash
# Server settings
PORT=8000

# LLM backend (ollama or transformers)
LLM_BACKEND=ollama
LLM_MODEL=llama3.2:3b

# Optional: API key for authentication
API_KEY=your_api_key_here
```

## Supported Models

### Ollama Models (Recommended)

| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| llama3.2:3b | 3B | Fast | Good |
| mistral:7b | 7B | Medium | Great |
| llama3.1:8b | 8B | Medium | Great |

### Hugging Face Models

| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| microsoft/Phi-3-mini-4k-instruct | 3.8B | Fast | Good |
| meta-llama/Llama-2-7b-chat-hf | 7B | Medium | Great |

## Architecture

```
┌─────────────────┐
│  Streamlit App  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI API   │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│ Ollama │ │DuckDuckGo│
└────────┘ └──────────┘
```

## Development

### Run in Development Mode

```bash
python app.py
```

### Run Tests

```bash
pytest tests/
```

### View Logs

```bash
# Docker
docker-compose logs -f api

# Manual
# Check terminal output
```

## Production Deployment

### Docker Compose (Recommended)

```bash
docker-compose up -d
```

### Kubernetes

See `k8s/` directory for Kubernetes manifests (coming soon).

### Cloud Deployment

- **AWS**: Use EC2 + Docker
- **GCP**: Use Cloud Run
- **Azure**: Use Container Instances

## Performance

### Benchmarks

| Operation | Time (avg) | Hardware |
|-----------|-----------|----------|
| Claim Extraction | 3-5s | CPU (8 cores) |
| Claim Extraction | 1-2s | GPU (NVIDIA T4) |
| Search | 1-2s | Any |

### Optimization Tips

1. Use GPU for faster inference
2. Use smaller models (llama3.2:3b) for speed
3. Enable caching for repeated queries
4. Use load balancer for high traffic

## Troubleshooting

### Port Already in Use

Change `PORT` in `.env` file.

### Ollama Not Found

```bash
docker exec -it callout-ollama ollama list
```

### Slow Response

- Use smaller model
- Enable GPU acceleration
- Increase Docker memory

## License

MIT

## Support

- Documentation: [SELF_HOSTED_API_SETUP.md](../SELF_HOSTED_API_SETUP.md)
- Issues: GitHub Issues
