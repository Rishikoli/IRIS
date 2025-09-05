# IRIS RegTech Platform - Demo Script

## Overview
This demo script showcases all major features of the IRIS (Intelligent Risk & Investigation System) RegTech platform. The demo is designed to demonstrate the platform's capabilities to both investors and regulators.

## Demo Environment Setup

### Prerequisites
1. Backend server running on `http://localhost:8000`
2. Frontend application running on `http://localhost:3000`
3. Sample data populated using `python backend/generate_sample_data.py`
4. All services (Gemini API, mock external APIs) configured

### Demo Data Overview
- **50 realistic investment tips** with varying risk levels (High: 30%, Medium: 40%, Low: 30%)
- **25 PDF document checks** including fake SEBI circulars and authentic documents
- **30 days of heatmap data** across 12 sectors and 15 regions
- **Multi-source data integration** from FMP, Google Trends, and Economic Times
- **3 fraud chain examples** demonstrating different fraud patterns
- **Forecasting data** for next 3 months across sectors and regions
- **Human review cases** showing AI-human collaboration

---

## Demo Scenario 1: Investor Protection Features (10 minutes)

### Target Audience: Individual Investors
**Objective:** Show how investors can protect themselves from fraud

### 1.1 Tip Risk Analysis (3 minutes)

**Navigation:** Home → Check Investment Tip

**Demo Steps:**
1. **High-Risk Tip Analysis**
   ```
   Input: "🚀 URGENT! Buy RELIANCE NOW! Guaranteed 500% returns in 2 weeks! Inside information from company director. Limited time offer! WhatsApp +91-9876543210 for more details. Don't miss this golden opportunity! 💰💰💰"
   ```
   
   **Expected Results:**
   - Risk Level: **HIGH** (Red badge)
   - Risk Score: **85-95**
   - Detected Issues:
     - Unrealistic return promises (500% guaranteed)
     - Urgency pressure tactics
     - Claims of insider information
     - Requests for contact via unofficial channels
   - Stock Symbol Detected: **RELIANCE**
   - Advisor Status: **Not mentioned/Unverified**

2. **Medium-Risk Tip Analysis**
   ```
   Input: "Good opportunity in TCS. Technical analysis shows strong breakout pattern. Target ₹4000 in 2-3 months. Stop loss at ₹3200. Do your own research before investing. Not SEBI registered advisor."
   ```
   
   **Expected Results:**
   - Risk Level: **MEDIUM** (Yellow badge)
   - Risk Score: **45-65**
   - Detected Issues:
     - Lacks proper disclaimers
     - Provides specific price targets without detailed analysis
     - Unverified advisor credentials
   - Stock Symbol Detected: **TCS**

3. **Low-Risk Educational Content**
   ```
   Input: "Long term investment idea: INFY is a fundamentally strong company with consistent growth. Current valuation seems reasonable. Suitable for 3-5 year investment horizon. Please do thorough research and consult certified financial planner."
   ```
   
   **Expected Results:**
   - Risk Level: **LOW** (Green badge)
   - Risk Score: **15-35**
   - Positive Indicators:
     - Educational content with proper disclaimers
     - Encourages independent research
     - Mentions consulting financial advisors
     - No unrealistic promises

### 1.2 Advisor Verification (2 minutes)

**Navigation:** Verify Financial Advisor

**Demo Steps:**
1. **Search for Legitimate Advisor**
   ```
   Input: "Rajesh Kumar"
   ```
   **Expected Results:**
   - Multiple matches found
   - Display registration details, validity period
   - SEBI registration status: **Verified**

2. **Search for Fake Advisor**
   ```
   Input: "Rajesh Sharma"
   ```
   **Expected Results:**
   - No matches found in SEBI directory
   - Clear warning: **"Not registered with SEBI"**
   - Recommendation to verify credentials

### 1.3 PDF Document Authenticity Check (5 minutes)

**Navigation:** Upload & Verify Documents

**Demo Steps:**
1. **Upload Fake SEBI Document**
   - Use sample file: `SEBI_Circular_Fake_Investment_Schemes.pdf`
   
   **Expected Results:**
   - Authenticity Score: **15-25** (Very Low)
   - Status: **Likely Fake** (Red warning)
   - Detected Anomalies:
     - Font inconsistency detected
     - Missing digital signature
     - Suspicious metadata timestamps
     - Logo quality issues
     - Grammatical errors in official language
   - OCR Text Preview showing suspicious content

2. **Upload Authentic Document**
   - Use sample file: `RBI_Policy_Document_Authentic.pdf`
   
   **Expected Results:**
   - Authenticity Score: **85-95** (High)
   - Status: **Likely Authentic** (Green indicator)
   - No significant anomalies detected
   - Professional formatting and language

**Key Demo Points:**
- Show drag-and-drop functionality
- Highlight real-time processing
- Explain authenticity scoring methodology
- Demonstrate clear visual indicators for fake vs. authentic documents

---

## Demo Scenario 2: Regulatory Monitoring Dashboard (15 minutes)

### Target Audience: Financial Regulators
**Objective:** Demonstrate comprehensive fraud monitoring and investigation capabilities

### 2.1 Unified Regulatory Dashboard (5 minutes)

**Navigation:** Dashboard

**Demo Steps:**
1. **Fraud Activity Heatmap**
   - Show sector-wise fraud distribution
   - Highlight high-activity sectors (Banking, Technology, Real Estate)
   - Switch to region-wise view
   - Point out hotspots (Mumbai, Delhi, Bangalore)

2. **Multi-Source Data Integration**
   - Show FMP market data indicators
   - Display Google Trends fraud keyword spikes
   - Highlight Economic Times regulatory news
   - Demonstrate data correlation analysis

3. **Time-based Filtering**
   - Filter by daily, weekly, monthly views
   - Show trend progression over time
   - Identify emerging patterns

### 2.2 AI-Powered Forecasting (4 minutes)

**Navigation:** Dashboard → Forecasting Section

**Demo Steps:**
1. **Sector Risk Forecasting**
   - Display next 3 months predictions
   - Show confidence intervals
   - Explain contributing factors:
     - Historical fraud patterns (30% weight)
     - Market volatility (25% weight)
     - Regulatory environment (20% weight)
     - Social media activity (25% weight)

2. **Regional Risk Forecasting**
   - Show geographic risk distribution
   - Highlight emerging risk areas
   - Display demographic and economic factors

3. **Explainable AI Features**
   - Show factor attribution
   - Display confidence ranges
   - Demonstrate forecast accuracy tracking

### 2.3 Fraud Chain Visualization (6 minutes)

**Navigation:** Fraud Chain Analysis

**Demo Steps:**
1. **Pump and Dump Chain**
   - Display "Pump and Dump - TECHM Stock" chain
   - Show connected nodes:
     - Initial tip (fake insider information)
     - Social media propagation
     - Stock price manipulation
     - Investor complaints
   - Demonstrate interactive exploration
   - Show timeline progression

2. **Fake Document Distribution Chain**
   - Display "Fake SEBI Circular Distribution" chain
   - Show how fake documents legitimize fraud schemes
   - Trace document distribution across platforms
   - Link to affected investors

3. **Unregistered Advisor Network**
   - Show network of connected fake advisors
   - Display cross-platform operations
   - Demonstrate pattern recognition

**Interactive Features:**
- Node clicking for detailed information
- Zoom and pan capabilities
- Export functionality (JSON, CSV)
- Timeline animation

---

## Demo Scenario 3: Human-in-the-Loop Review System (8 minutes)

### Target Audience: Regulatory Review Teams
**Objective:** Show AI-human collaboration for decision accuracy

### 3.1 Review Queue Management (4 minutes)

**Navigation:** Review System

**Demo Steps:**
1. **Priority Queue Display**
   - Show cases sorted by priority (High, Medium, Low)
   - Display AI confidence scores
   - Filter by case type (Tips, Documents, Fraud Chains)

2. **Case Review Process**
   - Select high-priority tip assessment
   - Show AI decision details:
     - Original risk level: Medium
     - AI confidence: 72%
     - Reasoning provided
   
3. **Human Override Example**
   - Demonstrate reviewer interface
   - Show decision options: Approve, Override, Need More Info
   - Add reviewer notes
   - Submit decision with rationale

### 3.2 AI-Human Performance Analytics (4 minutes)

**Navigation:** Review Analytics

**Demo Steps:**
1. **Decision Accuracy Metrics**
   - Show AI vs. Human agreement rates
   - Display override patterns
   - Highlight improvement areas

2. **Model Learning Feedback**
   - Show how human feedback improves AI
   - Display confidence score improvements
   - Demonstrate active learning capabilities

3. **Quality Assurance Dashboard**
   - Review decision consistency
   - Track reviewer performance
   - Show system reliability metrics

---

## Demo Scenario 4: Real-Time Monitoring & Alerts (5 minutes)

### Target Audience: Operations Teams
**Objective:** Demonstrate live monitoring capabilities

### 4.1 WebSocket Real-Time Updates (3 minutes)

**Demo Steps:**
1. **Live Alert Simulation**
   - Trigger high-risk tip submission
   - Show real-time dashboard updates
   - Display instant notifications

2. **Multi-Source Data Streaming**
   - Simulate market data updates
   - Show Google Trends spikes
   - Display news article processing

3. **Fraud Chain Evolution**
   - Show live chain updates
   - Demonstrate automatic linking
   - Display pattern recognition

### 4.2 Alert Management (2 minutes)

**Demo Steps:**
1. **Alert Prioritization**
   - Show alert severity levels
   - Demonstrate escalation rules
   - Display notification preferences

2. **Response Coordination**
   - Show alert acknowledgment
   - Demonstrate team coordination
   - Display resolution tracking

---

## Demo Scenario 5: Advanced Analytics & Reporting (7 minutes)

### Target Audience: Senior Management & Policy Makers
**Objective:** Show strategic insights and trend analysis

### 5.1 Comprehensive Analytics (4 minutes)

**Navigation:** Analytics Dashboard

**Demo Steps:**
1. **Platform-Wide Statistics**
   - Total tips analyzed: 50
   - High-risk cases identified: 15 (30%)
   - Documents verified: 25
   - Fraud chains detected: 3
   - Average response time: <2 seconds

2. **Trend Analysis**
   - Show fraud pattern evolution
   - Display seasonal variations
   - Highlight emerging threats

3. **Sector & Regional Insights**
   - Banking sector: Highest fraud activity
   - Mumbai region: Most cases reported
   - Technology sector: Emerging risks

### 5.2 Regulatory Reporting (3 minutes)

**Demo Steps:**
1. **Compliance Reports**
   - Generate monthly fraud summary
   - Show regulatory format compliance
   - Display audit trail completeness

2. **Export Capabilities**
   - Demonstrate PDF report generation
   - Show Excel data export
   - Display API integration options

3. **Stakeholder Dashboards**
   - Executive summary view
   - Operational metrics
   - Public awareness statistics

---

## Demo Wrap-up & Q&A (5 minutes)

### Key Takeaways
1. **For Investors:**
   - Easy-to-use tools for fraud detection
   - Clear risk indicators and explanations
   - Comprehensive advisor and document verification

2. **For Regulators:**
   - Real-time fraud monitoring
   - AI-powered predictive analytics
   - Comprehensive investigation tools
   - Human oversight and quality control

3. **For the Financial Ecosystem:**
   - Proactive fraud prevention
   - Data-driven policy making
   - Enhanced investor protection
   - Improved market integrity

### Technical Highlights
- **AI Integration:** Gemini 2.0 Flash for multimodal analysis
- **Real-time Processing:** Sub-2-second response times
- **Scalable Architecture:** Handles high-volume data streams
- **Multi-source Intelligence:** Integrated market, news, and trend data
- **Explainable AI:** Transparent decision-making process

### Future Enhancements
- Machine learning model improvements
- Additional data source integrations
- Enhanced visualization capabilities
- Mobile application development
- API ecosystem expansion

---

## Demo Troubleshooting

### Common Issues & Solutions

1. **Slow API Responses**
   - Check Gemini API key configuration
   - Verify database connection
   - Monitor system resources

2. **Missing Sample Data**
   - Run `python backend/generate_sample_data.py`
   - Verify database tables created
   - Check data insertion logs

3. **WebSocket Connection Issues**
   - Verify WebSocket endpoint configuration
   - Check browser console for errors
   - Test connection manually

4. **Frontend Display Issues**
   - Clear browser cache
   - Check React development server
   - Verify API endpoint connectivity

### Demo Environment Reset
```bash
# Reset database and regenerate sample data
cd backend
python generate_sample_data.py

# Restart services
python start_server.py

# Verify frontend
cd ../frontend
npm run dev
```

---

## Demo Success Metrics

### Engagement Indicators
- [ ] Audience asks technical questions
- [ ] Requests for specific use case demonstrations
- [ ] Interest in implementation timeline
- [ ] Questions about integration capabilities

### Feature Comprehension
- [ ] Understanding of AI risk assessment
- [ ] Appreciation for multi-source data integration
- [ ] Recognition of fraud chain visualization value
- [ ] Grasp of human-AI collaboration benefits

### Business Impact Recognition
- [ ] Acknowledgment of investor protection value
- [ ] Understanding of regulatory efficiency gains
- [ ] Recognition of proactive fraud prevention
- [ ] Appreciation for data-driven insights

This comprehensive demo script ensures all major IRIS platform features are showcased effectively, demonstrating both technical capabilities and business value to different stakeholder groups.