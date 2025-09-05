-- IRIS RegTech Platform - PostgreSQL schema
-- Generate tables equivalent to SQLAlchemy models in app/models.py
-- Safe to run multiple times.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tips
CREATE TABLE IF NOT EXISTS tips (
  id                varchar PRIMARY KEY,
  message           text NOT NULL,
  source            varchar(50) DEFAULT 'manual',
  submitter_id      varchar(100),
  created_at        timestamp WITHOUT time zone DEFAULT now(),
  updated_at        timestamp WITHOUT time zone DEFAULT now()
);

-- Assessments
CREATE TABLE IF NOT EXISTS assessments (
  id                varchar PRIMARY KEY,
  tip_id            varchar NOT NULL REFERENCES tips(id) ON DELETE CASCADE,
  level             varchar(10) NOT NULL,
  score             integer NOT NULL,
  reasons           jsonb NOT NULL,
  stock_symbols     jsonb DEFAULT '[]'::jsonb,
  advisor_info      jsonb,
  gemini_raw        jsonb,
  confidence        integer,
  created_at        timestamp WITHOUT time zone DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_assessments_tip_id ON assessments(tip_id);

-- PDF Checks
CREATE TABLE IF NOT EXISTS pdf_checks (
  id                 varchar PRIMARY KEY,
  file_hash          varchar(64) UNIQUE NOT NULL,
  filename           varchar(255) NOT NULL,
  file_size          integer,
  ocr_text           text,
  anomalies          jsonb DEFAULT '[]'::jsonb,
  score              integer,
  is_likely_fake     boolean,
  processing_time_ms integer,
  created_at         timestamp WITHOUT time zone DEFAULT now()
);

-- Heatmap Buckets
CREATE TABLE IF NOT EXISTS heatmap_buckets (
  id                  varchar PRIMARY KEY,
  dimension           varchar(20) NOT NULL,
  key                 varchar(100) NOT NULL,
  from_date           date NOT NULL,
  to_date             date NOT NULL,
  total_count         integer DEFAULT 0,
  high_risk_count     integer DEFAULT 0,
  medium_risk_count   integer DEFAULT 0,
  low_risk_count      integer DEFAULT 0,
  last_updated        timestamp WITHOUT time zone DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_heatmap_dim_key_dates ON heatmap_buckets(dimension, key, from_date, to_date);

-- FMP Market Data
CREATE TABLE IF NOT EXISTS fmp_market_data (
  id                     varchar PRIMARY KEY,
  symbol                 varchar(20) NOT NULL,
  price                  integer,
  change_percent         integer,
  volume                 integer,
  market_cap             bigint,
  unusual_activity       boolean DEFAULT false,
  fraud_relevance_score  integer,
  data_timestamp         timestamp WITHOUT time zone NOT NULL,
  created_at             timestamp WITHOUT time zone DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_fmp_market_data_symbol ON fmp_market_data(symbol);

-- Google Trends Data
CREATE TABLE IF NOT EXISTS google_trends_data (
  id                     varchar PRIMARY KEY,
  keyword                varchar(255) NOT NULL,
  region                 varchar(100),
  search_volume          integer,
  trend_direction        varchar(20),
  spike_detected         boolean DEFAULT false,
  fraud_correlation_score integer,
  timeframe              varchar(20),
  data_timestamp         timestamp WITHOUT time zone NOT NULL,
  created_at             timestamp WITHOUT time zone DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_google_trends_key_region ON google_trends_data(keyword, region);

-- Economic Times Articles
CREATE TABLE IF NOT EXISTS economic_times_articles (
  id                   varchar PRIMARY KEY,
  article_url          varchar(500) UNIQUE NOT NULL,
  title                text NOT NULL,
  content              text,
  category             varchar(100),
  author               varchar(255),
  published_at         timestamp WITHOUT time zone,
  scraped_at           timestamp WITHOUT time zone DEFAULT now(),
  fraud_relevance_score integer,
  sentiment            varchar(20),
  regulatory_mentions  jsonb DEFAULT '[]'::jsonb,
  stock_mentions       jsonb DEFAULT '[]'::jsonb,
  created_at           timestamp WITHOUT time zone DEFAULT now()
);

-- Data Indicators
CREATE TABLE IF NOT EXISTS data_indicators (
  id               varchar PRIMARY KEY,
  heatmap_sector   varchar(100),
  heatmap_region   varchar(100),
  indicator_type   varchar(50) NOT NULL,
  source           varchar(50) NOT NULL,
  relevance_score  integer NOT NULL,
  summary          text,
  details          jsonb DEFAULT '{}'::jsonb,
  active           boolean DEFAULT true,
  expires_at       timestamp WITHOUT time zone,
  created_at       timestamp WITHOUT time zone DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_data_indicators_sector ON data_indicators(heatmap_sector);
CREATE INDEX IF NOT EXISTS ix_data_indicators_region ON data_indicators(heatmap_region);

-- Cross Source Correlations
CREATE TABLE IF NOT EXISTS cross_source_correlations (
  id                    varchar PRIMARY KEY,
  correlation_type      varchar(50) NOT NULL,
  source_1              varchar(50) NOT NULL,
  source_1_id           varchar NOT NULL,
  source_2              varchar(50) NOT NULL,
  source_2_id           varchar NOT NULL,
  correlation_strength  integer NOT NULL,
  fraud_implication     text,
  analysis_summary      text,
  created_at            timestamp WITHOUT time zone DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_corr_sources ON cross_source_correlations(source_1, source_2);

-- Forecasts
CREATE TABLE IF NOT EXISTS forecasts (
  id                   varchar PRIMARY KEY,
  period               varchar(7) NOT NULL,
  dimension            varchar(20) NOT NULL,
  key                  varchar(100) NOT NULL,
  risk_score           integer NOT NULL,
  confidence_min       integer NOT NULL,
  confidence_max       integer NOT NULL,
  rationale            text,
  contributing_factors jsonb DEFAULT '[]'::jsonb,
  features             jsonb DEFAULT '{}'::jsonb,
  model_version        varchar(50) DEFAULT 'v1.0',
  created_at           timestamp WITHOUT time zone DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_forecasts_period_dim_key ON forecasts(period, dimension, key);

-- Fraud Chains
CREATE TABLE IF NOT EXISTS fraud_chains (
  id           varchar PRIMARY KEY,
  name         varchar(255),
  description  text,
  status       varchar(50) DEFAULT 'active',
  created_at   timestamp WITHOUT time zone DEFAULT now(),
  updated_at   timestamp WITHOUT time zone DEFAULT now()
);

-- Fraud Chain Nodes
CREATE TABLE IF NOT EXISTS fraud_chain_nodes (
  id             varchar PRIMARY KEY,
  chain_id       varchar NOT NULL REFERENCES fraud_chains(id) ON DELETE CASCADE,
  node_type      varchar(50) NOT NULL,
  reference_id   varchar NOT NULL,
  label          varchar(255),
  node_metadata  jsonb DEFAULT '{}'::jsonb,
  position_x     integer,
  position_y     integer,
  created_at     timestamp WITHOUT time zone DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_nodes_chain ON fraud_chain_nodes(chain_id);

-- Fraud Chain Edges
CREATE TABLE IF NOT EXISTS fraud_chain_edges (
  id                 varchar PRIMARY KEY,
  chain_id           varchar NOT NULL REFERENCES fraud_chains(id) ON DELETE CASCADE,
  from_node_id       varchar NOT NULL REFERENCES fraud_chain_nodes(id) ON DELETE CASCADE,
  to_node_id         varchar NOT NULL REFERENCES fraud_chain_nodes(id) ON DELETE CASCADE,
  relationship_type  varchar(100) NOT NULL,
  confidence         integer DEFAULT 100,
  edge_metadata      jsonb DEFAULT '{}'::jsonb,
  created_at         timestamp WITHOUT time zone DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_edges_chain ON fraud_chain_edges(chain_id);
CREATE INDEX IF NOT EXISTS ix_edges_from_to ON fraud_chain_edges(from_node_id, to_node_id);

-- Reviews (Human-in-the-Loop)
CREATE TABLE IF NOT EXISTS reviews (
  id              varchar PRIMARY KEY,
  case_id         varchar NOT NULL,
  case_type       varchar(50) NOT NULL,
  reviewer_id     varchar(100) NOT NULL,
  ai_decision     jsonb NOT NULL,
  human_decision  jsonb,
  decision        varchar(50) NOT NULL,
  notes           text,
  ai_confidence   integer,
  priority        varchar(20) DEFAULT 'medium',
  status          varchar(20) DEFAULT 'pending',
  created_at      timestamp WITHOUT time zone DEFAULT now(),
  updated_at      timestamp WITHOUT time zone DEFAULT now()
);
