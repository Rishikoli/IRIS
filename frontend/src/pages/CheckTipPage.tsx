import { useState } from 'react'
import TipAnalysisForm from '../components/TipAnalysisForm'
import RiskBadge from '../components/RiskBadge'
import { tipApi, CheckTipResponse } from '../services/api'

const CheckTipPage = () => {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<CheckTipResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleAnalyzeTip = async (message: string) => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await tipApi.checkTip({
        message,
        source: 'web_interface'
      })
      
      setResult(response.data)
    } catch (err: any) {
      console.error('Error analyzing tip:', err)
      setError(
        err.response?.data?.detail || 
        'Failed to analyze the tip. Please try again later.'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleNewAnalysis = () => {
    setResult(null)
    setError(null)
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="bg-primary-900/30  rounded-lg shadow-md p-8">
        <h1 className="text-3xl font-bold text-dark-primary mb-4">
          Tip Risk Analysis
        </h1>
        <p className="text-dark-primary">
          Paste a suspicious investment tip below to get an AI-powered risk assessment. 
          Our system analyzes the message for fraud indicators, unrealistic promises, and other red flags.
        </p>
        
        {/* How it works */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-blue-900 mb-2">How it works:</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• AI analyzes the message for fraud patterns and risk indicators</li>
            <li>• Detects stock symbols and advisor mentions</li>
            <li>• Provides risk score (0-100) and detailed explanations</li>
            <li>• Offers actionable recommendations based on risk level</li>
          </ul>
        </div>
      </div>

      {/* Analysis Form */}
      {!result && (
        <TipAnalysisForm onSubmit={handleAnalyzeTip} loading={loading} />
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center space-x-3">
            <svg className="w-6 h-6 text-red-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div>
              <h3 className="text-lg font-semibold text-red-900">Analysis Failed</h3>
              <p className="text-red-700">{error}</p>
            </div>
          </div>
          <button
            onClick={handleNewAnalysis}
            className="mt-4 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      )}

      {/* Results Display */}
      {result && (
        <div className="space-y-6">
          {/* Risk Assessment */}
          <RiskBadge
            level={result.assessment.level}
            score={result.assessment.score}
            reasons={result.assessment.reasons}
          />

          {/* Additional Information */}
          <div className="bg-primary-900/30  rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-dark-primary mb-4">
              Analysis Details
            </h2>
            
            <div className="grid md:grid-cols-2 gap-6">
              {/* Stock Symbols */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">
                  Stock Symbols Detected
                </h3>
                {result.assessment.stock_symbols.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {result.assessment.stock_symbols.map((symbol, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                      >
                        {symbol}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No stock symbols detected</p>
                )}
              </div>

              {/* Advisor Information */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">
                  Advisor Mentioned
                </h3>
                {result.assessment.advisor ? (
                  <div className="text-sm">
                    <p className="font-medium">{result.assessment.advisor.name}</p>
                    <p className="text-gray-600">
                      Status: {result.assessment.advisor.registration_status}
                    </p>
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No advisor mentioned</p>
                )}
              </div>
            </div>

            {/* Analysis Metadata */}
            <div className="mt-6 pt-4 border-t border-gray-200">
              <div className="flex justify-between items-center text-sm text-gray-500">
                <span>
                  Analysis ID: {result.assessment.assessment_id}
                </span>
                <span>
                  Confidence: {Math.round(result.assessment.confidence * 100)}%
                </span>
                <span>
                  Analyzed: {new Date(result.assessment.timestamp).toLocaleString()}
                </span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4">
            <button
              onClick={handleNewAnalysis}
              className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors"
            >
              Analyze Another Tip
            </button>
            <button
              onClick={() => window.print()}
              className="bg-gray-600 text-white px-6 py-2 rounded-md hover:bg-gray-700 transition-colors"
            >
              Print Results
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default CheckTipPage