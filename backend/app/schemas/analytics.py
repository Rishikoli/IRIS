#!/usr/bin/env python3
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Common
class ApiEnvelope(BaseModel):
    status: str = Field(example="success")
    timestamp: str = Field(example="2025-01-01T00:00:00Z")

# /summary
class RiskAnalysis(BaseModel):
    risk_distribution: Dict[str, int]
    high_risk_percentage: float
    avg_ai_confidence: float
    low_confidence_cases: int

class DocumentVerificationStats(BaseModel):
    authentic_documents: int
    fake_documents: int
    avg_authenticity_score: float
    total_processed: int

class RecentActivity(BaseModel):
    tips_last_7_days: int
    documents_last_7_days: int
    reviews_last_7_days: int

class ReviewSystemStats(BaseModel):
    pending_reviews: int
    completed_reviews: int
    review_completion_rate: float

class PlatformOverview(BaseModel):
    total_tips_analyzed: int
    total_documents_verified: int
    total_fraud_chains_detected: int
    total_human_reviews: int
    platform_uptime_days: int

class PlatformSummaryData(BaseModel):
    overview: PlatformOverview
    risk_analysis: RiskAnalysis
    document_verification: DocumentVerificationStats
    recent_activity: RecentActivity
    review_system: ReviewSystemStats
    insights: Optional[str] = None

class PlatformSummaryResponse(ApiEnvelope):
    data: PlatformSummaryData

# /trends/fraud
class FraudTrendPoint(BaseModel):
    date: str
    high_risk: int
    medium_risk: int
    low_risk: int
    total: int

class FraudTrendPeriod(BaseModel):
    start_date: str
    end_date: str
    days: int
    granularity: str

class FraudTrendsSummary(BaseModel):
    total_data_points: int
    trend_direction: str

class FraudTrendsData(BaseModel):
    period: FraudTrendPeriod
    tip_trends: List[FraudTrendPoint]
    summary: FraudTrendsSummary
    insights: Optional[str] = None

class FraudTrendsResponse(ApiEnvelope):
    data: FraudTrendsData

# /analysis/sectors
class SectorItem(BaseModel):
    sector: str
    total_cases: int
    high_risk_cases: int
    medium_risk_cases: int
    low_risk_cases: int
    high_risk_percentage: float
    risk_level: str

class SectorAnalysisSummary(BaseModel):
    total_sectors: int
    highest_risk_sector: Optional[str]
    avg_high_risk_percentage: float

class SectorAnalysisData(BaseModel):
    sectors: List[SectorItem]
    summary: SectorAnalysisSummary
    insights: Optional[str] = None
    external: Optional[Dict[str, Any]] = None

class SectorAnalysisResponse(ApiEnvelope):
    data: SectorAnalysisData

# /analysis/regions
class RegionItem(BaseModel):
    region: str
    total_cases: int
    high_risk_cases: int
    high_risk_percentage: float
    population_category: str

class RegionalAnalysisSummary(BaseModel):
    total_regions: int
    highest_activity_region: Optional[str]
    total_cases_all_regions: int

class RegionalAnalysisData(BaseModel):
    regions: List[RegionItem]
    summary: RegionalAnalysisSummary
    insights: Optional[str] = None

class RegionalAnalysisResponse(ApiEnvelope):
    data: RegionalAnalysisData

# /verification/advisors
class AdvisorMonthlyChecks(BaseModel):
    month: str
    checks: int
    verified: int
    fake: int

class AdvisorVerificationStats(BaseModel):
    total_advisor_checks: int
    verified_advisors: int
    unverified_advisors: int
    fake_credentials: int
    verification_success_rate: float

class AdvisorRiskIndicators(BaseModel):
    fake_credential_rate: float
    unverified_rate: float

class AdvisorVerificationTrends(BaseModel):
    monthly_checks: List[AdvisorMonthlyChecks]
    common_fraud_patterns: List[str]

class AdvisorVerificationData(BaseModel):
    verification_stats: AdvisorVerificationStats
    risk_indicators: AdvisorRiskIndicators
    trends: AdvisorVerificationTrends

class AdvisorVerificationResponse(ApiEnvelope):
    data: AdvisorVerificationData

# /documents/authenticity
class AuthenticityTrendPoint(BaseModel):
    date: str
    total_documents: int
    authentic_documents: int
    fake_documents: int
    authenticity_rate: float
    avg_authenticity_score: float

class AnomalyBin(BaseModel):
    anomaly_count: int
    document_count: int
    percentage: float

class DocumentAuthenticitySummary(BaseModel):
    total_documents_processed: int
    overall_authenticity_rate: float
    avg_authenticity_score: float
    most_common_anomalies: List[Dict[str, float]]

class DocumentAuthenticityData(BaseModel):
    trends: List[AuthenticityTrendPoint]
    anomaly_distribution: List[AnomalyBin]
    summary: DocumentAuthenticitySummary
    insights: Optional[str] = None

class DocumentAuthenticityResponse(ApiEnvelope):
    data: DocumentAuthenticityData

# /usage/platform
class TipSourceItem(BaseModel):
    source: str
    count: int

class SubmissionPatterns(BaseModel):
    tip_sources: List[TipSourceItem]
    most_popular_source: str

class PerformanceMetrics(BaseModel):
    avg_pdf_processing_time_ms: int
    min_pdf_processing_time_ms: int
    max_pdf_processing_time_ms: int
    processing_efficiency: str

class ReviewDecisionItem(BaseModel):
    decision: str
    count: int

class ReviewSystemUsage(BaseModel):
    review_decisions: List[ReviewDecisionItem]
    most_common_decision: str

class MonthAggregate(BaseModel):
    tips: int
    pdf_checks: int

class MonthlyComparison(BaseModel):
    current_month: MonthAggregate
    last_month: MonthAggregate
    growth_rates: Dict[str, float]

class SystemHealth(BaseModel):
    uptime_percentage: float
    avg_response_time_ms: int
    error_rate_percentage: float

class PlatformUsageData(BaseModel):
    submission_patterns: SubmissionPatterns
    performance_metrics: PerformanceMetrics
    review_system_usage: ReviewSystemUsage
    monthly_comparison: MonthlyComparison
    system_health: SystemHealth
    insights: Optional[str] = None

class PlatformUsageResponse(ApiEnvelope):
    data: PlatformUsageData
