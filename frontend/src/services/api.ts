import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for adding auth tokens (future use)
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Types
export interface Tip {
  id: string
  message: string
  source: string
  submitter_id?: string
  created_at: string
  updated_at: string
}

export interface Assessment {
  id: string
  tip_id: string
  level: 'Low' | 'Medium' | 'High'
  score: number
  reasons: string[]
  stock_symbols: string[]
  advisor_info?: any
  confidence?: number
  created_at: string
}

export interface RiskAssessmentResponse {
  level: 'Low' | 'Medium' | 'High'
  score: number
  reasons: string[]
  stock_symbols: string[]
  advisor?: {
    name: string
    verified: boolean
    registration_status: string
  } | null
  timestamp: string
  assessment_id: string
  confidence: number
}

export interface CheckTipResponse {
  tip_id: string
  assessment: RiskAssessmentResponse
}

export interface CheckTipRequest {
  message: string
  source?: string
  submitter_id?: string
}

export interface PDFCheck {
  id: string
  file_hash: string
  filename: string
  file_size?: number
  ocr_text?: string
  anomalies: any[]
  score?: number
  is_likely_fake?: boolean
  processing_time_ms?: number
  created_at: string
}

export interface PDFAnalysisResponse {
  id: string
  file_hash: string
  filename: string
  file_size: number
  ocr_text?: string
  anomalies: Array<{
    type: string
    description: string
    severity: 'low' | 'medium' | 'high'
    details?: any
  }>
  score: number // 0-100 authenticity score
  is_likely_fake: boolean
  processing_time_ms: number
  gemini_analysis?: any
  enhanced_validation?: {
    overall_authenticity_score: number
    is_likely_authentic: boolean
    validation_sources: string[]
    company_verification?: {
      companies_verified: Array<{
        symbol: string
        name: string
        sector: string
        market_cap: number
      }>
      companies_not_found: string[]
      market_data_flags: Array<{
        symbol: string
        flag_type: string
        news_count: number
        recent_news: any[]
      }>
      confidence: number
    }
    financial_data_consistency?: {
      verified_companies: number
      unverified_companies: number
      market_flags: number
    }
    news_correlation?: {
      relevant_articles: any[]
      contradictory_news: any[]
      supporting_news: any[]
      confidence: number
    }
    trend_analysis?: {
      trend_spikes: any[]
      fraud_correlations: any[]
      regional_patterns: any[]
      confidence: number
    }
    cross_source_flags: string[]
    cross_source_confirmations: string[]
    ai_content_analysis?: {
      authenticity_score: number
      confidence: number
      entity_consistency: {
        companies_legitimate: boolean
        financial_figures_realistic: boolean
        regulatory_language_accurate: boolean
      }
      red_flags: string[]
      supporting_evidence: string[]
      cross_reference_issues: string[]
      recommendations: string[]
    }
    validation_confidence: number
    recommendations: string[]
    processing_time_ms: number
    sources_checked: Record<string, boolean>
  }
  created_at: string
}

export interface AdvisorInfo {
  id: string
  name: string
  registration_number: string
  status: 'active' | 'suspended' | 'cancelled'
  registration_date: string
  validity_date: string
  category: string
  contact_info?: {
    email?: string
    phone?: string
    address?: string
  }
  compliance_score?: number
  match_score: number
}

export interface AdvisorVerificationResponse {
  success: boolean
  query: string
  total_matches: number
  advisors: AdvisorInfo[]
  message?: string
  cache_info?: any
}

// API functions
export const tipApi = {
  create: (data: { message: string; source?: string; submitter_id?: string }) =>
    api.post<Tip>('/tips', data),
  
  getById: (id: string) =>
    api.get<Tip>(`/tips/${id}`),
  
  getAll: (skip = 0, limit = 100) =>
    api.get<Tip[]>('/tips', { params: { skip, limit } }),
  
  delete: (id: string) =>
    api.delete(`/tips/${id}`),

  // Combined tip analysis endpoint
  checkTip: (data: CheckTipRequest) =>
    api.post<CheckTipResponse>('/check-tip', data),
}

export const assessmentApi = {
  create: (data: {
    tip_id: string
    level: string
    score: number
    reasons: string[]
    stock_symbols?: string[]
    advisor_info?: any
    gemini_raw?: any
    confidence?: number
  }) => api.post<Assessment>('/assessments', data),
  
  getById: (id: string) =>
    api.get<Assessment>(`/assessments/${id}`),
  
  getAll: (skip = 0, limit = 100) =>
    api.get<Assessment[]>('/assessments', { params: { skip, limit } }),
  
  getByTip: (tipId: string) =>
    api.get<Assessment[]>(`/tips/${tipId}/assessments`),
}

export const pdfCheckApi = {
  create: (data: {
    file_hash: string
    filename: string
    file_size?: number
    ocr_text?: string
    anomalies?: any[]
    score?: number
    is_likely_fake?: boolean
    processing_time_ms?: number
  }) => api.post<PDFCheck>('/pdf-checks', data),
  
  getById: (id: string) =>
    api.get<PDFCheck>(`/pdf-checks/${id}`),
  
  getAll: (skip = 0, limit = 100) =>
    api.get<PDFCheck[]>('/pdf-checks', { params: { skip, limit } }),
  
  getByHash: (hash: string) =>
    api.get<PDFCheck>(`/pdf-checks/hash/${hash}`),

  // PDF analysis endpoint
  analyzePDF: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    
    return api.post<PDFAnalysisResponse>('/check-pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 60 seconds for PDF processing
    })
  },
}

export const advisorApi = {
  verifyAdvisor: (params: {
    query: string
    limit?: number
    min_score?: number
    include_cache_info?: boolean
  }) => api.get<AdvisorVerificationResponse>('/verify-advisor', { params }),
  
  getById: (advisorId: string) =>
    api.get<AdvisorInfo>(`/advisor/${advisorId}`),
  
  getByRegistrationNumber: (regNumber: string) =>
    api.get<AdvisorInfo>(`/advisor/registration/${regNumber}`),
  
  getCacheStats: () =>
    api.get('/advisor-cache-stats'),
}

// Heatmap API types and functions
export interface HeatmapBucket {
  dimension: string
  key: string
  from_date: string
  to_date: string
  total_count: number
  high_risk_count: number
  medium_risk_count: number
  low_risk_count: number
  risk_score: number
  last_updated: string
}

export interface HeatmapStats {
  total_cases: number
  high_risk_cases: number
  medium_risk_cases: number
  low_risk_cases: number
  average_risk_score: number
  trend_direction: 'up' | 'down' | 'stable'
}

export interface FraudHeatmapResponse {
  data: HeatmapBucket[]
  stats: HeatmapStats
  filters: {
    dimension: string
    period: string
    from_date?: string
    to_date?: string
  }
}

// Drill-down data types
export interface DrillDownCase {
  id: string
  tip_id: string
  message: string
  risk_level: 'Low' | 'Medium' | 'High'
  risk_score: number
  reasons: string[]
  stock_symbols: string[]
  confidence: number
  created_at: string
  source: string
}

export interface DrillDownResponse {
  dimension: string
  key: string
  date_range: {
    from_date: string
    to_date: string
  }
  statistics: {
    total_cases: number
    high_risk_cases: number
    medium_risk_cases: number
    low_risk_cases: number
    average_risk_score: number
  }
  cases: DrillDownCase[]
  has_more: boolean
}

export const heatmapApi = {
  getFraudHeatmap: (params: {
    dimension: 'sector' | 'region'
    period?: 'daily' | 'weekly' | 'monthly'
    from_date?: string
    to_date?: string
  }) => api.get<FraudHeatmapResponse>('/fraud-heatmap', { params }),
  
  getHeatmapKeys: (dimension: 'sector' | 'region') =>
    api.get<{ keys: string[] }>(`/heatmap-keys/${dimension}`),
  
  populateSampleData: () =>
    api.post<{ message: string; cases_generated: number; sector_buckets: number; region_buckets: number }>('/populate-sample-heatmap-data'),
  
  generateRealtimeData: () =>
    api.post<{ message: string; cases_generated: number; timestamp: string }>('/generate-realtime-data'),
  
  getDrillDownData: (params: {
    dimension: 'sector' | 'region'
    key: string
    from_date?: string
    to_date?: string
  }) => api.get<DrillDownResponse>(`/heatmap-drill-down/${params.dimension}/${params.key}`, { 
    params: { from_date: params.from_date, to_date: params.to_date } 
  }),
}

// Multi-Source Data Integration API types and functions
export interface DataIndicator {
  id: string
  sector?: string
  region?: string
  indicator_type: string
  source: 'fmp' | 'google_trends' | 'economic_times'
  relevance_score: number
  summary: string
  details: Record<string, any>
  active: boolean
  created_at: string
}

export interface MultiSourceOverlay {
  indicators: DataIndicator[]
  summary: {
    total_indicators: number
    high_relevance_count: number
    sources_active: string[]
    avg_relevance_score: number
  }
  last_updated: string
  sources_status: {
    fmp: 'active' | 'inactive'
    google_trends: 'active' | 'inactive'
    economic_times: 'active' | 'inactive'
  }
}

export interface CrossSourceCorrelation {
  correlation_type: string
  source_1: string
  source_2: string
  correlation_strength: number
  fraud_implication: string
  analysis_summary: string
  created_at: string
}

export interface ConsolidatedModalData {
  sector: string
  region: string
  risk_level: 'low' | 'medium' | 'high'
  average_relevance: number
  total_indicators: number
  sources_data: Record<string, Array<{
    id: string
    type: string
    relevance_score: number
    summary: string
    details: Record<string, any>
    created_at: string
  }>>
  last_updated: string
}

export interface DataSourceToggle {
  fmp_enabled: boolean
  google_trends_enabled: boolean
  economic_times_enabled: boolean
}

export const multiSourceApi = {
  // Get multi-source indicators for heatmap overlay
  getIndicators: (params?: {
    sector?: string
    region?: string
    source?: string
    min_relevance?: number
  }) => api.get<MultiSourceOverlay>('/data/indicators', { params }),
  
  // Refresh data from all sources
  refreshData: (sources: DataSourceToggle) =>
    api.post<{ message: string; sources_enabled: DataSourceToggle; timestamp: string }>('/data/refresh', sources),
  
  // FMP API endpoints
  getFMPMarketData: (symbols?: string) =>
    api.get<{ data: any[]; timestamp: string; source: string }>('/fmp/market-data', { 
      params: symbols ? { symbols } : undefined 
    }),
  
  getFMPStockAlerts: () =>
    api.get<{ alerts: any[]; total_alerts: number; timestamp: string }>('/fmp/stock-alerts'),
  
  // Google Trends API endpoints
  getFraudKeywordTrends: (params?: {
    regions?: string
    timeframe?: string
  }) => api.get<{ trends: any[]; total_trends: number; timeframe: string; timestamp: string }>('/trends/fraud-keywords', { params }),
  
  getRegionalSpikes: () =>
    api.get<{ spikes: any[]; total_spikes: number; timestamp: string }>('/trends/regional-spikes'),
  
  // Economic Times API endpoints
  getEconomicTimesNews: (categories?: string) =>
    api.get<{ articles: any[]; total_articles: number; timestamp: string }>('/economic-times/latest-news', {
      params: categories ? { categories } : undefined
    }),
  
  getRegulatoryUpdates: () =>
    api.get<{ updates: any[]; total_updates: number; timestamp: string }>('/economic-times/regulatory-updates'),
  
  // Cross-source correlations
  getCorrelations: (params?: {
    min_strength?: number
    limit?: number
  }) => api.get<CrossSourceCorrelation[]>('/data/correlations', { params }),
  
  // Consolidated modal data
  getConsolidatedModal: (sector: string, region: string) =>
    api.get<ConsolidatedModalData>(`/data/consolidated-modal/${sector}/${region}`),
}

// Forecast API types and functions
export interface ForecastItem {
  key: string
  risk_score: number
  confidence_interval: [number, number]
  rationale: string
  contributing_factors: Array<{
    factor: string
    weight: number
    explanation: string
  }>
  features: Record<string, any>
  created_at?: string
}

export interface ForecastResponse {
  dimension: 'sector' | 'region'
  period: string
  forecasts: ForecastItem[]
  accuracy_metrics: {
    overall_accuracy: number
    high_risk_precision: number
    medium_risk_precision: number
    low_risk_precision: number
    trend_accuracy: number
    confidence_calibration: number
  }
  generated_at: string
}

export interface ForecastAccuracyResponse {
  dimension: 'sector' | 'region'
  accuracy_metrics: {
    overall_accuracy: number
    high_risk_precision: number
    medium_risk_precision: number
    low_risk_precision: number
    trend_accuracy: number
    confidence_calibration: number
  }
}

export interface ForecastComparisonResponse {
  dimension: 'sector' | 'region'
  periods: string[]
  comparison_data: Record<string, ForecastItem[]>
}

export const forecastApi = {
  // Get AI-powered fraud risk forecasts
  getForecast: (params: {
    dimension: 'sector' | 'region'
    period?: string
    regenerate?: boolean
  }) => api.get<ForecastResponse>('/forecast', { params }),
  
  // Get historical forecast accuracy metrics
  getAccuracy: (dimension: 'sector' | 'region') =>
    api.get<ForecastAccuracyResponse>('/forecast/accuracy', { 
      params: { dimension } 
    }),
  
  // Compare forecasts across different time periods
  compareForecast: (params: {
    dimension: 'sector' | 'region'
    periods: string[]
  }) => api.get<ForecastComparisonResponse>('/forecast/compare', { 
    params: { 
      dimension: params.dimension,
      periods: params.periods 
    } 
  }),
}

// Fraud Chain API types and functions
export interface FraudChainNode {
  id: string
  node_type: 'tip' | 'assessment' | 'document' | 'stock' | 'complaint' | 'advisor'
  reference_id: string
  label?: string
  metadata: Record<string, any>
  position_x?: number
  position_y?: number
  created_at: string
}

export interface FraudChainEdge {
  id: string
  from_node_id: string
  to_node_id: string
  relationship_type: 'leads_to' | 'references' | 'mentions' | 'involves' | 'similar_pattern' | 'escalates_to'
  confidence: number
  metadata: Record<string, any>
  created_at: string
}

export interface FraudChain {
  id: string
  name?: string
  description?: string
  status: 'active' | 'closed' | 'investigating'
  created_at: string
  updated_at: string
  nodes: FraudChainNode[]
  edges: FraudChainEdge[]
}

export interface FraudChainListItem {
  id: string
  name?: string
  description?: string
  status: 'active' | 'closed' | 'investigating'
  node_count: number
  edge_count: number
  created_at: string
  updated_at: string
}

export interface FraudChainExportResponse {
  export_format: 'json' | 'csv'
  export_timestamp: string
  chain_data?: FraudChain
}

export interface AutoLinkResponse {
  message: string
  chains_created: number
  links_added: number
}

export const fraudChainApi = {
  // Get list of fraud chains
  getChains: (params?: {
    status?: string
    limit?: number
    offset?: number
  }) => api.get<FraudChainListItem[]>('/fraud-chains', { params }),
  
  // Get detailed fraud chain with nodes and edges
  getChain: (chainId: string) =>
    api.get<FraudChain>(`/fraud-chain/${chainId}`),
  
  // Export fraud chain data
  exportChain: (chainId: string, format: 'json' | 'csv' = 'json') =>
    api.post<FraudChainExportResponse | Blob>(`/fraud-chain/${chainId}/export`, {}, {
      params: { format },
      responseType: format === 'csv' ? 'blob' : 'json'
    }),
  
  // Auto-link related fraud cases
  autoLink: () =>
    api.post<AutoLinkResponse>('/fraud-chains/auto-link'),
}

// Review API types and functions
export interface Review {
  id: string
  case_id: string
  case_type: 'assessment' | 'pdf_check' | 'fraud_chain'
  reviewer_id: string
  ai_decision: Record<string, any>
  human_decision?: Record<string, any>
  decision: 'approve' | 'override' | 'needs_more_info' | 'needs_review'
  notes?: string
  ai_confidence?: number
  priority: 'low' | 'medium' | 'high'
  status: 'pending' | 'completed' | 'escalated'
  created_at: string
  updated_at: string
}

export interface QueueItem {
  review_id: string
  case_id: string
  case_type: 'assessment' | 'pdf_check' | 'fraud_chain'
  priority: 'low' | 'medium' | 'high'
  ai_confidence?: number
  ai_decision: Record<string, any>
  created_at: string
  case_details: {
    type: string
    assessment_id?: string
    pdf_check_id?: string
    tip_message?: string
    filename?: string
    risk_level?: string
    risk_score?: number
    authenticity_score?: number
    reasons?: string[]
    stock_symbols?: string[]
    anomalies?: any[]
    is_likely_fake?: boolean
    created_at: string
  }
}

export interface ReviewStatistics {
  total_reviews: number
  pending_reviews: number
  completed_reviews: number
  pending_by_priority: {
    high: number
    medium: number
    low: number
  }
  reviews_by_type: {
    assessments: number
    pdf_checks: number
  }
  ai_vs_human: {
    ai_approved: number
    human_overridden: number
    override_rate: number
  }
}

export interface ReviewDecision {
  decision: 'approve' | 'override' | 'needs_more_info'
  notes?: string
  human_decision?: Record<string, any>
}

export interface QueueLowConfidenceResponse {
  message: string
  assessments_queued: number
  pdf_checks_queued: number
  total_queued: number
}

export const reviewApi = {
  // Get review queue with case details
  getReviewQueue: (params?: {
    skip?: number
    limit?: number
    sort_by?: 'priority' | 'confidence' | 'date'
  }) => api.get<QueueItem[]>('/review-queue', { params }),
  
  // Create a new review
  createReview: (data: {
    case_id: string
    case_type: 'assessment' | 'pdf_check' | 'fraud_chain'
    reviewer_id: string
    ai_decision: Record<string, any>
    decision: string
    notes?: string
    human_decision?: Record<string, any>
    ai_confidence?: number
    priority?: 'low' | 'medium' | 'high'
  }) => api.post<Review>('/review', data),
  
  // Update review with human decision
  updateReviewDecision: (reviewId: string, decision: ReviewDecision) =>
    api.put<Review>(`/review/${reviewId}`, decision),
  
  // Get specific review
  getReview: (reviewId: string) =>
    api.get<Review>(`/review/${reviewId}`),
  
  // Get all reviews with filtering
  getReviews: (params?: {
    skip?: number
    limit?: number
    status?: 'pending' | 'completed' | 'escalated'
    case_type?: 'assessment' | 'pdf_check' | 'fraud_chain'
    priority?: 'low' | 'medium' | 'high'
  }) => api.get<Review[]>('/reviews', { params }),
  
  // Queue low confidence cases for review
  queueLowConfidenceCases: (params?: {
    confidence_threshold?: number
    authenticity_threshold?: number
  }) => api.post<QueueLowConfidenceResponse>('/queue-low-confidence', {}, { params }),
  
  // Get review statistics
  getStatistics: () =>
    api.get<ReviewStatistics>('/statistics'),
}

export default api