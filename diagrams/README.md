# Callout Architecture Diagrams

This folder contains architectural diagrams for the Callout fake news detection system.

## Generated Diagrams

### 1. System Overview (`01_system_overview.png`)
High-level architecture showing:
- User interface (Streamlit)
- Verification pipeline
- Processing modules (parser, language detection, NLI, etc.)
- API routing (self-hosted vs external)

**Use this for:** Quick overview of the entire system

---

### 2. Verification Pipeline (`02_verification_pipeline.png`)
Detailed 7-stage verification process:
- Stage 1: Article parsing
- Stage 2: Language detection
- Stage 3: Claim extraction (with fallback)
- Stage 4: Evidence retrieval (search, filter, rank)
- Stage 5: NLI verification
- Stage 6: Tone analysis
- Stage 7: Verdict synthesis

**Use this for:** Understanding the verification workflow

---

### 3. Self-Hosted API Architecture (`03_self_hosted_architecture.png`)
Shows the self-hosted vs external API routing:
- API wrapper (smart router)
- Self-hosted path: FastAPI → Ollama + DuckDuckGo
- External path: OpenAI/Groq + Serper
- Cost comparison ($0 vs $1,500/month)

**Use this for:** Explaining the self-hosted advantage

---

### 4. Multilingual Pipeline (`04_multilingual_pipeline.png`)
Language-specific processing:
- Language detection (langdetect)
- English path: BART-large-mnli (95% accuracy)
- Multilingual path: mDeBERTa-v3-xnli (90% accuracy)
- Cross-lingual verification
- 19 languages supported

**Use this for:** Demonstrating multilingual capabilities

---

### 5. Deployment Architecture (`05_deployment_architecture.png`)
Production deployment setup:
- Load balancer (nginx)
- Multiple application instances
- Multiple API instances
- Ollama backend services
- Redis cache (80% hit rate)
- PostgreSQL database
- Prometheus + Grafana monitoring

**Use this for:** Showing scalability and production-readiness

---

### 6. Data Flow Example (`06_data_flow.png`)
Concrete example of data flowing through the system:
- Input: "Economy grew 10%"
- Claims extraction
- Evidence search: "Official data: 5% growth"
- NLI verification: CONTRADICTED (95%)
- Final verdict: FALSE

**Use this for:** Demonstrating how the system works with real data

---

## How to Regenerate Diagrams

If you need to modify or regenerate the diagrams:

```bash
# Install graphviz if not already installed
pip install graphviz

# Run the generation script
python diagrams/generate_architecture.py
```

## Diagram Format

All diagrams are generated as PNG files using Graphviz. The source code is in `generate_architecture.py`.

## Color Coding

- **Light Green**: User-facing components, inputs/outputs
- **Light Yellow**: UI and routing layers
- **Light Blue**: Core processing clusters
- **Light Coral**: API and backend services
- **Wheat**: Individual processing modules
- **Orange**: External services and caching
- **Light Gray**: Optional or alternative paths

## For Presentations

These diagrams are designed for:
- Mentor presentations
- Technical documentation
- System design discussions
- Investor pitches
- Developer onboarding

**Recommended order for presentation:**
1. System Overview (big picture)
2. Verification Pipeline (how it works)
3. Self-Hosted Architecture (cost advantage)
4. Multilingual Pipeline (unique feature)
5. Data Flow (concrete example)
6. Deployment Architecture (production-ready)

---

**Generated:** 2025-02-27  
**Tool:** Graphviz + Python  
**Format:** PNG  
**Resolution:** High (suitable for presentations)
