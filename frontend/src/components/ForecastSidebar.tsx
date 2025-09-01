import React from 'react'
import { ForecastItem } from '../services/api'

interface ForecastSidebarProps {
  selectedForecast: ForecastItem | null
  accuracyMetrics: {
    overall_accuracy: number
    high_risk_precision: number
    medium_risk_precision: number
    low_risk_precision: number
    trend_accuracy: number
    confidence_calibration: number
  }
  onClose?: () => void
}

const ForecastSidebar: React.FC<ForecastSidebarProps> = ({
  selectedForecast,
  accuracyMetrics,
  onClose
}) => {
  const getRiskLevelColor = (score: number) => {
    if (score >= 70) return 'text-red-600 bg-red-50'
    if (score >= 40) return 'text-amber-600 bg-amber-50'
    return 'text-emerald-600 bg-emerald-50'
  }

  const getRiskLevel = (score: number) => {
    if (score >= 70) return 'High Risk'
    if (score >= 40) return 'Medium Risk'
    return 'Low Risk'
  }

  return (
    <div className="bg-primary-900/30  rounded-lg shadow-md p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-dark-primary">
          Forecast Analysis
        </h3>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Selected Forecast Details */}
      {selectedForecast ? (
        <div className="space-y-4">
          {/* Risk Score */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-dark-primary">{selectedForecast.key}</h4>
              <span className={`px-2 py-1 text-sm font-medium rounded-full ${getRiskLevelColor(selectedForecast.risk_score)}`}>
                {getRiskLevel(selectedForecast.risk_score)}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-2xl font-bold text-dark-primary">
                {selectedForecast.risk_score}
              </span>
              <span className="text-gray-500">/100</span>
            </div>
            <div className="text-sm text-gray-600 mt-1">
              Confidence: {selectedForecast.confidence_interval[0]}-{selectedForecast.confidence_interval[1]}
            </div>
          </div>

          {/* AI Rationale */}
          <div>
            <h4 className="font-medium text-dark-primary mb-2">AI Rationale</h4>
            <p className="text-sm text-gray-700 bg-blue-50 p-3 rounded-lg">
              {selectedForecast.rationale}
            </p>
          </div>

          {/* Contributing Factors */}
          <div>
            <h4 className="font-medium text-dark-primary mb-3">Contributing Factors</h4>
            <div className="space-y-3">
              {selectedForecast.contributing_factors.map((factor, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-dark-primary text-sm">
                      {factor.factor}
                    </span>
                    <span className="text-xs text-gray-500">
                      Weight: {Math.round(factor.weight * 100)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${factor.weight * 100}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-600">
                    {factor.explanation}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Technical Features */}
          {selectedForecast.features && Object.keys(selectedForecast.features).length > 0 && (
            <div>
              <h4 className="font-medium text-dark-primary mb-2">Technical Features</h4>
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {Object.entries(selectedForecast.features).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className="text-gray-600 capitalize">
                        {key.replace(/_/g, ' ')}:
                      </span>
                      <span className="font-medium text-dark-primary">
                        {typeof value === 'number' ? value.toFixed(3) : String(value)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center text-gray-500 py-8">
          <div className="text-4xl mb-2">🎯</div>
          <p className="text-sm">Select a forecast item to view detailed analysis</p>
        </div>
      )}

      {/* Model Accuracy Metrics */}
      <div className="border-t border-gray-200 pt-6">
        <h4 className="font-medium text-dark-primary mb-3">Model Performance</h4>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Overall Accuracy</span>
            <div className="flex items-center space-x-2">
              <div className="w-16 bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full"
                  style={{ width: `${accuracyMetrics.overall_accuracy}%` }}
                ></div>
              </div>
              <span className="text-sm font-medium text-dark-primary">
                {accuracyMetrics.overall_accuracy.toFixed(1)}%
              </span>
            </div>
          </div>

          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">High Risk Precision</span>
            <div className="flex items-center space-x-2">
              <div className="w-16 bg-gray-200 rounded-full h-2">
                <div
                  className="bg-red-500 h-2 rounded-full"
                  style={{ width: `${accuracyMetrics.high_risk_precision}%` }}
                ></div>
              </div>
              <span className="text-sm font-medium text-dark-primary">
                {accuracyMetrics.high_risk_precision.toFixed(1)}%
              </span>
            </div>
          </div>

          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Trend Accuracy</span>
            <div className="flex items-center space-x-2">
              <div className="w-16 bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full"
                  style={{ width: `${accuracyMetrics.trend_accuracy}%` }}
                ></div>
              </div>
              <span className="text-sm font-medium text-dark-primary">
                {accuracyMetrics.trend_accuracy.toFixed(1)}%
              </span>
            </div>
          </div>

          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Confidence Calibration</span>
            <div className="flex items-center space-x-2">
              <div className="w-16 bg-gray-200 rounded-full h-2">
                <div
                  className="bg-purple-500 h-2 rounded-full"
                  style={{ width: `${accuracyMetrics.confidence_calibration}%` }}
                ></div>
              </div>
              <span className="text-sm font-medium text-dark-primary">
                {accuracyMetrics.confidence_calibration.toFixed(1)}%
              </span>
            </div>
          </div>
        </div>

        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
          <p className="text-xs text-blue-800">
            <strong>Note:</strong> Accuracy metrics are based on historical forecast performance 
            compared to actual fraud patterns observed.
          </p>
        </div>
      </div>
    </div>
  )
}

export default ForecastSidebar