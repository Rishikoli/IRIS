import os
import re
import json
import asyncio
from typing import Dict, List, Optional, Tuple
import httpx
from pydantic import BaseModel

class RiskAssessmentResult(BaseModel):
    level: str  # Low, Medium, High
    score: int  # 0-100
    reasons: List[str]
    stock_symbols: List[str]
    advisor_mentioned: Optional[str] = None
    confidence: float = 0.0

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.use_mock = not self.api_key or self.api_key == "your_gemini_api_key_here"
        
    async def analyze_tip(self, message: str) -> RiskAssessmentResult:
        """Analyze investment tip for risk assessment"""
        if self.use_mock:
            return await self._mock_analysis(message)
        
        try:
            return await self._gemini_analysis(message)
        except Exception as e:
            print(f"Gemini API error: {e}, falling back to mock")
            return await self._mock_analysis(message)
    
    async def analyze_text(self, prompt: str) -> str:
        """Generic text analysis using Gemini API"""
        if self.use_mock:
            return await self._mock_text_analysis(prompt)
        
        try:
            return await self._gemini_text_analysis(prompt)
        except Exception as e:
            print(f"Gemini API error: {e}, falling back to mock")
            return await self._mock_text_analysis(prompt)
    
    async def _gemini_text_analysis(self, prompt: str) -> str:
        """Call Gemini API for generic text analysis"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/models/gemini-2.0-flash-exp:generateContent",
                headers={"Content-Type": "application/json"},
                params={"key": self.api_key},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 500,
                    }
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Gemini API error: {response.status_code}")
            
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"].strip()
    
    async def _mock_text_analysis(self, prompt: str) -> str:
        """Mock text analysis for development/fallback"""
        await asyncio.sleep(0.3)  # Simulate API delay
        
        prompt_lower = prompt.lower()
        
        # Simple keyword-based responses for different types of analysis
        if "score" in prompt_lower and ("0-100" in prompt or "100" in prompt):
            # Scoring request
            if any(word in prompt_lower for word in ["fraud", "scam", "risk", "suspicious"]):
                return "75"  # High fraud relevance
            elif any(word in prompt_lower for word in ["news", "article", "regulatory"]):
                return "60"  # Medium relevance
            else:
                return "35"  # Low relevance
        
        elif "sentiment" in prompt_lower:
            # Sentiment analysis request
            if any(word in prompt_lower for word in ["warning", "action", "penalty", "fraud"]):
                return "negative"
            elif any(word in prompt_lower for word in ["growth", "positive", "rally", "gain"]):
                return "positive"
            else:
                return "neutral"
        
        elif "correlation" in prompt_lower:
            # Correlation analysis
            return "This correlation suggests increased fraud activity patterns that require enhanced monitoring and potential regulatory intervention."
        
        else:
            # Generic analysis
            return "Analysis indicates moderate risk levels with several factors requiring attention and continued monitoring."

    async def _gemini_analysis(self, message: str) -> RiskAssessmentResult:
        """Call actual Gemini API for analysis"""
        prompt = self._build_analysis_prompt(message)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/models/gemini-2.0-flash-exp:generateContent",
                headers={"Content-Type": "application/json"},
                params={"key": self.api_key},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 1000,
                    }
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Gemini API error: {response.status_code}")
            
            result = response.json()
            content = result["candidates"][0]["content"]["parts"][0]["text"]
            
            return await self._parse_gemini_response(content, message)
    
    async def _mock_analysis(self, message: str) -> RiskAssessmentResult:
        """Mock analysis for development/fallback"""
        # Simulate API delay
        await asyncio.sleep(0.5)
        
        message_lower = message.lower()
        
        # Risk indicators
        high_risk_indicators = [
            "guaranteed", "100%", "sure shot", "risk-free", "double your money",
            "urgent", "limited time", "act now", "secret", "insider",
            "500%", "1000%", "returns", "profit", "quick money"
        ]
        
        medium_risk_indicators = [
            "tip", "buy now", "sell now", "target", "breakout",
            "recommendation", "advice", "opportunity", "growth"
        ]
        
        # Count risk indicators
        high_risk_count = sum(1 for indicator in high_risk_indicators if indicator in message_lower)
        medium_risk_count = sum(1 for indicator in medium_risk_indicators if indicator in message_lower)
        
        # Extract stock symbols (basic pattern matching)
        stock_symbols = self._extract_stock_symbols(message)
        
        # Check for advisor mentions
        advisor_mentioned = self._extract_advisor_mention(message)
        
        # Determine risk level and score
        if high_risk_count >= 2:
            level = "High"
            score = min(85 + high_risk_count * 5, 100)
            reasons = [
                "Contains multiple high-risk indicators",
                "Uses pressure tactics and urgency",
                "Makes unrealistic return promises"
            ]
        elif high_risk_count >= 1 or medium_risk_count >= 3:
            level = "Medium"
            score = 50 + high_risk_count * 15 + medium_risk_count * 5
            reasons = [
                "Contains some risk indicators",
                "Appears to be investment advice",
                "Requires caution and verification"
            ]
        else:
            level = "Low"
            score = max(10, 30 - len(message) // 20)
            reasons = [
                "No significant risk indicators detected",
                "Appears to be informational",
                "Standard investment discussion"
            ]
        
        # Add specific reasons based on content
        if stock_symbols:
            reasons.append(f"Mentions specific stocks: {', '.join(stock_symbols)}")
        
        if advisor_mentioned:
            reasons.append(f"References advisor: {advisor_mentioned}")
        
        if "whatsapp" in message_lower or "telegram" in message_lower:
            reasons.append("Shared via messaging platform")
            score = min(score + 10, 100)
        
        return RiskAssessmentResult(
            level=level,
            score=score,
            reasons=reasons,
            stock_symbols=stock_symbols,
            advisor_mentioned=advisor_mentioned,
            confidence=0.85  # Mock confidence
        )
    
    def _build_analysis_prompt(self, message: str) -> str:
        """Build prompt for Gemini API"""
        return f"""
Analyze this investment tip/message for fraud risk. Provide a JSON response with the following structure:

{{
    "level": "Low|Medium|High",
    "score": 0-100,
    "reasons": ["reason1", "reason2", ...],
    "stock_symbols": ["SYMBOL1", "SYMBOL2", ...],
    "advisor_mentioned": "advisor name or null",
    "confidence": 0.0-1.0
}}

Consider these risk factors:
- Unrealistic return promises (guaranteed profits, 500%+ returns)
- Urgency and pressure tactics ("act now", "limited time")
- Lack of proper disclaimers or risk warnings
- Mentions of insider information or secret tips
- Unregistered advisor claims
- Pump and dump indicators

Message to analyze:
"{message}"

Respond only with valid JSON.
"""
    
    async def _parse_gemini_response(self, content: str, original_message: str) -> RiskAssessmentResult:
        """Parse Gemini API response"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return RiskAssessmentResult(**data)
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
        
        # Fallback to mock if parsing fails
        return await self._mock_analysis(original_message)
    
    def _extract_stock_symbols(self, message: str) -> List[str]:
        """Extract potential stock symbols from message"""
        # Look for patterns like stock symbols (2-5 uppercase letters)
        symbols = re.findall(r'\b[A-Z]{2,5}\b', message)
        
        # Filter out common words that aren't stock symbols
        common_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'HAD', 'BUT', 'WORD', 'TIME', 'WILL', 'EACH', 'TELL', 'DOES', 'SET', 'THREE', 'WANT', 'AIR', 'WELL', 'ALSO', 'PLAY', 'SMALL', 'END', 'PUT', 'HOME', 'READ', 'HAND', 'PORT', 'LARGE', 'SPELL', 'ADD', 'EVEN', 'LAND', 'HERE', 'MUST', 'BIG', 'HIGH', 'SUCH', 'FOLLOW', 'ACT', 'WHY', 'ASK', 'MEN', 'CHANGE', 'WENT', 'LIGHT', 'KIND', 'OFF', 'NEED', 'HOUSE', 'PICTURE', 'TRY', 'US', 'AGAIN', 'ANIMAL', 'POINT', 'MOTHER', 'WORLD', 'NEAR', 'BUILD', 'SELF', 'EARTH', 'FATHER', 'HEAD', 'STAND', 'OWN', 'PAGE', 'SHOULD', 'COUNTRY', 'FOUND', 'ANSWER', 'SCHOOL', 'GROW', 'STUDY', 'STILL', 'LEARN', 'PLANT', 'COVER', 'FOOD', 'SUN', 'FOUR', 'BETWEEN', 'STATE', 'KEEP', 'EYE', 'NEVER', 'LAST', 'LET', 'THOUGHT', 'CITY', 'TREE', 'CROSS', 'FARM', 'HARD', 'START', 'MIGHT', 'STORY', 'SAW', 'FAR', 'SEA', 'DRAW', 'LEFT', 'LATE', 'RUN', 'DONT', 'WHILE', 'PRESS', 'CLOSE', 'NIGHT', 'REAL', 'LIFE', 'FEW', 'NORTH', 'OPEN', 'SEEM', 'TOGETHER', 'NEXT', 'WHITE', 'CHILDREN', 'BEGIN', 'GOT', 'WALK', 'EXAMPLE', 'EASE', 'PAPER', 'GROUP', 'ALWAYS', 'MUSIC', 'THOSE', 'BOTH', 'MARK', 'OFTEN', 'LETTER', 'UNTIL', 'MILE', 'RIVER', 'CAR', 'FEET', 'CARE', 'SECOND', 'BOOK', 'CARRY', 'TOOK', 'SCIENCE', 'EAT', 'ROOM', 'FRIEND', 'BEGAN', 'IDEA', 'FISH', 'MOUNTAIN', 'STOP', 'ONCE', 'BASE', 'HEAR', 'HORSE', 'CUT', 'SURE', 'WATCH', 'COLOR', 'FACE', 'WOOD', 'MAIN', 'ENOUGH', 'PLAIN', 'GIRL', 'USUAL', 'YOUNG', 'READY', 'ABOVE', 'EVER', 'RED', 'LIST', 'THOUGH', 'FEEL', 'TALK', 'BIRD', 'SOON', 'BODY', 'DOG', 'FAMILY', 'DIRECT', 'LEAVE', 'SONG', 'MEASURE', 'DOOR', 'PRODUCT', 'BLACK', 'SHORT', 'NUMERAL', 'CLASS', 'WIND', 'QUESTION', 'HAPPEN', 'COMPLETE', 'SHIP', 'AREA', 'HALF', 'ROCK', 'ORDER', 'FIRE', 'SOUTH', 'PROBLEM', 'PIECE', 'TOLD', 'KNEW', 'PASS', 'SINCE', 'TOP', 'WHOLE', 'KING', 'SPACE', 'HEARD', 'BEST', 'HOUR', 'BETTER', 'DURING', 'HUNDRED', 'FIVE', 'REMEMBER', 'STEP', 'EARLY', 'HOLD', 'WEST', 'GROUND', 'INTEREST', 'REACH', 'FAST', 'VERB', 'SING', 'LISTEN', 'SIX', 'TABLE', 'TRAVEL', 'LESS', 'MORNING', 'TEN', 'SIMPLE', 'SEVERAL', 'VOWEL', 'TOWARD', 'WAR', 'LAY', 'AGAINST', 'PATTERN', 'SLOW', 'CENTER', 'LOVE', 'PERSON', 'MONEY', 'SERVE', 'APPEAR', 'ROAD', 'MAP', 'RAIN', 'RULE', 'GOVERN', 'PULL', 'COLD', 'NOTICE', 'VOICE', 'UNIT', 'POWER', 'TOWN', 'FINE', 'CERTAIN', 'FLY', 'FALL', 'LEAD', 'CRY', 'DARK', 'MACHINE', 'NOTE', 'WAIT', 'PLAN', 'FIGURE', 'STAR', 'BOX', 'NOUN', 'FIELD', 'REST', 'CORRECT', 'ABLE', 'POUND', 'DONE', 'BEAUTY', 'DRIVE', 'STOOD', 'CONTAIN', 'FRONT', 'TEACH', 'WEEK', 'FINAL', 'GAVE', 'GREEN', 'OH', 'QUICK', 'DEVELOP', 'OCEAN', 'WARM', 'FREE', 'MINUTE', 'STRONG', 'SPECIAL', 'MIND', 'BEHIND', 'CLEAR', 'TAIL', 'PRODUCE', 'FACT', 'STREET', 'INCH', 'MULTIPLY', 'NOTHING', 'COURSE', 'STAY', 'WHEEL', 'FULL', 'FORCE', 'BLUE', 'OBJECT', 'DECIDE', 'SURFACE', 'DEEP', 'MOON', 'ISLAND', 'FOOT', 'SYSTEM', 'BUSY', 'TEST', 'RECORD', 'BOAT', 'COMMON', 'GOLD', 'POSSIBLE', 'PLANE', 'STEAD', 'DRY', 'WONDER', 'LAUGH', 'THOUSANDS', 'AGO', 'RAN', 'CHECK', 'GAME', 'SHAPE', 'EQUATE', 'MISS', 'BROUGHT', 'HEAT', 'SNOW', 'TIRE', 'BRING', 'YES', 'DISTANT', 'FILL', 'EAST', 'PAINT', 'LANGUAGE', 'AMONG'}
        
        # Filter out common words and return unique symbols
        filtered_symbols = [symbol for symbol in symbols if symbol not in common_words]
        return list(set(filtered_symbols))
    
    def _extract_advisor_mention(self, message: str) -> Optional[str]:
        """Extract advisor mentions from message"""
        advisor_patterns = [
            r'advisor\s+([A-Za-z\s]+)',
            r'analyst\s+([A-Za-z\s]+)',
            r'expert\s+([A-Za-z\s]+)',
            r'by\s+([A-Za-z\s]+)\s+(?:sir|madam)',
            r'([A-Za-z\s]+)\s+(?:sir|madam)\s+says',
        ]
        
        for pattern in advisor_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None

# Global service instance
gemini_service = GeminiService()