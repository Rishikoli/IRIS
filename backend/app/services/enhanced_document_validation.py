import asyncio
import json
import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import httpx

from app.services.fmp_service import FMPIntegrationService
from app.services.google_trends_service import GoogleTrendsService
from app.services.economic_times_service import EconomicTimesScrapingService
from app.services.gemini_service import GeminiService

class DocumentValidationResult(BaseModel):
    """Enhanced document validation result with multi-source verification"""
    overall_authenticity_score: int  # 0-100
    is_likely_authentic: bool
    validation_sources: List[str]
    
    # Company/Entity validation
    company_verification: Optional[Dict] = None
    financial_data_consistency: Optional[Dict] = None
    
    # News and trends validation
    news_correlation: Optional[Dict] = None
    trend_analysis: Optional[Dict] = None
    
    # Cross-source validation
    cross_source_flags: List[str] = []
    cross_source_confirmations: List[str] = []
    
    # Enhanced AI analysis
    ai_content_analysis: Optional[Dict] = None
    
    # Recommendations
    validation_confidence: float  # 0.0-1.0
    recommendations: List[str] = []
    
    # Processing metadata
    processing_time_ms: int
    sources_checked: Dict[str, bool] = {}

class EnhancedDocumentValidator:
    """Enhanced document validator using multi-source data verification"""
    
    def __init__(self):
        self.fmp_service = FMPIntegrationService()
        self.trends_service = GoogleTrendsService()
        self.news_service = EconomicTimesScrapingService()
        self.gemini_service = GeminiService()
        
    async def validate_document(
        self, 
        ocr_text: str, 
        filename: str, 
        basic_anomalies: List[Dict],
        basic_score: int
    ) -> DocumentValidationResult:
        """
        Perform enhanced document validation using multiple data sources
        """
        start_time = datetime.now()
        
        result = DocumentValidationResult(
            overall_authenticity_score=basic_score,
            is_likely_authentic=basic_score >= 60,
            validation_sources=[],
            processing_time_ms=0,
            validation_confidence=0.5
        )
        
        try:
            # Extract entities and claims from document
            entities = await self._extract_entities_and_claims(ocr_text, filename)
            
            # Parallel validation across multiple sources
            validation_tasks = []
            
            # Company/Financial validation
            if entities.get('companies') or entities.get('stock_symbols'):
                validation_tasks.append(self._validate_company_information(entities))
                result.validation_sources.append('fmp_financial_data')
            
            # News correlation validation
            if entities.get('companies') or entities.get('regulatory_claims'):
                validation_tasks.append(self._validate_news_correlation(entities))
                result.validation_sources.append('economic_times_news')
            
            # Trend analysis validation
            if entities.get('companies') or entities.get('keywords'):
                validation_tasks.append(self._validate_trend_analysis(entities))
                result.validation_sources.append('google_trends')
            
            # Enhanced AI content analysis
            validation_tasks.append(self._enhanced_ai_analysis(ocr_text, filename, entities))
            result.validation_sources.append('gemini_ai_analysis')
            
            # Execute all validations in parallel
            validation_results = await asyncio.gather(*validation_tasks, return_exceptions=True)
            
            # Process validation results
            await self._process_validation_results(result, validation_results, entities)
            
            # Calculate final authenticity score
            result.overall_authenticity_score = await self._calculate_enhanced_score(
                basic_score, result, basic_anomalies
            )
            result.is_likely_authentic = result.overall_authenticity_score >= 60
            
            # Generate recommendations
            result.recommendations = await self._generate_recommendations(result, entities)
            
        except Exception as e:
            print(f"Enhanced validation error: {e}")
            result.cross_source_flags.append(f"Validation error: {str(e)}")
            result.validation_confidence = 0.3
        
        # Calculate processing time
        end_time = datetime.now()
        result.processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        return result
    
    async def _extract_entities_and_claims(self, text: str, filename: str) -> Dict[str, Any]:
        """Extract companies, stock symbols, claims, and other entities from document"""
        entities = {
            'companies': [],
            'stock_symbols': [],
            'regulatory_claims': [],
            'financial_figures': [],
            'dates': [],
            'keywords': [],
            'document_type': 'unknown'
        }
        
        text_lower = text.lower()
        
        # Extract stock symbols (NSE/BSE format)
        stock_pattern = r'\b[A-Z]{2,6}\b'
        potential_stocks = re.findall(stock_pattern, text)
        # Filter common false positives
        excluded = {'SEBI', 'NSE', 'BSE', 'RBI', 'IRDAI', 'PDF', 'CEO', 'CFO', 'IPO', 'FPO'}
        entities['stock_symbols'] = [s for s in potential_stocks if s not in excluded]
        
        # Extract company names (basic pattern matching)
        company_patterns = [
            r'([A-Z][a-z]+ (?:Limited|Ltd|Corporation|Corp|Inc|Company))',
            r'([A-Z][a-z]+ [A-Z][a-z]+ (?:Limited|Ltd))',
        ]
        for pattern in company_patterns:
            matches = re.findall(pattern, text)
            entities['companies'].extend(matches)
        
        # Extract regulatory claims
        regulatory_keywords = [
            'sebi', 'securities and exchange board', 'rbi', 'reserve bank',
            'irdai', 'insurance regulatory', 'mca', 'ministry of corporate affairs'
        ]
        for keyword in regulatory_keywords:
            if keyword in text_lower:
                entities['regulatory_claims'].append(keyword)
        
        # Extract financial figures
        financial_pattern = r'₹\s*[\d,]+(?:\.\d+)?(?:\s*(?:crore|lakh|thousand))?'
        entities['financial_figures'] = re.findall(financial_pattern, text)
        
        # Extract dates
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{4}',
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',
            r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}'
        ]
        for pattern in date_patterns:
            entities['dates'].extend(re.findall(pattern, text))
        
        # Determine document type
        if 'sebi' in text_lower or 'securities and exchange board' in text_lower:
            entities['document_type'] = 'sebi_document'
        elif 'annual report' in text_lower or 'financial statement' in text_lower:
            entities['document_type'] = 'financial_report'
        elif 'circular' in text_lower or 'notification' in text_lower:
            entities['document_type'] = 'regulatory_circular'
        elif 'prospectus' in text_lower:
            entities['document_type'] = 'prospectus'
        
        # Extract relevant keywords for trend analysis
        keywords = ['fraud', 'scam', 'investigation', 'penalty', 'violation', 'compliance']
        entities['keywords'] = [kw for kw in keywords if kw in text_lower]
        
        return entities
    
    async def _validate_company_information(self, entities: Dict) -> Dict:
        """Validate company information using FMP financial data"""
        try:
            validation_result = {
                'source': 'fmp_financial_data',
                'companies_verified': [],
                'companies_not_found': [],
                'financial_inconsistencies': [],
                'market_data_flags': [],
                'confidence': 0.5
            }
            
            # Check each company/stock symbol
            for symbol in entities.get('stock_symbols', []):
                try:
                    # Get company profile
                    company_data = await self.fmp_service.get_company_profile(symbol)
                    if company_data:
                        validation_result['companies_verified'].append({
                            'symbol': symbol,
                            'name': company_data.get('companyName', ''),
                            'sector': company_data.get('sector', ''),
                            'market_cap': company_data.get('mktCap', 0)
                        })
                    else:
                        validation_result['companies_not_found'].append(symbol)
                        
                    # Get recent news for the company
                    news_data = await self.fmp_service.get_company_news(symbol)
                    if news_data:
                        # Check for fraud/regulatory news
                        fraud_news = [
                            news for news in news_data 
                            if any(keyword in news.get('title', '').lower() 
                                  for keyword in ['fraud', 'scam', 'sebi', 'penalty', 'investigation'])
                        ]
                        if fraud_news:
                            validation_result['market_data_flags'].append({
                                'symbol': symbol,
                                'flag_type': 'regulatory_news',
                                'news_count': len(fraud_news),
                                'recent_news': fraud_news[:3]  # Latest 3 news items
                            })
                            
                except Exception as e:
                    print(f"Error validating company {symbol}: {e}")
                    validation_result['companies_not_found'].append(symbol)
            
            # Calculate confidence based on verification results
            total_entities = len(entities.get('stock_symbols', []))
            if total_entities > 0:
                verified_count = len(validation_result['companies_verified'])
                validation_result['confidence'] = verified_count / total_entities
            
            return validation_result
            
        except Exception as e:
            return {
                'source': 'fmp_financial_data',
                'error': str(e),
                'confidence': 0.0
            }
    
    async def _validate_news_correlation(self, entities: Dict) -> Dict:
        """Validate document claims against recent news"""
        try:
            validation_result = {
                'source': 'economic_times_news',
                'relevant_articles': [],
                'contradictory_news': [],
                'supporting_news': [],
                'confidence': 0.5
            }
            
            # Get recent financial news
            recent_news = await self.news_service.scrape_latest_news(['markets', 'policy'])
            
            if recent_news:
                # Analyze news relevance to document entities
                for article in recent_news[:20]:  # Check latest 20 articles
                    article_text = f"{article.get('title', '')} {article.get('content', '')}".lower()
                    
                    # Check for company mentions
                    mentioned_companies = []
                    for company in entities.get('companies', []):
                        if company.lower() in article_text:
                            mentioned_companies.append(company)
                    
                    # Check for stock symbol mentions
                    mentioned_symbols = []
                    for symbol in entities.get('stock_symbols', []):
                        if symbol.lower() in article_text:
                            mentioned_symbols.append(symbol)
                    
                    # Check for regulatory keyword mentions
                    mentioned_regulatory = []
                    for claim in entities.get('regulatory_claims', []):
                        if claim in article_text:
                            mentioned_regulatory.append(claim)
                    
                    if mentioned_companies or mentioned_symbols or mentioned_regulatory:
                        article_relevance = {
                            'title': article.get('title', ''),
                            'url': article.get('url', ''),
                            'published_date': article.get('published_at', ''),
                            'mentioned_companies': mentioned_companies,
                            'mentioned_symbols': mentioned_symbols,
                            'mentioned_regulatory': mentioned_regulatory,
                            'sentiment': self._analyze_article_sentiment(article_text)
                        }
                        validation_result['relevant_articles'].append(article_relevance)
                        
                        # Categorize as supporting or contradictory
                        if any(keyword in article_text for keyword in ['fraud', 'scam', 'penalty', 'violation']):
                            validation_result['contradictory_news'].append(article_relevance)
                        elif any(keyword in article_text for keyword in ['approved', 'compliance', 'legitimate']):
                            validation_result['supporting_news'].append(article_relevance)
            
            # Calculate confidence based on news correlation
            total_relevant = len(validation_result['relevant_articles'])
            if total_relevant > 0:
                supporting_ratio = len(validation_result['supporting_news']) / total_relevant
                contradictory_ratio = len(validation_result['contradictory_news']) / total_relevant
                
                if contradictory_ratio > 0.5:
                    validation_result['confidence'] = 0.2  # High contradiction
                elif supporting_ratio > 0.5:
                    validation_result['confidence'] = 0.8  # High support
                else:
                    validation_result['confidence'] = 0.5  # Neutral
            
            return validation_result
            
        except Exception as e:
            return {
                'source': 'economic_times_news',
                'error': str(e),
                'confidence': 0.0
            }
    
    async def _validate_trend_analysis(self, entities: Dict) -> Dict:
        """Validate using Google Trends data"""
        try:
            validation_result = {
                'source': 'google_trends',
                'trend_spikes': [],
                'fraud_correlations': [],
                'regional_patterns': [],
                'confidence': 0.5
            }
            
            # Analyze trends for companies and keywords
            search_terms = []
            search_terms.extend(entities.get('companies', []))
            search_terms.extend(entities.get('stock_symbols', []))
            search_terms.extend([f"{kw} fraud" for kw in entities.get('keywords', [])])
            
            if search_terms:
                # Get trend data for relevant terms
                trend_data = await self.trends_service.fetch_fraud_trends(['IN'], '7d')
                
                for trend in trend_data:
                    keyword = trend.get('keyword', '')
                    
                    # Check if trend keyword relates to document entities
                    if any(term.lower() in keyword.lower() for term in search_terms):
                        trend_info = {
                            'keyword': keyword,
                            'search_volume': trend.get('search_volume', 0),
                            'trend_direction': trend.get('trend_direction', 'stable'),
                            'region': trend.get('region', 'IN')
                        }
                        
                        validation_result['trend_spikes'].append(trend_info)
                        
                        # Check for fraud-related spikes
                        if 'fraud' in keyword.lower() or 'scam' in keyword.lower():
                            validation_result['fraud_correlations'].append(trend_info)
            
            # Calculate confidence based on trend analysis
            if validation_result['fraud_correlations']:
                validation_result['confidence'] = 0.3  # Fraud trends reduce confidence
            elif validation_result['trend_spikes']:
                validation_result['confidence'] = 0.7  # Normal trends increase confidence
            
            return validation_result
            
        except Exception as e:
            return {
                'source': 'google_trends',
                'error': str(e),
                'confidence': 0.0
            }
    
    async def _enhanced_ai_analysis(self, text: str, filename: str, entities: Dict) -> Dict:
        """Enhanced AI analysis with entity context"""
        try:
            # Create enhanced prompt with entity context
            prompt = f"""
Analyze this document for authenticity with the following extracted context:

Document: {filename}
Companies mentioned: {entities.get('companies', [])}
Stock symbols: {entities.get('stock_symbols', [])}
Regulatory claims: {entities.get('regulatory_claims', [])}
Document type: {entities.get('document_type', 'unknown')}
Financial figures: {entities.get('financial_figures', [])}

Perform multi-dimensional analysis:
1. Content authenticity and consistency
2. Regulatory language accuracy
3. Financial data plausibility
4. Cross-reference entity relationships
5. Document structure and format

Provide detailed JSON response:
{{
    "authenticity_score": 0-100,
    "confidence": 0.0-1.0,
    "entity_consistency": {{
        "companies_legitimate": true/false,
        "financial_figures_realistic": true/false,
        "regulatory_language_accurate": true/false
    }},
    "red_flags": ["flag1", "flag2"],
    "supporting_evidence": ["evidence1", "evidence2"],
    "cross_reference_issues": ["issue1", "issue2"],
    "recommendations": ["rec1", "rec2"]
}}

Document text (first 3000 characters):
{text[:3000]}
"""
            
            if self.gemini_service.use_mock:
                return await self._mock_enhanced_ai_analysis(entities, text)
            
            # Call Gemini API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.gemini_service.base_url}/models/gemini-2.0-flash-exp:generateContent",
                    headers={"Content-Type": "application/json"},
                    params={"key": self.gemini_service.api_key},
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "temperature": 0.1,
                            "maxOutputTokens": 1500,
                        }
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise Exception(f"Gemini API error: {response.status_code}")
                
                result = response.json()
                content = result["candidates"][0]["content"]["parts"][0]["text"]
                
                # Parse JSON response
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    ai_result = json.loads(json_match.group())
                    ai_result['source'] = 'gemini_enhanced_ai'
                    return ai_result
                else:
                    raise Exception("No valid JSON found in response")
                    
        except Exception as e:
            print(f"Enhanced AI analysis failed: {e}")
            return await self._mock_enhanced_ai_analysis(entities, text)
    
    async def _mock_enhanced_ai_analysis(self, entities: Dict, text: str) -> Dict:
        """Mock enhanced AI analysis"""
        await asyncio.sleep(0.5)  # Simulate API call
        
        # Analyze based on entities and content
        score = 70
        confidence = 0.7
        red_flags = []
        supporting_evidence = []
        
        # Check entity consistency
        if not entities.get('companies') and not entities.get('stock_symbols'):
            red_flags.append("No verifiable company entities found")
            score -= 15
        
        if entities.get('document_type') == 'sebi_document':
            if entities.get('regulatory_claims'):
                supporting_evidence.append("Contains appropriate SEBI regulatory language")
                score += 10
            else:
                red_flags.append("Claims to be SEBI document but lacks regulatory terminology")
                score -= 20
        
        if len(text) < 500:
            red_flags.append("Document content is unusually short")
            score -= 15
        
        return {
            'source': 'gemini_enhanced_ai',
            'authenticity_score': max(0, min(100, score)),
            'confidence': confidence,
            'entity_consistency': {
                'companies_legitimate': len(entities.get('companies', [])) > 0,
                'financial_figures_realistic': len(entities.get('financial_figures', [])) > 0,
                'regulatory_language_accurate': len(entities.get('regulatory_claims', [])) > 0
            },
            'red_flags': red_flags,
            'supporting_evidence': supporting_evidence,
            'cross_reference_issues': [],
            'recommendations': ["Verify with official sources", "Cross-check company information"]
        }
    
    def _analyze_article_sentiment(self, article_text: str) -> str:
        """Simple sentiment analysis for news articles"""
        positive_words = ['approved', 'success', 'growth', 'profit', 'compliance', 'legitimate']
        negative_words = ['fraud', 'scam', 'penalty', 'violation', 'investigation', 'suspended']
        
        positive_count = sum(1 for word in positive_words if word in article_text)
        negative_count = sum(1 for word in negative_words if word in article_text)
        
        if negative_count > positive_count:
            return 'negative'
        elif positive_count > negative_count:
            return 'positive'
        else:
            return 'neutral'
    
    async def _process_validation_results(
        self, 
        result: DocumentValidationResult, 
        validation_results: List, 
        entities: Dict
    ):
        """Process and integrate validation results from all sources"""
        
        for i, validation_result in enumerate(validation_results):
            if isinstance(validation_result, Exception):
                result.cross_source_flags.append(f"Validation source {i} failed: {str(validation_result)}")
                continue
            
            source = validation_result.get('source', f'unknown_source_{i}')
            result.sources_checked[source] = True
            
            # Process FMP financial data results
            if source == 'fmp_financial_data':
                result.company_verification = validation_result
                result.financial_data_consistency = {
                    'verified_companies': len(validation_result.get('companies_verified', [])),
                    'unverified_companies': len(validation_result.get('companies_not_found', [])),
                    'market_flags': len(validation_result.get('market_data_flags', []))
                }
                
                if validation_result.get('market_data_flags'):
                    result.cross_source_flags.append("Companies have recent regulatory news/flags")
                if validation_result.get('companies_verified'):
                    result.cross_source_confirmations.append("Companies verified in financial databases")
            
            # Process news correlation results
            elif source == 'economic_times_news':
                result.news_correlation = validation_result
                
                if validation_result.get('contradictory_news'):
                    result.cross_source_flags.append("Recent news contradicts document claims")
                if validation_result.get('supporting_news'):
                    result.cross_source_confirmations.append("Recent news supports document authenticity")
            
            # Process trend analysis results
            elif source == 'google_trends':
                result.trend_analysis = validation_result
                
                if validation_result.get('fraud_correlations'):
                    result.cross_source_flags.append("Fraud-related search trends detected for entities")
                if validation_result.get('trend_spikes'):
                    result.cross_source_confirmations.append("Normal search trends for mentioned entities")
            
            # Process enhanced AI analysis
            elif source == 'gemini_enhanced_ai':
                result.ai_content_analysis = validation_result
                
                if validation_result.get('red_flags'):
                    result.cross_source_flags.extend(validation_result['red_flags'])
                if validation_result.get('supporting_evidence'):
                    result.cross_source_confirmations.extend(validation_result['supporting_evidence'])
    
    async def _calculate_enhanced_score(
        self, 
        basic_score: int, 
        result: DocumentValidationResult, 
        basic_anomalies: List[Dict]
    ) -> int:
        """Calculate enhanced authenticity score using multi-source validation"""
        
        score = basic_score
        
        # Adjust based on company verification
        if result.company_verification:
            confidence = result.company_verification.get('confidence', 0.5)
            if confidence > 0.7:
                score += 10  # High company verification confidence
            elif confidence < 0.3:
                score -= 15  # Low company verification confidence
        
        # Adjust based on news correlation
        if result.news_correlation:
            contradictory_count = len(result.news_correlation.get('contradictory_news', []))
            supporting_count = len(result.news_correlation.get('supporting_news', []))
            
            if contradictory_count > supporting_count:
                score -= 20  # More contradictory news
            elif supporting_count > contradictory_count:
                score += 10  # More supporting news
        
        # Adjust based on trend analysis
        if result.trend_analysis:
            fraud_correlations = len(result.trend_analysis.get('fraud_correlations', []))
            if fraud_correlations > 0:
                score -= 15  # Fraud trends detected
        
        # Adjust based on enhanced AI analysis
        if result.ai_content_analysis:
            ai_score = result.ai_content_analysis.get('authenticity_score', 50)
            ai_confidence = result.ai_content_analysis.get('confidence', 0.5)
            
            # Weight AI score by confidence
            weighted_ai_adjustment = int((ai_score - 50) * ai_confidence * 0.3)
            score += weighted_ai_adjustment
        
        # Cross-source validation bonus/penalty
        confirmations = len(result.cross_source_confirmations)
        flags = len(result.cross_source_flags)
        
        if confirmations > flags:
            score += min(15, confirmations * 3)  # Bonus for confirmations
        elif flags > confirmations:
            score -= min(25, flags * 5)  # Penalty for flags
        
        # Calculate validation confidence
        sources_with_results = sum(1 for checked in result.sources_checked.values() if checked)
        total_sources = len(result.validation_sources)
        
        if total_sources > 0:
            result.validation_confidence = sources_with_results / total_sources
        
        return max(0, min(100, score))
    
    async def _generate_recommendations(
        self, 
        result: DocumentValidationResult, 
        entities: Dict
    ) -> List[str]:
        """Generate actionable recommendations based on validation results"""
        
        recommendations = []
        
        # Basic recommendations
        if result.overall_authenticity_score < 40:
            recommendations.extend([
                "⚠️ HIGH RISK: Document appears to be fake or heavily manipulated",
                "Do not trust this document for any financial decisions",
                "Report this document to relevant authorities if received as official communication"
            ])
        elif result.overall_authenticity_score < 60:
            recommendations.extend([
                "⚠️ MEDIUM RISK: Document authenticity is questionable",
                "Verify document independently through official channels",
                "Exercise extreme caution before acting on this document"
            ])
        else:
            recommendations.append("✅ Document appears authentic, but independent verification is still recommended")
        
        # Source-specific recommendations
        if result.company_verification:
            unverified = len(result.company_verification.get('companies_not_found', []))
            if unverified > 0:
                recommendations.append(f"⚠️ {unverified} companies mentioned could not be verified in financial databases")
        
        if result.news_correlation:
            contradictory = len(result.news_correlation.get('contradictory_news', []))
            if contradictory > 0:
                recommendations.append(f"⚠️ Found {contradictory} recent news articles that contradict document claims")
        
        if result.trend_analysis:
            fraud_trends = len(result.trend_analysis.get('fraud_correlations', []))
            if fraud_trends > 0:
                recommendations.append(f"⚠️ Detected {fraud_trends} fraud-related search trends for mentioned entities")
        
        # Entity-specific recommendations
        if entities.get('document_type') == 'sebi_document':
            recommendations.append("📋 For SEBI documents, verify directly at sebi.gov.in")
        
        if entities.get('stock_symbols'):
            recommendations.append("📈 Verify stock information on official exchanges (NSE/BSE)")
        
        # Confidence-based recommendations
        if result.validation_confidence < 0.5:
            recommendations.append("⚠️ Limited validation sources available - seek additional verification")
        
        return recommendations

# Global service instance
enhanced_document_validator = EnhancedDocumentValidator()