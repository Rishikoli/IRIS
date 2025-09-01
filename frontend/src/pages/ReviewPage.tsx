import { useState, useEffect } from 'react'
import { reviewApi, QueueItem, ReviewDecision, ReviewStatistics } from '../services/api'
import ReviewQueueItem from '../components/ReviewQueueItem'

const ReviewPage = () => {
  const [queueItems, setQueueItems] = useState<QueueItem[]>([])
  const [statistics, setStatistics] = useState<ReviewStatistics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState({
    sortBy: 'priority' as 'priority' | 'confidence' | 'date',
    caseType: 'all' as 'all' | 'assessment' | 'pdf_check',
    priority: 'all' as 'all' | 'high' | 'medium' | 'low'
  })
  const [pagination, setPagination] = useState({
    skip: 0,
    limit: 20
  })
  const [submittingReview, setSubmittingReview] = useState<string | null>(null)

  const loadReviewQueue = async () => {
    try {
      setLoading(true)
      setError(null)

      const params: any = {
        skip: pagination.skip,
        limit: pagination.limit,
        sort_by: filters.sortBy
      }

      const response = await reviewApi.getReviewQueue(params)
      let filteredItems = response.data

      // Apply client-side filters
      if (filters.caseType !== 'all') {
        filteredItems = filteredItems.filter(item => item.case_type === filters.caseType)
      }
      if (filters.priority !== 'all') {
        filteredItems = filteredItems.filter(item => item.priority === filters.priority)
      }

      setQueueItems(filteredItems)
    } catch (err) {
      console.error('Failed to load review queue:', err)
      setError('Failed to load review queue. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const loadStatistics = async () => {
    try {
      const response = await reviewApi.getStatistics()
      setStatistics(response.data)
    } catch (err) {
      console.error('Failed to load statistics:', err)
    }
  }

  const queueLowConfidenceCases = async () => {
    try {
      const response = await reviewApi.queueLowConfidenceCases({
        confidence_threshold: 70,
        authenticity_threshold: 30
      })
      
      alert(`Queued ${response.data.total_queued} cases for review (${response.data.assessments_queued} assessments, ${response.data.pdf_checks_queued} PDF checks)`)
      
      // Reload the queue
      await loadReviewQueue()
      await loadStatistics()
    } catch (err) {
      console.error('Failed to queue low confidence cases:', err)
      alert('Failed to queue low confidence cases. Please try again.')
    }
  }

  const handleReviewDecision = async (reviewId: string, decision: ReviewDecision) => {
    try {
      setSubmittingReview(reviewId)
      
      await reviewApi.updateReviewDecision(reviewId, decision)
      
      // Remove the reviewed item from the queue
      setQueueItems(prev => prev.filter(item => item.review_id !== reviewId))
      
      // Reload statistics to reflect the change
      await loadStatistics()
      
    } catch (err) {
      console.error('Failed to submit review decision:', err)
      throw err // Re-throw to let the component handle the error
    } finally {
      setSubmittingReview(null)
    }
  }

  useEffect(() => {
    loadReviewQueue()
    loadStatistics()
  }, [pagination, filters.sortBy])

  useEffect(() => {
    // Reset pagination when filters change
    setPagination(prev => ({ ...prev, skip: 0 }))
  }, [filters.caseType, filters.priority])

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const handleLoadMore = () => {
    setPagination(prev => ({ ...prev, skip: prev.skip + prev.limit }))
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-dark-primary mb-2">
          Human-in-the-Loop Review
        </h1>
        <p className="text-gray-600">
          Review AI decisions and provide overrides with explanations.
        </p>
      </div>

      {/* Statistics Dashboard */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h3 className="text-sm font-medium text-gray-500 mb-1">Total Reviews</h3>
            <p className="text-2xl font-bold text-gray-900">{statistics.total_reviews}</p>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h3 className="text-sm font-medium text-gray-500 mb-1">Pending Reviews</h3>
            <p className="text-2xl font-bold text-yellow-600">{statistics.pending_reviews}</p>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h3 className="text-sm font-medium text-gray-500 mb-1">Completed Reviews</h3>
            <p className="text-2xl font-bold text-green-600">{statistics.completed_reviews}</p>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h3 className="text-sm font-medium text-gray-500 mb-1">Override Rate</h3>
            <p className="text-2xl font-bold text-red-600">{statistics.ai_vs_human.override_rate.toFixed(1)}%</p>
          </div>
        </div>
      )}

      {/* AI vs Human Comparison */}
      {statistics && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">AI vs Human Decision Comparison</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{statistics.ai_vs_human.ai_approved}</div>
              <div className="text-sm text-gray-500">AI Decisions Approved</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{statistics.ai_vs_human.human_overridden}</div>
              <div className="text-sm text-gray-500">AI Decisions Overridden</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {statistics.ai_vs_human.ai_approved + statistics.ai_vs_human.human_overridden > 0 
                  ? ((statistics.ai_vs_human.ai_approved / (statistics.ai_vs_human.ai_approved + statistics.ai_vs_human.human_overridden)) * 100).toFixed(1)
                  : 0}%
              </div>
              <div className="text-sm text-gray-500">AI Accuracy Rate</div>
            </div>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          {/* Filters */}
          <div className="flex flex-wrap items-center space-x-4">
            <div>
              <label className="text-sm font-medium text-gray-700 mr-2">Sort by:</label>
              <select
                value={filters.sortBy}
                onChange={(e) => handleFilterChange('sortBy', e.target.value)}
                className="text-sm border border-gray-300 rounded-md px-2 py-1"
              >
                <option value="priority">Priority</option>
                <option value="confidence">AI Confidence</option>
                <option value="date">Date Created</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 mr-2">Case Type:</label>
              <select
                value={filters.caseType}
                onChange={(e) => handleFilterChange('caseType', e.target.value)}
                className="text-sm border border-gray-300 rounded-md px-2 py-1"
              >
                <option value="all">All Types</option>
                <option value="assessment">Tip Analysis</option>
                <option value="pdf_check">PDF Check</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 mr-2">Priority:</label>
              <select
                value={filters.priority}
                onChange={(e) => handleFilterChange('priority', e.target.value)}
                className="text-sm border border-gray-300 rounded-md px-2 py-1"
              >
                <option value="all">All Priorities</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
          </div>

          {/* Actions */}
          <div className="flex space-x-2">
            <button
              onClick={queueLowConfidenceCases}
              className="px-4 py-2 text-sm font-medium bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Queue Low Confidence Cases
            </button>
            <button
              onClick={() => {
                loadReviewQueue()
                loadStatistics()
              }}
              className="px-4 py-2 text-sm font-medium bg-gray-600 text-white rounded-md hover:bg-gray-700"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Review Queue */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-dark-primary">
            Review Queue ({queueItems.length} items)
          </h2>
        </div>
        
        <div className="p-6">
          {loading && (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-gray-600">Loading review queue...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
              <p className="text-red-800">{error}</p>
              <button
                onClick={loadReviewQueue}
                className="mt-2 px-3 py-1 text-sm bg-red-100 text-red-800 rounded-md hover:bg-red-200"
              >
                Retry
              </button>
            </div>
          )}

          {!loading && !error && queueItems.length === 0 && (
            <div className="text-center py-8">
              <div className="text-gray-400 mb-2">
                <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-1">No items in review queue</h3>
              <p className="text-gray-600 mb-4">All cases have been reviewed or there are no low-confidence cases to review.</p>
              <button
                onClick={queueLowConfidenceCases}
                className="px-4 py-2 text-sm font-medium bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Queue Low Confidence Cases
              </button>
            </div>
          )}

          {!loading && !error && queueItems.length > 0 && (
            <div className="space-y-4">
              {queueItems.map((item) => (
                <ReviewQueueItem
                  key={item.review_id}
                  item={item}
                  onReviewDecision={handleReviewDecision}
                  isLoading={submittingReview === item.review_id}
                />
              ))}

              {/* Load More Button */}
              {queueItems.length >= pagination.limit && (
                <div className="text-center pt-4">
                  <button
                    onClick={handleLoadMore}
                    className="px-4 py-2 text-sm font-medium bg-gray-600 text-white rounded-md hover:bg-gray-700"
                  >
                    Load More
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ReviewPage