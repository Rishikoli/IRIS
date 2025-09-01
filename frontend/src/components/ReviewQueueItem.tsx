import React, { useState } from 'react'
import { QueueItem, ReviewDecision } from '../services/api'

interface ReviewQueueItemProps {
  item: QueueItem
  onReviewDecision: (reviewId: string, decision: ReviewDecision) => Promise<void>
  isLoading?: boolean
}

const ReviewQueueItem: React.FC<ReviewQueueItemProps> = ({
  item,
  onReviewDecision,
  isLoading = false
}) => {
  const [showDetails, setShowDetails] = useState(false)
  const [showDecisionForm, setShowDecisionForm] = useState(false)
  const [decision, setDecision] = useState<'approve' | 'override' | 'needs_more_info'>('approve')
  const [notes, setNotes] = useState('')
  const [humanDecision, setHumanDecision] = useState<Record<string, any>>({})
  const [submitting, setSubmitting] = useState(false)

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'High':
        return 'bg-red-100 text-red-800'
      case 'Medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'Low':
        return 'bg-green-100 text-green-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const handleSubmitDecision = async () => {
    if (submitting) return

    setSubmitting(true)
    try {
      const reviewDecision: ReviewDecision = {
        decision,
        notes: notes.trim() || undefined,
        human_decision: Object.keys(humanDecision).length > 0 ? humanDecision : undefined
      }

      await onReviewDecision(item.review_id, reviewDecision)
      setShowDecisionForm(false)
      setNotes('')
      setHumanDecision({})
    } catch (error) {
      console.error('Failed to submit review decision:', error)
    } finally {
      setSubmitting(false)
    }
  }

  const handleOverrideDecision = () => {
    if (item.case_type === 'assessment' && item.case_details.risk_level) {
      const currentLevel = item.case_details.risk_level
      const newLevel = currentLevel === 'High' ? 'Medium' : 
                      currentLevel === 'Medium' ? 'Low' : 'High'
      
      setHumanDecision({
        level: newLevel,
        score: currentLevel === 'High' ? 30 : 
               currentLevel === 'Medium' ? 10 : 80,
        override_reason: 'Human reviewer assessment'
      })
    } else if (item.case_type === 'pdf_check' && item.case_details.authenticity_score !== undefined) {
      const currentScore = item.case_details.authenticity_score
      const newScore = currentScore < 50 ? 80 : 20
      
      setHumanDecision({
        authenticity_score: newScore,
        is_likely_fake: newScore < 50,
        override_reason: 'Human reviewer assessment'
      })
    }
  }

  return (
    <div className="border border-gray-200 rounded-lg p-4 bg-white shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-3">
          <span className="text-sm font-medium text-gray-900">
            Case #{item.case_id.slice(-8)}
          </span>
          <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getPriorityColor(item.priority)}`}>
            {item.priority.charAt(0).toUpperCase() + item.priority.slice(1)} Priority
          </span>
          <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
            {item.case_type === 'assessment' ? 'Tip Analysis' : 
             item.case_type === 'pdf_check' ? 'PDF Check' : 'Fraud Chain'}
          </span>
        </div>
        <div className="flex items-center space-x-2">
          {item.ai_confidence && (
            <span className="text-sm text-gray-500">
              AI Confidence: {item.ai_confidence}%
            </span>
          )}
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            {showDetails ? 'Hide Details' : 'Show Details'}
          </button>
        </div>
      </div>

      {/* AI Decision Summary */}
      <div className="mb-3">
        <h4 className="text-sm font-medium text-gray-900 mb-2">AI Decision:</h4>
        {item.case_type === 'assessment' && (
          <div className="flex items-center space-x-3">
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getRiskLevelColor(item.case_details.risk_level || '')}`}>
              {item.case_details.risk_level} Risk
            </span>
            <span className="text-sm text-gray-600">
              Score: {item.case_details.risk_score}/100
            </span>
          </div>
        )}
        {item.case_type === 'pdf_check' && (
          <div className="flex items-center space-x-3">
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${
              item.case_details.is_likely_fake ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
            }`}>
              {item.case_details.is_likely_fake ? 'Likely Fake' : 'Likely Authentic'}
            </span>
            <span className="text-sm text-gray-600">
              Authenticity: {item.case_details.authenticity_score}/100
            </span>
          </div>
        )}
      </div>

      {/* Case Details */}
      {showDetails && (
        <div className="mb-4 p-3 bg-gray-50 rounded-md">
          <h5 className="text-sm font-medium text-gray-900 mb-2">Case Details:</h5>
          {item.case_type === 'assessment' && (
            <div className="space-y-2">
              <div>
                <span className="text-xs font-medium text-gray-700">Message:</span>
                <p className="text-xs text-gray-600 mt-1">{item.case_details.tip_message}</p>
              </div>
              {item.case_details.reasons && (
                <div>
                  <span className="text-xs font-medium text-gray-700">Reasons:</span>
                  <ul className="text-xs text-gray-600 mt-1 list-disc list-inside">
                    {item.case_details.reasons.map((reason, idx) => (
                      <li key={idx}>{reason}</li>
                    ))}
                  </ul>
                </div>
              )}
              {item.case_details.stock_symbols && item.case_details.stock_symbols.length > 0 && (
                <div>
                  <span className="text-xs font-medium text-gray-700">Stock Symbols:</span>
                  <span className="text-xs text-gray-600 ml-2">
                    {item.case_details.stock_symbols.join(', ')}
                  </span>
                </div>
              )}
            </div>
          )}
          {item.case_type === 'pdf_check' && (
            <div className="space-y-2">
              <div>
                <span className="text-xs font-medium text-gray-700">Filename:</span>
                <span className="text-xs text-gray-600 ml-2">{item.case_details.filename}</span>
              </div>
              {item.case_details.anomalies && item.case_details.anomalies.length > 0 && (
                <div>
                  <span className="text-xs font-medium text-gray-700">Detected Anomalies:</span>
                  <ul className="text-xs text-gray-600 mt-1 list-disc list-inside">
                    {item.case_details.anomalies.map((anomaly, idx) => (
                      <li key={idx}>{anomaly.description || anomaly.type}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
          <div className="mt-2 text-xs text-gray-500">
            Created: {new Date(item.case_details.created_at).toLocaleString()}
          </div>
        </div>
      )}

      {/* Decision Form */}
      {showDecisionForm && (
        <div className="mb-4 p-3 bg-blue-50 rounded-md border border-blue-200">
          <h5 className="text-sm font-medium text-gray-900 mb-3">Review Decision:</h5>
          
          <div className="space-y-3">
            <div>
              <label className="text-xs font-medium text-gray-700 block mb-1">Decision:</label>
              <select
                value={decision}
                onChange={(e) => {
                  setDecision(e.target.value as any)
                  if (e.target.value === 'override') {
                    handleOverrideDecision()
                  } else {
                    setHumanDecision({})
                  }
                }}
                className="w-full text-sm border border-gray-300 rounded-md px-2 py-1"
              >
                <option value="approve">Approve AI Decision</option>
                <option value="override">Override AI Decision</option>
                <option value="needs_more_info">Needs More Information</option>
              </select>
            </div>

            {decision === 'override' && Object.keys(humanDecision).length > 0 && (
              <div className="p-2 bg-yellow-50 border border-yellow-200 rounded">
                <span className="text-xs font-medium text-yellow-800">Override Decision:</span>
                <div className="text-xs text-yellow-700 mt-1">
                  {item.case_type === 'assessment' && humanDecision.level && (
                    <div>New Risk Level: {humanDecision.level} (Score: {humanDecision.score})</div>
                  )}
                  {item.case_type === 'pdf_check' && humanDecision.authenticity_score !== undefined && (
                    <div>New Authenticity Score: {humanDecision.authenticity_score}/100</div>
                  )}
                </div>
              </div>
            )}

            <div>
              <label className="text-xs font-medium text-gray-700 block mb-1">
                Notes {decision === 'override' ? '(Required)' : '(Optional)'}:
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder={decision === 'override' ? 'Please explain your reasoning for overriding the AI decision...' : 'Add any additional notes...'}
                className="w-full text-sm border border-gray-300 rounded-md px-2 py-1 h-20 resize-none"
                required={decision === 'override'}
              />
            </div>
          </div>

          <div className="flex space-x-2 mt-3">
            <button
              onClick={handleSubmitDecision}
              disabled={submitting || (decision === 'override' && !notes.trim())}
              className="px-3 py-1 text-xs font-medium bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? 'Submitting...' : 'Submit Decision'}
            </button>
            <button
              onClick={() => {
                setShowDecisionForm(false)
                setNotes('')
                setHumanDecision({})
                setDecision('approve')
              }}
              disabled={submitting}
              className="px-3 py-1 text-xs font-medium bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 disabled:opacity-50"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      {!showDecisionForm && (
        <div className="flex space-x-2">
          <button
            onClick={() => setShowDecisionForm(true)}
            disabled={isLoading}
            className="px-3 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-md hover:bg-blue-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Review Case
          </button>
          <button
            onClick={() => {
              setDecision('approve')
              setShowDecisionForm(true)
            }}
            disabled={isLoading}
            className="px-3 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-md hover:bg-green-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Quick Approve
          </button>
          <button
            onClick={() => {
              setDecision('override')
              handleOverrideDecision()
              setShowDecisionForm(true)
            }}
            disabled={isLoading}
            className="px-3 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-md hover:bg-red-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Quick Override
          </button>
        </div>
      )}
    </div>
  )
}

export default ReviewQueueItem