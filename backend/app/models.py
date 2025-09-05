from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, ForeignKey, JSON, Date, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date
import uuid

from app.database import Base

class Tip(Base):
    __tablename__ = "tips"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    message = Column(Text, nullable=False)
    source = Column(String(50), default="manual")
    submitter_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to assessments
    assessments = relationship("Assessment", back_populates="tip")

class Assessment(Base):
    __tablename__ = "assessments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tip_id = Column(String, ForeignKey("tips.id"), nullable=False)
    level = Column(String(10), nullable=False)  # Low, Medium, High
    score = Column(Integer, nullable=False)  # 0-100
    reasons = Column(JSON, nullable=False)  # List of reasons
    stock_symbols = Column(JSON, default=lambda: [])  # List of stock symbols
    advisor_info = Column(JSON, nullable=True)  # Advisor information if found
    gemini_raw = Column(JSON, nullable=True)  # Raw Gemini API response
    confidence = Column(Integer, nullable=True)  # AI confidence score
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to tip
    tip = relationship("Tip", back_populates="assessments")

class PDFCheck(Base):
    __tablename__ = "pdf_checks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    file_hash = Column(String(64), unique=True, nullable=False)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)
    ocr_text = Column(Text, nullable=True)
    anomalies = Column(JSON, default=lambda: [])  # List of detected anomalies
    score = Column(Integer, nullable=True)  # Authenticity score 0-100
    is_likely_fake = Column(Boolean, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class HeatmapBucket(Base):
    __tablename__ = "heatmap_buckets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dimension = Column(String(20), nullable=False)  # 'sector' or 'region'
    key = Column(String(100), nullable=False)  # sector name or region name
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    total_count = Column(Integer, default=0)
    high_risk_count = Column(Integer, default=0)
    medium_risk_count = Column(Integer, default=0)
    low_risk_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)

# Multi-Source Data Integration Models
class FMPMarketData(Base):
    __tablename__ = "fmp_market_data"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(20), nullable=False)
    price = Column(Integer, nullable=True)  # Store as cents to avoid decimal issues
    change_percent = Column(Integer, nullable=True)  # Store as basis points (0.01% = 1)
    volume = Column(Integer, nullable=True)
    market_cap = Column(BigInteger, nullable=True)
    unusual_activity = Column(Boolean, default=False)
    fraud_relevance_score = Column(Integer, nullable=True)  # 0-100
    data_timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class GoogleTrendsData(Base):
    __tablename__ = "google_trends_data"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    keyword = Column(String(255), nullable=False)
    region = Column(String(100), nullable=True)
    search_volume = Column(Integer, nullable=True)
    trend_direction = Column(String(20), nullable=True)  # 'rising', 'falling', 'stable'
    spike_detected = Column(Boolean, default=False)
    fraud_correlation_score = Column(Integer, nullable=True)  # 0-100
    timeframe = Column(String(20), nullable=True)  # '1h', '1d', '7d', '30d'
    data_timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class EconomicTimesArticle(Base):
    __tablename__ = "economic_times_articles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_url = Column(String(500), unique=True, nullable=False)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # 'markets', 'policy', 'banking'
    author = Column(String(255), nullable=True)
    published_at = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    fraud_relevance_score = Column(Integer, nullable=True)  # 0-100
    sentiment = Column(String(20), nullable=True)  # 'positive', 'negative', 'neutral'
    regulatory_mentions = Column(JSON, default=lambda: [])  # ['SEBI', 'RBI', 'IRDAI']
    stock_mentions = Column(JSON, default=lambda: [])
    created_at = Column(DateTime, default=datetime.utcnow)

class DataIndicator(Base):
    __tablename__ = "data_indicators"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    heatmap_sector = Column(String(100), nullable=True)
    heatmap_region = Column(String(100), nullable=True)
    indicator_type = Column(String(50), nullable=False)  # 'fmp_alert', 'trend_spike', 'news_sentiment'
    source = Column(String(50), nullable=False)  # 'fmp', 'google_trends', 'economic_times'
    relevance_score = Column(Integer, nullable=False)  # 0-100
    summary = Column(Text, nullable=True)
    details = Column(JSON, default=lambda: {})
    active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class CrossSourceCorrelation(Base):
    __tablename__ = "cross_source_correlations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    correlation_type = Column(String(50), nullable=False)  # 'market_news_trend', 'regulatory_stock_spike'
    source_1 = Column(String(50), nullable=False)  # 'fmp', 'google_trends', 'economic_times'
    source_1_id = Column(String, nullable=False)
    source_2 = Column(String(50), nullable=False)
    source_2_id = Column(String, nullable=False)
    correlation_strength = Column(Integer, nullable=False)  # 0-100 (instead of 0-1 float)
    fraud_implication = Column(Text, nullable=True)
    analysis_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Forecast(Base):
    __tablename__ = "forecasts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    period = Column(String(7), nullable=False)  # YYYY-MM format
    dimension = Column(String(20), nullable=False)  # 'sector' or 'region'
    key = Column(String(100), nullable=False)  # sector name or region name
    risk_score = Column(Integer, nullable=False)  # 0-100
    confidence_min = Column(Integer, nullable=False)  # Lower bound of confidence interval
    confidence_max = Column(Integer, nullable=False)  # Upper bound of confidence interval
    rationale = Column(Text, nullable=True)  # AI-generated explanation
    contributing_factors = Column(JSON, default=lambda: [])  # List of factor objects
    features = Column(JSON, default=lambda: {})  # Time-series features used
    model_version = Column(String(50), default="v1.0")
    created_at = Column(DateTime, default=datetime.utcnow)

# Fraud Chain Detection Models
class FraudChain(Base):
    __tablename__ = "fraud_chains"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active")  # 'active', 'closed', 'investigating'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    nodes = relationship("FraudChainNode", back_populates="chain", cascade="all, delete-orphan")
    edges = relationship("FraudChainEdge", back_populates="chain", cascade="all, delete-orphan")

class FraudChainNode(Base):
    __tablename__ = "fraud_chain_nodes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    chain_id = Column(String, ForeignKey("fraud_chains.id"), nullable=False)
    node_type = Column(String(50), nullable=False)  # 'tip', 'document', 'stock', 'complaint', 'advisor'
    reference_id = Column(String, nullable=False)  # points to tips.id, pdf_checks.id, etc.
    label = Column(String(255), nullable=True)
    node_metadata = Column(JSON, default=lambda: {})  # Additional node-specific data
    position_x = Column(Integer, nullable=True)  # For visualization positioning
    position_y = Column(Integer, nullable=True)  # For visualization positioning
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chain = relationship("FraudChain", back_populates="nodes")

class FraudChainEdge(Base):
    __tablename__ = "fraud_chain_edges"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    chain_id = Column(String, ForeignKey("fraud_chains.id"), nullable=False)
    from_node_id = Column(String, ForeignKey("fraud_chain_nodes.id"), nullable=False)
    to_node_id = Column(String, ForeignKey("fraud_chain_nodes.id"), nullable=False)
    relationship_type = Column(String(100), nullable=False)  # 'references', 'leads_to', 'mentions', 'involves'
    confidence = Column(Integer, default=100)  # 0-100 confidence score
    edge_metadata = Column(JSON, default=lambda: {})  # Additional edge-specific data
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chain = relationship("FraudChain", back_populates="edges")
    from_node = relationship("FraudChainNode", foreign_keys=[from_node_id])
    to_node = relationship("FraudChainNode", foreign_keys=[to_node_id])

# Human-in-the-Loop Review System Models
class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, nullable=False)  # ID of the case being reviewed (assessment, pdf_check, etc.)
    case_type = Column(String(50), nullable=False)  # 'assessment', 'pdf_check', 'fraud_chain'
    reviewer_id = Column(String(100), nullable=False)  # ID of the reviewer
    ai_decision = Column(JSON, nullable=False)  # Original AI decision data
    human_decision = Column(JSON, nullable=True)  # Human override decision
    decision = Column(String(50), nullable=False)  # 'approve', 'override', 'needs_more_info'
    notes = Column(Text, nullable=True)  # Reviewer notes
    ai_confidence = Column(Integer, nullable=True)  # AI confidence score (0-100)
    priority = Column(String(20), default="medium")  # 'low', 'medium', 'high'
    status = Column(String(20), default="pending")  # 'pending', 'completed', 'escalated'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)