import React, { useState, useEffect } from 'react'
import { multiSourceApi, ConsolidatedModalData } from '../services/api'

interface ConsolidatedDataModalProps {
  isOpen: boolean
  onClose: () => void
  sector: string
  region: string
}

const ConsolidatedDataModal: React.FC<ConsolidatedDataModalProps> = ({
  isOpen,
  onClose,
  sector,
  region
}) => {
  const [data, setData] = useState<ConsolidatedModalData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<string>('overview')

  useEffect(() => {
    if (isOpen && sector && region) {
      fetchConsolidatedData()
    }
  }, [isOpen, sector, region])

  const fetchConsolidatedData = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await multiSourceApi.getConsolidatedModal(sector, region)
      setData(response.data)
    } catch (err) {
      setError('Failed to fetch consolidated data')
      console.error('Error fetching consolidated data:', err)
    } finally {
      setLoading(false)
    }
  }

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'high': return 'text-danger-200 bg-danger-900'
      case 'medium': return 'text-warning-200 bg-warning-900'
      case 'low': return 'text-success-200 bg-success-900'
      default: return 'text-dark-secondary bg-dark-700'
    }
  }

  const getSourceIcon = (source: string) => {
    switch (source) {
      case 'fmp': return '📈'
      case 'google_trends': return '🔍'
      case 'economic_times': return '📰'
      default: return '📊'
    }
  }

  const getSourceName = (source: string) => {
    switch (source) {
      case 'fmp': return 'Financial Market Data'
      case 'google_trends': return 'Google Trends'
      case 'economic_times': return 'Economic Times'
      default: return source
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-dark-secondary rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden border border-gray-200 dark:border-dark-border">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-dark-border">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-dark-text">
              Multi-Source Analysis: {sector} - {region}
            </h2>
            {data && (
              <div className="flex items-center space-x-4 mt-2">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskLevelColor(data.risk_level)}`}>
                  {data.risk_level.toUpperCase()} RISK
                </span>
                <span className="text-sm text-gray-600 dark:text-dark-muted">
                  Relevance Score: {data.average_relevance}/100
                </span>
                <span className="text-sm text-gray-600 dark:text-dark-muted">
                  {data.total_indicators} indicators
                </span>
              </div>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 dark:text-dark-muted hover:text-gray-600 dark:hover:text-dark-text transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="text-danger-500 text-xl mb-2">⚠️</div>
                <p className="text-dark-secondary">{error}</p>
                <button
                  onClick={fetchConsolidatedData}
                  className="mt-4 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors"
                >
                  Retry
                </button>
              </div>
            </div>
          ) : data ? (
            <div className="p-6">
              {/* Tabs */}
              <div className="flex space-x-1 mb-6 bg-dark-800 p-1 rounded-lg border border-dark-primary">
                <button
                  onClick={() => setActiveTab('overview')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeTab === 'overview'
                      ? 'bg-primary-600 text-white shadow-lg'
                      : 'text-dark-secondary hover:text-dark-primary hover:bg-dark-700'
                  }`}
                >
                  Overview
                </button>
                {Object.keys(data.sources_data).map(source => (
                  <button
                    key={source}
                    onClick={() => setActiveTab(source)}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                      activeTab === source
                        ? 'bg-primary-600 text-white shadow-lg'
                        : 'text-dark-secondary hover:text-dark-primary hover:bg-dark-700'
                    }`}
                  >
                    {getSourceIcon(source)} {getSourceName(source)}
                    <span className="ml-2 bg-dark-600 text-dark-primary px-2 py-0.5 rounded-full text-xs">
                      {data.sources_data[source]?.length || 0}
                    </span>
                  </button>
                ))}
              </div>

              {/* Tab Content */}
              {activeTab === 'overview' ? (
                <div className="space-y-6">
                  {/* Summary Stats */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-dark-primary">{data.total_indicators}</div>
                      <div className="text-sm text-gray-600">Total Indicators</div>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-dark-primary">{data.average_relevance.toFixed(1)}</div>
                      <div className="text-sm text-gray-600">Avg Relevance Score</div>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-dark-primary">{Object.keys(data.sources_data).length}</div>
                      <div className="text-sm text-gray-600">Active Sources</div>
                    </div>
                  </div>

                  {/* Sources Summary */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-dark-primary">Data Sources Summary</h3>
                    {Object.entries(data.sources_data).map(([source, indicators]) => {
                      const avgRelevance = indicators.length > 0 
                        ? indicators.reduce((sum, ind) => sum + ind.relevance_score, 0) / indicators.length
                        : 0
                      
                      return (
                        <div key={source} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center space-x-2">
                              <span className="text-xl">{getSourceIcon(source)}</span>
                              <span className="font-medium text-dark-primary">{getSourceName(source)}</span>
                            </div>
                            <div className="flex items-center space-x-4 text-sm text-gray-600">
                              <span>{indicators.length} indicators</span>
                              <span>Avg: {avgRelevance.toFixed(1)}/100</span>
                            </div>
                          </div>
                          
                          {/* Top indicators preview */}
                          <div className="space-y-2">
                            {indicators.slice(0, 2).map((indicator, idx) => (
                              <div key={idx} className="text-sm text-gray-700 bg-gray-50 p-2 rounded">
                                <div className="font-medium">{indicator.summary}</div>
                                <div className="text-xs text-gray-500 mt-1">
                                  Relevance: {indicator.relevance_score}/100 • {indicator.type}
                                </div>
                              </div>
                            ))}
                            {indicators.length > 2 && (
                              <div className="text-sm text-blue-600 cursor-pointer hover:text-blue-800"
                                   onClick={() => setActiveTab(source)}>
                                View {indicators.length - 2} more indicators →
                              </div>
                            )}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              ) : (
                /* Source-specific tab content */
                <div className="space-y-4">
                  <div className="flex items-center space-x-2 mb-4">
                    <span className="text-2xl">{getSourceIcon(activeTab)}</span>
                    <h3 className="text-lg font-semibold text-dark-primary">{getSourceName(activeTab)}</h3>
                    <span className="bg-gray-200 text-gray-700 px-2 py-1 rounded-full text-sm">
                      {data.sources_data[activeTab]?.length || 0} indicators
                    </span>
                  </div>

                  {data.sources_data[activeTab]?.length > 0 ? (
                    <div className="space-y-3">
                      {data.sources_data[activeTab].map((indicator, idx) => (
                        <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex-1">
                              <div className="font-medium text-dark-primary mb-1">{indicator.summary}</div>
                              <div className="text-sm text-gray-600">
                                Type: {indicator.type} • Relevance: {indicator.relevance_score}/100
                              </div>
                            </div>
                            <div className="text-xs text-gray-500">
                              {new Date(indicator.created_at).toLocaleString()}
                            </div>
                          </div>
                          
                          {/* Indicator details */}
                          {indicator.details && Object.keys(indicator.details).length > 0 && (
                            <div className="mt-3 p-3 bg-gray-50 rounded text-sm">
                              <div className="font-medium text-gray-700 mb-2">Details:</div>
                              <div className="space-y-1">
                                {Object.entries(indicator.details).slice(0, 3).map(([key, value]) => (
                                  <div key={key} className="flex justify-between">
                                    <span className="text-gray-600 capitalize">{key.replace(/_/g, ' ')}:</span>
                                    <span className="text-dark-primary font-medium">
                                      {typeof value === 'string' ? value.slice(0, 50) + (value.length > 50 ? '...' : '') : String(value)}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      No indicators available from this source
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : null}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 px-6 py-4 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              {data && `Last updated: ${new Date(data.last_updated).toLocaleString()}`}
            </div>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ConsolidatedDataModal