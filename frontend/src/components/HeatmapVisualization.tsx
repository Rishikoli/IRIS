import React, { useState, useEffect } from 'react'
import { HeatmapBucket, DataIndicator, multiSourceApi, DataSourceToggle } from '../services/api'
import { ResponsiveContainer, Treemap, Tooltip } from 'recharts'

interface HeatmapVisualizationProps {
  data: HeatmapBucket[]
  dimension: 'sector' | 'region'
  onCellClick?: (key: string) => void
  className?: string
}

interface DataSourceIndicator {
  source: 'fmp' | 'google_trends' | 'economic_times'
  count: number
  avgRelevance: number
  color: string
  icon: string
}



const HeatmapVisualization: React.FC<HeatmapVisualizationProps> = ({
  data,
  dimension,
  onCellClick,
  className = ''
}) => {
  // Multi-source data state
  const [indicators, setIndicators] = useState<DataIndicator[]>([])
  const [sourcesEnabled, setSourcesEnabled] = useState<DataSourceToggle>({
    fmp_enabled: true,
    google_trends_enabled: true,
    economic_times_enabled: true
  })
  const [showOverlays, setShowOverlays] = useState(true)
  const [loading, setLoading] = useState(false)

  // Fetch multi-source indicators
  useEffect(() => {
    const fetchIndicators = async () => {
      try {
        setLoading(true)
        const response = await multiSourceApi.getIndicators({
          min_relevance: 40
        })
        setIndicators(response.data.indicators)
      } catch (error) {
        console.error('Error fetching multi-source indicators:', error)
      } finally {
        setLoading(false)
      }
    }

    if (showOverlays) {
      fetchIndicators()
    }
  }, [showOverlays])

  // Handle source toggle
  const handleSourceToggle = async (source: keyof DataSourceToggle) => {
    const newSources = {
      ...sourcesEnabled,
      [source]: !sourcesEnabled[source]
    }
    setSourcesEnabled(newSources)
    
    try {
      await multiSourceApi.refreshData(newSources)
      // Refresh indicators after a short delay
      setTimeout(() => {
        if (showOverlays) {
          multiSourceApi.getIndicators({ min_relevance: 40 })
            .then(response => setIndicators(response.data.indicators))
            .catch(console.error)
        }
      }, 2000)
    } catch (error) {
      console.error('Error refreshing data sources:', error)
    }
  }

  // Get indicators for a specific cell
  const getCellIndicators = (key: string): DataSourceIndicator[] => {
    const cellIndicators = indicators.filter(indicator => 
      (dimension === 'sector' && indicator.sector === key) ||
      (dimension === 'region' && indicator.region === key)
    )

    const sourceGroups = cellIndicators.reduce((acc, indicator) => {
      if (!acc[indicator.source]) {
        acc[indicator.source] = []
      }
      acc[indicator.source].push(indicator)
      return acc
    }, {} as Record<string, DataIndicator[]>)

    const sourceColors = {
      fmp: '#3b82f6', // blue
      google_trends: '#ef4444', // red
      economic_times: '#10b981' // green
    }

    const sourceIcons = {
      fmp: '📈',
      google_trends: '🔍',
      economic_times: '📰'
    }

    return Object.entries(sourceGroups).map(([source, sourceIndicators]) => ({
      source: source as 'fmp' | 'google_trends' | 'economic_times',
      count: sourceIndicators.length,
      avgRelevance: sourceIndicators.reduce((sum, ind) => sum + ind.relevance_score, 0) / sourceIndicators.length,
      color: sourceColors[source as keyof typeof sourceColors],
      icon: sourceIcons[source as keyof typeof sourceIcons]
    }))
  }
  // Color scale based on risk score - defined first to avoid hoisting issues
  const getColorByRiskScore = (score: number) => {
    if (score >= 80) return '#dc2626' // red-600
    if (score >= 60) return '#ea580c' // orange-600
    if (score >= 40) return '#d97706' // amber-600
    if (score >= 20) return '#ca8a04' // yellow-600
    return '#16a34a' // green-600
  }

  // Group data by key and calculate average risk scores
  const groupedData = data.reduce((acc, item) => {
    if (!acc[item.key]) {
      acc[item.key] = {
        key: item.key,
        name: item.key,
        total_count: 0,
        high_risk_count: 0,
        medium_risk_count: 0,
        low_risk_count: 0,
        risk_scores: [],
        avg_risk_score: 0
      }
    }
    acc[item.key].total_count += item.total_count
    acc[item.key].high_risk_count += item.high_risk_count
    acc[item.key].medium_risk_count += item.medium_risk_count
    acc[item.key].low_risk_count += item.low_risk_count
    acc[item.key].risk_scores.push(item.risk_score)
    return acc
  }, {} as Record<string, any>)

  // Calculate average risk scores and prepare treemap data
  const heatmapData = Object.values(groupedData).map((group: any) => {
    const avgScore = group.risk_scores.length > 0 
      ? group.risk_scores.reduce((sum: number, score: number) => sum + score, 0) / group.risk_scores.length
      : 0
    
    return {
      ...group,
      avg_risk_score: avgScore,
      value: Math.max(group.total_count, 1), // Ensure minimum size for visibility
      fill: getColorByRiskScore(avgScore)
    }
  })

  // Custom tooltip component
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length && payload[0].payload) {
      const data = payload[0].payload
      return (
        <div className="bg-primary-900/30  p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-dark-primary">{data.name || data.key || 'Unknown'}</p>
          <p className="text-sm text-gray-600">Total Cases: {data.total_count || 0}</p>
          <p className="text-sm text-gray-600">Risk Score: {(data.avg_risk_score || 0).toFixed(1)}</p>
          <div className="mt-2 space-y-1">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-red-500 rounded"></div>
              <span className="text-xs">High Risk: {data.high_risk_count || 0}</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-yellow-500 rounded"></div>
              <span className="text-xs">Medium Risk: {data.medium_risk_count || 0}</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded"></div>
              <span className="text-xs">Low Risk: {data.low_risk_count || 0}</span>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-2">Click to drill down</p>
        </div>
      )
    }
    return null
  }

  // Custom content for treemap cells
  const CustomizedContent = (props: any) => {
    const { x, y, width, height, payload, name } = props
    
    // Safety checks for payload
    if (!payload) {
      return null
    }
    
    const fillColor = payload.fill || getColorByRiskScore(payload.avg_risk_score || 0)
    const riskScore = payload.avg_risk_score || 0
    const cellKey = payload.key || name
    
    return (
      <g>
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          style={{
            fill: fillColor,
            stroke: '#fff',
            strokeWidth: 2,
            cursor: 'pointer'
          }}
          onClick={() => onCellClick?.(cellKey)}
          className="hover:opacity-80 transition-opacity"
        />
        {width > 60 && height > 40 && (
          <>
            <text
              x={x + width / 2}
              y={y + height / 2 - 8}
              textAnchor="middle"
              fill={riskScore >= 40 ? '#fff' : '#000'}
              fontSize="12"
              fontWeight="600"
            >
              {name || cellKey}
            </text>
            <text
              x={x + width / 2}
              y={y + height / 2 + 8}
              textAnchor="middle"
              fill={riskScore >= 40 ? '#fff' : '#000'}
              fontSize="10"
            >
              {riskScore.toFixed(1)}
            </text>
          </>
        )}
      </g>
    )
  }

  return (
    <div className={`bg-white dark:bg-dark-secondary rounded-lg shadow-md p-6 border border-gray-200 dark:border-dark-border ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-dark-text">
          Fraud Risk Heatmap - {dimension === 'sector' ? 'By Sector' : 'By Region'}
        </h3>
        
        {/* Multi-Source Data Controls */}
        <div className="flex items-center space-x-4">
          {/* Data Source Toggles */}
          <div className="flex items-center space-x-2 text-sm">
            <span className="text-gray-600 dark:text-dark-muted">Data Sources:</span>
            <button
              onClick={() => handleSourceToggle('fmp_enabled')}
              className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                sourcesEnabled.fmp_enabled
                  ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400 border border-blue-200 dark:border-blue-700'
                  : 'bg-gray-100 dark:bg-dark-hover text-gray-500 dark:text-dark-muted border border-gray-200 dark:border-dark-border'
              }`}
              title="Financial Market Data"
            >
              📈 FMP
            </button>
            <button
              onClick={() => handleSourceToggle('google_trends_enabled')}
              className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                sourcesEnabled.google_trends_enabled
                  ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400 border border-red-200 dark:border-red-700'
                  : 'bg-gray-100 dark:bg-dark-hover text-gray-500 dark:text-dark-muted border border-gray-200 dark:border-dark-border'
              }`}
              title="Google Trends Data"
            >
              🔍 Trends
            </button>
            <button
              onClick={() => handleSourceToggle('economic_times_enabled')}
              className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                sourcesEnabled.economic_times_enabled
                  ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400 border border-green-200 dark:border-green-700'
                  : 'bg-gray-100 dark:bg-dark-hover text-gray-500 dark:text-dark-muted border border-gray-200 dark:border-dark-border'
              }`}
              title="Economic Times News"
            >
              📰 News
            </button>
          </div>

          {/* Overlay Toggle */}
          <button
            onClick={() => setShowOverlays(!showOverlays)}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              showOverlays
                ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-400 border border-purple-200 dark:border-purple-700'
                : 'bg-gray-100 dark:bg-dark-hover text-gray-600 dark:text-dark-muted border border-gray-200 dark:border-dark-border'
            }`}
          >
            {showOverlays ? '🔍 Hide Overlays' : '🔍 Show Overlays'}
          </button>
        </div>
      </div>

      {/* Risk Level Legend */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-4 text-sm">
          <span className="text-gray-600">Risk Level:</span>
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-1">
              <div className="w-4 h-4 bg-green-600 rounded"></div>
              <span>Low (0-20)</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-4 h-4 bg-yellow-600 rounded"></div>
              <span>Medium (20-60)</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-4 h-4 bg-red-600 rounded"></div>
              <span>High (60+)</span>
            </div>
          </div>
        </div>

        {/* Multi-Source Indicators Summary */}
        {showOverlays && (
          <div className="flex items-center space-x-2 text-xs text-gray-600">
            {loading ? (
              <span>Loading indicators...</span>
            ) : indicators.length > 0 ? (
              <>
                <span>Active Indicators:</span>
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                  📈 {indicators.filter(i => i.source === 'fmp').length}
                </span>
                <span className="bg-red-100 text-red-800 px-2 py-1 rounded">
                  🔍 {indicators.filter(i => i.source === 'google_trends').length}
                </span>
                <span className="bg-green-100 text-green-800 px-2 py-1 rounded">
                  📰 {indicators.filter(i => i.source === 'economic_times').length}
                </span>
              </>
            ) : (
              <span>No indicators available</span>
            )}
          </div>
        )}
      </div>

      {/* Debug Info */}
      <div className="mb-4 p-2 bg-gray-100 rounded text-xs text-gray-600">
        Debug: Raw data items: {data.length}, Processed items: {heatmapData.length}
        {heatmapData.length > 0 && (
          <div>Sample: {heatmapData[0].name} (Score: {heatmapData[0].avg_risk_score}, Cases: {heatmapData[0].total_count})</div>
        )}
      </div>

      {heatmapData.length === 0 ? (
        <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
          <div className="text-center">
            <div className="text-gray-400 mb-2">📊</div>
            <p className="text-gray-500">No heatmap data available</p>
            <p className="text-sm text-gray-400">Try adjusting your filters or time range</p>
            <p className="text-xs text-gray-400 mt-2">Raw data length: {data.length}</p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Enhanced Grid Heatmap with Multi-Source Overlays */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {heatmapData.map((item: any, index) => {
              const cellIndicators = showOverlays ? getCellIndicators(item.key) : []
              
              return (
                <div
                  key={item.key || index}
                  className="relative p-4 rounded-lg cursor-pointer hover:opacity-80 transition-opacity border-2 border-white"
                  style={{ backgroundColor: item.fill }}
                  onClick={() => onCellClick?.(item.key)}
                  title={`${item.name}: ${item.total_count} cases, Risk: ${item.avg_risk_score.toFixed(1)}`}
                >
                  {/* Multi-Source Indicators Overlay */}
                  {showOverlays && cellIndicators.length > 0 && (
                    <div className="absolute top-1 right-1 flex flex-wrap gap-1">
                      {cellIndicators.map((indicator, idx) => (
                        <div
                          key={idx}
                          className="w-4 h-4 rounded-full flex items-center justify-center text-xs font-bold text-white shadow-sm"
                          style={{ backgroundColor: indicator.color }}
                          title={`${indicator.source}: ${indicator.count} indicators (avg relevance: ${indicator.avgRelevance.toFixed(1)})`}
                        >
                          {indicator.count}
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="text-center">
                    <div 
                      className="font-semibold text-sm mb-1"
                      style={{ color: item.avg_risk_score >= 40 ? '#fff' : '#000' }}
                    >
                      {item.name}
                    </div>
                    <div 
                      className="text-xs"
                      style={{ color: item.avg_risk_score >= 40 ? '#fff' : '#000' }}
                    >
                      {item.avg_risk_score.toFixed(1)}
                    </div>
                    <div 
                      className="text-xs mt-1"
                      style={{ color: item.avg_risk_score >= 40 ? '#fff' : '#000' }}
                    >
                      {item.total_count} cases
                    </div>
                    
                    {/* Multi-Source Summary */}
                    {showOverlays && cellIndicators.length > 0 && (
                      <div 
                        className="text-xs mt-1 font-medium"
                        style={{ color: item.avg_risk_score >= 40 ? '#fff' : '#000' }}
                      >
                        +{cellIndicators.reduce((sum, ind) => sum + ind.count, 0)} alerts
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>

          {/* Recharts Treemap as backup */}
          <div className="h-96 w-full border border-gray-200 rounded-lg">
            <ResponsiveContainer width="100%" height="100%">
              <Treemap
                data={heatmapData}
                dataKey="value"
                aspectRatio={4/3}
                stroke="#fff"
                content={<CustomizedContent />}
              >
                <Tooltip content={<CustomTooltip />} />
              </Treemap>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Summary Stats */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
        <div className="text-center">
          <div className="text-2xl font-bold text-dark-primary">
            {heatmapData.reduce((sum: number, item: any) => sum + item.total_count, 0)}
          </div>
          <div className="text-sm text-gray-600">Total Cases</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-red-600">
            {heatmapData.filter((item: any) => item.avg_risk_score >= 70).length}
          </div>
          <div className="text-sm text-gray-600">High Risk Areas</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-yellow-600">
            {heatmapData.filter((item: any) => item.avg_risk_score >= 40 && item.avg_risk_score < 70).length}
          </div>
          <div className="text-sm text-gray-600">Medium Risk Areas</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">
            {heatmapData.length > 0 
              ? (heatmapData.reduce((sum: number, item: any) => sum + item.avg_risk_score, 0) / heatmapData.length).toFixed(1)
              : '0.0'
            }
          </div>
          <div className="text-sm text-gray-600">Avg Risk Score</div>
        </div>
      </div>

      {/* Interactive Instructions */}
      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
        <p className="text-sm text-blue-800">
          💡 <strong>Interactive Features:</strong> Hover over cells for details, click to drill down into specific {dimension} data
        </p>
      </div>
    </div>
  )
}

export default HeatmapVisualization