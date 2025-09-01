import React, { useState } from 'react'
import { advisorApi, AdvisorInfo, AdvisorVerificationResponse } from '../services/api'

interface AdvisorSearchFormProps {
  onSearch: (query: string) => void
  loading: boolean
}

const AdvisorSearchForm: React.FC<AdvisorSearchFormProps> = ({ onSearch, loading }) => {
  const [query, setQuery] = useState('')
  const [errors, setErrors] = useState<string[]>([])

  const validateInput = (input: string): string[] => {
    const validationErrors: string[] = []

    if (!input.trim()) {
      validationErrors.push('Please enter an advisor name or registration number')
    } else if (input.trim().length < 2) {
      validationErrors.push('Search query must be at least 2 characters long')
    } else if (input.trim().length > 200) {
      validationErrors.push('Search query must be less than 200 characters')
    }

    return validationErrors
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const validationErrors = validateInput(query)
    setErrors(validationErrors)

    if (validationErrors.length === 0) {
      onSearch(query.trim())
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setQuery(value)

    // Clear errors when user starts typing
    if (errors.length > 0) {
      setErrors([])
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="advisor-query" className="block text-sm font-medium text-gray-700 mb-2">
          Advisor Name or Registration Number
        </label>
        <input
          type="text"
          id="advisor-query"
          value={query}
          onChange={handleInputChange}
          className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 ${errors.length > 0
            ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
            : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
            }`}
          placeholder="Enter advisor name (e.g., 'Rajesh Kumar') or registration ID (e.g., 'INA000001234')"
          disabled={loading}
        />
        {errors.length > 0 && (
          <div className="mt-2">
            {errors.map((error, index) => (
              <p key={index} className="text-sm text-red-600">
                {error}
              </p>
            ))}
          </div>
        )}
      </div>

      <button
        type="submit"
        disabled={loading || query.trim().length < 2}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? (
          <span className="flex items-center justify-center">
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Searching...
          </span>
        ) : (
          'Verify Advisor'
        )}
      </button>
    </form>
  )
}

interface AdvisorCardProps {
  advisor: AdvisorInfo
  onViewDetails: (advisor: AdvisorInfo) => void
}

const AdvisorCard: React.FC<AdvisorCardProps> = ({ advisor, onViewDetails }) => {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'suspended':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'cancelled':
        return 'bg-red-100 text-red-800 border-red-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return '✓'
      case 'suspended':
        return '⚠'
      case 'cancelled':
        return '✗'
      default:
        return '?'
    }
  }

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    } catch {
      return dateString
    }
  }

  const getMatchScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600'
    if (score >= 0.5) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="bg-primary-900/30  border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-dark-primary mb-2">{advisor.name}</h3>
          <p className="text-sm text-gray-600 mb-2">
            Registration: <span className="font-mono">{advisor.registration_number}</span>
          </p>
          <p className="text-sm text-gray-600 mb-2">
            Category: <span className="font-medium">{advisor.category}</span>
          </p>
        </div>

        <div className="flex flex-col items-end space-y-2">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(advisor.status)}`}>
            <span className="mr-1">{getStatusIcon(advisor.status)}</span>
            {advisor.status.charAt(0).toUpperCase() + advisor.status.slice(1)}
          </span>

          <div className="text-right">
            <p className="text-xs text-gray-500">Match Score</p>
            <p className={`text-sm font-semibold ${getMatchScoreColor(advisor.match_score)}`}>
              {Math.round(advisor.match_score * 100)}%
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm text-gray-600 mb-4">
        <div>
          <p className="font-medium text-gray-700">Registration Date</p>
          <p>{formatDate(advisor.registration_date)}</p>
        </div>
        <div>
          <p className="font-medium text-gray-700">Valid Until</p>
          <p>{formatDate(advisor.validity_date)}</p>
        </div>
      </div>

      {advisor.compliance_score && (
        <div className="mb-4">
          <div className="flex justify-between items-center mb-1">
            <span className="text-sm font-medium text-gray-700">Compliance Score</span>
            <span className="text-sm font-semibold text-dark-primary">{advisor.compliance_score}/100</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${advisor.compliance_score >= 80 ? 'bg-green-500' :
                advisor.compliance_score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
              style={{ width: `${advisor.compliance_score}%` }}
            ></div>
          </div>
        </div>
      )}

      <button
        onClick={() => onViewDetails(advisor)}
        className="w-full text-blue-600 hover:text-blue-800 text-sm font-medium py-2 border border-blue-200 rounded-md hover:bg-blue-50 transition-colors"
      >
        View Details
      </button>
    </div>
  )
}

interface AdvisorDetailsModalProps {
  advisor: AdvisorInfo | null
  onClose: () => void
}

const AdvisorDetailsModal: React.FC<AdvisorDetailsModalProps> = ({ advisor, onClose }) => {
  if (!advisor) return null

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    } catch {
      return dateString
    }
  }

  const getStatusMessage = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'This advisor is currently registered and authorized to provide financial services.'
      case 'suspended':
        return 'This advisor is temporarily suspended by SEBI. Exercise caution before engaging their services.'
      case 'cancelled':
        return 'This advisor\'s registration has been cancelled or revoked. Do not engage their services.'
      default:
        return 'Status information is not available.'
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-primary-900/30  rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-start mb-6">
            <h2 className="text-2xl font-bold text-dark-primary">Advisor Details</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
            >
              ×
            </button>
          </div>

          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-dark-primary mb-2">{advisor.name}</h3>
              <p className="text-gray-600">Registration Number: <span className="font-mono font-medium">{advisor.registration_number}</span></p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Registration Information</h4>
                <div className="space-y-2 text-sm">
                  <p><span className="font-medium">Category:</span> {advisor.category}</p>
                  <p><span className="font-medium">Registration Date:</span> {formatDate(advisor.registration_date)}</p>
                  <p><span className="font-medium">Valid Until:</span> {formatDate(advisor.validity_date)}</p>
                </div>
              </div>

              <div>
                <h4 className="font-medium text-gray-700 mb-2">Status & Compliance</h4>
                <div className="space-y-2 text-sm">
                  <p>
                    <span className="font-medium">Status:</span>
                    <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${advisor.status === 'active' ? 'bg-green-100 text-green-800' :
                      advisor.status === 'suspended' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                      {advisor.status.charAt(0).toUpperCase() + advisor.status.slice(1)}
                    </span>
                  </p>
                  {advisor.compliance_score && (
                    <p><span className="font-medium">Compliance Score:</span> {advisor.compliance_score}/100</p>
                  )}
                </div>
              </div>
            </div>

            {advisor.contact_info && (
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Contact Information</h4>
                <div className="space-y-2 text-sm">
                  {advisor.contact_info.email && (
                    <p><span className="font-medium">Email:</span> {advisor.contact_info.email}</p>
                  )}
                  {advisor.contact_info.phone && (
                    <p><span className="font-medium">Phone:</span> {advisor.contact_info.phone}</p>
                  )}
                  {advisor.contact_info.address && (
                    <p><span className="font-medium">Address:</span> {advisor.contact_info.address}</p>
                  )}
                </div>
              </div>
            )}

            <div className={`p-4 rounded-lg border ${advisor.status === 'active' ? 'bg-green-50 border-green-200' :
              advisor.status === 'suspended' ? 'bg-yellow-50 border-yellow-200' :
                'bg-red-50 border-red-200'
              }`}>
              <p className={`text-sm ${advisor.status === 'active' ? 'text-green-800' :
                advisor.status === 'suspended' ? 'text-yellow-800' :
                  'text-red-800'
                }`}>
                <strong>Status Information:</strong> {getStatusMessage(advisor.status)}
              </p>
            </div>
          </div>

          <div className="mt-6 flex justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

const VerifyAdvisorPage = () => {
  const [loading, setLoading] = useState(false)
  const [searchResults, setSearchResults] = useState<AdvisorVerificationResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [selectedAdvisor, setSelectedAdvisor] = useState<AdvisorInfo | null>(null)
  const [sortBy, setSortBy] = useState<'match_score' | 'compliance_score' | 'name'>('match_score')
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'suspended' | 'cancelled'>('all')

  const handleSearch = async (query: string) => {
    setLoading(true)
    setError(null)
    setSearchResults(null)

    try {
      const response = await advisorApi.verifyAdvisor({
        query,
        limit: 20,
        min_score: 0.1,
        include_cache_info: false
      })

      setSearchResults(response.data)
    } catch (err: any) {
      console.error('Advisor verification error:', err)
      setError(
        err.response?.data?.detail ||
        err.message ||
        'An error occurred while searching for advisors. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleViewDetails = (advisor: AdvisorInfo) => {
    setSelectedAdvisor(advisor)
  }

  const handleCloseModal = () => {
    setSelectedAdvisor(null)
  }

  const getSortedAndFilteredAdvisors = () => {
    if (!searchResults?.advisors) return []

    let filtered = searchResults.advisors

    // Apply status filter
    if (filterStatus !== 'all') {
      filtered = filtered.filter(advisor => advisor.status === filterStatus)
    }

    // Apply sorting
    return filtered.sort((a, b) => {
      switch (sortBy) {
        case 'match_score':
          return b.match_score - a.match_score
        case 'compliance_score':
          return (b.compliance_score || 0) - (a.compliance_score || 0)
        case 'name':
          return a.name.localeCompare(b.name)
        default:
          return 0
      }
    })
  }

  const sortedAdvisors = getSortedAndFilteredAdvisors()

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-primary-900/30  rounded-lg shadow-md p-8 mb-6">
        <h1 className="text-3xl font-bold text-dark-primary mb-6">
          Advisor Verification
        </h1>
        <p className="text-gray-600 mb-8">
          Verify if a financial advisor is registered with SEBI. Search by name or registration number to check their current status and credentials.
        </p>

        <AdvisorSearchForm onSearch={handleSearch} loading={loading} />
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Search Error</h3>
              <p className="mt-1 text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {searchResults && (
        <div className="bg-primary-900/30  rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-xl font-semibold text-dark-primary">Search Results</h2>
              <p className="text-gray-600 mt-1">{searchResults.message}</p>
            </div>

            {searchResults.advisors.length > 1 && (
              <div className="flex space-x-4">
                <div>
                  <label htmlFor="filter-status" className="block text-sm font-medium text-gray-700 mb-1">
                    Filter by Status
                  </label>
                  <select
                    id="filter-status"
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value as any)}
                    className="text-sm border border-gray-300 rounded-md px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="all">All Status</option>
                    <option value="active">Active</option>
                    <option value="suspended">Suspended</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="sort-by" className="block text-sm font-medium text-gray-700 mb-1">
                    Sort by
                  </label>
                  <select
                    id="sort-by"
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as any)}
                    className="text-sm border border-gray-300 rounded-md px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="match_score">Match Score</option>
                    <option value="compliance_score">Compliance Score</option>
                    <option value="name">Name</option>
                  </select>
                </div>
              </div>
            )}
          </div>

          {sortedAdvisors.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-gray-400 mb-4">
                <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 20.4a7.962 7.962 0 01-8-7.109C4 11.27 6.145 9.4 8.5 9.4L12 6l3.5 3.4c2.355 0 4.5 1.87 4.5 4.291z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-dark-primary mb-2">No advisors found</h3>
              <p className="text-gray-600">
                {filterStatus !== 'all'
                  ? `No ${filterStatus} advisors match your search criteria.`
                  : 'No advisors match your search criteria. Please try a different name or registration number.'
                }
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {sortedAdvisors.map((advisor) => (
                <AdvisorCard
                  key={advisor.id}
                  advisor={advisor}
                  onViewDetails={handleViewDetails}
                />
              ))}
            </div>
          )}
        </div>
      )}

      <AdvisorDetailsModal
        advisor={selectedAdvisor}
        onClose={handleCloseModal}
      />
    </div>
  )
}

export default VerifyAdvisorPage