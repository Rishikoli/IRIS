import React from 'react'
import { HeatmapStats } from '../services/api'

interface TrendIndicatorsProps {
  stats: HeatmapStats
  className?: string
}

const TrendIndicators: React.FC<TrendIndicatorsProps> = ({ stats, className = '' }) => {
  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case 'up':
        return '📈'
      case 'down':
        return '📉'
      case 'stable':
      default:
        return '➡️'
    }
  }

  const getTrendColor = (direction: string) => {
    switch (direction) {
      case 'up':
        return 'text-red-600'
      case 'down':
        return 'text-green-600'
      case 'stable':
      default:
        return 'text-blue-600'
    }
  }

  const getTrendText = (direction: string) => {
    switch (direction) {
      case 'up':
        return 'Increasing Risk'
      case 'down':
        return 'Decreasing Risk'
      case 'stable':
      default:
        return 'Stable Risk'
    }
  }

  const getRiskLevelColor = (score: number) => {
    if (score >= 70) return 'text-red-600'
    if (score >= 40) return 'text-yellow-600'
    return 'text-green-600'
  }

  const getRiskLevelText = (score: number) => {
    if (score >= 70) return 'High Risk'
    if (score >= 40) return 'Medium Risk'
    return 'Low Risk'
  }

  return (
    <div className={`bg-primary-900/30  rounded-lg shadow-md p-6 ${className}`}>
      <h3 className="text-xl font-semibold text-dark-primary mb-6">Fraud Activity Statistics</h3>
      
      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
        <div className="text-center">
          <div className="text-3xl font-bold text-dark-primary mb-1">
            {stats.total_cases.toLocaleString()}
          </div>
          <div className="text-sm text-gray-600">Total Cases</div>
        </div>
        
        <div className="text-center">
          <div className="text-3xl font-bold text-red-600 mb-1">
            {stats.high_risk_cases.toLocaleString()}
          </div>
          <div className="text-sm text-gray-600">High Risk</div>
          <div className="text-xs text-gray-500 mt-1">
            {stats.total_cases > 0 ? ((stats.high_risk_cases / stats.total_cases) * 100).toFixed(1) : 0}%
          </div>
        </div>
        
        <div className="text-center">
          <div className="text-3xl font-bold text-yellow-600 mb-1">
            {stats.medium_risk_cases.toLocaleString()}
          </div>
          <div className="text-sm text-gray-600">Medium Risk</div>
          <div className="text-xs text-gray-500 mt-1">
            {stats.total_cases > 0 ? ((stats.medium_risk_cases / stats.total_cases) * 100).toFixed(1) : 0}%
          </div>
        </div>
        
        <div className="text-center">
          <div className="text-3xl font-bold text-green-600 mb-1">
            {stats.low_risk_cases.toLocaleString()}
          </div>
          <div className="text-sm text-gray-600">Low Risk</div>
          <div className="text-xs text-gray-500 mt-1">
            {stats.total_cases > 0 ? ((stats.low_risk_cases / stats.total_cases) * 100).toFixed(1) : 0}%
          </div>
        </div>
      </div>

      {/* Risk Level and Trend */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6 border-t border-gray-200">
        <div className="flex items-center justify-center p-4 bg-gray-50 rounded-lg">
          <div className="text-center">
            <div className={`text-2xl font-bold mb-2 ${getRiskLevelColor(stats.average_risk_score)}`}>
              {stats.average_risk_score.toFixed(1)}
            </div>
            <div className="text-sm text-gray-600 mb-1">Average Risk Score</div>
            <div className={`text-xs font-medium ${getRiskLevelColor(stats.average_risk_score)}`}>
              {getRiskLevelText(stats.average_risk_score)}
            </div>
          </div>
        </div>
        
        <div className="flex items-center justify-center p-4 bg-gray-50 rounded-lg">
          <div className="text-center">
            <div className="text-2xl mb-2">
              {getTrendIcon(stats.trend_direction)}
            </div>
            <div className="text-sm text-gray-600 mb-1">Risk Trend</div>
            <div className={`text-xs font-medium ${getTrendColor(stats.trend_direction)}`}>
              {getTrendText(stats.trend_direction)}
            </div>
          </div>
        </div>
      </div>

      {/* Risk Distribution Bar */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Risk Distribution</span>
          <span className="text-xs text-gray-500">{stats.total_cases} total cases</span>
        </div>
        
        {stats.total_cases > 0 ? (
          <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
            <div className="h-full flex">
              <div 
                className="bg-red-500 h-full"
                style={{ width: `${(stats.high_risk_cases / stats.total_cases) * 100}%` }}
                title={`High Risk: ${stats.high_risk_cases} cases`}
              ></div>
              <div 
                className="bg-yellow-500 h-full"
                style={{ width: `${(stats.medium_risk_cases / stats.total_cases) * 100}%` }}
                title={`Medium Risk: ${stats.medium_risk_cases} cases`}
              ></div>
              <div 
                className="bg-green-500 h-full"
                style={{ width: `${(stats.low_risk_cases / stats.total_cases) * 100}%` }}
                title={`Low Risk: ${stats.low_risk_cases} cases`}
              ></div>
            </div>
          </div>
        ) : (
          <div className="w-full bg-gray-200 rounded-full h-4">
            <div className="bg-gray-300 h-full rounded-full flex items-center justify-center">
              <span className="text-xs text-gray-500">No data</span>
            </div>
          </div>
        )}
        
        <div className="flex justify-between text-xs text-gray-500 mt-2">
          <span>High ({((stats.high_risk_cases / Math.max(stats.total_cases, 1)) * 100).toFixed(1)}%)</span>
          <span>Medium ({((stats.medium_risk_cases / Math.max(stats.total_cases, 1)) * 100).toFixed(1)}%)</span>
          <span>Low ({((stats.low_risk_cases / Math.max(stats.total_cases, 1)) * 100).toFixed(1)}%)</span>
        </div>
      </div>
    </div>
  )
}

export default TrendIndicators