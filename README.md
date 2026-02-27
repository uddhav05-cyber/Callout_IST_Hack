# Fake News Detection System

A multi-source verification system that analyzes news articles to determine their veracity through explainable AI.

## Project Structure

```
fake-news-detection-system/
├── src/                    # Source code
│   └── __init__.py
├── tests/                  # Test files
│   └── __init__.py
├── config/                 # Configuration files
│   ├── __init__.py
│   └── logging_config.py
├── logs/                   # Application logs (auto-created)
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment variables
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run the application:
```bash
streamlit run app.py
```

## Dependencies

- **streamlit**: Web UI framework
- **langchain**: LLM integration
- **transformers**: NLI model
- **torch**: Deep learning backend
- **requests**: HTTP client
- **beautifulsoup4**: HTML parsing
- **python-dotenv**: Environment variable management
- **pydantic**: Data validation
- **pytest**: Testing framework

## API Keys Required

- OpenAI or Groq API key (for claim extraction)
- Serper.dev or Tavily API key (for evidence retrieval)
- TinEye API key (optional, for image verification)

## License

MIT
