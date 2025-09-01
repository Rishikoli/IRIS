"""
Corporate Announcement Models for IRIS RegTech Platform
"""
from sqlalchemy import Column, String, Text, DateTime, Integer, Float, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime

class CorporateAnnouncement(Base):
    __tablename__ = "corporate_announcements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic announcement info
    company_symbol = Column(String(20), nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    exchange = Column(String(10), nullable=False)  # NSE, BSE
    announcement_id = Column(String(100), unique=True, nullable=False)
    
    # Content
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)  # merger, acquisition, results, etc.
    
    # Metadata
    announcement_date = Column(DateTime, nullable=False)
    filing_date = Column(DateTime, nullable=False)
    source_url = Column(String(500))
    
    # Processing status
    processed = Column(Boolean, default=False)
    credibility_score = Column(Integer)  # 0-100
    risk_level = Column(String(10))  # Low, Medium, High
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    verifications = relationship("AnnouncementVerification", back_populates="announcement")
    alerts = relationship("MediaAlert", back_populates="announcement")

class AnnouncementVerification(Base):
    __tablename__ = "announcement_verifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    announcement_id = Column(UUID(as_uuid=True), ForeignKey("corporate_announcements.id"))
    
    # Verification types
    verification_type = Column(String(50), nullable=False)  # counterparty, historical, public_domain
    verification_source = Column(String(100), nullable=False)
    
    # Results
    status = Column(String(20), nullable=False)  # verified, disputed, inconclusive
    confidence_score = Column(Float)  # 0-1
    details = Column(JSON)
    discrepancies = Column(JSON)
    
    # Evidence
    source_data = Column(JSON)
    cross_reference_url = Column(String(500))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    announcement = relationship("CorporateAnnouncement", back_populates="verifications")

class HistoricalPerformance(Base):
    __tablename__ = "historical_performance"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_symbol = Column(String(20), nullable=False, index=True)
    
    # Financial metrics
    quarter = Column(String(7), nullable=False)  # 2024Q1
    revenue = Column(Float)
    profit = Column(Float)
    growth_rate = Column(Float)
    
    # Performance indicators
    market_cap = Column(Float)
    pe_ratio = Column(Float)
    debt_equity_ratio = Column(Float)
    
    # Metadata
    data_source = Column(String(50))
    filing_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class MediaAlert(Base):
    __tablename__ = "media_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    announcement_id = Column(UUID(as_uuid=True), ForeignKey("corporate_announcements.id"))
    
    # Alert details
    alert_type = Column(String(50), nullable=False)  # fraud_warning, credibility_concern
    severity = Column(String(10), nullable=False)  # Low, Medium, High, Critical
    
    # Content
    headline = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    detailed_analysis = Column(Text)
    
    # Targeting
    target_media_houses = Column(JSON)  # List of media house IDs/emails
    sent_status = Column(String(20), default='pending')  # pending, sent, acknowledged
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime)
    
    # Relationships
    announcement = relationship("CorporateAnnouncement", back_populates="alerts")

class FraudPattern(Base):
    __tablename__ = "fraud_patterns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Pattern identification
    pattern_type = Column(String(50), nullable=False)  # performance_mismatch, timing_suspicious
    pattern_hash = Column(String(64), unique=True, nullable=False)
    
    # Pattern details
    description = Column(Text, nullable=False)
    indicators = Column(JSON, nullable=False)
    risk_weight = Column(Float, nullable=False)  # 0-1
    
    # Statistics
    occurrence_count = Column(Integer, default=1)
    detection_accuracy = Column(Float)  # Historical accuracy of this pattern
    
    # Timestamps
    first_detected = Column(DateTime, default=datetime.utcnow)
    last_detected = Column(DateTime, default=datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.utcnow)