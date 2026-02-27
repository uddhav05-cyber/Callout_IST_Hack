"""
Local LLM Service using Ollama or Hugging Face Transformers

This service provides claim extraction using self-hosted language models.
No external API keys required!

Supported backends:
1. Ollama (recommended) - Easy to use, supports Llama, Mistral, etc.
2. Hugging Face Transformers - Direct model loading
"""

import os
import re
import logging
from typing import List, Dict, Any, Optional
import asyncio

logger = logging.getLogger(__name__)


class LocalLLMService:
    """Service for local LLM inference"""
    
    def __init__(self):
        self.backend = os.getenv("LLM_BACKEND", "ollama")  # ollama or transformers
        self.model_name = os.getenv("LLM_MODEL", "llama3.2:3b")  # For Ollama
        self.ready = False
        
        # Initialize based on backend
        if self.backend == "ollama":
            self._init_ollama()
        else:
            self._init_transformers()
    
    def _init_ollama(self):
        """Initialize Ollama client"""
        try:
            import ollama
            self.client = ollama
            self.ready = True
            logger.info(f"Ollama initialized with model: {self.model_name}")
        except ImportError:
            logger.error("Ollama not installed. Install with: pip install ollama")
            self.ready = False
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            self.ready = False
    
    def _init_transformers(self):
        """Initialize Hugging Face Transformers"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            model_name = os.getenv("HF_MODEL", "microsoft/Phi-3-mini-4k-instruct")
            
            logger.info(f"Loading model: {model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto"
            )
            self.ready = True
            logger.info(f"Transformers initialized with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Transformers: {e}")
            self.ready = False
    
    def is_ready(self) -> bool:
        """Check if service is ready"""
        return self.ready
    
    def detect_language(self, text: str) -> str:
        """
        Detect language from text.
        
        Uses langdetect library (no API needed).
        """
        try:
            from langdetect import detect
            return detect(text)
        except:
            return "en"  # Default to English
    
    async def extract_claims(
        self,
        article_text: str,
        language: str = "en",
        max_claims: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Extract claims from article text using local LLM.
        
        Args:
            article_text: Article text to extract claims from
            language: Language code
            max_claims: Maximum number of claims to extract
        
        Returns:
            List of claim dictionaries
        """
        if not self.ready:
            raise RuntimeError("LLM service not ready")
        
        # Build prompt
        prompt = self._build_claim_extraction_prompt(article_text, language)
        
        # Generate response
        if self.backend == "ollama":
            response = await self._generate_ollama(prompt)
        else:
            response = await self._generate_transformers(prompt)
        
        # Parse claims from response
        claims = self._parse_claims(response, article_text)
        
        # Limit to max_claims
        return claims[:max_claims]
    
    def _build_claim_extraction_prompt(self, article_text: str, language: str) -> str:
        """Build prompt for claim extraction"""
        
        # Language-specific instructions
        instructions = {
            "en": """You are a fact-checking assistant. Extract atomic, verifiable factual claims from the article.

INSTRUCTIONS:
1. Extract ONLY factual claims that can be verified
2. DO NOT extract opinions, subjective statements, or predictions
3. Each claim should be atomic (one fact per claim) and self-contained
4. Assign an importance score (0.0 to 1.0) to each claim
5. Provide brief context for each claim

FORMAT YOUR RESPONSE AS:
CLAIM: [claim text]
IMPORTANCE: [score between 0.0 and 1.0]
CONTEXT: [brief context]
---""",
            "es": """Eres un asistente de verificación de hechos. Extrae afirmaciones fácticas atómicas y verificables del artículo.

INSTRUCCIONES:
1. Extrae SOLO afirmaciones fácticas que puedan ser verificadas
2. NO extraigas opiniones, declaraciones subjetivas o predicciones
3. Cada afirmación debe ser atómica (un hecho por afirmación) y autónoma
4. Asigna una puntuación de importancia (0.0 a 1.0) a cada afirmación
5. Proporciona un contexto breve para cada afirmación

FORMATEA TU RESPUESTA COMO:
CLAIM: [texto de la afirmación]
IMPORTANCE: [puntuación entre 0.0 y 1.0]
CONTEXT: [contexto breve]
---"""
        }
        
        instruction = instructions.get(language, instructions["en"])
        
        prompt = f"""{instruction}

ARTICLE TEXT:
{article_text[:2000]}

EXTRACTED CLAIMS:
"""
        
        return prompt
    
    async def _generate_ollama(self, prompt: str) -> str:
        """Generate response using Ollama"""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.generate(
                    model=self.model_name,
                    prompt=prompt,
                    options={
                        "temperature": 0.1,
                        "num_predict": 1024
                    }
                )
            )
            return response['response']
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise
    
    async def _generate_transformers(self, prompt: str) -> str:
        """Generate response using Transformers"""
        try:
            import torch
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            def generate():
                inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=1024,
                    temperature=0.1,
                    do_sample=True
                )
                return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            response = await loop.run_in_executor(None, generate)
            
            # Extract only the generated part (after prompt)
            if prompt in response:
                response = response.split(prompt)[-1]
            
            return response
        except Exception as e:
            logger.error(f"Transformers generation failed: {e}")
            raise
    
    def _parse_claims(self, response: str, article_text: str) -> List[Dict[str, Any]]:
        """Parse claims from LLM response"""
        claims = []
        
        # Split by claim separator
        claim_blocks = response.split('---')
        
        for block in claim_blocks:
            block = block.strip()
            if not block:
                continue
            
            # Extract claim text
            claim_match = re.search(r'CLAIM:\s*(.+?)(?=\n|$)', block, re.IGNORECASE)
            if not claim_match:
                continue
            claim_text = claim_match.group(1).strip()
            
            # Extract importance score
            importance_match = re.search(r'IMPORTANCE:\s*([\d.]+)', block, re.IGNORECASE)
            if importance_match:
                try:
                    importance = float(importance_match.group(1))
                    importance = max(0.0, min(1.0, importance))
                except ValueError:
                    importance = 0.5
            else:
                importance = 0.5
            
            # Extract context
            context_match = re.search(r'CONTEXT:\s*(.+?)(?=\n\n|$)', block, re.IGNORECASE | re.DOTALL)
            if context_match:
                context = context_match.group(1).strip()
            else:
                context = ""
            
            if claim_text:
                claims.append({
                    "text": claim_text,
                    "importance": importance,
                    "context": context
                })
        
        # If no claims found, use fallback extraction
        if not claims:
            claims = self._fallback_extraction(article_text)
        
        logger.info(f"Parsed {len(claims)} claims from LLM response")
        return claims
    
    def _fallback_extraction(self, article_text: str) -> List[Dict[str, Any]]:
        """Fallback rule-based extraction"""
        claims = []
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', article_text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        for sentence in sentences[:10]:  # Take first 10 sentences
            claims.append({
                "text": sentence,
                "importance": 0.5,
                "context": sentence
            })
        
        return claims
