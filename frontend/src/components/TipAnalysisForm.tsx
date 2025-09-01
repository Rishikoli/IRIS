import React, { useState } from 'react'

interface TipAnalysisFormProps {
  onSubmit: (message: string) => Promise<void>
  loading: boolean
}

const TipAnalysisForm: React.FC<TipAnalysisFormProps> = ({ onSubmit, loading }) => {
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validation
    if (!message.trim()) {
      setError('Please enter a message to analyze')
      return
    }

    if (message.trim().length < 10) {
      setError('Message must be at least 10 characters long')
      return
    }

    if (message.trim().length > 5000) {
      setError('Message must be less than 5000 characters')
      return
    }

    setError('')
    
    try {
      await onSubmit(message.trim())
    } catch (err) {
      setError('Failed to analyze message. Please try again.')
    }
  }

  const handleClear = () => {
    setMessage('')
    setError('')
  }

  const sampleTips = [
    "🚀 URGENT: Buy XYZ stock NOW! Guaranteed 500% returns in 1 week! Limited time offer - act fast before it's too late!",
    "ABC company quarterly results look promising. Stock might see some upward movement based on fundamentals.",
    "Secret insider tip: DEF stock will double tomorrow! My advisor friend confirmed this. Don't miss out!"
  ]

  const handleSampleClick = (sample: string) => {
    setMessage(sample)
    setError('')
  }

  return (
    <div className="bg-primary-900/30  rounded-lg shadow-md p-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="tip-message" className="block text-sm font-medium text-gray-700 mb-2">
            Investment Tip Message
          </label>
          <textarea
            id="tip-message"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={6}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 resize-none"
            placeholder="Paste the investment tip or message you want to analyze here..."
            disabled={loading}
          />
          <div className="flex justify-between mt-1">
            <span className="text-xs text-gray-500">
              {message.length}/5000 characters
            </span>
            {message.length > 0 && (
              <button
                type="button"
                onClick={handleClear}
                className="text-xs text-blue-600 hover:text-blue-800"
                disabled={loading}
              >
                Clear
              </button>
            )}
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        <div className="flex space-x-3">
          <button
            type="submit"
            disabled={loading || !message.trim()}
            className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <div className="flex items-center justify-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Analyzing...</span>
              </div>
            ) : (
              'Analyze Tip'
            )}
          </button>
        </div>
      </form>

      {/* Sample Tips Section */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <h3 className="text-sm font-medium text-gray-700 mb-3">
          Try these sample tips:
        </h3>
        <div className="space-y-2">
          {sampleTips.map((sample, index) => (
            <button
              key={index}
              type="button"
              onClick={() => handleSampleClick(sample)}
              disabled={loading}
              className="w-full text-left p-3 text-sm bg-gray-50 hover:bg-gray-100 rounded-md border border-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className="text-gray-600">Sample {index + 1}:</span>
              <span className="block mt-1 text-gray-800">{sample}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Disclaimer */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
        <p className="text-xs text-blue-800">
          <strong>Disclaimer:</strong> This analysis is for informational purposes only and should not be considered as financial advice. 
          Always conduct your own research and consult with qualified financial advisors before making investment decisions.
        </p>
      </div>
    </div>
  )
}

export default TipAnalysisForm