#!/bin/bash

# Quick start script for self-hosted API

echo "🚀 Starting Callout Self-Hosted API..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Start services
echo "📦 Starting Docker containers..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 5

# Check if Ollama is running
if docker ps | grep -q callout-ollama; then
    echo "✅ Ollama service is running"
else
    echo "❌ Ollama service failed to start"
    exit 1
fi

# Check if API is running
if docker ps | grep -q callout-api; then
    echo "✅ API service is running"
else
    echo "❌ API service failed to start"
    exit 1
fi

# Pull LLM model if not already present
echo ""
echo "📥 Checking for LLM model..."
if docker exec callout-ollama ollama list | grep -q "llama3.2:3b"; then
    echo "✅ Model llama3.2:3b already downloaded"
else
    echo "📥 Downloading llama3.2:3b model (this may take a few minutes)..."
    docker exec callout-ollama ollama pull llama3.2:3b
    echo "✅ Model downloaded successfully"
fi

# Test API health
echo ""
echo "🧪 Testing API health..."
sleep 2
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ API is healthy and ready!"
else
    echo "⚠️  API health check failed. Check logs with: docker-compose logs api"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Update your .env file:"
echo "      USE_SELF_HOSTED_API=true"
echo "      SELF_HOSTED_API_URL=http://localhost:8000"
echo ""
echo "   2. Run Callout:"
echo "      cd .."
echo "      streamlit run app.py"
echo ""
echo "📊 Useful commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop services: docker-compose down"
echo "   - Restart services: docker-compose restart"
echo ""
