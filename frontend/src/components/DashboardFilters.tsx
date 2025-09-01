import React from 'react'

interface DashboardFiltersProps {
  dimension: 'sector' | 'region'
  period: 'daily' | 'weekly' | 'monthly'
  fromDate: string
  toDate: string
  onDimensionChange: (dimension: 'sector' | 'region') => void
  onPeriodChange: (period: 'daily' | 'weekly' | 'monthly') => void
  onFromDateChange: (date: string) => void
  onToDateChange: (date: string) => void
  onRefresh: () => void
  loading?: boolean
}

const DashboardFilters: React.FC<DashboardFiltersProps> = ({
  dimension,
  period,
  fromDate,
  toDate,
  onDimensionChange,
  onPeriodChange,
  onFromDateChange,
  onToDateChange,
  onRefresh,
  loading = false
}) => {
  return (
    <div className="bg-primary-900/30  rounded-lg shadow-md p-6 mb-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-4">
          {/* Dimension Toggle */}
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">View by:</label>
            <div className="flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => onDimensionChange('sector')}
                className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                  dimension === 'sector'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:text-dark-primary'
                }`}
              >
                Sector
              </button>
              <button
                onClick={() => onDimensionChange('region')}
                className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                  dimension === 'region'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:text-dark-primary'
                }`}
              >
                Region
              </button>
            </div>
          </div>

          {/* Period Filter */}
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Period:</label>
            <select
              value={period}
              onChange={(e) => onPeriodChange(e.target.value as 'daily' | 'weekly' | 'monthly')}
              className="px-3 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>

          {/* Date Range */}
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">From:</label>
            <input
              type="date"
              value={fromDate}
              onChange={(e) => onFromDateChange(e.target.value)}
              className="px-3 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">To:</label>
            <input
              type="date"
              value={toDate}
              onChange={(e) => onToDateChange(e.target.value)}
              className="px-3 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        {/* Refresh Button */}
        <button
          onClick={onRefresh}
          disabled={loading}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Loading...</span>
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>Refresh</span>
            </>
          )}
        </button>
      </div>

      {/* Quick Filters */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-700">Quick filters:</span>
          <button
            onClick={() => {
              const today = new Date()
              const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
              onFromDateChange(lastWeek.toISOString().split('T')[0])
              onToDateChange(today.toISOString().split('T')[0])
              onPeriodChange('daily')
            }}
            className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
          >
            Last 7 days
          </button>
          <button
            onClick={() => {
              const today = new Date()
              const lastMonth = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
              onFromDateChange(lastMonth.toISOString().split('T')[0])
              onToDateChange(today.toISOString().split('T')[0])
              onPeriodChange('weekly')
            }}
            className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
          >
            Last 30 days
          </button>
          <button
            onClick={() => {
              const today = new Date()
              const lastQuarter = new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000)
              onFromDateChange(lastQuarter.toISOString().split('T')[0])
              onToDateChange(today.toISOString().split('T')[0])
              onPeriodChange('monthly')
            }}
            className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
          >
            Last 3 months
          </button>
        </div>
      </div>
    </div>
  )
}

export default DashboardFilters