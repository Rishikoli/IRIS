#!/usr/bin/env python3
"""
IRIS RegTech Platform - Sample Data Generation Script
Generates comprehensive demo data for all platform features
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta, date
import random
import json
import hashlib
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import (
    Base, Tip, Assessment, PDFCheck, HeatmapBucket, FMPMarketData,
    GoogleTrendsData, EconomicTimesArticle, DataIndicator, CrossSourceCorrelation,
    Forecast, FraudChain, FraudChainNode, FraudChainEdge, Review
)

# Create all tables
Base.metadata.create_all(bind=engine)

class SampleDataGenerator:
    def __init__(self):
        self.db = SessionLocal()
        self.sectors = [
            "Banking", "Technology", "Pharmaceuticals", "Real Estate", 
            "Telecommunications", "Energy", "Automotive", "FMCG", 
            "Metals & Mining", "Textiles", "Infrastructure", "Healthcare"
        ]
        
        self.regions = [
            "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", 
            "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
            "Kochi", "Chandigarh", "Bhopal", "Indore", "Nagpur"
        ]
        
        self.stock_symbols = [
            "RELIANCE", "TCS", "HDFCBANK", "INFY", "HINDUNILVR", "ICICIBANK",
            "KOTAKBANK", "BHARTIARTL", "ITC", "SBIN", "BAJFINANCE", "ASIANPAINT",
            "MARUTI", "AXISBANK", "LT", "SUNPHARMA", "TITAN", "ULTRACEMCO",
            "NESTLEIND", "WIPRO", "TECHM", "POWERGRID", "NTPC", "ONGC"
        ]
        
        self.fraud_keywords = [
            "stock tip scam", "investment fraud", "ponzi scheme", "fake advisor",
            "guaranteed returns", "insider trading", "pump and dump", "chit fund fraud"
        ]

    def generate_realistic_tips(self, count=50):
        """Generate realistic investment tips with varying risk levels"""
        
        # High-risk tip templates
        high_risk_tips = [
            "🚀 URGENT! Buy {stock} NOW! Guaranteed 500% returns in 2 weeks! Inside information from company director. Limited time offer! WhatsApp +91-9876543210 for more details. Don't miss this golden opportunity! 💰💰💰",
            "BREAKING: {stock} will announce merger tomorrow! Buy immediately before price rockets! My uncle works in the company. 1000% guaranteed profit! Send ₹50,000 to get premium tips. Trust me, I made ₹10 lakhs last month! 🔥",
            "SECRET TIP: Government will announce new policy favoring {stock} sector. Buy {stock} at current price ₹{price}. Will reach ₹{target_price} by next week GUARANTEED! No risk, only profit! Contact advisor Rajesh Sharma (SEBI Reg: FAKE123) 📈",
            "INSIDER NEWS: {stock} getting huge foreign investment! Current price ₹{price}, will become ₹{target_price} in 3 days! I have connections in the company. Send money now, thank me later! 100% sure shot! 💎",
            "URGENT ALERT: {stock} will be in news tomorrow! Buy now at ₹{price}, sell at ₹{target_price}! My track record: 50 successful tips, 0 losses! Join my premium group for ₹5000. Limited seats only! 🎯"
        ]
        
        # Medium-risk tip templates
        medium_risk_tips = [
            "Good opportunity in {stock}. Technical analysis shows strong breakout pattern. Target ₹{target_price} in 2-3 months. Stop loss at ₹{stop_loss}. Do your own research before investing. Not SEBI registered advisor.",
            "{stock} showing good fundamentals. Recent quarterly results were positive. May reach ₹{target_price} in 6 months. This is just my opinion, please consult your financial advisor before investing.",
            "Bullish on {stock} for long term. Good management, strong business model. Current price ₹{price} looks attractive. Expected target ₹{target_price} in 1 year. Invest only surplus money.",
            "Technical view on {stock}: Breaking resistance at ₹{price}. Next target ₹{target_price}. Good volume support. Suitable for swing trading. Risk-reward ratio 1:3. Trade with proper stop loss.",
            "{stock} sector looking promising due to government policies. {stock} is a good player in this space. May give 20-30% returns in 6-12 months. Invest gradually through SIP mode."
        ]
        
        # Low-risk tip templates  
        low_risk_tips = [
            "Long term investment idea: {stock} is a fundamentally strong company with consistent growth. Current valuation seems reasonable. Suitable for 3-5 year investment horizon. Please do thorough research.",
            "Sharing my portfolio holding: {stock} - bought at ₹{price}, currently at ₹{current_price}. Good dividend yield and stable business. This is not a recommendation, just sharing my experience.",
            "Educational post: {stock} business model analysis. Revenue growth has been steady at 15% CAGR. Debt levels are manageable. Good for learning about {sector} sector. Always invest based on your risk appetite.",
            "Market observation: {stock} has been consolidating around ₹{price} levels. Good support at ₹{support}. For educational purposes only. Please consult certified financial planner for investment advice.",
            "Fundamental analysis of {stock}: Strong balance sheet, good cash flows, experienced management. Trading at reasonable P/E ratio. Suitable for conservative investors. This is my personal view, not advice."
        ]
        
        tips_data = []
        
        for i in range(count):
            # Determine risk level distribution (30% high, 40% medium, 30% low)
            risk_rand = random.random()
            if risk_rand < 0.3:
                risk_level = "High"
                template = random.choice(high_risk_tips)
                score = random.randint(75, 95)
                reasons = [
                    "Unrealistic return promises (500%+ guaranteed)",
                    "Urgency pressure tactics",
                    "Claims of insider information",
                    "Requests for immediate money transfer",
                    "Fake SEBI registration claims"
                ]
            elif risk_rand < 0.7:
                risk_level = "Medium" 
                template = random.choice(medium_risk_tips)
                score = random.randint(40, 74)
                reasons = [
                    "Lacks proper disclaimers",
                    "Provides specific price targets without analysis",
                    "No mention of risks involved",
                    "Unverified advisor credentials"
                ]
            else:
                risk_level = "Low"
                template = random.choice(low_risk_tips)
                score = random.randint(10, 39)
                reasons = [
                    "Educational content with proper disclaimers",
                    "Encourages independent research",
                    "Mentions risk factors appropriately",
                    "No unrealistic promises"
                ]
            
            # Fill template with random data
            stock = random.choice(self.stock_symbols)
            price = random.randint(100, 2000)
            target_price = price + random.randint(50, 500) if risk_level == "High" else price + random.randint(10, 100)
            stop_loss = price - random.randint(10, 50)
            current_price = price + random.randint(-20, 20)
            support = price - random.randint(20, 50)
            sector = random.choice(self.sectors)
            
            message = template.format(
                stock=stock,
                price=price,
                target_price=target_price,
                stop_loss=stop_loss,
                current_price=current_price,
                support=support,
                sector=sector
            )
            
            # Create tip
            tip = Tip(
                message=message,
                source=random.choice(["telegram", "whatsapp", "twitter", "manual", "sms"]),
                submitter_id=f"user_{random.randint(1000, 9999)}",
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            
            # Create corresponding assessment
            assessment = Assessment(
                tip_id=tip.id,
                level=risk_level,
                score=score,
                reasons=reasons[:random.randint(2, len(reasons))],
                stock_symbols=[stock] if stock in message else [],
                advisor_info={
                    "mentioned": "Rajesh Sharma" in message,
                    "sebi_registered": False,
                    "registration_id": "FAKE123" if "Rajesh Sharma" in message else None
                } if "advisor" in message.lower() or "Rajesh Sharma" in message else None,
                confidence=random.randint(80, 95),
                gemini_raw={
                    "analysis": f"Risk assessment for {stock} tip",
                    "confidence": random.randint(80, 95),
                    "model": "gemini-2.0-flash"
                }
            )
            
            tips_data.append((tip, assessment))
        
        return tips_data

    def generate_pdf_checks(self, count=25):
        """Generate sample PDF document checks"""
        
        pdf_scenarios = [
            {
                "filename": "SEBI_Circular_Fake_Investment_Schemes.pdf",
                "is_fake": True,
                "score": 15,
                "anomalies": [
                    "Font inconsistency detected",
                    "Missing digital signature",
                    "Suspicious metadata timestamps",
                    "Logo quality issues",
                    "Grammatical errors in official language"
                ],
                "ocr_text": "SEBI CIRCULAR - BEWARE OF FAKE INVESTMENT SCHEMES\n\nThis is to inform all investors that the following schemes are not authorized by SEBI:\n1. Quick Rich Investment Plan - 500% returns guaranteed\n2. Golden Future Scheme - Double your money in 30 days\n\nInvestors are advised to verify all investment schemes before investing.\n\nSEBI Registration: XYZ123 (FAKE)\nDate: 2024-01-15"
            },
            {
                "filename": "RBI_Policy_Document_Authentic.pdf", 
                "is_fake": False,
                "score": 92,
                "anomalies": [],
                "ocr_text": "RESERVE BANK OF INDIA\nMONETARY POLICY COMMITTEE RESOLUTION\n\nThe Monetary Policy Committee (MPC) at its meeting held during December 6-8, 2023 decided to:\n\n• Keep the policy repo rate unchanged at 6.50%\n• Continue with the stance of withdrawal of accommodation\n\nThe MPC noted that inflation has moderated but remains above the target.\n\nGovernor: Shaktikanta Das\nDate: December 8, 2023"
            },
            {
                "filename": "Fake_Stock_Recommendation_Report.pdf",
                "is_fake": True, 
                "score": 25,
                "anomalies": [
                    "Unverified analyst credentials",
                    "Unrealistic price targets",
                    "Missing risk disclaimers",
                    "Poor document formatting"
                ],
                "ocr_text": "PREMIUM STOCK RESEARCH REPORT\n\nBUY RECOMMENDATION: RELIANCE\nCurrent Price: ₹2,500\nTarget Price: ₹5,000 (100% upside)\nTime Frame: 3 months\n\nGuaranteed returns based on insider information. Our success rate is 100%.\n\nAnalyst: John Doe (Fake Credentials)\nCompany: XYZ Research (Unregistered)"
            }
        ]
        
        pdf_data = []
        
        for i in range(count):
            if i < len(pdf_scenarios):
                scenario = pdf_scenarios[i]
            else:
                # Generate random scenarios
                is_fake = random.choice([True, False])
                scenario = {
                    "filename": f"Document_{i}_{random.choice(['SEBI', 'RBI', 'Company', 'Research'])}.pdf",
                    "is_fake": is_fake,
                    "score": random.randint(10, 40) if is_fake else random.randint(70, 95),
                    "anomalies": random.sample([
                        "Font inconsistency", "Missing signature", "Metadata issues",
                        "Logo problems", "Grammar errors", "Formatting issues"
                    ], random.randint(0, 3)) if is_fake else [],
                    "ocr_text": f"Sample document content for {random.choice(self.stock_symbols)} analysis..."
                }
            
            file_content = scenario["ocr_text"].encode()
            file_hash = hashlib.sha256(file_content).hexdigest()
            
            pdf_check = PDFCheck(
                file_hash=file_hash,
                filename=scenario["filename"],
                file_size=len(file_content),
                ocr_text=scenario["ocr_text"],
                anomalies=scenario["anomalies"],
                score=scenario["score"],
                is_likely_fake=scenario["is_fake"],
                processing_time_ms=random.randint(500, 3000),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 15))
            )
            
            pdf_data.append(pdf_check)
        
        return pdf_data

    def generate_heatmap_data(self):
        """Generate heatmap bucket data for sectors and regions"""
        
        heatmap_data = []
        
        # Generate data for last 30 days
        for days_back in range(30):
            date_point = date.today() - timedelta(days=days_back)
            
            # Sector data
            for sector in self.sectors:
                total = random.randint(5, 50)
                high_risk = random.randint(0, int(total * 0.3))
                medium_risk = random.randint(0, int((total - high_risk) * 0.6))
                low_risk = total - high_risk - medium_risk
                
                bucket = HeatmapBucket(
                    dimension="sector",
                    key=sector,
                    from_date=date_point,
                    to_date=date_point,
                    total_count=total,
                    high_risk_count=high_risk,
                    medium_risk_count=medium_risk,
                    low_risk_count=low_risk,
                    last_updated=datetime.utcnow()
                )
                heatmap_data.append(bucket)
            
            # Region data
            for region in self.regions:
                total = random.randint(3, 30)
                high_risk = random.randint(0, int(total * 0.25))
                medium_risk = random.randint(0, int((total - high_risk) * 0.5))
                low_risk = total - high_risk - medium_risk
                
                bucket = HeatmapBucket(
                    dimension="region",
                    key=region,
                    from_date=date_point,
                    to_date=date_point,
                    total_count=total,
                    high_risk_count=high_risk,
                    medium_risk_count=medium_risk,
                    low_risk_count=low_risk,
                    last_updated=datetime.utcnow()
                )
                heatmap_data.append(bucket)
        
        return heatmap_data

    def generate_multi_source_data(self):
        """Generate FMP, Google Trends, and Economic Times data"""
        
        # FMP Market Data
        fmp_data = []
        for symbol in self.stock_symbols[:15]:  # Generate for subset of stocks
            for days_back in range(7):  # Last 7 days
                timestamp = datetime.utcnow() - timedelta(days=days_back)
                
                market_data = FMPMarketData(
                    symbol=symbol,
                    price=random.randint(50000, 300000),  # Price in cents
                    change_percent=random.randint(-500, 500),  # Change in basis points
                    volume=random.randint(100000, 10000000),
                    market_cap=random.randint(1000000000, 100000000000),
                    unusual_activity=random.choice([True, False]),
                    fraud_relevance_score=random.randint(0, 100),
                    data_timestamp=timestamp
                )
                fmp_data.append(market_data)
        
        # Google Trends Data
        trends_data = []
        for keyword in self.fraud_keywords:
            for region in self.regions[:10]:  # Subset of regions
                for days_back in range(7):
                    timestamp = datetime.utcnow() - timedelta(days=days_back)
                    
                    trend_data = GoogleTrendsData(
                        keyword=keyword,
                        region=region,
                        search_volume=random.randint(10, 100),
                        trend_direction=random.choice(["rising", "falling", "stable"]),
                        spike_detected=random.choice([True, False]),
                        fraud_correlation_score=random.randint(60, 95),
                        timeframe="1d",
                        data_timestamp=timestamp
                    )
                    trends_data.append(trend_data)
        
        # Economic Times Articles
        et_articles = []
        article_templates = [
            {
                "title": "SEBI warns investors against unregistered investment advisors",
                "content": "The Securities and Exchange Board of India (SEBI) has issued a warning to investors about the rising number of unregistered investment advisors operating through social media platforms...",
                "category": "policy",
                "regulatory_mentions": ["SEBI"],
                "fraud_relevance_score": 95
            },
            {
                "title": "Stock market volatility increases amid global uncertainty",
                "content": "Indian stock markets witnessed increased volatility as global economic uncertainty continues to impact investor sentiment...",
                "category": "markets", 
                "regulatory_mentions": [],
                "fraud_relevance_score": 30
            },
            {
                "title": "RBI issues guidelines on digital lending platforms",
                "content": "The Reserve Bank of India has issued comprehensive guidelines for digital lending platforms to protect borrowers from predatory practices...",
                "category": "banking",
                "regulatory_mentions": ["RBI"],
                "fraud_relevance_score": 75
            }
        ]
        
        for i, template in enumerate(article_templates):
            for days_back in range(5):  # Multiple articles over 5 days
                timestamp = datetime.utcnow() - timedelta(days=days_back)
                
                article = EconomicTimesArticle(
                    article_url=f"https://economictimes.indiatimes.com/article-{i}-{days_back}",
                    title=template["title"],
                    content=template["content"],
                    category=template["category"],
                    author=f"ET Reporter {i}",
                    published_at=timestamp,
                    fraud_relevance_score=template["fraud_relevance_score"],
                    sentiment=random.choice(["positive", "negative", "neutral"]),
                    regulatory_mentions=template["regulatory_mentions"],
                    stock_mentions=random.sample(self.stock_symbols, random.randint(0, 3))
                )
                et_articles.append(article)
        
        return fmp_data, trends_data, et_articles

    def generate_fraud_chains(self):
        """Generate sample fraud chain data showing different fraud patterns"""
        
        chains_data = []
        
        # Chain 1: Pump and Dump Scheme
        chain1 = FraudChain(
            name="Pump and Dump - TECHM Stock",
            description="Coordinated scheme to artificially inflate TECHM stock price through fake tips and then dump shares",
            status="investigating"
        )
        
        # Chain 2: Fake SEBI Document Scheme  
        chain2 = FraudChain(
            name="Fake SEBI Circular Distribution",
            description="Distribution of fake SEBI documents to legitimize fraudulent investment schemes",
            status="active"
        )
        
        # Chain 3: Unregistered Advisor Network
        chain3 = FraudChain(
            name="Unregistered Advisor Network",
            description="Network of fake advisors providing guaranteed return schemes across multiple platforms",
            status="closed"
        )
        
        chains_data.extend([chain1, chain2, chain3])
        
        return chains_data

    def generate_forecasts(self):
        """Generate AI forecasting data"""
        
        forecasts_data = []
        
        # Generate forecasts for next 3 months
        for month_offset in range(1, 4):
            forecast_date = date.today() + timedelta(days=30 * month_offset)
            period = forecast_date.strftime("%Y-%m")
            
            # Sector forecasts
            for sector in self.sectors:
                risk_score = random.randint(20, 80)
                confidence_range = random.randint(5, 15)
                
                forecast = Forecast(
                    period=period,
                    dimension="sector",
                    key=sector,
                    risk_score=risk_score,
                    confidence_min=max(0, risk_score - confidence_range),
                    confidence_max=min(100, risk_score + confidence_range),
                    rationale=f"Based on historical patterns and current market trends, {sector} sector shows moderate risk indicators. Key factors include market volatility and regulatory changes.",
                    contributing_factors=[
                        {"factor": "Historical fraud patterns", "weight": 0.3, "explanation": "Past fraud cases in this sector"},
                        {"factor": "Market volatility", "weight": 0.25, "explanation": "Current market conditions"},
                        {"factor": "Regulatory environment", "weight": 0.2, "explanation": "Recent regulatory changes"},
                        {"factor": "Social media activity", "weight": 0.25, "explanation": "Increased suspicious social media activity"}
                    ],
                    features={"trend": "stable", "volatility": "medium", "volume": "normal"}
                )
                forecasts_data.append(forecast)
            
            # Region forecasts
            for region in self.regions:
                risk_score = random.randint(15, 70)
                confidence_range = random.randint(8, 20)
                
                forecast = Forecast(
                    period=period,
                    dimension="region", 
                    key=region,
                    risk_score=risk_score,
                    confidence_min=max(0, risk_score - confidence_range),
                    confidence_max=min(100, risk_score + confidence_range),
                    rationale=f"Regional analysis for {region} indicates moderate fraud risk based on demographic factors and historical data patterns.",
                    contributing_factors=[
                        {"factor": "Population density", "weight": 0.2, "explanation": "Higher density areas show more fraud activity"},
                        {"factor": "Digital literacy", "weight": 0.3, "explanation": "Digital literacy levels affect susceptibility"},
                        {"factor": "Economic indicators", "weight": 0.25, "explanation": "Local economic conditions"},
                        {"factor": "Previous incidents", "weight": 0.25, "explanation": "Historical fraud incidents in the region"}
                    ],
                    features={"population": "high", "literacy": "medium", "economic_growth": "stable"}
                )
                forecasts_data.append(forecast)
        
        return forecasts_data

    def generate_reviews(self, tips_data, pdf_data):
        """Generate human review data for low-confidence AI decisions"""
        
        reviews_data = []
        
        # Review some tips (focus on medium confidence scores)
        for tip, assessment in tips_data[:10]:  # Review first 10 tips
            if assessment.confidence < 85:  # Low confidence cases
                review = Review(
                    case_id=assessment.id,
                    case_type="assessment",
                    reviewer_id=f"reviewer_{random.randint(1, 5)}",
                    ai_decision={
                        "level": assessment.level,
                        "score": assessment.score,
                        "confidence": assessment.confidence
                    },
                    human_decision={
                        "level": assessment.level,  # Could be different
                        "score": assessment.score + random.randint(-10, 10),
                        "notes": "Adjusted based on contextual analysis"
                    },
                    decision=random.choice(["approve", "override", "needs_more_info"]),
                    notes=f"Reviewed {assessment.level} risk assessment. AI confidence was {assessment.confidence}%. Human reviewer analysis confirms/adjusts the decision.",
                    ai_confidence=assessment.confidence,
                    priority=random.choice(["low", "medium", "high"]),
                    status="completed"
                )
                reviews_data.append(review)
        
        # Review some PDF checks
        for pdf in pdf_data[:5]:  # Review first 5 PDFs
            if pdf.score < 60:  # Uncertain authenticity scores
                review = Review(
                    case_id=pdf.id,
                    case_type="pdf_check",
                    reviewer_id=f"reviewer_{random.randint(1, 5)}",
                    ai_decision={
                        "score": pdf.score,
                        "is_likely_fake": pdf.is_likely_fake,
                        "anomalies": pdf.anomalies
                    },
                    human_decision={
                        "score": pdf.score + random.randint(-15, 15),
                        "is_likely_fake": pdf.is_likely_fake,
                        "additional_notes": "Manual verification completed"
                    },
                    decision=random.choice(["approve", "override"]),
                    notes=f"PDF authenticity review for {pdf.filename}. Score: {pdf.score}%. Human verification {'confirms' if random.choice([True, False]) else 'adjusts'} AI assessment.",
                    priority="medium",
                    status="completed"
                )
                reviews_data.append(review)
        
        return reviews_data

    def generate_all_data(self):
        """Generate all sample data and insert into database"""
        
        print("🚀 Starting IRIS RegTech sample data generation...")
        
        try:
            # Clear existing data
            print("🧹 Clearing existing data...")
            self.db.query(Review).delete()
            self.db.query(FraudChainEdge).delete()
            self.db.query(FraudChainNode).delete()
            self.db.query(FraudChain).delete()
            self.db.query(Forecast).delete()
            self.db.query(CrossSourceCorrelation).delete()
            self.db.query(DataIndicator).delete()
            self.db.query(EconomicTimesArticle).delete()
            self.db.query(GoogleTrendsData).delete()
            self.db.query(FMPMarketData).delete()
            self.db.query(HeatmapBucket).delete()
            self.db.query(PDFCheck).delete()
            self.db.query(Assessment).delete()
            self.db.query(Tip).delete()
            self.db.commit()
            
            # Generate tips and assessments
            print("📝 Generating tips and assessments...")
            tips_data = self.generate_realistic_tips(50)
            for tip, assessment in tips_data:
                self.db.add(tip)
                self.db.flush()  # Get tip.id
                assessment.tip_id = tip.id
                self.db.add(assessment)
            
            # Generate PDF checks
            print("📄 Generating PDF document checks...")
            pdf_data = self.generate_pdf_checks(25)
            for pdf in pdf_data:
                self.db.add(pdf)
            
            # Generate heatmap data
            print("🗺️ Generating heatmap data...")
            heatmap_data = self.generate_heatmap_data()
            for bucket in heatmap_data:
                self.db.add(bucket)
            
            # Generate multi-source data
            print("📊 Generating multi-source integration data...")
            fmp_data, trends_data, et_articles = self.generate_multi_source_data()
            
            for data in fmp_data:
                self.db.add(data)
            for data in trends_data:
                self.db.add(data)
            for article in et_articles:
                self.db.add(article)
            
            # Generate fraud chains
            print("🔗 Generating fraud chain data...")
            chains_data = self.generate_fraud_chains()
            for chain in chains_data:
                self.db.add(chain)
            
            # Generate forecasts
            print("🔮 Generating AI forecasting data...")
            forecasts_data = self.generate_forecasts()
            for forecast in forecasts_data:
                self.db.add(forecast)
            
            # Generate reviews
            print("👥 Generating human review data...")
            reviews_data = self.generate_reviews(tips_data, pdf_data)
            for review in reviews_data:
                self.db.add(review)
            
            # Commit all data
            self.db.commit()
            
            print("✅ Sample data generation completed successfully!")
            print(f"Generated:")
            print(f"  • {len(tips_data)} tips with assessments")
            print(f"  • {len(pdf_data)} PDF document checks")
            print(f"  • {len(heatmap_data)} heatmap data points")
            print(f"  • {len(fmp_data)} FMP market data entries")
            print(f"  • {len(trends_data)} Google Trends data points")
            print(f"  • {len(et_articles)} Economic Times articles")
            print(f"  • {len(chains_data)} fraud chains")
            print(f"  • {len(forecasts_data)} forecast entries")
            print(f"  • {len(reviews_data)} human reviews")
            
        except Exception as e:
            print(f"❌ Error generating sample data: {e}")
            self.db.rollback()
            raise
        finally:
            self.db.close()

if __name__ == "__main__":
    generator = SampleDataGenerator()
    generator.generate_all_data()