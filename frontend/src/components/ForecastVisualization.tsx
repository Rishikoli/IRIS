import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ErrorBar, Cell } from 'recharts'
import { ForecastItem } from '../services/api'

interface ForecastVisualizationProps {
  forecasts: ForecastItem[]
  dimension: 'sector' | 'region'
  showConfidenceIntervals?: boolean
  onItemClick?: (key: string) => void
}

const ForecastVisualization: React.FC<ForecastVisualizationProps> = ({
  forecasts,
  dimension,
  showConfidenceIntervals = true,
  onItemClick
}) => {
  // Transform data for chart
  const chartData = forecasts.map(forecast => ({
    key: forecast.key,
    risk_score: forecast.risk_score,
    confidence_min: forecast.confidence_interval[0],
    confidence_max: forecast.confidence_interval[1],
    error_low: forecast.risk_score - forecast.confidence_interval[0],
    error_high: forecast.confidence_interval[1] - forecast.risk_score,
    rationale: forecast.rationale
  }))

  // Color function based on risk score
  const getRiskColor = (score: number) => {
    if (score >= 70) return '#ef4444' // red-500
    if (score >= 40) return '#f59e0b' // amber-500
    return '#10b981' // emerald-500
  }

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-primary-900/30  p-4 border border-gray-200 rounded-lg shadow-lg max-w-xs">
          <p className="font-semibold text-dark-primary mb-2">{label}</p>
          <p className="text-sm text-gray-700 mb-1">
            Risk Score: <span className="font-medium">{data.risk_score}/100</span>
          </p>
          {showConfidenceIntervals && (
            <p className="text-sm text-gray-700 mb-2">
              Confidence: {data.confidence_min}-{data.confidence_max}
            </p>
          )}
          <p className="text-xs text-gray-600 italic">
            {data.rationale}
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="bg-primary-900/30  rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-dark-primary">
          Risk Forecast by {dimension === 'sector' ? 'Sector' : 'Region'}
        </h3>
        <div className="flex items-center space-x-4 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-red-500 rounded"></div>
            <span className="text-gray-600">High Risk (70+)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-amber-500 rounded"></div>
            <span className="text-gray-600">Medium Risk (40-69)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-emerald-500 rounded"></div>
            <span className="text-gray-600">Low Risk (0-39)</span>
          </div>
        </div>
      </div>

      {forecasts.length === 0 ? (
        <div className="h-64 flex items-center justify-center text-gray-500">
          <div className="text-center">
            <div className="text-4xl mb-2">🔮</div>
            <p>No forecast data available</p>
            <p className="text-sm">Generate forecasts to see predictions</p>
          </div>
        </div>
      ) : (
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="key" 
                angle={-45}
                textAnchor="end"
                height={80}
                interval={0}
                fontSize={12}
              />
              <YAxis 
                domain={[0, 100]}
                label={{ value: 'Risk Score', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar 
                dataKey="risk_score" 
                cursor="pointer"
                onClick={(data) => data?.key && onItemClick?.(String(data.key))}
              >
                {showConfidenceIntervals && (
                  <ErrorBar 
                    dataKey="error_low" 
                    width={4}
                    stroke="#666"
                  />
                )}
                {chartData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={getRiskColor(entry.risk_score)} 
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {forecasts.length > 0 && (
        <div className="mt-4 text-xs text-gray-500 text-center">
          Click on bars to view detailed forecast rationale and contributing factors
        </div>
      )}
    </div>
  )
}

export default ForecastVisualization