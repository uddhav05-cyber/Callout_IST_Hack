"""
Self-Hosted API Server for Callout Fake News Detection System

This FastAPI server provides endpoints for:
1. Claim extraction using local LLM (Llama, Mistral, etc.)
2. Web search using DuckDuckGo (free, no API key needed)
3. Optional: Image verification using local models

No external API keys required!
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Import our local services
from services.llm_service import LocalLLMService
from services.search_service import LocalSearchService


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Initialize FastAPI app
app = FastAPI(
    title="Callout API",
    description="Self-hosted API for fake news detection",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize services
llm_service = LocalLLMService()
search_service = LocalSearchService()


# Request/Response Models
class ClaimExtractionRequest(BaseModel):
    article_text: str = Field(..., min_length=10, description="Article text to extract claims from")
    language: str = Field(default="en", description="Language code (en, es, fr, etc.)")
    max_claims: int = Field(default=10, ge=1, le=20, description="Maximum number of claims to extract")


class Claim(BaseModel):
    text: str
    importance: float = Field(ge=0.0, le=1.0)
    context: str


class ClaimExtractionResponse(BaseModel):
    claims: List[Claim]
    language_detected: str
    processing_time_seconds: float


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Search query")
    max_results: int = Field(default=10, ge=1, le=20, description="Maximum number of results")


class SearchResult(BaseModel):
    url: str
    title: str
    snippet: str
    domain: str
    published_date: Optional[str] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    processing_time_seconds: float


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "llm": llm_service.is_ready(),
            "search": search_service.is_ready()
        }
    }


# Claim extraction endpoint
@app.post("/api/v1/extract-claims", response_model=ClaimExtractionResponse)
async def extract_claims(request: ClaimExtractionRequest):
    """
    Extract factual claims from article text using local LLM.
    
    This endpoint uses a self-hosted language model (no external API needed).
    """
    try:
        start_time = datetime.utcnow()
        
        logger.info(f"Extracting claims from article ({len(request.article_text)} chars)")
        
        # Extract claims using local LLM
        claims = await llm_service.extract_claims(
            article_text=request.article_text,
            language=request.language,
            max_claims=request.max_claims
        )
        
        # Detect language
        language_detected = llm_service.detect_language(request.article_text)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info(f"Extracted {len(claims)} claims in {processing_time:.2f}s")
        
        return ClaimExtractionResponse(
            claims=claims,
            language_detected=language_detected,
            processing_time_seconds=processing_time
        )
    
    except Exception as e:
        logger.error(f"Error extracting claims: {e}")
        raise HTTPException(status_code=500, detail=f"Claim extraction failed: {str(e)}")


# Search endpoint
@app.post("/api/v1/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Search for evidence using DuckDuckGo (no API key needed).
    
    This endpoint uses DuckDuckGo's free search API.
    """
    try:
        start_time = datetime.utcnow()
        
        logger.info(f"Searching for: {request.query}")
        
        # Search using DuckDuckGo
        results = await search_service.search(
            query=request.query,
            max_results=request.max_results
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info(f"Found {len(results)} results in {processing_time:.2f}s")
        
        return SearchResponse(
            results=results,
            query=request.query,
            processing_time_seconds=processing_time
        )
    
    except Exception as e:
        logger.error(f"Error searching: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


# API key generation endpoint (for your own authentication)
@app.post("/api/v1/generate-api-key")
async def generate_api_key(request: Request):
    """
    Generate a new API key for authentication.
    
    In production, this should be protected with admin authentication.
    """
    import secrets
    
    # Generate a secure random API key
    api_key = f"callout_{secrets.token_urlsafe(32)}"
    
    # In production, store this in a database
    logger.info(f"Generated new API key: {api_key[:20]}...")
    
    return {
        "api_key": api_key,
        "created_at": datetime.utcnow().isoformat(),
        "note": "Store this key securely. It won't be shown again."
    }


if __name__ == "__main__":
    # Run the server
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
