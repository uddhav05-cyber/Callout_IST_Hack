# Requirements Document: Fake News Detection System

## Introduction

The Fake News Detection System is a multi-source verification platform that analyzes news articles, text claims, and media content to determine their veracity through explainable AI. The system provides users with transparent, evidence-based assessments that separate factual accuracy from emotional manipulation, empowering them to make informed decisions about information credibility.

## Glossary

- **System**: The Fake News Detection System as a whole
- **Claim_Extractor**: Component that decomposes articles into atomic, verifiable claims
- **Evidence_Retriever**: Component that searches for supporting or contradicting evidence from trusted sources
- **NLI_Engine**: Natural Language Inference engine that compares claims against evidence
- **Synthesizer**: Component that aggregates verification results into final verdicts
- **Tone_Analyzer**: Component that detects emotional manipulation separate from factual content
- **Visual_Verifier**: Component that verifies images and videos through reverse search
- **Atomic_Claim**: A single, verifiable factual statement extracted from an article
- **Evidence**: Information retrieved from external sources to verify a claim
- **Verdict**: Final assessment of claim veracity (TRUE, FALSE, MISLEADING, UNVERIFIED)
- **Evidence_Card**: Visual presentation of claim-evidence comparison with highlighted discrepancies
- **Credibility_Score**: Numerical rating (0-1) of a source's trustworthiness
- **Confidence_Score**: Numerical rating (0-100) of the system's certainty in a verdict
- **NLI_Result**: Output from Natural Language Inference model showing entailment, contradiction, or neutral relationship

## Requirements

### Requirement 1: Article Input Processing

**User Story:** As a user, I want to submit news articles via URL or direct text, so that I can verify their accuracy without manual data entry.

#### Acceptance Criteria

1. WHEN a user provides a valid article URL, THE System SHALL fetch and parse the article content within 10 seconds
2. WHEN a user provides direct text input, THE System SHALL accept text up to 50,000 characters
3. WHEN a user provides an invalid or inaccessible URL, THE System SHALL return a clear error message and suggest text input as an alternative
4. WHEN a user submits an article, THE System SHALL validate the input format before processing
5. THE System SHALL support both HTTP and HTTPS URLs
6. WHEN fetching a URL, THE System SHALL enforce a 10-second timeout and maximum of 3 redirects

### Requirement 2: Claim Extraction

**User Story:** As a user, I want the system to identify specific factual claims in an article, so that I can understand exactly what statements are being verified.

#### Acceptance Criteria

1. WHEN an article is processed, THE Claim_Extractor SHALL decompose it into atomic, verifiable claims
2. WHEN extracting claims, THE Claim_Extractor SHALL filter out opinions and subjective statements
3. WHEN multiple claims are extracted, THE Claim_Extractor SHALL rank them by importance for verification priority
4. WHEN an article contains no verifiable factual claims, THE System SHALL return an UNVERIFIED verdict with explanation
5. THE Claim_Extractor SHALL complete processing within 5 seconds per article
6. WHEN an article is longer than 100 characters, THE Claim_Extractor SHALL extract at least one claim
7. THE Claim_Extractor SHALL assign each claim a unique identifier and importance score between 0 and 1

### Requirement 3: Evidence Retrieval

**User Story:** As a user, I want the system to find evidence from trusted sources, so that I can see what reliable outlets report about the same claims.

#### Acceptance Criteria

1. WHEN a claim is extracted, THE Evidence_Retriever SHALL search for supporting and contradicting evidence from external sources
2. WHEN search results are returned, THE Evidence_Retriever SHALL filter results to include only sources meeting the minimum credibility threshold
3. WHEN filtering sources, THE Evidence_Retriever SHALL assign credibility scores based on source reputation
4. WHEN ranking evidence, THE Evidence_Retriever SHALL use a combined score of 70% relevance and 30% credibility
5. THE Evidence_Retriever SHALL limit results to a maximum of 5 evidence items per claim
6. THE Evidence_Retriever SHALL complete evidence retrieval within 3 seconds per claim
7. WHEN no trusted sources are found for a claim, THE System SHALL mark that claim as UNVERIFIED

### Requirement 4: Cross-Verification with Natural Language Inference

**User Story:** As a user, I want the system to compare claims against evidence using AI, so that I can see whether evidence supports or contradicts each claim.

#### Acceptance Criteria

1. WHEN a claim and evidence pair is provided, THE NLI_Engine SHALL classify the relationship as SUPPORTS, REFUTES, or NEUTRAL
2. WHEN running inference, THE NLI_Engine SHALL generate three scores: entailment, contradiction, and neutral
3. THE NLI_Engine SHALL ensure the sum of the three scores equals 1.0 within a tolerance of 0.01
4. THE NLI_Engine SHALL assign the label matching the highest score
5. THE NLI_Engine SHALL complete verification within 1 second per claim-evidence pair
6. WHEN the NLI model fails to load, THE System SHALL fall back to keyword-based matching and reduce confidence by 30%

### Requirement 5: Score Aggregation and Verdict Generation

**User Story:** As a user, I want to see an overall verdict for the article, so that I can quickly understand whether it's likely true or false.

#### Acceptance Criteria

1. WHEN multiple evidence items are analyzed for a claim, THE System SHALL aggregate NLI scores using weighted averaging
2. WHEN calculating the final verdict, THE System SHALL use the formula: 60% evidence match + 20% source credibility + 20% writing style
3. WHEN a claim has more than 60% supporting evidence and less than 20% refuting evidence, THE System SHALL assign a TRUE verdict
4. WHEN a claim has more than 60% refuting evidence and less than 20% supporting evidence, THE System SHALL assign a FALSE verdict
5. WHEN a claim has both supporting and refuting evidence above 30%, THE System SHALL assign a MISLEADING verdict
6. WHEN insufficient evidence is available, THE System SHALL assign an UNVERIFIED verdict
7. THE System SHALL ensure all confidence scores are between 0 and 100
8. THE System SHALL ensure all credibility scores are between 0 and 1
9. WHEN more than half the claims are false, THE System SHALL reduce the final score by 50%

### Requirement 6: Evidence Card Generation

**User Story:** As a user, I want to see side-by-side comparisons of claims and evidence, so that I can understand the specific discrepancies.

#### Acceptance Criteria

1. WHEN a verdict is generated, THE Synthesizer SHALL create evidence cards for each verified claim
2. WHEN creating evidence cards, THE Synthesizer SHALL include the claim text, evidence snippet, source URL, source name, and relationship label
3. WHEN displaying evidence cards, THE System SHALL highlight specific discrepancies between claims and evidence
4. THE System SHALL ensure every claim in the breakdown has at least one corresponding evidence card
5. WHEN evidence contradicts a claim, THE Synthesizer SHALL identify and display the contradicting portions

### Requirement 7: Tone Analysis and Emotional Manipulation Detection

**User Story:** As a user, I want to see whether an article uses emotional manipulation, so that I can distinguish factual accuracy from persuasive tactics.

#### Acceptance Criteria

1. WHEN an article is analyzed, THE Tone_Analyzer SHALL generate a separate emotional manipulation score
2. WHEN analyzing tone, THE Tone_Analyzer SHALL detect sensationalist phrases and clickbait patterns
3. WHEN calculating the final verdict, THE System SHALL separate factual accuracy scores from emotional manipulation scores
4. THE Tone_Analyzer SHALL assign an objectivity score between 0 and 1
5. THE System SHALL display both factual accuracy and emotional manipulation scores to users

### Requirement 8: Visual Content Verification

**User Story:** As a user, I want to verify images and videos in articles, so that I can detect manipulated or out-of-context media.

#### Acceptance Criteria

1. WHEN a user provides an image URL, THE Visual_Verifier SHALL perform reverse image search
2. WHEN reverse search results are found, THE Visual_Verifier SHALL display the original source and first publication date
3. WHEN analyzing an image, THE Visual_Verifier SHALL detect potential manipulation or editing
4. WHEN manipulation is detected, THE System SHALL classify it as EDITED, DEEPFAKE, or OUT_OF_CONTEXT
5. THE Visual_Verifier SHALL assign a confidence score to manipulation detection results

### Requirement 9: Explanation Generation

**User Story:** As a user, I want clear explanations of verdicts in simple language, so that I can understand the reasoning without technical knowledge.

#### Acceptance Criteria

1. WHEN a verdict is generated, THE Synthesizer SHALL create a human-readable explanation
2. WHEN generating explanations, THE System SHALL use simple, non-technical language
3. WHEN a claim is marked FALSE, THE System SHALL explain which evidence contradicts it and why
4. WHEN a claim is marked MISLEADING, THE System SHALL explain the conflicting evidence
5. THE System SHALL provide claim-by-claim breakdowns with individual explanations

### Requirement 10: Performance and Response Time

**User Story:** As a user, I want fast verification results, so that I can quickly assess multiple articles.

#### Acceptance Criteria

1. THE System SHALL complete the entire verification pipeline within 30 seconds for articles with 5-10 claims
2. THE Claim_Extractor SHALL process articles within 5 seconds
3. THE Evidence_Retriever SHALL retrieve evidence within 3 seconds per claim using parallel processing
4. THE NLI_Engine SHALL verify claim-evidence pairs within 1 second each
5. WHEN processing multiple claims, THE System SHALL use parallel processing to reduce total time

### Requirement 11: Error Handling and Resilience

**User Story:** As a user, I want the system to handle errors gracefully, so that I can still get partial results when services fail.

#### Acceptance Criteria

1. WHEN an LLM API call fails, THE System SHALL retry with exponential backoff up to 3 attempts
2. WHEN all LLM retries fail, THE System SHALL fall back to rule-based claim extraction
3. WHEN a search API returns a rate limit error, THE System SHALL queue remaining claims and return partial results
4. WHEN the NLI model fails to load, THE System SHALL fall back to keyword-based matching and display a warning
5. WHEN no trusted sources are found, THE System SHALL return an UNVERIFIED verdict with explanation
6. WHEN conflicting evidence is found, THE System SHALL assign a MISLEADING verdict and display all evidence
7. THE System SHALL log all errors with timestamps for debugging

### Requirement 12: Source Credibility Management

**User Story:** As a user, I want evidence from trustworthy sources, so that I can rely on the verification results.

#### Acceptance Criteria

1. THE System SHALL maintain a database of source credibility scores
2. WHEN looking up a source, THE System SHALL return a credibility score between 0 and 1
3. WHEN a source is not in the database, THE System SHALL assign a default credibility score of 0.5
4. THE System SHALL categorize sources as TRUSTED (0.8-1.0), MAINSTREAM (0.5-0.79), QUESTIONABLE (0.3-0.49), or UNRELIABLE (0.0-0.29)
5. WHEN filtering evidence, THE System SHALL exclude sources below the minimum credibility threshold

### Requirement 13: Caching and Optimization

**User Story:** As a developer, I want the system to cache results, so that repeated queries are faster and API costs are reduced.

#### Acceptance Criteria

1. WHEN an article is verified, THE System SHALL cache the results using a hash-based key
2. WHEN a cached article is requested again, THE System SHALL return cached results instead of re-processing
3. THE System SHALL set a 24-hour time-to-live for cached search results
4. THE System SHALL cache the NLI model in memory to avoid reloading
5. THE System SHALL cache source credibility scores with weekly updates

### Requirement 14: Input Validation and Security

**User Story:** As a system administrator, I want robust input validation, so that the system is protected from malicious inputs.

#### Acceptance Criteria

1. WHEN validating URLs, THE System SHALL block private IP ranges including localhost and 192.168.x.x
2. WHEN validating text input, THE System SHALL enforce a maximum length of 50,000 characters
3. WHEN validating image input, THE System SHALL accept only JPEG, PNG, and GIF formats with a maximum size of 10 MB
4. THE System SHALL sanitize HTML and script tags from all text inputs
5. THE System SHALL validate UTF-8 encoding for all text inputs
6. WHEN fetching URLs, THE System SHALL enforce HTTPS when possible

### Requirement 15: User Interface and Display

**User Story:** As a user, I want an intuitive interface, so that I can easily submit articles and understand results.

#### Acceptance Criteria

1. WHEN the application starts, THE System SHALL display a clear interface for article submission
2. WHEN processing an article, THE System SHALL display progress indicators and loading animations
3. WHEN results are ready, THE System SHALL display the overall verdict, confidence score, factual accuracy score, and emotional manipulation score
4. WHEN displaying results, THE System SHALL show claim-by-claim breakdowns with supporting and contradicting evidence
5. WHEN displaying evidence cards, THE System SHALL format them with clear visual separation and highlighted discrepancies
6. THE System SHALL allow users to export results as PDF or JSON
7. THE System SHALL provide example articles for demonstration purposes

### Requirement 16: API Integration and Configuration

**User Story:** As a developer, I want flexible API configuration, so that I can use different service providers based on availability and cost.

#### Acceptance Criteria

1. THE System SHALL support multiple LLM providers including OpenAI, Groq, and Ollama
2. THE System SHALL support multiple search API providers including Serper.dev and Tavily
3. THE System SHALL load API keys from environment variables
4. THE System SHALL allow configuration of maximum claims per article, maximum evidence per claim, and minimum credibility threshold
5. THE System SHALL allow configuration of the NLI model name and cache TTL

### Requirement 17: Claim Importance Ranking

**User Story:** As a user, I want the most important claims verified first, so that I get the most relevant information quickly.

#### Acceptance Criteria

1. WHEN multiple claims are extracted, THE Claim_Extractor SHALL assign importance scores to each claim
2. WHEN ranking claims, THE System SHALL sort them by importance in descending order
3. WHEN processing claims, THE System SHALL prioritize high-importance claims for verification
4. THE System SHALL ensure importance scores are between 0 and 1
5. WHEN API quotas are limited, THE System SHALL verify only the highest-importance claims

### Requirement 18: Verdict Consistency

**User Story:** As a user, I want consistent verdicts, so that similar evidence patterns produce similar results.

#### Acceptance Criteria

1. WHEN a verdict is LIKELY_TRUE, THE System SHALL ensure the confidence score is greater than 60
2. WHEN a verdict is LIKELY_FALSE, THE System SHALL ensure the confidence score is greater than 60
3. WHEN a verdict is UNVERIFIED, THE System SHALL ensure the confidence score is less than 50
4. WHEN a verdict is MISLEADING, THE System SHALL ensure the confidence score is approximately 50
5. WHEN the same article is verified multiple times, THE System SHALL produce identical results
6. WHEN more than 40% of claims are FALSE, THE System SHALL assign a LIKELY_FALSE verdict
7. WHEN the final score is below 40, THE System SHALL assign a LIKELY_FALSE verdict
8. WHEN more than 60% of claims are TRUE and score is above 65, THE System SHALL assign a LIKELY_TRUE verdict
9. WHEN the score is between 40 and 65, THE System SHALL assign a MISLEADING verdict
10. THE System SHALL NOT assign LIKELY_TRUE verdict to articles with predominantly false claims

### Requirement 19: Evidence Relevance Scoring

**User Story:** As a user, I want relevant evidence, so that I can see information directly related to each claim.

#### Acceptance Criteria

1. WHEN evidence is retrieved, THE Evidence_Retriever SHALL assign a relevance score between 0 and 1
2. WHEN calculating relevance, THE System SHALL compare claim text to evidence snippets
3. WHEN ranking evidence, THE System SHALL prioritize items with higher relevance scores
4. THE System SHALL ensure all evidence items have positive relevance scores

### Requirement 20: Parallel Processing

**User Story:** As a user, I want fast processing, so that I don't wait unnecessarily for sequential operations.

#### Acceptance Criteria

1. WHEN retrieving evidence for multiple claims, THE System SHALL process claims in parallel
2. WHEN running NLI inference for multiple claim-evidence pairs, THE System SHALL batch process when possible
3. WHEN making API calls, THE System SHALL use asynchronous operations
4. THE System SHALL limit concurrent operations to avoid overwhelming external services

