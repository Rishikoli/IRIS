"""
Corporate Announcement Scraping Service
Scrapes NSE, BSE and other sources for corporate announcements
"""
import asyncio
import aiohttp
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
from dataclasses import dataclass
from app.exceptions import ExternalServiceException

logger = logging.getLogger(__name__)

@dataclass
class AnnouncementData:
    company_symbol: str
    company_name: str
    exchange: str
    announcement_id: str
    title: str
    content: str
    category: str
    announcement_date: datetime
    filing_date: datetime
    source_url: str

class NSEAnnouncementScraper:
    """Scraper for NSE corporate announcements"""
    
    BASE_URL = "https://www.nseindia.com"
    ANNOUNCEMENTS_URL = f"{BASE_URL}/api/corporates-announcements"
    
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/companies-listing/corporate-filings-announcements'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_recent_announcements(self, days: int = 7) -> List[AnnouncementData]:
        """Fetch recent announcements from NSE"""
        try:
            # First, get the main page to establish session
            async with self.session.get(f"{self.BASE_URL}/companies-listing/corporate-filings-announcements") as response:
                if response.status != 200:
                    raise ExternalServiceException("nse", f"Failed to access NSE main page: {response.status}")
            
            # Now fetch announcements
            params = {
                'index': 'equities',
                'from_date': (datetime.now() - timedelta(days=days)).strftime('%d-%m-%Y'),
                'to_date': datetime.now().strftime('%d-%m-%Y')
            }
            
            async with self.session.get(self.ANNOUNCEMENTS_URL, params=params) as response:
                if response.status != 200:
                    logger.warning(f"NSE API returned status {response.status}, falling back to HTML scraping")
                    return await self._scrape_html_announcements(days)
                
                data = await response.json()
                return self._parse_nse_json_response(data)
                
        except Exception as e:
            logger.error(f"Error fetching NSE announcements: {str(e)}")
            # Fallback to HTML scraping
            return await self._scrape_html_announcements(days)
    
    async def _scrape_html_announcements(self, days: int) -> List[AnnouncementData]:
        """Fallback HTML scraping method"""
        announcements = []
        try:
            url = f"{self.BASE_URL}/companies-listing/corporate-filings-announcements"
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Look for announcement tables or divs
                announcement_rows = soup.find_all('tr', class_='announcement-row') or soup.find_all('div', class_='announcement-item')
                
                for row in announcement_rows[:50]:  # Limit to recent 50
                    try:
                        announcement = self._parse_html_row(row)
                        if announcement:
                            announcements.append(announcement)
                    except Exception as e:
                        logger.warning(f"Error parsing announcement row: {str(e)}")
                        continue
                        
        except Exception as e:
            logger.error(f"HTML scraping failed: {str(e)}")
            
        return announcements
    
    def _parse_nse_json_response(self, data: Dict) -> List[AnnouncementData]:
        """Parse NSE JSON API response"""
        announcements = []
        
        if not isinstance(data, dict) or 'data' not in data:
            return announcements
            
        for item in data.get('data', []):
            try:
                announcement = AnnouncementData(
                    company_symbol=item.get('symbol', '').strip(),
                    company_name=item.get('companyName', '').strip(),
                    exchange='NSE',
                    announcement_id=f"NSE_{item.get('an_dt', '')}_{item.get('symbol', '')}_{item.get('seq_id', '')}",
                    title=item.get('subject', '').strip(),
                    content=item.get('desc', '').strip() or item.get('subject', '').strip(),
                    category=self._categorize_announcement(item.get('subject', '')),
                    announcement_date=self._parse_date(item.get('an_dt')),
                    filing_date=self._parse_date(item.get('an_dt')),
                    source_url=item.get('attachmentName', '') or f"{self.BASE_URL}/companies-listing/corporate-filings-announcements"
                )
                
                if announcement.company_symbol and announcement.title:
                    announcements.append(announcement)
                    
            except Exception as e:
                logger.warning(f"Error parsing NSE announcement: {str(e)}")
                continue
                
        return announcements
    
    def _parse_html_row(self, row) -> Optional[AnnouncementData]:
        """Parse HTML table row for announcement data"""
        try:
            cells = row.find_all(['td', 'div'])
            if len(cells) < 4:
                return None
                
            # Extract data from cells (adjust based on actual HTML structure)
            symbol = cells[0].get_text(strip=True)
            company_name = cells[1].get_text(strip=True)
            subject = cells[2].get_text(strip=True)
            date_str = cells[3].get_text(strip=True)
            
            return AnnouncementData(
                company_symbol=symbol,
                company_name=company_name,
                exchange='NSE',
                announcement_id=f"NSE_{date_str}_{symbol}_{hash(subject) % 10000}",
                title=subject,
                content=subject,
                category=self._categorize_announcement(subject),
                announcement_date=self._parse_date(date_str),
                filing_date=self._parse_date(date_str),
                source_url=f"{self.BASE_URL}/companies-listing/corporate-filings-announcements"
            )
            
        except Exception as e:
            logger.warning(f"Error parsing HTML row: {str(e)}")
            return None
    
    def _categorize_announcement(self, title: str) -> str:
        """Categorize announcement based on title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['merger', 'acquisition', 'amalgamation']):
            return 'merger_acquisition'
        elif any(word in title_lower for word in ['result', 'financial', 'quarterly', 'annual']):
            return 'financial_results'
        elif any(word in title_lower for word in ['dividend', 'bonus', 'split']):
            return 'corporate_action'
        elif any(word in title_lower for word in ['board', 'meeting', 'director']):
            return 'board_meeting'
        elif any(word in title_lower for word in ['agreement', 'contract', 'mou']):
            return 'business_agreement'
        else:
            return 'general'
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        if not date_str:
            return datetime.now()
            
        # Try different date formats
        formats = ['%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
                
        # If all formats fail, return current time
        logger.warning(f"Could not parse date: {date_str}")
        return datetime.now()

class BSEAnnouncementScraper:
    """Scraper for BSE corporate announcements"""
    
    BASE_URL = "https://www.bseindia.com"
    ANNOUNCEMENTS_URL = f"{BASE_URL}/corporates/ann.html"
    
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_recent_announcements(self, days: int = 7) -> List[AnnouncementData]:
        """Fetch recent announcements from BSE"""
        announcements = []
        
        try:
            async with self.session.get(self.ANNOUNCEMENTS_URL) as response:
                if response.status != 200:
                    raise ExternalServiceException("bse", f"Failed to access BSE announcements: {response.status}")
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find announcement table
                table = soup.find('table', {'id': 'ctl00_ContentPlaceHolder1_gvData'}) or soup.find('table', class_='TTRow')
                
                if not table:
                    logger.warning("Could not find BSE announcements table")
                    return announcements
                
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows[:50]:  # Limit to recent 50
                    try:
                        announcement = self._parse_bse_row(row)
                        if announcement:
                            announcements.append(announcement)
                    except Exception as e:
                        logger.warning(f"Error parsing BSE row: {str(e)}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error fetching BSE announcements: {str(e)}")
            
        return announcements
    
    def _parse_bse_row(self, row) -> Optional[AnnouncementData]:
        """Parse BSE table row"""
        try:
            cells = row.find_all('td')
            if len(cells) < 5:
                return None
            
            # BSE table structure: Date, Company, Category, Subject, PDF Link
            date_str = cells[0].get_text(strip=True)
            company_info = cells[1].get_text(strip=True)
            category = cells[2].get_text(strip=True)
            subject = cells[3].get_text(strip=True)
            
            # Extract company symbol and name
            company_parts = company_info.split('-', 1)
            symbol = company_parts[0].strip() if company_parts else company_info
            company_name = company_parts[1].strip() if len(company_parts) > 1 else company_info
            
            return AnnouncementData(
                company_symbol=symbol,
                company_name=company_name,
                exchange='BSE',
                announcement_id=f"BSE_{date_str}_{symbol}_{hash(subject) % 10000}",
                title=subject,
                content=subject,
                category=category.lower().replace(' ', '_'),
                announcement_date=self._parse_date(date_str),
                filing_date=self._parse_date(date_str),
                source_url=self.ANNOUNCEMENTS_URL
            )
            
        except Exception as e:
            logger.warning(f"Error parsing BSE row: {str(e)}")
            return None
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse BSE date format"""
        if not date_str:
            return datetime.now()
            
        formats = ['%d %b %Y', '%d-%m-%Y', '%Y-%m-%d']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
                
        logger.warning(f"Could not parse BSE date: {date_str}")
        return datetime.now()

class AnnouncementScrapingService:
    """Main service for scraping corporate announcements"""
    
    def __init__(self):
        self.scrapers = {
            'NSE': NSEAnnouncementScraper,
            'BSE': BSEAnnouncementScraper
        }
    
    async def fetch_all_recent_announcements(self, days: int = 7) -> List[AnnouncementData]:
        """Fetch announcements from all exchanges"""
        all_announcements = []
        
        for exchange, scraper_class in self.scrapers.items():
            try:
                async with scraper_class() as scraper:
                    announcements = await scraper.get_recent_announcements(days)
                    all_announcements.extend(announcements)
                    logger.info(f"Fetched {len(announcements)} announcements from {exchange}")
                    
            except Exception as e:
                logger.error(f"Error fetching from {exchange}: {str(e)}")
                continue
        
        # Remove duplicates based on company symbol and title
        unique_announcements = self._deduplicate_announcements(all_announcements)
        
        logger.info(f"Total unique announcements fetched: {len(unique_announcements)}")
        return unique_announcements
    
    def _deduplicate_announcements(self, announcements: List[AnnouncementData]) -> List[AnnouncementData]:
        """Remove duplicate announcements"""
        seen = set()
        unique = []
        
        for announcement in announcements:
            # Create a key based on company symbol and title
            key = f"{announcement.company_symbol}_{announcement.title}".lower()
            key = re.sub(r'\s+', ' ', key).strip()
            
            if key not in seen:
                seen.add(key)
                unique.append(announcement)
        
        return unique

# Singleton instance
announcement_scraper = AnnouncementScrapingService()