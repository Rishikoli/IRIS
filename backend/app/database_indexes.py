#!/usr/bin/env python3
"""
IRIS RegTech Platform - Database Indexing for Demo Performance
Adds strategic indexes to improve query performance for demo scenarios
"""

from sqlalchemy import text, Index
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models import (
    Tip, Assessment, PDFCheck, HeatmapBucket, FMPMarketData,
    GoogleTrendsData, EconomicTimesArticle, DataIndicator,
    Forecast, FraudChain, FraudChainNode, FraudChainEdge, Review
)

def create_performance_indexes():
    """Create indexes for improved demo performance"""
    
    db = SessionLocal()
    
    try:
        print("📊 Creating performance indexes for IRIS RegTech demo...")
        
        # Tips table indexes
        print("  • Creating tips indexes...")
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_tips_created_at ON tips(created_at DESC)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_tips_source ON tips(source)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_tips_submitter_id ON tips(submitter_id)"))
        
        # Assessments table indexes
        print("  • Creating assessments indexes...")
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_assessments_tip_id ON assessments(tip_id)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_assessments_level ON assessments(level)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_assessments_score ON assessments(score DESC)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_assessments_confidence ON assessments(confidence DESC)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_assessments_created_at ON assessments(created_at DESC)"))
        
        # PDF checks table indexes
        print("  • Creating pdf_checks indexes...")
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_pdf_checks_file_hash ON pdf_checks(file_hash)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_pdf_checks_score ON pdf_checks(score DESC)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_pdf_checks_is_likely_fake ON pdf_checks(is_likely_fake)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_pdf_checks_created_at ON pdf_checks(created_at DESC)"))
        
        # Heatmap buckets table indexes - Critical for dashboard performance
        print("  • Creating heatmap_buckets indexes...")
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_heatmap_dimension_key ON heatmap_buckets(dimension, key)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_heatmap_date_range ON heatmap_buckets(from_date, to_date)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_heatmap_total_count ON heatmap_buckets(total_count DESC)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_heatmap_high_risk ON heatmap_buckets(high_risk_count DESC)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_heatmap_last_updated ON heatmap_buckets(last_updated DESC)"))
        
        # FMP market data indexes
        print("  • Creating fmp_market_data indexes...")
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_fmp_symbol ON fmp_market_data(symbol)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_fmp_data_timestamp ON fmp_market_data(data_timestamp DESC)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_fmp_unusual_activity ON fmp_market_data(unusual_activity)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_fmp_fraud_relevance ON fmp_market_data(fraud_relevance_score DESC)"))
        
        # Google Trends data indexes
        print("  • Creating google_trends_data indexes...")
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_trends_keyword ON google_trends_data(keyword)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_trends_region ON google_trends_data(region)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_trends_timestamp ON google_trends_data(data_timestamp DESC)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_trends_spike_detected ON google_trends_data(spike_detected)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_trends_fraud_correlation ON google_trends_data(fraud_correlation_score DESC)"))
        
        # Economic Times articles indexes
        print("  • Creating economic_times_articles indexes...")
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_et_article_url ON economic_times_articles(article_url)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_et_category ON economic_times_articles(category)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_et_published_at ON economic_times_articles(published_at DESC)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_et_fraud_relevance ON economic_times_articles(fraud_relevance_score DESC)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_et_sentiment ON economic_times_articles(sentiment)"))
        
        # Data indicators indexes
        print("  • Creating data_indicators indexes...")
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_indicators_sector ON data_indicators(heatmap_sector)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_indicators_region ON data_indicators(heatmap_region)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_indicators_type ON data_indicators(indicator_type)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_indicators_source ON data_indicators(source)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_indicators_relevance ON data_indicators(relevance_score DESC)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_indicators_active ON data_indicators(active)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_indicators_created_at ON data_indicators(created_at DESC)"))
        
        # Forecasts table indexes
        print("  • Creating forecasts indexes...")
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_forecasts_period ON forecasts(period)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_forecasts_dimension_key ON forecasts(dimension, key)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_forecasts_risk_score ON forecasts(risk_score DESC)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_forecasts_created_at ON forecasts(created_at DESC)"))
        
        # Fraud chains indexes
        print("  • Creating fraud_chains indexes...")
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_fraud_chains_status ON fraud_chains(status)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_fraud_chains_created_at ON fraud_chains(created_at DESC)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_fraud_chains_updated_at ON fraud_chains(updated_at DESC)"))
        
        # Fraud chain nodes indexes
        print("  • Creating fraud_chain_nodes indexes...")
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_fraud_nodes_chain_id ON fraud_chain_nodes(chain_id)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_fraud_nodes_type ON fraud_chain_nodes(node_type)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_fraud_nodes_reference_id ON fraud_chain_nodes(reference_id)"))
        
        # Fraud chain edges indexes
        print("  • Creating fraud_chain_edges indexes...")
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_fraud_edges_chain_id ON fraud_chain_edges(chain_id)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_fraud_edges_from_node ON fraud_chain_edges(from_node_id)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_fraud_edges_to_node ON fraud_chain_edges(to_node_id)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_fraud_edges_relationship ON fraud_chain_edges(relationship_type)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_fraud_edges_confidence ON fraud_chain_edges(confidence DESC)"))
        
        # Reviews table indexes
        print("  • Creating reviews indexes...")
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_reviews_case_id ON reviews(case_id)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_reviews_case_type ON reviews(case_type)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_reviews_reviewer_id ON reviews(reviewer_id)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_reviews_decision ON reviews(decision)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_reviews_priority ON reviews(priority)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_reviews_status ON reviews(status)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_reviews_created_at ON reviews(created_at DESC)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_reviews_ai_confidence ON reviews(ai_confidence DESC)"))
        
        # Composite indexes for common query patterns
        print("  • Creating composite indexes for common queries...")
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_assessments_level_score ON assessments(level, score DESC)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_heatmap_dimension_date ON heatmap_buckets(dimension, from_date, to_date)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_reviews_status_priority ON reviews(status, priority)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_indicators_active_relevance ON data_indicators(active, relevance_score DESC)"))
        
        db.commit()
        print("✅ All performance indexes created successfully!")
        
        # Analyze tables for query optimization
        print("📈 Analyzing tables for query optimization...")
        db.execute(text("ANALYZE"))
        db.commit()
        
        print("✅ Database analysis completed!")
        
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def drop_all_indexes():
    """Drop all custom indexes (for cleanup)"""
    
    db = SessionLocal()
    
    try:
        print("🧹 Dropping all custom indexes...")
        
        # Get all custom indexes
        result = db.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name LIKE 'idx_%'
        """))
        
        indexes = result.fetchall()
        
        for (index_name,) in indexes:
            try:
                db.execute(text(f"DROP INDEX IF EXISTS {index_name}"))
                print(f"  • Dropped index: {index_name}")
            except Exception as e:
                print(f"  • Warning: Could not drop {index_name}: {e}")
        
        db.commit()
        print("✅ All custom indexes dropped!")
        
    except Exception as e:
        print(f"❌ Error dropping indexes: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        drop_all_indexes()
    else:
        create_performance_indexes()
