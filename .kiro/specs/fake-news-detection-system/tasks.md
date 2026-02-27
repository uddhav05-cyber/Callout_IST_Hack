# Implementation Plan: Fake News Detection System

## Overview

This implementation plan breaks down the fake news detection system into discrete coding tasks. The system will be built in Python using Streamlit for the UI, LangChain for LLM integration, HuggingFace Transformers for NLI, and free-tier APIs (Groq/OpenAI, Serper/Tavily). The implementation follows an incremental approach where each task builds on previous work, with testing integrated throughout.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create project directory structure (src/, tests/, config/)
  - Create requirements.txt with all dependencies (streamlit, langchain, transformers, torch, requests, beautifulsoup4, python-dotenv, pydantic, pytest)
  - Create .env.example file with required API key placeholders
  - Create .gitignore file to exclude .env, __pycache__, and cache directories
  - Set up basic logging configuration
  - _Requirements: 16.3, 16.4_

- [x] 2. Implement core data models
  - [x] 2.1 Create Pydantic models for all data structures
    - Implement Claim model with id, text, context, importance fields
    - Implement Evidence model with id, sourceURL, sourceDomain, snippet, publishDate, credibilityScore, relevanceScore fields
    - Implement NLIResult model with claimID, evidenceID, entailmentScore, contradictionScore, neutralScore, label fields
    - Implement VerificationScore model with claimID, supportCount, refuteCount, neutralCount, confidenceScore, verdict fields
    - Implement FinalVerdict model with overallVerdict, confidenceScore, factualAccuracyScore, emotionalManipulationScore, claimBreakdown, evidenceCards, explanation fields
    - Implement EvidenceCard model with claim, evidenceSnippet, sourceURL, sourceName, relationship, highlightedDiscrepancies fields
    - Implement ToneScore model with emotionalIntensity, sensationalismScore, manipulativePhrases, objectivityScore fields
    - Add validation rules to ensure score bounds (0-1 for credibility, 0-100 for confidence)
    - _Requirements: 1.4, 5.7, 5.8, 14.2, 14.3, 14.4, 14.5_
  
  - [ ]* 2.2 Write property test for data model validation
    - **Property 1: Score Validity**
    - **Validates: Requirements 5.7, 5.8**

- [x] 3. Implement configuration and environment management
  - [x] 3.1 Create configuration module
    - Load API keys from environment variables (OPENAI_API_KEY, GROQ_API_KEY, SERPER_API_KEY, TAVILY_API_KEY)
    - Define configurable constants (MAX_CLAIMS_PER_ARTICLE=10, MAX_EVIDENCE_PER_CLAIM=5, MINIMUM_CREDIBILITY_THRESHOLD=0.3)
    - Define timeout and retry settings (REQUEST_TIMEOUT_SECONDS=10, MAX_RETRIES=3, CACHE_TTL_HOURS=24)
    - Define NLI model configuration (NLI_MODEL_NAME="facebook/bart-large-mnli")
    - Add validation to ensure required API keys are present
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5_
  
  - [ ]* 3.2 Write unit tests for configuration loading
    - Test missing API keys raise appropriate errors
    - Test default values are applied correctly
    - _Requirements: 16.3, 16.4_

- [x] 4. Implement source credibility database
  - [x] 4.1 Create source credibility lookup system
    - Create JSON file with trusted source domains and credibility scores
    - Implement function to load credibility database from JSON
    - Implement lookupSourceCredibility(domain) function that returns SourceCredibility object
    - Return default credibility score of 0.5 for unknown domains
    - Categorize sources as TRUSTED (0.8-1.0), MAINSTREAM (0.5-0.79), QUESTIONABLE (0.3-0.49), UNRELIABLE (0.0-0.29)
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 3.2, 3.3_
  
  - [ ]* 4.2 Write unit tests for credibility lookup
    - Test known trusted sources return correct scores
    - Test unknown domains return default 0.5
    - Test category mapping is correct
    - _Requirements: 12.2, 12.3, 12.4_

- [x] 5. Implement article input processing module
  - [x] 5.1 Create article parser
    - Implement parseArticleFromURL(url) function using requests and BeautifulSoup
    - Add URL validation (format check, block private IPs, enforce HTTPS when possible)
    - Implement 10-second timeout and max 3 redirects
    - Strip HTML tags and extract main article text
    - Normalize whitespace and handle UTF-8 encoding
    - Implement error handling for invalid/inaccessible URLs with clear error messages
    - _Requirements: 1.1, 1.3, 1.4, 1.5, 1.6, 14.1, 14.4, 14.5, 14.6_
  
  - [x] 5.2 Create text input handler
    - Implement function to accept direct text input
    - Validate text length (max 50,000 characters)
    - Sanitize HTML and script tags from input
    - Validate UTF-8 encoding
    - _Requirements: 1.2, 14.2, 14.4, 14.5_
  
  - [ ]* 5.3 Write unit tests for input processing
    - Test valid URL parsing
    - Test invalid URL error handling
    - Test text length validation
    - Test HTML sanitization
    - Test private IP blocking
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 14.1, 14.2_

- [x] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement claim extraction module
  - [x] 7.1 Create LLM integration for claim extraction
    - Set up LangChain with OpenAI/Groq API client
    - Implement buildClaimExtractionPrompt(articleText) function with clear instructions to extract factual claims
    - Implement callLLM(prompt) function with error handling and retry logic (exponential backoff, 3 attempts)
    - Implement parseLLMResponse(response) to extract claims from LLM output
    - Add fallback to rule-based extraction (sentence splitting + keyword filtering) if LLM fails
    - _Requirements: 2.1, 11.1, 11.2, 16.1_
  
  - [x] 7.2 Implement claim filtering and ranking
    - Implement isFactualClaim(claim) function to filter out opinions
    - Implement calculateImportance(claim, articleText) function to score claim importance
    - Implement extractClaims(articleText) main function that orchestrates extraction, filtering, and ranking
    - Sort claims by importance in descending order
    - Limit to MAX_CLAIMS_PER_ARTICLE top claims
    - Assign unique UUID to each claim
    - Handle edge case: return UNVERIFIED verdict if no claims extracted
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 17.1, 17.2, 17.3, 17.4, 17.5_
  
  - [ ]* 7.3 Write property test for claim extraction
    - **Property 5: Claim Extraction Non-Empty**
    - **Property 9: Claim Importance Ordering**
    - **Validates: Requirements 2.6, 17.2, 17.4**
  
  - [ ]* 7.4 Write unit tests for claim extraction
    - Test with factual news articles
    - Test with opinion pieces (should extract few/no claims)
    - Test with empty input
    - Test LLM failure fallback
    - Test importance scoring
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 11.2_

- [x] 8. Implement evidence retrieval module
  - [x] 8.1 Create search API integration
    - Implement callSearchAPI(query) function for Serper.dev or Tavily API
    - Add API key configuration and error handling
    - Implement rate limit handling (queue remaining claims, return partial results)
    - Parse search results to extract URL, snippet, domain
    - _Requirements: 3.1, 11.3, 16.2_
  
  - [x] 8.2 Implement evidence filtering and ranking
    - Implement optimizeQueryForSearch(claimText) to build effective search queries
    - Implement extractDomain(url) helper function
    - Implement calculateRelevance(claimText, snippet) function using text similarity
    - Implement filterTrustedSources(results) to filter by credibility threshold
    - Implement searchEvidence(claim) main function that orchestrates search, filtering, and ranking
    - Rank evidence by combined score (70% relevance + 30% credibility)
    - Limit to MAX_EVIDENCE_PER_CLAIM top results
    - Handle case when no trusted sources found (mark claim as UNVERIFIED)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 12.5, 19.1, 19.2, 19.3, 19.4_
  
  - [ ]* 8.3 Write property test for evidence retrieval
    - **Property 6: Evidence Credibility Threshold**
    - **Property 10: Evidence Relevance**
    - **Validates: Requirements 3.2, 19.1, 19.4**
  
  - [ ]* 8.4 Write unit tests for evidence retrieval
    - Test search API integration with mocked responses
    - Test credibility filtering
    - Test relevance scoring
    - Test rate limit handling
    - Test no results scenario
    - _Requirements: 3.1, 3.2, 3.7, 11.3_

- [x] 9. Implement NLI engine for cross-verification
  - [x] 9.1 Load and configure HuggingFace NLI model
    - Load facebook/bart-large-mnli or microsoft/deberta-v3-base-mnli model
    - Implement model caching in memory to avoid reloading
    - Add error handling for model loading failures with fallback to keyword matching
    - Reduce confidence by 30% when using fallback
    - _Requirements: 4.6, 11.4, 13.4_
  
  - [x] 9.2 Implement NLI inference
    - Implement formatForNLI(premise, hypothesis) to prepare model input
    - Implement verifyClaimAgainstEvidence(claim, evidence) function
    - Extract entailment, contradiction, and neutral scores from model output
    - Validate that scores sum to approximately 1.0 (within 0.01 tolerance)
    - Assign label (SUPPORTS, REFUTES, NEUTRAL) based on highest score
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [x] 9.3 Implement score aggregation
    - Implement aggregateNLIScores(results) function
    - Count support, refute, and neutral evidence
    - Calculate weighted scores using evidence credibility as weights
    - Determine verdict based on thresholds (>60% support = TRUE, >60% refute = FALSE, both >30% = MISLEADING, else UNVERIFIED)
    - Calculate confidence score based on evidence strength
    - _Requirements: 5.1, 5.3, 5.4, 5.5, 5.6, 5.9_
  
  - [ ]* 9.4 Write property test for NLI engine
    - **Property 4: NLI Score Normalization**
    - **Property 7: Verification Score Aggregation**
    - **Validates: Requirements 4.3, 5.1**
  
  - [ ]* 9.5 Write unit tests for NLI engine
    - Test with clear entailment pairs
    - Test with clear contradiction pairs
    - Test with neutral pairs
    - Test score normalization
    - Test model loading failure fallback
    - Test aggregation with various evidence patterns
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.6, 5.1_

- [x] 10. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Implement tone analysis module
  - [x] 11.1 Create tone analyzer
    - Implement detectManipulativePhrases(text) function using keyword patterns
    - Implement analyzeTone(text) function to calculate emotional intensity and sensationalism score
    - Calculate objectivity score (inverse of sensationalism)
    - Return ToneScore object with all metrics
    - _Requirements: 7.1, 7.2, 7.4_
  
  - [ ]* 11.2 Write unit tests for tone analysis
    - Test with neutral, objective text
    - Test with sensationalist text
    - Test with emotional language
    - Test manipulative phrase detection
    - _Requirements: 7.1, 7.2, 7.4_

- [x] 12. Implement synthesis module
  - [x] 12.1 Create final verdict calculation
    - Implement calculateFinalScore(verificationScores, toneScore, sourceCredibility) function
    - Apply weighted formula: 60% evidence match + 20% source credibility + 20% writing style
    - Apply penalty for misleading claims (reduce by 20% per misleading claim)
    - Apply penalty if more than half claims are false (reduce by 50%)
    - Clamp final score to [0, 100] range
    - Determine overall verdict based on score and evidence patterns
    - _Requirements: 5.2, 5.9, 7.3_
  
  - [x] 12.2 Create evidence card generator
    - Implement createEvidenceCards(claims, evidence, nliResults) function
    - For each claim, create EvidenceCard with claim text, evidence snippet, source info, and relationship
    - Implement highlightDiscrepancies(claim, evidence) to identify contradicting portions
    - Ensure every claim has at least one evidence card
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [x] 12.3 Create explanation generator
    - Implement generateExplanation(verdict) function
    - Use simple, non-technical language
    - Explain why claims are marked TRUE, FALSE, or MISLEADING
    - Provide claim-by-claim breakdown explanations
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [x] 12.4 Implement main synthesis function
    - Implement generateVerdict(verificationScores) main function
    - Combine all scores (evidence, credibility, tone)
    - Generate evidence cards
    - Generate explanation
    - Return complete FinalVerdict object
    - _Requirements: 5.1, 5.2, 5.7, 7.3, 7.5_
  
  - [ ]* 12.5 Write property test for synthesis
    - **Property 2: Verdict Consistency**
    - **Property 3: Evidence Card Completeness**
    - **Property 8: Weighted Score Bounds**
    - **Validates: Requirements 5.7, 6.4, 18.1, 18.2, 18.3, 18.4**
  
  - [ ]* 12.6 Write unit tests for synthesis
    - Test final score calculation with various inputs
    - Test evidence card generation
    - Test explanation generation
    - Test penalty application
    - Test verdict determination logic
    - _Requirements: 5.2, 5.3, 5.4, 5.5, 5.6, 5.9, 6.1, 6.2, 9.1, 9.3, 9.4_

- [ ] 13. Implement visual verification module
  - [ ] 13.1 Create reverse image search integration
    - Implement reverseImageSearch(imageURL) function using Google or TinEye API
    - Parse results to find original source and first publication date
    - Return list of ImageMatch objects with similarity scores
    - _Requirements: 8.1, 8.2_
  
  - [ ] 13.2 Create manipulation detection
    - Implement detectManipulation(imageURL) function
    - Check for out-of-context usage by comparing dates and contexts
    - Classify manipulation type (NONE, EDITED, DEEPFAKE, OUT_OF_CONTEXT)
    - Return ManipulationReport with confidence score
    - _Requirements: 8.3, 8.4, 8.5_
  
  - [ ]* 13.3 Write unit tests for visual verification
    - Test reverse image search with mocked API
    - Test manipulation detection logic
    - Test image input validation
    - _Requirements: 8.1, 8.3, 14.3_

- [ ] 14. Implement main verification pipeline
  - [x] 14.1 Create orchestration function
    - Implement verifyArticle(input) main function that orchestrates all components
    - Step 1: Parse article content from URL or text
    - Step 2: Extract atomic claims
    - Step 3: Retrieve evidence for each claim (use parallel processing)
    - Step 4: Run NLI verification for all claim-evidence pairs (use batching when possible)
    - Step 5: Analyze tone separately
    - Step 6: Synthesize final verdict
    - Add assertions for preconditions and postconditions
    - _Requirements: 1.1, 1.2, 2.1, 3.1, 4.1, 5.1, 7.1, 20.1, 20.2, 20.3_
  
  - [ ] 14.2 Implement parallel processing
    - Use asyncio or concurrent.futures for parallel evidence retrieval
    - Batch NLI inference when possible
    - Use async operations for API calls
    - Limit concurrent operations to avoid overwhelming services
    - _Requirements: 20.1, 20.2, 20.3, 20.4_
  
  - [ ]* 14.3 Write integration tests for main pipeline
    - Test end-to-end flow with sample articles
    - Test with URL input
    - Test with text input
    - Test error handling at each stage
    - Test parallel processing
    - _Requirements: 1.1, 1.2, 10.1, 20.1_

- [x] 15. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 16. Implement caching system
  - [ ] 16.1 Create cache manager
    - Implement hash-based caching for article results
    - Implement cache for search results with 24-hour TTL
    - Implement cache for source credibility scores with weekly updates
    - Use file-based cache (JSON) or SQLite for persistence
    - _Requirements: 13.1, 13.2, 13.3, 13.5_
  
  - [ ]* 16.2 Write unit tests for caching
    - Test cache hit and miss scenarios
    - Test TTL expiration
    - Test cache invalidation
    - _Requirements: 13.1, 13.2, 13.3_

- [ ] 17. Implement comprehensive error handling
  - [ ] 17.1 Add error handling throughout pipeline
    - Implement retry logic with exponential backoff for API calls
    - Implement fallback mechanisms (rule-based extraction, keyword matching)
    - Implement partial result handling for rate limits
    - Add logging for all errors with timestamps
    - Create user-friendly error messages
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7_
  
  - [ ]* 17.2 Write unit tests for error handling
    - Test LLM API failure and fallback
    - Test search API rate limit handling
    - Test NLI model failure and fallback
    - Test invalid URL handling
    - Test no trusted sources scenario
    - Test conflicting evidence scenario
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6_

- [x] 18. Implement Streamlit user interface
  - [x] 18.1 Create main UI layout
    - Create Streamlit app.py with clear title and description
    - Add input section with tabs for URL input and text input
    - Add submit button with validation
    - Add example articles section for demonstration
    - _Requirements: 15.1, 15.7_
  
  - [x] 18.2 Create results display
    - Display overall verdict with color coding (green=TRUE, red=FALSE, yellow=MISLEADING, gray=UNVERIFIED)
    - Display confidence score with progress bar
    - Display factual accuracy score and emotional manipulation score separately
    - Create claim-by-claim breakdown section with expandable details
    - _Requirements: 15.3, 15.4, 7.5_
  
  - [x] 18.3 Create evidence card display
    - Format evidence cards with clear visual separation
    - Highlight discrepancies between claims and evidence
    - Show source name, URL, and relationship label (SUPPORTS/REFUTES/NEUTRAL)
    - Use color coding for relationship types
    - _Requirements: 15.5, 6.2, 6.3_
  
  - [x] 18.4 Add progress indicators
    - Show loading spinner during processing
    - Display progress messages for each stage (extracting claims, retrieving evidence, verifying, synthesizing)
    - Show estimated time remaining
    - _Requirements: 15.2_
  
  - [x] 18.5 Add export functionality
    - Implement export to JSON function
    - Implement export to PDF function (using reportlab or similar)
    - Add download buttons for both formats
    - _Requirements: 15.6_
  
  - [ ]* 18.6 Write UI tests
    - Test input validation in UI
    - Test results display with sample data
    - Test export functionality
    - _Requirements: 15.1, 15.3, 15.6_

- [ ] 19. Implement performance optimizations
  - [ ] 19.1 Optimize for response time targets
    - Ensure claim extraction completes within 5 seconds
    - Ensure evidence retrieval completes within 3 seconds per claim
    - Ensure NLI verification completes within 1 second per pair
    - Ensure total pipeline completes within 30 seconds for 5-10 claims
    - Add performance logging to track bottlenecks
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [ ] 19.2 Implement resource management
    - Limit max claims per article to configured value
    - Limit max evidence per claim to configured value
    - Set timeouts for all external API calls
    - Implement circuit breaker pattern for failing services
    - _Requirements: 17.4, 17.5, 3.5_
  
  - [ ]* 19.3 Write performance tests
    - Test response time for various article sizes
    - Test parallel processing efficiency
    - Test cache performance improvement
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [ ] 20. Final integration and testing
  - [ ] 20.1 Create end-to-end test suite
    - Test complete pipeline with real articles (use cached API responses)
    - Test all error scenarios
    - Test all verdict types (TRUE, FALSE, MISLEADING, UNVERIFIED)
    - Test with various article types (news, opinion, mixed)
    - _Requirements: 18.5_
  
  - [ ] 20.2 Create example articles for demo
    - Curate 5-10 example articles covering different scenarios
    - Include articles with clear true/false claims
    - Include articles with misleading information
    - Include articles with emotional manipulation
    - Add to UI as quick-start examples
    - _Requirements: 15.7_
  
  - [ ]* 20.3 Write property-based tests for system invariants
    - Test idempotency (same input produces same output)
    - Test monotonicity (more supporting evidence increases confidence)
    - Test commutativity (evidence order doesn't affect verdict)
    - _Requirements: 18.5_

- [ ] 21. Checkpoint - Final verification
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 22. Documentation and deployment preparation
  - [ ] 22.1 Create README.md
    - Add project description and features
    - Add installation instructions
    - Add configuration guide (API keys, environment variables)
    - Add usage examples
    - Add troubleshooting section
    - _Requirements: 16.3, 16.4, 16.5_
  
  - [ ] 22.2 Prepare for deployment
    - Test on Streamlit Community Cloud or Hugging Face Spaces
    - Verify all dependencies are in requirements.txt
    - Create deployment configuration files if needed
    - Test with free-tier API limits
    - _Requirements: 16.1, 16.2_

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation and provide opportunities to address issues
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- The implementation uses Python with Streamlit, LangChain, HuggingFace Transformers, and free-tier APIs
- Parallel processing is used throughout to meet the 30-second response time target
- Caching is implemented to reduce API costs and improve performance
- Error handling includes fallback mechanisms to ensure graceful degradation
