# Requirements Document

## Introduction

IRIS (Intelligent Risk & Investigation System) is a comprehensive RegTech platform designed to detect, explain, forecast, and visualize fraud chains affecting retail investors in India. The system serves two primary audiences: individual investors who need to verify tips and advisors, and regulators who require real-time monitoring and investigation tools. The platform leverages AI (Gemini 2.0 Flash) for multimodal analysis of text and documents, providing risk assessments, fraud detection, and predictive analytics.

## Requirements

### Requirement 1: Tip Risk Analysis for Investors

**User Story:** As an investor, I want to paste a suspicious investment tip and get an immediate risk assessment with clear explanations, so that I can make informed decisions and avoid potential fraud.

#### Acceptance Criteria

1. WHEN an investor submits a text message THEN the system SHALL analyze the content using AI and return a risk level (Low/Medium/High) with a numerical score (0-100)
2. WHEN the analysis is complete THEN the system SHALL provide specific reasons for the risk assessment in natural language
3. WHEN a stock symbol is mentioned in the tip THEN the system SHALL identify and highlight it in the response
4. WHEN the tip mentions an advisor THEN the system SHALL indicate whether the advisor appears to be registered
5. IF the risk level is High THEN the system SHALL display a red indicator with prominent warnings
6. IF the risk level is Medium THEN the system SHALL display a yellow indicator with caution messages
7. IF the risk level is Low THEN the system SHALL display a green indicator with reassurance

### Requirement 2: Advisor Verification

**User Story:** As an investor, I want to verify if a financial advisor is registered with SEBI, so that I can ensure I'm dealing with legitimate professionals.

#### Acceptance Criteria

1. WHEN an investor searches for an advisor by name or ID THEN the system SHALL check against the SEBI directory
2. WHEN an advisor is found THEN the system SHALL display their registration status, details, and validity period
3. WHEN an advisor is not found THEN the system SHALL clearly indicate they are not registered and provide warnings
4. WHEN the search query is ambiguous THEN the system SHALL return multiple matches with clear differentiation
5. WHEN the SEBI data is unavailable THEN the system SHALL inform the user and suggest alternative verification methods

### Requirement 3: PDF Document Authenticity Check

**User Story:** As an investor, I want to upload PDF documents claiming to be from SEBI or other regulatory bodies and verify their authenticity, so that I can avoid falling for fake regulatory documents.

#### Acceptance Criteria

1. WHEN an investor uploads a PDF file THEN the system SHALL perform OCR to extract text content
2. WHEN the OCR is complete THEN the system SHALL analyze the document using AI for authenticity markers
3. WHEN analyzing the document THEN the system SHALL check for digital signatures, font consistency, logo accuracy, and metadata anomalies
4. WHEN the analysis is complete THEN the system SHALL provide a likelihood score for document authenticity
5. WHEN suspicious elements are detected THEN the system SHALL list specific anomalies found
6. WHEN the document appears fake THEN the system SHALL provide clear warnings and explain the detected issues
7. IF the file is not a PDF or is corrupted THEN the system SHALL reject the upload with appropriate error messages

### Requirement 4: Unified Regulatory Overview Dashboard

**User Story:** As a regulator, I want to access a comprehensive dashboard that combines real-time fraud activity patterns with AI-powered forecasting in one unified view, so that I can simultaneously monitor current threats and prepare for future risks.

#### Acceptance Criteria

1. WHEN a regulator accesses the dashboard THEN the system SHALL display fraud activity heatmaps by sector and region alongside AI forecasting predictions
2. WHEN viewing the unified dashboard THEN the system SHALL allow filtering by time period (daily, weekly, monthly) for both current and forecasted data
3. WHEN fraud patterns are detected THEN the system SHALL highlight areas with increasing activity and correlate with forecast predictions
4. WHEN clicking on a heatmap region THEN the system SHALL provide drill-down details of specific cases and related forecast rationale
5. WHEN new high-risk cases are detected THEN the system SHALL provide real-time alerts and update forecast confidence levels
6. WHEN generating reports THEN the system SHALL include trend analysis, statistical summaries, and forecast accuracy metrics
7. WHEN relevant financial news is available THEN the system SHALL overlay news indicators on both current and forecasted heatmaps
8. WHEN clicking on news indicators THEN the system SHALL display related news articles with fraud relevance scores and forecast impact
9. WHEN news sentiment indicates potential fraud risks THEN the system SHALL correlate news data with both current patterns and future predictions
10. WHEN accessing forecasts within the dashboard THEN the system SHALL display predicted risk levels for the next month by sector and region
11. WHEN generating forecasts THEN the system SHALL use historical fraud data and trend analysis with AI-generated rationale
12. WHEN presenting forecasts THEN the system SHALL provide explainable factors and confidence intervals alongside current data
13. WHEN risk levels change significantly THEN the system SHALL highlight these changes prominently in both current and forecast views
14. WHEN forecasts are updated THEN the system SHALL maintain historical forecast accuracy metrics and compare with actual outcomes
15. WHEN switching between current and forecast views THEN the system SHALL provide seamless navigation within the unified dashboard

### Requirement 6: Chain-of-Fraud Detection and Visualization

**User Story:** As a regulator, I want to visualize the complete lifecycle of fraud cases from initial tips to investor losses, so that I can understand fraud patterns and improve detection mechanisms.

#### Acceptance Criteria

1. WHEN fraud cases are related THEN the system SHALL automatically link them into fraud chains
2. WHEN displaying fraud chains THEN the system SHALL show nodes (tips, documents, stocks, complaints) and edges (relationships)
3. WHEN a user clicks on a chain node THEN the system SHALL display detailed information about that element
4. WHEN chains are complex THEN the system SHALL provide filtering and zoom capabilities
5. WHEN new elements are added to existing chains THEN the system SHALL update the visualization automatically
6. WHEN exporting chain data THEN the system SHALL provide structured formats for further analysis

### Requirement 7: Human-in-the-Loop Review System

**User Story:** As a regulator, I want to review AI decisions and provide overrides with explanations, so that I can ensure accuracy and continuously improve the system's performance.

#### Acceptance Criteria

1. WHEN AI makes risk assessments THEN the system SHALL queue them for potential human review based on confidence levels
2. WHEN a reviewer accesses the queue THEN the system SHALL display cases sorted by priority and risk level
3. WHEN reviewing a case THEN the system SHALL allow approval, override, or request for more information
4. WHEN overriding an AI decision THEN the system SHALL require explanatory notes from the reviewer
5. WHEN decisions are made THEN the system SHALL log all actions with timestamps and reviewer identification
6. WHEN generating reports THEN the system SHALL show AI vs human decision accuracy metrics
7. WHEN patterns in overrides are detected THEN the system SHALL flag potential model improvement areas

### Requirement 8: System Integration and API

**User Story:** As a developer, I want well-defined APIs connecting the frontend and backend systems, so that the platform can be maintained and extended efficiently.

#### Acceptance Criteria

1. WHEN the frontend makes API requests THEN the system SHALL respond with consistent JSON structures
2. WHEN errors occur THEN the system SHALL return standardized error responses with appropriate HTTP status codes
3. WHEN handling file uploads THEN the system SHALL support multipart form data with size and type validation
4. WHEN providing real-time updates THEN the system SHALL support WebSocket connections for live alerts
5. WHEN accessing sensitive endpoints THEN the system SHALL implement proper authentication and authorization
6. WHEN API usage exceeds limits THEN the system SHALL implement rate limiting with clear error messages
7. WHEN CORS is required THEN the system SHALL properly configure cross-origin resource sharing for the frontend

### Requirement 9: Multi-Source Real-time Data Integration and Correlation

**User Story:** As a regulator, I want to see real-time financial news, market data, and trend analysis overlaid on fraud heatmaps with AI-powered relevance scoring, so that I can correlate market events with fraud activity patterns and identify emerging threats.

#### Acceptance Criteria

1. WHEN the system fetches financial data THEN it SHALL integrate with FMP API to retrieve real-time stock prices, market news, and financial statements
2. WHEN the system monitors trends THEN it SHALL integrate with Google Trends API to track search volume for fraud-related keywords by region
3. WHEN the system gathers news THEN it SHALL perform real-time web scraping of Economic Times for Indian financial news
4. WHEN data is retrieved from multiple sources THEN the system SHALL use AI to score their relevance to fraud detection (0-100 scale)
5. WHEN high-relevance data is identified THEN the system SHALL display multi-source indicators on corresponding heatmap sectors/regions
6. WHEN a user clicks on data indicators THEN the system SHALL show consolidated summaries with fraud correlation analysis from all sources
7. WHEN Google Trends show spikes in fraud-related searches THEN the system SHALL highlight regions with increased fraud risk
8. WHEN FMP data indicates unusual stock activity THEN the system SHALL correlate with existing fraud cases and tip analysis
9. WHEN Economic Times articles mention regulatory actions THEN the system SHALL cross-reference with platform fraud patterns
10. WHEN any data source is unavailable THEN the system SHALL gracefully degrade without affecting core heatmap functionality
11. WHEN displaying data overlays THEN the system SHALL provide toggle controls for each data source (FMP, Google Trends, Economic Times)
12. WHEN market volatility increases THEN the system SHALL automatically correlate with fraud pattern changes across all data sources

### Requirement 10: Data Security and Compliance

**User Story:** As a compliance officer, I want to ensure that the system handles sensitive financial data securely and meets regulatory requirements, so that we maintain user trust and legal compliance.

#### Acceptance Criteria

1. WHEN storing user data THEN the system SHALL encrypt sensitive information at rest and in transit
2. WHEN processing documents THEN the system SHALL not retain private investor communications beyond analysis
3. WHEN accessing the system THEN the system SHALL implement role-based access controls
4. WHEN logging activities THEN the system SHALL maintain audit trails without exposing sensitive data
5. WHEN displaying results THEN the system SHALL include appropriate disclaimers about informational nature
6. WHEN handling API keys THEN the system SHALL store them securely in environment variables
7. WHEN deploying to production THEN the system SHALL enforce HTTPS and implement basic security headers