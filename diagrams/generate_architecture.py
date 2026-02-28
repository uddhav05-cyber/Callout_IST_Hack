"""
Generate architecture diagrams for Callout system
"""

from graphviz import Digraph

# Create diagrams directory if it doesn't exist
import os
os.makedirs('diagrams', exist_ok=True)

# 1. SYSTEM OVERVIEW DIAGRAM
def create_system_overview():
    dot = Digraph(comment='Callout System Overview', format='png')
    dot.attr(rankdir='TB', size='12,10')
    dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue')
    
    # User layer
    dot.node('user', 'User\n(Web Browser)', fillcolor='lightgreen')
    
    # UI layer
    dot.node('ui', 'Streamlit UI\n(app.py)', fillcolor='lightyellow')
    
    # Core pipeline
    dot.node('pipeline', 'Verification Pipeline\n(verification_pipeline.py)', fillcolor='lightcoral')
    
    # Processing modules
    dot.node('parser', 'Article Parser\n(BeautifulSoup)', fillcolor='wheat')
    dot.node('lang', 'Language Detection\n(langdetect)', fillcolor='wheat')
    dot.node('claims', 'Claim Extraction\n(LLM)', fillcolor='wheat')
    dot.node('evidence', 'Evidence Retrieval\n(Search API)', fillcolor='wheat')
    dot.node('nli', 'NLI Verification\n(BART/mDeBERTa)', fillcolor='wheat')
    dot.node('tone', 'Tone Analysis', fillcolor='wheat')
    dot.node('synthesis', 'Verdict Synthesis', fillcolor='wheat')
    
    # External services
    dot.node('api_wrapper', 'API Wrapper\n(Smart Router)', fillcolor='lightgray')
    dot.node('self_hosted', 'Self-Hosted API\n(FastAPI + Ollama)', fillcolor='lightgreen')
    dot.node('external', 'External APIs\n(OpenAI/Groq/Serper)', fillcolor='orange')
    
    # Connections
    dot.edge('user', 'ui', 'Submit Article')
    dot.edge('ui', 'pipeline', 'Process')
    dot.edge('pipeline', 'parser', '1. Parse')
    dot.edge('pipeline', 'lang', '2. Detect Language')
    dot.edge('pipeline', 'claims', '3. Extract Claims')
    dot.edge('pipeline', 'evidence', '4. Search Evidence')
    dot.edge('pipeline', 'nli', '5. Verify Claims')
    dot.edge('pipeline', 'tone', '6. Analyze Tone')
    dot.edge('pipeline', 'synthesis', '7. Synthesize')
    
    dot.edge('claims', 'api_wrapper', 'LLM Request')
    dot.edge('evidence', 'api_wrapper', 'Search Request')
    dot.edge('api_wrapper', 'self_hosted', 'Route (if enabled)')
    dot.edge('api_wrapper', 'external', 'Route (if disabled)')
    
    dot.edge('synthesis', 'ui', 'Result')
    dot.edge('ui', 'user', 'Display')
    
    dot.render('diagrams/01_system_overview', cleanup=True)
    print("✓ Created: 01_system_overview.png")

# 2. VERIFICATION PIPELINE DIAGRAM
def create_verification_pipeline():
    dot = Digraph(comment='Verification Pipeline', format='png')
    dot.attr(rankdir='TB', size='10,12')
    dot.attr('node', shape='box', style='rounded,filled')
    
    # Input
    dot.node('input', 'Article Input\n(URL or Text)', fillcolor='lightgreen', shape='parallelogram')
    
    # Stage 1
    with dot.subgraph(name='cluster_1') as c:
        c.attr(label='Stage 1: Parsing', style='filled', color='lightgray')
        c.node('parse', 'Parse Article\n(BeautifulSoup)', fillcolor='wheat')
        c.node('extract_text', 'Extract Text', fillcolor='wheat')
    
    # Stage 2
    with dot.subgraph(name='cluster_2') as c:
        c.attr(label='Stage 2: Language Detection', style='filled', color='lightgray')
        c.node('detect_lang', 'Detect Language\n(langdetect)', fillcolor='wheat')
        c.node('select_model', 'Select NLI Model\n(BART/mDeBERTa)', fillcolor='wheat')
    
    # Stage 3
    with dot.subgraph(name='cluster_3') as c:
        c.attr(label='Stage 3: Claim Extraction', style='filled', color='lightgray')
        c.node('extract_claims', 'Extract Claims\n(LLM)', fillcolor='wheat')
        c.node('fallback', 'Fallback\n(Rule-based)', fillcolor='orange')
    
    # Stage 4
    with dot.subgraph(name='cluster_4') as c:
        c.attr(label='Stage 4: Evidence Retrieval', style='filled', color='lightgray')
        c.node('search', 'Search Evidence\n(DuckDuckGo/Serper)', fillcolor='wheat')
        c.node('filter', 'Filter by Credibility\n(>= 0.3)', fillcolor='wheat')
        c.node('rank', 'Rank by Relevance\n(0.7*rel + 0.3*cred)', fillcolor='wheat')
    
    # Stage 5
    with dot.subgraph(name='cluster_5') as c:
        c.attr(label='Stage 5: NLI Verification', style='filled', color='lightgray')
        c.node('nli_verify', 'Verify Each Claim\n(NLI Model)', fillcolor='wheat')
        c.node('confidence', 'Calculate Confidence', fillcolor='wheat')
    
    # Stage 6
    with dot.subgraph(name='cluster_6') as c:
        c.attr(label='Stage 6: Analysis', style='filled', color='lightgray')
        c.node('tone_analysis', 'Tone Analysis\n(Sentiment)', fillcolor='wheat')
        c.node('aggregate', 'Aggregate Results', fillcolor='wheat')
    
    # Stage 7
    with dot.subgraph(name='cluster_7') as c:
        c.attr(label='Stage 7: Synthesis', style='filled', color='lightgray')
        c.node('synthesize', 'Synthesize Verdict', fillcolor='wheat')
        c.node('explain', 'Generate Explanation', fillcolor='wheat')
    
    # Output
    dot.node('output', 'Verification Result\n(Verdict + Evidence)', fillcolor='lightgreen', shape='parallelogram')
    
    # Connections
    dot.edge('input', 'parse')
    dot.edge('parse', 'extract_text')
    dot.edge('extract_text', 'detect_lang')
    dot.edge('detect_lang', 'select_model')
    dot.edge('select_model', 'extract_claims')
    dot.edge('extract_claims', 'search', label='Success')
    dot.edge('extract_claims', 'fallback', label='Failure', style='dashed')
    dot.edge('fallback', 'search')
    dot.edge('search', 'filter')
    dot.edge('filter', 'rank')
    dot.edge('rank', 'nli_verify')
    dot.edge('nli_verify', 'confidence')
    dot.edge('confidence', 'tone_analysis')
    dot.edge('tone_analysis', 'aggregate')
    dot.edge('aggregate', 'synthesize')
    dot.edge('synthesize', 'explain')
    dot.edge('explain', 'output')
    
    dot.render('diagrams/02_verification_pipeline', cleanup=True)
    print("✓ Created: 02_verification_pipeline.png")

# 3. SELF-HOSTED API ARCHITECTURE
def create_self_hosted_architecture():
    dot = Digraph(comment='Self-Hosted API Architecture', format='png')
    dot.attr(rankdir='LR', size='12,8')
    dot.attr('node', shape='box', style='rounded,filled')
    
    # Client
    dot.node('client', 'Callout App\n(Streamlit)', fillcolor='lightgreen')
    
    # API Wrapper
    dot.node('wrapper', 'API Wrapper\n(api_wrapper.py)', fillcolor='lightyellow')
    
    # Self-hosted API
    with dot.subgraph(name='cluster_api') as c:
        c.attr(label='Self-Hosted API Server', style='filled', color='lightblue')
        c.node('fastapi', 'FastAPI\n(app.py)', fillcolor='wheat')
        c.node('llm_service', 'LLM Service\n(llm_service.py)', fillcolor='wheat')
        c.node('search_service', 'Search Service\n(search_service.py)', fillcolor='wheat')
    
    # Backend services
    dot.node('ollama', 'Ollama\n(Local LLM)', fillcolor='lightcoral', shape='cylinder')
    dot.node('duckduckgo', 'DuckDuckGo\n(Free Search)', fillcolor='lightcoral', shape='cylinder')
    
    # External APIs (alternative)
    with dot.subgraph(name='cluster_external') as c:
        c.attr(label='External APIs (Optional)', style='filled', color='orange')
        c.node('openai', 'OpenAI\n(GPT-4)', fillcolor='wheat')
        c.node('groq', 'Groq\n(Llama)', fillcolor='wheat')
        c.node('serper', 'Serper\n(Google Search)', fillcolor='wheat')
    
    # Connections
    dot.edge('client', 'wrapper', 'Request')
    dot.edge('wrapper', 'fastapi', 'Self-Hosted\n(if enabled)', color='green', penwidth='2')
    dot.edge('wrapper', 'openai', 'External\n(if disabled)', color='orange', style='dashed')
    dot.edge('wrapper', 'groq', 'External\n(if disabled)', color='orange', style='dashed')
    dot.edge('wrapper', 'serper', 'External\n(if disabled)', color='orange', style='dashed')
    
    dot.edge('fastapi', 'llm_service', 'Claim Extraction')
    dot.edge('fastapi', 'search_service', 'Evidence Search')
    
    dot.edge('llm_service', 'ollama', 'LLM Request')
    dot.edge('search_service', 'duckduckgo', 'Search Query')
    
    dot.edge('ollama', 'llm_service', 'Response')
    dot.edge('duckduckgo', 'search_service', 'Results')
    
    dot.edge('llm_service', 'fastapi', 'Claims')
    dot.edge('search_service', 'fastapi', 'Evidence')
    
    dot.edge('fastapi', 'wrapper', 'Response')
    dot.edge('openai', 'wrapper', 'Response', style='dashed')
    dot.edge('groq', 'wrapper', 'Response', style='dashed')
    dot.edge('serper', 'wrapper', 'Response', style='dashed')
    
    dot.edge('wrapper', 'client', 'Result')
    
    dot.render('diagrams/03_self_hosted_architecture', cleanup=True)
    print("✓ Created: 03_self_hosted_architecture.png")

# 4. MULTILINGUAL PIPELINE
def create_multilingual_pipeline():
    dot = Digraph(comment='Multilingual Pipeline', format='png')
    dot.attr(rankdir='TB', size='10,10')
    dot.attr('node', shape='box', style='rounded,filled')
    
    # Input
    dot.node('input', 'Article Text\n(Any Language)', fillcolor='lightgreen', shape='parallelogram')
    
    # Language detection
    dot.node('detect', 'Language Detection\n(langdetect)', fillcolor='lightyellow')
    
    # Language routing
    dot.node('route', 'Route by Language', fillcolor='lightcoral', shape='diamond')
    
    # English path
    with dot.subgraph(name='cluster_en') as c:
        c.attr(label='English Path', style='filled', color='lightblue')
        c.node('en_model', 'BART-large-mnli\n(95% accuracy)', fillcolor='wheat')
        c.node('en_prompt', 'English Prompts', fillcolor='wheat')
    
    # Multilingual path
    with dot.subgraph(name='cluster_ml') as c:
        c.attr(label='Multilingual Path (19 languages)', style='filled', color='lightgreen')
        c.node('ml_model', 'mDeBERTa-v3-xnli\n(90% accuracy)', fillcolor='wheat')
        c.node('ml_prompt', 'Native Prompts\n(Hindi, Spanish, etc.)', fillcolor='wheat')
    
    # Cross-lingual verification
    dot.node('cross_lingual', 'Cross-Lingual NLI\n(Hindi claim vs English evidence)', fillcolor='orange')
    
    # Output
    dot.node('output', 'Verification Result\n(Native Language)', fillcolor='lightgreen', shape='parallelogram')
    
    # Connections
    dot.edge('input', 'detect')
    dot.edge('detect', 'route')
    dot.edge('route', 'en_model', label='English (en)')
    dot.edge('route', 'ml_model', label='Other (hi, es, fr, etc.)')
    
    dot.edge('en_model', 'en_prompt')
    dot.edge('ml_model', 'ml_prompt')
    
    dot.edge('en_prompt', 'cross_lingual')
    dot.edge('ml_prompt', 'cross_lingual')
    
    dot.edge('cross_lingual', 'output')
    
    # Add language examples
    dot.node('langs', '19 Languages:\n• English\n• Hindi, Bengali, Tamil\n• Spanish, French, German\n• Chinese, Japanese, Arabic\n• And 10 more...', 
             fillcolor='lightyellow', shape='note')
    
    dot.render('diagrams/04_multilingual_pipeline', cleanup=True)
    print("✓ Created: 04_multilingual_pipeline.png")

# 5. DEPLOYMENT ARCHITECTURE
def create_deployment_architecture():
    dot = Digraph(comment='Deployment Architecture', format='png')
    dot.attr(rankdir='TB', size='12,10')
    dot.attr('node', shape='box', style='rounded,filled')
    
    # User
    dot.node('users', 'Users\n(Web Browsers)', fillcolor='lightgreen', shape='ellipse')
    
    # Load balancer
    dot.node('lb', 'Load Balancer\n(nginx)', fillcolor='lightyellow')
    
    # Application instances
    with dot.subgraph(name='cluster_app') as c:
        c.attr(label='Application Layer (Docker Compose)', style='filled', color='lightblue')
        c.node('app1', 'Streamlit UI\nInstance 1', fillcolor='wheat')
        c.node('app2', 'Streamlit UI\nInstance 2', fillcolor='wheat')
        c.node('app3', 'Streamlit UI\nInstance N', fillcolor='wheat')
    
    # API instances
    with dot.subgraph(name='cluster_api') as c:
        c.attr(label='API Layer (Docker Compose)', style='filled', color='lightcoral')
        c.node('api1', 'FastAPI\nInstance 1', fillcolor='wheat')
        c.node('api2', 'FastAPI\nInstance 2', fillcolor='wheat')
        c.node('api3', 'FastAPI\nInstance N', fillcolor='wheat')
    
    # Backend services
    with dot.subgraph(name='cluster_backend') as c:
        c.attr(label='Backend Services', style='filled', color='lightgreen')
        c.node('ollama1', 'Ollama\nInstance 1', fillcolor='wheat', shape='cylinder')
        c.node('ollama2', 'Ollama\nInstance 2', fillcolor='wheat', shape='cylinder')
    
    # Cache
    dot.node('redis', 'Redis Cache\n(80% hit rate)', fillcolor='orange', shape='cylinder')
    
    # Database
    dot.node('db', 'PostgreSQL\n(Verification History)', fillcolor='orange', shape='cylinder')
    
    # Monitoring
    with dot.subgraph(name='cluster_monitor') as c:
        c.attr(label='Monitoring', style='filled', color='yellow')
        c.node('prometheus', 'Prometheus\n(Metrics)', fillcolor='wheat')
        c.node('grafana', 'Grafana\n(Dashboards)', fillcolor='wheat')
    
    # Connections
    dot.edge('users', 'lb', 'HTTPS')
    dot.edge('lb', 'app1')
    dot.edge('lb', 'app2')
    dot.edge('lb', 'app3')
    
    dot.edge('app1', 'api1')
    dot.edge('app2', 'api2')
    dot.edge('app3', 'api3')
    
    dot.edge('api1', 'ollama1')
    dot.edge('api2', 'ollama2')
    dot.edge('api3', 'ollama1')
    
    dot.edge('api1', 'redis', 'Cache Check')
    dot.edge('api2', 'redis', 'Cache Check')
    dot.edge('api3', 'redis', 'Cache Check')
    
    dot.edge('api1', 'db', 'Store Results')
    dot.edge('api2', 'db', 'Store Results')
    dot.edge('api3', 'db', 'Store Results')
    
    dot.edge('app1', 'prometheus', 'Metrics', style='dashed')
    dot.edge('api1', 'prometheus', 'Metrics', style='dashed')
    dot.edge('prometheus', 'grafana', 'Query')
    
    dot.render('diagrams/05_deployment_architecture', cleanup=True)
    print("✓ Created: 05_deployment_architecture.png")

# 6. DATA FLOW DIAGRAM
def create_data_flow():
    dot = Digraph(comment='Data Flow', format='png')
    dot.attr(rankdir='LR', size='14,10')
    dot.attr('node', shape='box', style='rounded,filled')
    
    # Input
    dot.node('article', 'Article\n"Economy grew 10%"', fillcolor='lightgreen', shape='note')
    
    # Processing stages
    dot.node('claims', 'Claims\n["Economy grew 10%"]', fillcolor='lightyellow', shape='note')
    dot.node('evidence', 'Evidence\n["Official data: 5% growth"]', fillcolor='lightyellow', shape='note')
    dot.node('nli_result', 'NLI Result\nCONTRADICTED (95%)', fillcolor='lightyellow', shape='note')
    dot.node('verdict', 'Final Verdict\nFALSE (95% confidence)', fillcolor='lightcoral', shape='note')
    
    # Processing nodes
    dot.node('extract', 'Claim Extraction\n(LLM)', fillcolor='wheat')
    dot.node('search', 'Evidence Search\n(DuckDuckGo)', fillcolor='wheat')
    dot.node('verify', 'NLI Verification\n(BART)', fillcolor='wheat')
    dot.node('synthesize', 'Synthesis\n(Aggregate)', fillcolor='wheat')
    
    # Connections with data labels
    dot.edge('article', 'extract', 'Input Text')
    dot.edge('extract', 'claims', 'Extract')
    dot.edge('claims', 'search', 'Query')
    dot.edge('search', 'evidence', 'Retrieve')
    dot.edge('claims', 'verify', 'Hypothesis')
    dot.edge('evidence', 'verify', 'Premise')
    dot.edge('verify', 'nli_result', 'Classify')
    dot.edge('nli_result', 'synthesize', 'Aggregate')
    dot.edge('synthesize', 'verdict', 'Output')
    
    dot.render('diagrams/06_data_flow', cleanup=True)
    print("✓ Created: 06_data_flow.png")

# Generate all diagrams
if __name__ == "__main__":
    print("Generating architecture diagrams...")
    print()
    
    create_system_overview()
    create_verification_pipeline()
    create_self_hosted_architecture()
    create_multilingual_pipeline()
    create_deployment_architecture()
    create_data_flow()
    
    print()
    print("✓ All diagrams generated successfully!")
    print("✓ Location: diagrams/ folder")
    print()
    print("Diagrams created:")
    print("  1. 01_system_overview.png - High-level system architecture")
    print("  2. 02_verification_pipeline.png - Detailed verification pipeline")
    print("  3. 03_self_hosted_architecture.png - Self-hosted API architecture")
    print("  4. 04_multilingual_pipeline.png - Multilingual processing")
    print("  5. 05_deployment_architecture.png - Production deployment")
    print("  6. 06_data_flow.png - Data flow example")
