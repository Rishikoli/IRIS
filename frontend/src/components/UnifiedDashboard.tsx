import React, { useState, useEffect, useMemo } from 'react'
import IndiaHeatmap from './IndiaHeatmap'
import ForecastVisualization from './ForecastVisualization'
import ForecastSidebar from './ForecastSidebar'
import DashboardFilters from './DashboardFilters'
import TrendIndicators from './TrendIndicators'
import { heatmapApi, forecastApi, FraudHeatmapResponse, ForecastResponse, ForecastItem } from '../services/api'
import customIndiaMap from '../maps/customIndiaMap'

interface UnifiedDashboardProps {
  onHeatmapCellClick?: (key: string) => void
}

const UnifiedDashboard: React.FC<UnifiedDashboardProps> = ({ onHeatmapCellClick }) => {
  // View state
  const [activeView, setActiveView] = useState<'current' | 'forecast' | 'unified'>('unified')

  // Filter state
  const [dimension, setDimension] = useState<'sector' | 'region'>('sector')
  const [period, setPeriod] = useState<'daily' | 'weekly' | 'monthly'>('weekly')
  const [fromDate, setFromDate] = useState(() => {
    const date = new Date()
    date.setDate(date.getDate() - 30)
    return date.toISOString().split('T')[0]
  })
  const [toDate, setToDate] = useState(() => {
    return new Date().toISOString().split('T')[0]
  })

  // Heatmap state
  const [heatmapData, setHeatmapData] = useState<FraudHeatmapResponse | null>(null)
  const [heatmapLoading, setHeatmapLoading] = useState(false)
  const [heatmapError, setHeatmapError] = useState<string | null>(null)

  // Forecast state
  const [forecastData, setForecastData] = useState<ForecastResponse | null>(null)
  const [forecastLoading, setForecastLoading] = useState(false)
  const [forecastError, setForecastError] = useState<string | null>(null)
  const [selectedForecast, setSelectedForecast] = useState<ForecastItem | null>(null)

  // Forecast period selection
  const [forecastPeriod, setForecastPeriod] = useState(() => {
    const nextMonth = new Date()
    nextMonth.setMonth(nextMonth.getMonth() + 1)
    return nextMonth.toISOString().slice(0, 7) // YYYY-MM format
  })

  // Fetch heatmap data
  const fetchHeatmapData = async () => {
    setHeatmapLoading(true)
    setHeatmapError(null)

    try {
      const response = await heatmapApi.getFraudHeatmap({
        dimension,
        period,
        from_date: fromDate,
        to_date: toDate
      })
      setHeatmapData(response.data)
    } catch (err: any) {
      console.error('Error fetching heatmap data:', err)
      setHeatmapError(
        err.response?.data?.detail ||
        'Failed to load heatmap data. Please try again later.'
      )
    } finally {
      setHeatmapLoading(false)
    }
  }

  // Fetch forecast data
  const fetchForecastData = async (regenerate = false) => {
    setForecastLoading(true)
    setForecastError(null)

    try {
      const response = await forecastApi.getForecast({
        dimension,
        period: forecastPeriod,
        regenerate
      })
      setForecastData(response.data)

      // Auto-select first forecast item if none selected
      if (!selectedForecast && response.data.forecasts.length > 0) {
        setSelectedForecast(response.data.forecasts[0])
      }
    } catch (err: any) {
      console.error('Error fetching forecast data:', err)
      setForecastError(
        err.response?.data?.detail ||
        'Failed to load forecast data. Please try again later.'
      )
    } finally {
      setForecastLoading(false)
    }
  }

  // Load data on component mount and filter changes
  useEffect(() => {
    fetchHeatmapData()
  }, [dimension, period, fromDate, toDate])

  useEffect(() => {
    fetchForecastData()
  }, [dimension, forecastPeriod])

  // Handle forecast item selection
  const handleForecastItemClick = (key: string) => {
    const forecast = forecastData?.forecasts.find(f => f.key === key)
    if (forecast) {
      setSelectedForecast(forecast)
    }
  }

  // Generate available forecast periods (next 6 months) - memoized to prevent regeneration
  const forecastPeriods = useMemo(() => {
    const periods = []
    const current = new Date()
    for (let i = 1; i <= 6; i++) {
      const date = new Date(current)
      date.setMonth(date.getMonth() + i)
      periods.push({
        value: date.toISOString().slice(0, 7),
        label: date.toLocaleDateString('en-US', { year: 'numeric', month: 'long' })
      })
    }
    return periods
  }, [])

  const viewTabs = [
    { id: 'unified', name: 'Unified View', icon: '🔄' },
    { id: 'current', name: 'Current Patterns', icon: '📊' },
    { id: 'forecast', name: 'AI Forecasts', icon: '🔮' }
  ]

  return (
    <div className="space-y-6">
      {/* Dashboard Filters */}
      <DashboardFilters
        dimension={dimension}
        period={period}
        fromDate={fromDate}
        toDate={toDate}
        onDimensionChange={setDimension}
        onPeriodChange={setPeriod}
        onFromDateChange={setFromDate}
        onToDateChange={setToDate}
        onRefresh={() => {
          fetchHeatmapData()
          fetchForecastData()
        }}
        loading={heatmapLoading || forecastLoading}
      />

      {/* View Toggle */}
      <div className="bg-primary-900/30 rounded-lg shadow-md p-4">
        <div className="flex items-center justify-between">
          <div className="flex space-x-1">
            {viewTabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveView(tab.id as any)}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${activeView === tab.id
                  ? 'bg-blue-600 text-white'
                  : 'text-blue-200 hover:text-white hover:bg-blue-800'
                  }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </div>

          {/* Forecast Period Selector */}
          {(activeView === 'forecast' || activeView === 'unified') && (
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-blue-200">
                Forecast Period:
              </label>
              <select
                value={forecastPeriod}
                onChange={(e) => setForecastPeriod(e.target.value)}
                className="text-sm border border-blue-600 bg-blue-800 text-white rounded-md px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-400"
              >
                {forecastPeriods.map((periodOption) => (
                  <option key={periodOption.value} value={periodOption.value}>
                    {periodOption.label}
                  </option>
                ))}
              </select>
              <button
                onClick={() => fetchForecastData(true)}
                disabled={forecastLoading}
                className="text-sm bg-blue-600 text-white px-3 py-1 rounded-md hover:bg-blue-500 disabled:opacity-50"
              >
                {forecastLoading ? 'Generating...' : 'Regenerate'}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Statistics Overview */}
      {heatmapData && (
        <TrendIndicators stats={heatmapData.stats} />
      )}

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Visualization Area */}
        <div className={`${activeView === 'unified' ? 'lg:col-span-3' : 'lg:col-span-4'} space-y-6`}>
          {/* Current Patterns View */}
          {(activeView === 'current' || activeView === 'unified') && (
            <div>
              {heatmapError && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">❌</span>
                    <div>
                      <h3 className="text-lg font-semibold text-red-900">Failed to Load Current Data</h3>
                      <p className="text-red-700">{heatmapError}</p>
                    </div>
                  </div>
                  <button
                    onClick={fetchHeatmapData}
                    className="mt-4 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
                  >
                    Retry
                  </button>
                </div>
              )}

              {heatmapLoading && !heatmapData && (
                <div className="bg-primary-900 rounded-lg shadow-md p-12">
                  <div className="flex items-center justify-center space-x-3">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
                    <span className="text-lg text-blue-200">Loading current fraud patterns...</span>
                  </div>
                </div>
              )}

              {heatmapData && !heatmapError && (
                <IndiaHeatmap
                  data={heatmapData.data}
                  dimension={dimension}
                  onCellClick={onHeatmapCellClick}
                  customSvg={customIndiaMap}
                />
              )}
            </div>
          )}

          {/* Forecast View */}
          {(activeView === 'forecast' || activeView === 'unified') && (
            <div>
              {forecastError && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">❌</span>
                    <div>
                      <h3 className="text-lg font-semibold text-red-900">Failed to Load Forecast Data</h3>
                      <p className="text-red-700">{forecastError}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => fetchForecastData()}
                    className="mt-4 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
                  >
                    Retry
                  </button>
                </div>
              )}

              {forecastLoading && !forecastData && (
                <div className="bg-primary-900 rounded-lg shadow-md p-12">
                  <div className="flex items-center justify-center space-x-3">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
                    <span className="text-lg text-blue-200">Generating AI forecasts...</span>
                  </div>
                </div>
              )}

              {forecastData && !forecastError && (
                <ForecastVisualization
                  forecasts={forecastData.forecasts}
                  dimension={dimension}
                  showConfidenceIntervals={true}
                  onItemClick={handleForecastItemClick}
                />
              )}
            </div>
          )}
        </div>

        {/* Sidebar for Unified View */}
        {activeView === 'unified' && (
          <div className="lg:col-span-1">
            <ForecastSidebar
              selectedForecast={selectedForecast}
              accuracyMetrics={forecastData?.accuracy_metrics || {
                overall_accuracy: 0,
                high_risk_precision: 0,
                medium_risk_precision: 0,
                low_risk_precision: 0,
                trend_accuracy: 0,
                confidence_calibration: 0
              }}
            />
          </div>
        )}
      </div>

      {/* Navigation Helper */}
      {activeView === 'unified' && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <div className="text-blue-600 text-xl">💡</div>
            <div>
              <h4 className="font-medium text-blue-900 mb-1">Unified Dashboard Navigation</h4>
              <p className="text-sm text-blue-800">
                The heatmap shows current fraud patterns, while the forecast chart predicts future risks.
                Click on forecast bars to see detailed AI analysis in the sidebar.
                Use the view toggle to focus on current patterns or forecasts individually.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default UnifiedDashboard